import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from config import DevConfig, ProdConfig
import database as db
from validation import validate_name, validate_stock, validate_value
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

app = Flask(__name__)

if os.environ.get("FLASK_ENV") == "production":
    app.config.from_object(ProdConfig)
else:
    app.config.from_object(DevConfig)

app.secret_key = app.config["SECRET_KEY"]

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

def page_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login_page"))
        return func(*args, **kwargs)
    return wrapper

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login_page")) if request.path.startswith("/") and request.method == "GET" else (jsonify({"message" : "please login"}), 401)
        user = db.get_user_by_username(session.get("username"))
        if not user or user[7] != "admin":
            # page request -> redirect, API request -> JSON 403
            if request.path.startswith("/api/"):
                return jsonify({"message" : "admin only"}), 403
            return redirect(url_for("inventory"))
        return func(*args, **kwargs)
    return wrapper

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/inventory")
@page_login_required
def inventory():
    return render_template("home.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/dashboard")
@page_login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/reports")
@page_login_required
def reports():
    return render_template("reports.html")
@app.route("/accountsetting")
@page_login_required
def accountsetting():
    return render_template("accountsetting.html")
@app.route("/activity_log")
@page_login_required
def activity_log_page():
    return render_template("activity_log.html")
@app.route("/sales_history")
@page_login_required
def sales_history_page():
    return render_template("sales_history.html")
@app.route("/api/session-status", methods = ["GET"])
def session_status():
    username = session.get("username")
    role = None
    if username:
        u = db.get_user_by_username(username)
        role = u[7] if u else None
    return jsonify({
        "logged_in" : bool(session.get("logged_in")),
        "username" : username,
        "role" : role
    })


@app.route("/api/me")
@login_required
def get_me():
    username = session.get("username")
    user = db.get_user_by_username(username)
    if not user:
          return jsonify({"message": "user not found"}), 404
    # user is (id, username, password_hash, full_name, email, dob, created_at, role)
    return jsonify({
          "id": user[0],
          "username": user[1],
          "full_name": user[3],
          "email": user[4],
          "dob": user[5],
          "created_at": user[6],
          "role" : user[7]
      })

@app.route("/api/change-password", methods=["POST"])
@login_required
def change_password():
    data = request.get_json()
    username = session.get("username")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return jsonify({"message": "old and new password required"}), 400
    if len(new_password) < 6:
        return jsonify({"message": "new password must be at least 6 characters"}), 400

    user = db.get_user_by_username(username)
    if not user or not check_password_hash(user[2], old_password):
        return jsonify({"message": "old password is incorrect"}), 401

    new_hash = generate_password_hash(new_password)
    db.update_user_password(username, new_hash)
    return jsonify({"message": "password updated"}), 200

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
        f"Sold {data.get('quantity')}x {name} at Rs. {item[2]} each "
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

@app.route("/api/sales/weekly")
def get_weekly_sales():
    from datetime import timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)
    sales_by_day = db.get_sales_by_day(
        start_date.strftime("%Y-%m-%d 00:00:00"),
        end_date.strftime("%Y-%m-%d 23:59:59")
    )
    sales_dict = {row[0] : row[1] for row in sales_by_day}
    result = []
    for i in range(7):
        day = start_date + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        day_str = day.strftime("%a")
        result.append({
            "date" : date_str,
            "day" : day_str,
            "revenue" : sales_dict.get(date_str, 0)
        })
    return jsonify(result)

@app.route("/api/activities/all")
def get_all_activities():
    start = request.args.get("start")
    end = request.args.get("end")

    if start and end:
        activities = db.get_activities_by_range(start, end)
    else:
        activities = db.get_recent_activities(limit=100)
    result = []
    for row in activities:
        result.append({
            "id" : row[0],
            "username" : row[1],
            "action" : row[2],
            "item_name" : row[3],
            "details" : row[4],
            "timestamp" : row[5]
        })
    return jsonify(result)

@app.route("/api/sales/summary")
@login_required
def get_sales_summary():
    start = request.args.get("start")
    end = request.args.get("end")

    if not start or not end:
        return jsonify({"message" : "start and end dates are required"}), 400
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")   
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"message" : "dates must be YYYY-MM-DD format"}), 400
    if(start_date > end_date):
        return jsonify({"message" : "start date cannot be after end date"}), 400
    # ===== GET SALES DATA =====
    sales = db.get_sales_by_range(
        start_date.strftime("%Y-%m-%d 00:00:00"),
        end_date.strftime("%Y-%m-%d 23:59:59")
    )
    # ===== CALCULATE SUMMARY STATS =====
    total_revenue = sum(quantity * price for _,_, quantity, price, _,_ in sales)
    total_transactions = len(sales)
    average_sale = total_revenue / total_transactions if total_transactions > 0 else 0
    # =====FIND BEST SELLER BY REVENUE =====    
    item_revenue = {}
    for _, item_name, quantity, price, _,_ in sales:
        item_revenue[item_name] = item_revenue.get(item_name, 0) + (quantity * price)
    best_seller = max(item_revenue.items(), key=lambda x : x[1])[0] if item_revenue else "N/A"
    return jsonify({
        "total_revenue" : total_revenue,
        "total_transactions" : total_transactions,
        "average_sale" : round(average_sale, 2),
        "best_seller" : best_seller
    })

