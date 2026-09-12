from flask import Flask, render_template, jsonify, request, session
import database as db
from validation import validate_name, validate_stock, validate_value
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

app = Flask(__name__)
app.secret_key = "viuewhfu934hfewh82hjfdhw8r"
db.create_table()
db.create_sales_table()
db.create_users_table()
db.create_activity_log_table()

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return jsonify({"message" : "please login"}),401
        return func(*args, **kwargs)
    return wrapper


@app.route("/")                                 
def home():
    return render_template("home.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/reports")
def reports():
    return render_template("reports.html")

@app.route("/accountsetting")
def accountsetting():
    return render_template("accountsetting.html")

@app.route("/api/session-status", methods = ["GET"])
def session_status():
    return jsonify({
        "logged_in" : bool(session.get("logged_in")),
        "username" : session.get("username")
    })


@app.route("/api/items")                                
def get_items():
    rows = db.load_all_items()
    items_lst = []
    for row in rows:
        items_lst.append({
            "name" : row[0],
            "stock" : row[1],
            "value" : row[2]
        })
    return jsonify(items_lst)

@app.route("/api/items", methods = ["POST"])             
@login_required
def  add_item():
    data = request.get_json()
    username = session["username"]
    if not validate_name(data.get("name")):
        return jsonify({"message" : "invalid name entered"}),400
    if not validate_stock(data.get("stock")):
        return jsonify({"message" : "invalid stock entered"}),400
    if not validate_value(data.get("value")):
        return jsonify({"message" : "invalid value entered"}),400
    name = data.get("name")
    stock = data.get("stock")
    value = data.get("value")
    existing = db.get_item_by_name(name)
    if(existing):
        new_stock = existing[1] + stock
        db.update_item(name, new_stock=new_stock)
        db.record_activity(
            username,
            "item_restocked",
            name,
            f"restocked {stock}x {name}"
        )
        message = "item restocked"
    else:
        db.save_item(name, stock, value)
        db.record_activity(
            username,
            "item_added",
            name,
            f"added {stock}x {name} {value} each"
        )
        message = "item added"
    item = db.get_item_by_name(name)

    return jsonify({
        "message" : message,
        "item" : {"name" : item[0], "stock" : item[1], "value" : item[2]}
        }), 201

@app.route("/api/items/<name>", methods = ["DELETE"])        
@login_required
def delete_item(name):
    username = session["username"]
    rows = db.load_all_items()
    if not any(row[0] == name for row in rows):
        return jsonify({"error" : "item not found"}),404
    db.delete_item_from_db(name)
    db.record_activity(
        username,
        "ited_deleted",
        name,
        f"deleted {name}"
    )
    return jsonify({"message" : "item deleted"}),200

@app.route("/api/items/<name>", methods = ["PUT"])            
@login_required
def edit_item(name):
    data = request.get_json()
    if not validate_name(data.get("name")):
        return jsonify({"message" : "invalid name entered"}),400
    if not validate_stock(data.get("stock")):
        return jsonify({"message" : "invalid stock entered"}),400
    if not validate_value(data.get("value")):
        return jsonify({"message" : "invalid value entered"}),400
    username = session["username"]
    old_item = db.get_item_by_name(name)
    if not old_item:
        return jsonify({"message" : "item not found"}),404
    old_name, old_stock, old_value = old_item
    new_name = data.get("name")
    new_stock = data.get("stock")
    new_value = data.get("value")
    success = db.update_item(
        name,
        data.get("name"),
        data.get("stock"),
        data.get("value")
    )
    changes = []
    if new_name != old_name:
      changes.append(f'changed name from {old_name} to {new_name}')
    if new_stock != old_stock:
      changes.append(f"changed stock from {old_stock} to {new_stock}")
    if new_value != old_value:
      changes.append(f"changed price from Rs. {old_value} to Rs. {new_value}")
      if(changes):
        db.record_activity(
            username,
            "item_updated",
            new_name,
            "; ".join(changes)
        )
    if not success:
        return jsonify({"message": "item not found"}), 404

    return jsonify({"message": "item updated"}), 200

