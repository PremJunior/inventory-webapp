from flask import Flask, render_template, jsonify, request
from inventory import item, inventory

app = Flask(__name__)
my_inventory = inventory()
@app.route("/")
def home():
    return render_template("home.html", items =  my_inventory.items.values())

# @app.route("/about-us")
# def about_page():
#     return "This is about us page"

# @app.route("/contact-us")
# def contact_us_page():
#     return "This is contact us page"

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

if __name__ == "__main__": 
    app.run(debug=True)