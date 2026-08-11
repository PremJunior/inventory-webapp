from flask import Flask, render_template, jsonify, request
from inventory import item, inventory

app = Flask(__name__)
my_inventory = inventory()
@app.route("/")
def home():
    return render_template("home.html", items =  my_inventory.items.values())

@app.route("/api/items")
def get_items():
    items_lst = []
    for name, obj in my_inventory.items.items():
        items_lst.append({
            "name" : obj.name,
            "stock" : obj.stock,
            "value" : obj.value
        })
    return jsonify(items_lst)

@app.route("/api/items", methods = ["POST"])
def  add_item():
    data = request.get_json()
    my_inventory.add_item(
        data["name"],
        data["stock"],
        data["value"]
    )
    return jsonify({"message" : "item added"}), 201

@app.route("/api/items/<name>", methods = ["DELETE"])
def delete_item(name):
    if name not in my_inventory.items:
        return jsonify({"error" : "item not found"}),404
    my_inventory.delete_item(name)
    return jsonify({"message" : "item deleted"}),200

@app.route("/api/items/<name>", methods = ["PUT"])
def edit_item(name):
    data = request.get_json()
    if name not in my_inventory.items:
        return jsonify({"message" : "item not found"}),404
    my_inventory.edit_item(
        name,
        data.get("name"),
        data.get("stock"),
        data.get("value")
    )
    return jsonify({"message" : "item updated"}),200

if __name__ == "__main__": 
    app.run(debug=True)