@app.route("/api/items/<name>/sell", methods = ["POST"])
@login_required
def sell_item(name):
    username = session["username"]
    data = request.get_json()
    if not validate_name(name):
        return jsonify({"message" : "invalid name entered"}),400
    if not validate_stock(data.get("quantity")):
        return jsonify({"message" : "invalid quantity"}),400
    item = db.get_item_by_name(name)
    if not item:
        return jsonify({"message" : "item not found"}),404
    if item[1] < data.get("quantity"):
        return jsonify({"message" : "insufficient stock"}),400
    remaining = item[1] - data.get("quantity")
    db.update_item(name, new_stock= remaining)
    db.record_sale(name, data.get("quantity"), item[2], username)
    db.record_activity(
        username,
        "item_sold",
        name,
        f"Sold {data.get('quantity')} units at Rs. {item[2]} each "
    )
    return jsonify({"message" : "item sold", "stock" : remaining}),200

@app.route("/api/sales", methods = ["GET"])
def get_sales():
    sales = db.get_all_sales()
    sales_list = []
    for sale in sales:
        sales_list.append({
            "id" : sale[0],
            "name" : sale[1],
            "quantity" : sale[2],
            "price" : sale[3],
            "timestamp" : sale[4]
        })
    return jsonify(sales_list)

@app.route("/api/login", methods = ["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = db.get_user_by_username(username)
    if user is None:
        return jsonify({"message" : "invalid username or password"}),401
    if check_password_hash(user[2], password):
        session["logged_in"] = True
        session["username"] = username
        return jsonify({"message" : "logged in successfully"}),200
    else:
        return jsonify({"message" : "invalid username or password"}),401


@app.route("/api/signup", methods = ["POST"])
def signup():
    try:
        data = request.get_json()
        fullname = data.get("fullname")
        dob = data.get("dob")
        email = data.get("email")
        username = data.get("username")
        passwordhash = generate_password_hash(data.get("password"))

        existing_user = db.get_user_by_username(username)
        if existing_user:
            return jsonify({"message" : "username already taken"}), 400
        existing_email = db.get_user_by_email(email)
        if existing_email:
            return jsonify({"message" : "email already registered"}), 400
        
        if db.create_user(username, passwordhash, fullname, email, dob, timestamp):
            session["logged_in"] = True
            session["username"] = username
            return jsonify({"message" : "signed up successfully"}), 200
        else:
            return jsonify({"message" : "failed to sign up"}), 400
    except Exception as e:
        print(f"error: {e}")
        return jsonify({"message" : "Internal server error"}), 500



@app.route("/api/logout", methods = ["POST"])
def logout():
    session.clear()
    return jsonify({"message" : "logged out successfully"}), 200


@app.route("/api/dashboard/stats")
@login_required
def dashboard_stats():
    start = request.args.get("start")
    end = request.args.get("end")

    if not start or not end:
        return jsonify({"message": "A start and end date are required"}), 400

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"message": "Dates must use the YYYY-MM-DD format"}), 400

    if start_date > end_date:
        return jsonify({"message": "The start date cannot be after the end date"}), 400

    sales = db.get_sales_by_range(
        start_date.strftime("%Y-%m-%d 00:00:00"),
        end_date.strftime("%Y-%m-%d 23:59:59")
    )
    total_sales_value = sum(quantity * price for _, _, quantity, price, _ , _ in sales)
    items = db.load_all_items()
    low_stock_items = [
        {"name": name, "stock": stock}
        for name, stock, _ in items
        if stock < 10
    ]

    return jsonify({
        "total_sales_count": len(sales),
        "total_sales_value": total_sales_value,
        "total_items": len(items),
        "low_stock_count": len(low_stock_items),
        "low_stock_items": low_stock_items
    })

@app.route("/api/activities")
def get_activities():
    rows = db.get_recent_activities()
    activities = []
    for row in rows:
        activities.append({
            "id" : row[0],
            "username" : row[1],
            "action" : row[2],
            "item_name" : row[3],
            "details" : row[4],
            "timestamp" : row[5]
        })
    return jsonify(activities)
if __name__ == "__main__": 
    app.run(debug=True)

