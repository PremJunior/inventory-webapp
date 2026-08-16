from flask import Flask, render_template, jsonify, request
import database as db
from validation import validate_name, validate_stock, validate_value

app = Flask(__name__)

@app.route("/")                                 #done
def home():
    return render_template("home.html")

@app.route("/api/items")                                #done
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

@app.route("/api/items", methods = ["POST"])                #done
def  add_item():
    data = request.get_json()
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
        message = "stock updated"
    else:
        db.save_item(name, stock, value)
        message = "item added"
    item = db.get_item_by_name(name)

    return jsonify({
        "message" : message,
        "item" : {"name" : item[0], "stock" : item[1], "value" : item[2]}
        }), 201

@app.route("/api/items/<name>", methods = ["DELETE"])               #done
def delete_item(name):
    rows = db.load_all_items()
    if not any(row[0] == name for row in rows):
        return jsonify({"error" : "item not found"}),404
    db.delete_item_from_db(name)
    return jsonify({"message" : "item deleted"}),200

@app.route("/api/items/<name>", methods = ["PUT"])              #done
def edit_item(name):
    data = request.get_json()
    if not validate_name(data.get("name")):
        return jsonify({"message" : "invalid name entered"}),400
    if not validate_stock(data.get("stock")):
        return jsonify({"message" : "invalid stock entered"}),400
    if not validate_value(data.get("value")):
        return jsonify({"message" : "invalid value entered"}),400
    success = db.update_item(
        name,
        data.get("name"),
        data.get("stock"),
        data.get("value")
    )
    if not success:
        return jsonify({"message": "item not found"}), 404

    return jsonify({"message": "item updated"}), 200

@app.route("/api/items/<name>/sell", methods = ["POST"])
def sell_item(name):
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
    return jsonify({"message" : "item sold", "stock" : remaining}),200

if __name__ == "__main__": 
    app.run(debug=True)