@app.route("/api/sales/daily")
@login_required
def get_daily_sales():
    start = request.args.get("start")
    end = request.args.get("end")

    if not start or not end:
        return jsonify({"message" : "start and end dates are required"}), 400
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"message" : "Dates must be YYYY-MM-DD format"}), 400
    if start_date > end_date:
        return jsonify({"message" : "start date cannot be after end date"}), 400
    from datetime import timedelta

    sales_by_day = db.get_sales_by_day(
        start_date.strftime("%Y-%m-%d 00:00:00"),
        end_date.strftime("%Y-%m-%d 23:59:59")
    )

    sales_dict = {row[0] : row[1] for row in sales_by_day}

    result = []
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        day_str = current.strftime("%a")

        result.append({
            "date" : date_str,
            "day" : day_str,
            "revenue" : sales_dict.get(date_str, 0)
        })
        current += timedelta(days=1)
    return jsonify(result)

@app.route("/api/sales/top-items")
@login_required
def get_top_items():
    start = request.args.get("start")
    end = request.args.get("end")

    if not start or not end:
        return jsonify({"message" : "start and end dates are required"}), 400
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"message" : "Dates must be YYYY-MM-DD format"}), 400
    if start_date > end_date:
        return jsonify({"message" : "start date cannot be after end date"}), 400

    sales = db.get_sales_by_range(
        start_date.strftime("%Y-%m-%d 00:00:00"),
        end_date.strftime("%Y-%m-%d 23:59:59")
    )
    # ===== CALCULATE REVENUE PER ITEM =====
    item_revenue = {}
    for _, item_name, quantity, price, _,_ in sales:
        item_revenue[item_name] = item_revenue.get(item_name, 0) + (quantity * price)
    # ===== SORT BY REVENUE AND GET TOP 5 =====
    sorted_items = sorted(item_revenue.items(), key=lambda x : x[1], reverse=True)[:5]
    result = [{"name" : name, "revenue" : revenue} for name, revenue in sorted_items]
    return jsonify(result)

@app.route("/api/sales/detailed")
@login_required
def get_detailed_sales():
    start = request.args.get("start")
    end = request.args.get("end")

    if not start or not end:
        return jsonify({"message" : "start and end dates are required"}), 400
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"message" : "Dates must be YYYY-MM-DD format"}), 400
    if start_date > end_date:
        return jsonify({"message" : "start date cannot be after end date"}), 400

    sales = db.get_sales_by_range(
        start_date.strftime("%Y-%m-%d 00:00:00"),
        end_date.strftime("%Y-%m-%d 23:59:59")
    )
    result = []
    for sale in sales:
        result.append({
            "id" : sale[0],
            "item_name" : sale[1],
            "quantity": sale[2],
            "price": sale[3],
            "timestamp": sale[4],
            "sold_by": sale[5]
        })
    result.sort(key=lambda x: x["id"], reverse=True)
    return jsonify(result)

@app.route("/admin")
@admin_required
def admin_page():
    return render_template("admin.html")

@app.route("/api/admin/users")
@admin_required
def admin_list_users():
    rows = db.get_all_users()
    users = []
    for row in rows:
        users.append({
            "id" : row[0],
            "username" : row[1],
            "full_name" : row[2],
            "email" : row[3],
            "dob" : row[4],
            "created_at" : row[5],
            "role" : row[6]
        })
    return jsonify(users)

@app.route("/api/admin/users/<username>/promote", methods=["POST"])
@admin_required
def admin_promote_user(username):
    user = db.get_user_by_username(username)
    if not user:
        return jsonify({"message": "user not found"}), 404
    if user[7] == "admin":
        return jsonify({"message": "already admin"}), 400
    db.update_user_role(username, "admin")
    return jsonify({"message": "promoted"}), 200

@app.route("/api/admin/users/<username>/revoke", methods=["POST"])
@admin_required
def admin_revoke_user(username):
    if username == session.get("username"):
        return jsonify({"message": "cannot revoke yourself"}), 400
    user = db.get_user_by_username(username)
    if not user:
        return jsonify({"message": "user not found"}), 404
    if user[7] != "admin":
        return jsonify({"message": "not an admin"}), 400
    all_users = db.get_all_users()
    admins = [u for u in all_users if u[6] == "admin"]
    if len(admins) <= 1:
        return jsonify({"message": "cannot revoke last admin"}), 400
    db.update_user_role(username, "seller")
    return jsonify({"message": "revoked"}), 200

@app.route("/api/admin/users/<int:user_id>", methods = ["DELETE"])
@admin_required
def admin_delete_user(user_id):
    me = db.get_user_by_username(session.get("username"))
    if me and me[0] == user_id:
        return jsonify({"message" : "cannot delete yourself"}), 400
    target = db.get_user_by_id(user_id)
    if not target:
        return jsonify({"message" : "user not found"}), 404
    db.delete_user_by_id(user_id)
    return jsonify({"message" : "user deleted"}), 200

@app.route("/api/admin/users/<username>", methods=["DELETE"])
@admin_required
def admin_delete_user_by_name(username):
    if username == session.get("username"):
        return jsonify({"message": "cannot delete yourself"}), 400
    user = db.get_user_by_username(username)
    if not user:
        return jsonify({"message": "user not found"}), 404
    db.delete_user_by_id(user[0])
    return jsonify({"message": "user deleted"}), 200

if __name__ == "__main__": 
    app.run(debug=True)