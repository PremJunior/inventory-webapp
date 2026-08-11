import json

class InsufficientStockError(Exception):
    pass

class item:
    def __init__(self, name : str ,stock : int, value : int) -> None:
        self.name = name
        self.stock = stock
        self.value = value

    def __str__(self):
        return f"{self.name} : {self.stock} units {self.value} rupees each"
    def __repr__(self):
        return f"item('{self.name}', {self.stock}, {self.value})"
    
    @property
    def stock(self):
        return self._stock
    @stock.setter
    def stock(self, newvalue):
        if newvalue < 0:
            raise ValueError("stock cant be negative")
        else:
            self._stock = newvalue

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, newvalue):
        if newvalue < 0:
            raise ValueError("price cant be negative")
        else:
            self._value = newvalue

    def restock(self, quantity : int) -> bool:
        try:
            if quantity  < 0:
                print("negative stock cant be added")
                return False
            else:
                self.stock += quantity 
                print(f"{quantity} units added to {self.name}")
                return True
        except ValueError as e:
            raise ValueError(f"restock failed: {e}")

    def sell(self, quantity : int):
        if quantity < 0:
            raise ValueError("cannot sell negative quantity")
        if self.stock < quantity:
            raise InsufficientStockError(f" cannot sell {quantity}. Only {self.stock} left")
        else:
            self.stock -= quantity

    def edit(self, name : str = None, stock : int = None, value : int = None) -> bool:
        name_changed = True
        if name is not None:
            if not all(char.isalpha() or char == " " for char in name):
                print("Invalid name, numbers and special characters are not allowed")
                name_changed = False
            else:
                self.name = name
        if stock is not None:
            try:
                self.stock = stock
            except ValueError as e:
                print(f"stock update failed. {e}")
        if value is not None:
            try:
                self.value = value
            except ValueError as e:
                print(f"value update failed.{e}")
        return name_changed

    def total_value(self):
        total = self.stock * self.value
        return total


class inventory:
    def __init__(self):
        self.items = {}

    def __str__(self):
        return f"this object has {len(self.items)} distinct products "

    def add_item(self, name, quantity, price):
        if name in self.items:
            print(f"{name} already exists")
            if self.items[name].restock(quantity):
                print("items restocked")
        else:
            new_item = item(name, quantity, price)
            self.items[name] = new_item 
            print(f"{name} added to inventory")

    def sell_item(self, name, quantity):
        if name not in self.items:
            print("item doesnt exist")
            return
        try:
            self.items[name].sell(quantity)
            print(f"{quantity} units of {name} sold")
        except ValueError as e:
            print(f"Invalid quantity entered: {e}")
        except InsufficientStockError as e:
            print(f"Insufficient stock: {e}")

    def edit_item(self, current_name, new_name=None, new_stock=None, new_value=None):
        if current_name not in self.items:
            print("item not found")
            return
        obj = self.items[current_name]
        name_ok = obj.edit(name=new_name, stock=new_stock, value=new_value)
        if new_name is not None and name_ok:
            self.items[new_name] = obj      # add under new key
            del self.items[current_name]    # remove old key
        if name_ok or new_stock is not None or new_value is not None:
            print("item updated")


    def total_inventory_value(self):
        total = 0
        for stock in self.items:
            total += self.items[stock].total_value()
        print(f"total value of inventory is {total}")

    def show_all(self):
        print(f"{'Name':<12}{'Quantity':<12}Price")
        for name in self.items:
            print(f"{name:<12}{self.items[name].stock:<12}{self.items[name].value}")

    def save_inventory(self):
        data = {}
        for name in self.items:
            obj = self.items[name]
            data[name] = {"stock" : obj.stock,"value":obj.value}
        with open("oop_inventory.json","w") as f:
            json.dump(data, f)

    def load_inventory(self):
        try:
            with open("oop_inventory.json","r") as f:
                data = json.load(f)
            for name in data:
                self.items[name] = item(name, data[name]["stock"], data[name]["value"])
        except FileNotFoundError:
            print("file not found, making fresh")

    def delete_item(self, name):
        if name in self.items:
            del self.items[name]
            print(f"{name} deleted")
        else:
            print(f"{name} not found")
    def low_stock_items(self):
        return [p.name for p in self.items.values() if p.stock < 10]

def main():
    p1 = inventory()
    p1.load_inventory()
    running = True
    while running:
        print("1. Add item")
        print("2. Sell item")
        print("3. Show all items")
        print("4. Total inventory value")
        print("5. Edit item")
        print("6. Delete item")
        print("7. Show low stock items")
        print("8. Exit")

        query = input("Choose operation: ")
        while query not in ("1","2","3","4","5","6","7","8"):
            print("Invalid input try again.")
            query = input("Chooe operation: ")
        if query == "1":
            name = input("Name of item: ")
            quantity = int(input("Quantity: "))
            if name in p1.items:
                p1.add_item(name, quantity, None)
            else:
                price = int(input("enter price: "))
                p1.add_item(name, quantity, price)
        elif query == "2":
            name = input("Name of item: ")
            try:
                quantity = int(input("Quantity: "))
            except ValueError:
                print("Invalid quantity entered")
                continue
            p1.sell_item(name, quantity)
        elif query == "3":
            p1.show_all()
        elif query == "4":
            p1.total_inventory_value()
        elif query == "5":
            name = input("Enter Product's name: ")
            new_name = input("Enter new name: ")
            new_quantity = input("enter new quantity: ")
            new_price = input("enter new price: ")

            new_name = new_name if new_name != "" else None
            new_quantity = int(new_quantity) if new_quantity != "" else None
            new_price = int(new_price) if new_price != "" else None
            p1.edit_item(name,new_name,new_quantity,new_price)
        elif query == "6":
            name = input("enter product's name: ")
            p1.delete_item(name)
        elif query == "7":
            low_items = p1.low_stock_items()
            if low_items:
                print("low items: ",low_items)
            else:
                print("no low items detected")
        elif query == "8":
            running = False
            print("Data saved")
            print("Exiting....")
        p1.save_inventory()

if __name__ == "__main__":
    main()
