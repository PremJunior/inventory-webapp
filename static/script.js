
        document.querySelector("#addBtn").addEventListener("click", async() => {
            try{
                let name = document.querySelector("#itemName").value.trim();
                let stock = document.querySelector("#itemStock").value.trim();
                let value = document.querySelector("#itemValue").value.trim();
                if (name === "" || stock === "" || value === "") {
                    alert("All fields are required.");
                    return;
                }
                if (!/^[A-Za-z\s]+$/.test(name)) {
                    alert("Name can only contain letters and spaces.");
                    return;
                }
                if (parseInt(stock) < 0 || parseInt(value) < 0) {
                    alert("Stock and value cannot be negative.");
                    return;
                }
                let result = await apiRequest("/api/items", {
                    method : "POST",
                    headers : {"Content-Type" : "application/json"},
                    body : JSON.stringify({name : name, stock : parseInt(stock), value : parseInt(value)})
                });
                let newItem = result.item;
                let existingEditBtn = document.querySelector(`.editBtn[data-name = "${newItem.name}"]`);
                if(existingEditBtn){
                    let li = existingEditBtn.closest("li");
                    let itemInfo = li.querySelector(".itemInfo");

                    let stockClass = newItem.stock < 10 ? "stock-low" : "stock-ok";
                    let stockText = newItem.stock < 10 ? `${newItem.stock} left` : `${newItem.stock} units`;

                    itemInfo.innerHTML = `
                        <span class="itemNameValue">${newItem.name} - ${newItem.value} each</span>
                        <span class="stock-pill ${stockClass}">${stockText}</span>
                    `;
                    existingEditBtn.dataset.stock = newItem.stock;
                    showToast(`${newItem.name} restocked successfully`)
                }
                else{
                    let itemList = document.querySelector("#itemList");
                    let li = createItemElement(newItem);
                    itemList.appendChild(li);
                    showToast(`${newItem.name} added successfully`);
                }
                document.querySelector("#itemName").value = "";
                document.querySelector("#itemStock").value = "";
                document.querySelector("#itemValue").value = "";
            }catch(error){
                alert(error.message);
            }
        });

        function createItemElement(item) {
            let li = document.createElement("li");
            let stockClass = item.stock < 10 ? "stock-low" : "stock-ok";
            let stockText = item.stock < 10 ? `${item.stock} left` : `${item.stock} units`;
            li.innerHTML = `
                <span class="itemInfo">
                    <span class="itemNameValue">${item.name} - ${item.value} each</span>
                    <span class="stock-pill ${stockClass}">${stockText}</span>
                </span>
                <button class="editBtn"
                    data-name="${item.name}"
                    data-stock="${item.stock}"
                    data-value="${item.value}">
                    Edit
                </button>
                <button class="deleteBtn"
                    data-name="${item.name}">
                    Delete
                </button>
                <button class = "sellBtn"
                    data-name = "${item.name}">
                    Sell
                </button>
            `;

            let deleteBtn = li.querySelector(".deleteBtn");

            deleteBtn.addEventListener("click", async () => {
                let name = deleteBtn.dataset.name;
                try{
                    await deleteItem(name);
                    li.remove();
                    showToast(`${name} deleted successfully`);
                }catch(error){
                    alert(error.message)
                }
            });

            let editBtn = li.querySelector(".editBtn");

            editBtn.addEventListener("click", async () => {
                let name = editBtn.dataset.name;
                let stock = editBtn.dataset.stock;
                let value = editBtn.dataset.value;

                let newName = prompt("Enter new name: ", name);
                let newStock = prompt("Enter new stock: ", stock);
                let newValue = prompt("Enter new value: ", value);

                if (newName === null || newStock === null || newValue === null) {
                    return;
                }
                try{
                    await editItem(
                        name,
                        newName !== "" ? newName : null,
                        newStock !== "" ? parseInt(newStock) : null,
                        newValue !== "" ? parseInt(newValue) : null
                    );
                    showToast("Item edited successfully")

                    let itemInfo = li.querySelector(".itemInfo");
                    let displayedName = newName !== "" ? newName : name;
                    let displayedStock = newStock !== "" ? newStock : stock;
                    let displayedValue = newValue !== "" ? newValue : value;
                    let stockClass = displayedStock < 10 ? "stock-low" : "stock-ok";
                    let stockText = displayedStock < 10 ? `${displayedStock} left` : `${displayedStock} units`;
                    itemInfo.innerHTML = `
                        <span class="itemNameValue">${displayedName} - ${displayedValue} each</span>
                        <span class="stock-pill ${stockClass}">${stockText}</span>
                    `;

                    editBtn.dataset.name = displayedName;
                    editBtn.dataset.stock = displayedStock;
                    editBtn.dataset.value = displayedValue;
                    deleteBtn.dataset.name = displayedName;
                }catch(error){
                    alert(error.message)
                }
            });
            let sellBtn = li. querySelector(".sellBtn");
            sellBtn.addEventListener("click" , async() => {
                let input = prompt("how many to sell");
                if(input == null){
                    return
                }
                let quantity = parseInt(input);
                let name = sellBtn.dataset.name
                try{
                    let result = await sellItem(name, quantity);
                    showToast(`${name} sold successfully`)
                    let displayedStock = result.stock;
                    let stockClass = displayedStock < 10 ? "stock-low" : "stock-ok";
                    let stockText = displayedStock < 10 ? `${displayedStock} left` : `${displayedStock} units`;
                    let itemInfo = li.querySelector(".itemInfo");
                    itemInfo.innerHTML = `
                        <span class="itemNameValue">${name} - ${editBtn.dataset.value} each</span>
                        <span class="stock-pill ${stockClass}">${stockText}</span>
                    `;
                    editBtn.dataset.stock = displayedStock;
                }catch(error){
                    alert(error.message)
                }
            })

            return li;
        }
        async function apiRequest(url, options = {}) {
            try{
                let response = await fetch(url, options);
                let result = await response.json();
                if(!response.ok){
                    throw new Error(result.message);
                }
                return result;
            }catch(error){
                console.log("API error: ",error);
                throw error;
            }
            
        }

        async function sellItem(name, quantity) {
            let result = await apiRequest(`/api/items/${name}/sell`, {
                method : "POST",
                headers : {"Content-Type" : "application/json"},
                body : JSON.stringify({quantity : quantity})
            });
            return result
        }

        async function deleteItem(name) {
            let result = await apiRequest(`/api/items/${name}`, {
            method : "DELETE"
            });
            return result;
        };

        async function editItem(name, newName, newStock, newValue) {
            let result = await apiRequest(`/api/items/${name}`, {
                method: "PUT",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    name: newName,
                    stock: newStock,
                    value: newValue
                })
            });
            return result
            }

        async function loadItems() {
            try{
                let result = await apiRequest("/api/items");

                let itemList = document.querySelector("#itemList");
                result.forEach(item => {
                    let li = createItemElement(item);
                    itemList.appendChild(li);
                });
                let totalItems = result.length;
                let lowStockItems = result.filter(item => item.stock < 10);
                let lowStockCount = lowStockItems.length;
                document.getElementById("statTotal").textContent = totalItems;
                document.getElementById("statLowStock").textContent = lowStockCount;
            }catch(error){
                console.log("Error: ", error);
                return false;
            }
        }

        function showToast(message, type = "success"){
            let container = document.getElementById("toastContainer");
            let toast = document.createElement("div");
            toast.className = `toast ${type}`;
            toast.textContent = message;
            container.appendChild(toast);

            setTimeout(() => toast.classList.add("show"), 10);
            setTimeout(() => {
                toast.classList.remove("show");
                setTimeout(() => toast.remove(), 200);
            },2500);
        }

        async function loadSalesHistory() {
            try{
                let result = await apiRequest("/api/sales");
                let salesList = document.querySelector("#salesList");
                result.forEach(sale =>{
                    let li = document.createElement("li");
                    li.className = "sale-entry";
                    li.innerHTML = `
                        ${sale.quantity}x ${sale.name} @ ${sale.price} each
                        <div class="sale-time">${sale.timestamp}</div>
                    `;
                    salesList.appendChild(li);   
                });
            }catch(error){
                console.log("Error: ", error);
                }
        }

        loadItems()
        loadSalesHistory()
    
