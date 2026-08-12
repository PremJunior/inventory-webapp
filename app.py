from flask import Flask, render_template, jsonify, request
from inventory import item, inventory
import database as db

app = Flask(__name__)
my_inventory = inventory()

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
    db.save_item(
        data["name"],
        data["stock"],                          
        data["value"]
    )
    return jsonify({"message" : "item added"}), 201

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
    success = db.update_item(
        name,
        data.get("name"),
        data.get("stock"),
        data.get("value")
    )

    if not success:
        return jsonify({"message": "item not found"}), 404

    return jsonify({"message": "item updated"}), 200

if __name__ == "__main__": 
    app.run(debug=True)