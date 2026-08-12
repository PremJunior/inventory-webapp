
        document.querySelector("#addBtn").addEventListener("click", async() => {
            let name = document.querySelector("#itemName").value;
            let stock = document.querySelector("#itemStock").value;
            let value = document.querySelector("#itemValue").value;

            let response = await fetch("/api/items", {
                method : "POST",
                headers : {"Content-Type" : "application/json"},
                body : JSON.stringify({name : name, stock : parseInt(stock), value : parseInt(value)})
            });
            let result = await response.json();
            console.log(result);
            location.reload();
        });

        async function deleteItem(name) {
            let response = await fetch(`/api/items/${name}`, {
                method : "DELETE"
            });
            let result = await response.json();
            console.log(result)
        }

        async function edit_item(name, newName, newStock, newValue) {
        let response = await fetch(`/api/items/${name}`, {
            method: "PUT",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                name: newName,
                stock: newStock,
                value: newValue
            })
        });

        let result = await response.json();
        console.log(result);

        return response;
    }

        async function loadItems() {
            let response = await fetch("/api/items");
            let items = await response.json();

            let itemList = document.querySelector("#itemList");
            items.forEach(item => {
                let li = document.createElement("li");
                li.innerHTML = `
                    <span class ="itemInfo">
                        ${item.name} - ${item.stock} units @ ${item.value} each
                    </span>
                    <button class ="editBtn" data-name ="${item.name}" data-stock ="${item.stock}" data-value ="${item.value}">Edit</button>
                    <button class ="deleteBtn" data-name ="${item.name}">Delete</button>
                `;
                let deleteBtn = li.querySelector(".deleteBtn");
                deleteBtn.addEventListener("click", async () => {
                    let name = deleteBtn.dataset.name;
                    await deleteItem(name)
                    li.remove();
                });
                let editBtn = li.querySelector(".editBtn");
                editBtn.addEventListener("click", async() => {
                    let name = editBtn.dataset.name;
                    let stock = editBtn.dataset.stock;
                    let value = editBtn.dataset.value;

                    let newName = prompt("Enter new name: ", name);
                    let newStock = prompt("Enter new stock: ", stock);
                    let newValue = prompt("Enter new value: ", value);
                    if (newName === null || newStock === null || newValue === null) {
                        return;
                    }


                    let response = await edit_item(
                        name,
                        newName !==""? newName : null,
                        newStock !==""? parseInt(newStock) : null,
                        newValue !==""? parseInt(newValue) : null
                    );
                    if (response.ok){
                        let itemInfo = li.querySelector(".itemInfo");
                        let displayedName = newName !==""? newName : name;
                        let displayedStock = newStock !==""? newStock : stock;
                        let displayedValue = newValue !==""? newValue : value;
                        itemInfo.textContent = `${displayedName} - ${displayedStock} units @ ${displayedValue} each`;

                        editBtn.dataset.name = displayedName;
                        editBtn.dataset.stock = displayedStock;
                        editBtn.dataset.value = displayedValue;
                        deleteBtn.dataset.name = displayedName;
                    }
                });

                itemList.appendChild(li);
            });
        }
        loadItems()

