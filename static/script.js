// ===== API REQUEST =====
async function apiRequest(url, options = {}) {
    try {
        let response = await fetch(url, options);
        let result = await response.json();
        if (!response.ok) {
            throw new Error(result.message || "Request failed");
        }
        return result;
    } catch (error) {
        console.log("API error: ", error);
        throw error;
    }
}

// ===== ADD ITEM =====
document.querySelector("#addBtn")?.addEventListener("click", async () => {
    try {
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
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                name: name, 
                stock: parseInt(stock), 
                value: parseInt(value) 
            })
        });
        
        let newItem = result.item;
        let existingEditBtn = document.querySelector(`.editBtn[data-name="${newItem.name}"]`);
        
        if (existingEditBtn) {
            let li = existingEditBtn.closest("li");
            let itemInfo = li.querySelector(".itemInfo");
            let stockClass = newItem.stock < 10 ? "stock-low" : "stock-ok";
            let stockText = newItem.stock < 10 ? `${newItem.stock} left` : `${newItem.stock} units`;

            itemInfo.innerHTML = `
                <span class="itemNameValue">${newItem.name} - ${newItem.value} each</span>
                <span class="stock-pill ${stockClass}">${stockText}</span>
            `;
            existingEditBtn.dataset.stock = newItem.stock;
            showToast(`${newItem.name} restocked successfully`);
        } else {
            let itemList = document.querySelector("#itemList");
            let li = createItemElement(newItem);
            itemList.appendChild(li);
            showToast(`${newItem.name} added successfully`);
        }
        
        document.querySelector("#itemName").value = "";
        document.querySelector("#itemStock").value = "";
        document.querySelector("#itemValue").value = "";
        updateStats();
        applyFilters();
        
    } catch (error) {
        if (!error.message.includes("already exists") && !error.message.includes("duplicate")) {
            alert(error.message);
        }
    }
});

// ===== LOGIN TOAST =====
let params = new URLSearchParams(window.location.search);
if (params.get("login") === "success") {
    showToast("Logged in Successfully");
    history.replaceState({}, "", "/");
}

// ===== LOGOUT =====
document.getElementById("logoutLink").addEventListener("click", async (event) => {
    event.preventDefault();
    try {
        const response = await fetch("/api/logout", { method: "POST" });
        const result = await response.json();
        if (!response.ok) {
            throw new Error("logout failed");
        }
        window.location.href = "/login";
    } catch (error) {
        console.log("Logout error: ", error);
    }
});

// ===== CREATE ITEM ELEMENT =====
function createItemElement(item) {
    let li = document.createElement("li");
    let stockClass = item.stock < 10 ? "stock-low" : "stock-ok";
    let stockText = item.stock < 10 ? `${item.stock} left` : `${item.stock} units`;
    
    li.innerHTML = `
        <span class="itemInfo">
            <span class="itemNameValue">${item.name} - ${item.value} each</span>
            <span class="stock-pill ${stockClass}">${stockText}</span>
        </span>
        <span class="item-actions">
            <button class="btn-icon editBtn" data-name="${item.name}" data-stock="${item.stock}" data-value="${item.value}">✏️ Edit</button>
            <button class="btn-icon sellBtn" data-name="${item.name}">💰 Sell</button>
            <button class="btn-icon deleteBtn" data-name="${item.name}">🗑️ Delete</button>
        </span>
    `;

    let deleteBtn = li.querySelector(".deleteBtn");
    deleteBtn.addEventListener("click", async () => {
        let name = deleteBtn.dataset.name;
        try {
            await deleteItem(name);
            li.remove();
            showToast(`${name} deleted successfully`);
            updateStats();
            applyFilters();
        } catch (error) {
            alert(error.message);
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
        try {
            await editItem(
                name,
                newName !== "" ? newName : null,
                newStock !== "" ? parseInt(newStock) : null,
                newValue !== "" ? parseInt(newValue) : null
            );
            showToast("Item edited successfully");

            let itemInfo = li.querySelector(".itemInfo");
            let displayedName = newName !== "" ? newName : name;
            let displayedStock = newStock !== "" ? parseInt(newStock) : parseInt(stock);
            let displayedValue = newValue !== "" ? parseInt(newValue) : parseInt(value);
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
            updateStats();
            applyFilters();
        } catch (error) {
            alert(error.message);
        }
    });

    let sellBtn = li.querySelector(".sellBtn");
    sellBtn.addEventListener("click", async () => {
        let input = prompt("How many to sell?");
        if (input == null) {
            return;
        }
        let quantity = parseInt(input);
        if (isNaN(quantity) || quantity <= 0) {
            alert("Please enter a valid quantity.");
            return;
        }
        let name = sellBtn.dataset.name;
        try {
            let result = await sellItem(name, quantity);
            showToast(`${name} sold successfully`);
            let displayedStock = result.stock;
            let stockClass = displayedStock < 10 ? "stock-low" : "stock-ok";
            let stockText = displayedStock < 10 ? `${displayedStock} left` : `${displayedStock} units`;
            let itemInfo = li.querySelector(".itemInfo");
            itemInfo.innerHTML = `
                <span class="itemNameValue">${name} - ${editBtn.dataset.value} each</span>
                <span class="stock-pill ${stockClass}">${stockText}</span>
            `;
            editBtn.dataset.stock = displayedStock;
            updateStats();
            applyFilters();
            loadSalesHistory();
        } catch (error) {
            alert(error.message);
        }
    });

    return li;
}

// ===== CRUD FUNCTIONS =====
async function sellItem(name, quantity) {
    let result = await apiRequest(`/api/items/${name}/sell`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quantity: quantity })
    });
    return result;
}

async function deleteItem(name) {
    let result = await apiRequest(`/api/items/${name}`, {
        method: "DELETE"
    });
    return result;
}

async function editItem(name, newName, newStock, newValue) {
    let result = await apiRequest(`/api/items/${name}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name: newName,
            stock: newStock,
            value: newValue
        })
    });
    return result;
}

// ===== UPDATE STATS =====
async function updateStats() {
    try {
        let result = await apiRequest("/api/items");
        let totalItems = result.length;
        let lowStockItems = result.filter(item => item.stock < 10);
        let lowStockCount = lowStockItems.length;
        
        document.getElementById("statTotal").textContent = totalItems;
        document.getElementById("statLowStock").textContent = lowStockCount;
        
    } catch (error) {
        console.log("Error updating stats: ", error);
    }
}

//=========UPDATE TODAY SALES=========  
function updateTodaySales(sales){
    let todaySales = document.getElementById("statTodaySales");
    if (!todaySales) return;

    let today = new Date();
    let todayTotal = sales.reduce((sum, sale) => {
        let saleDate = new Date(sale.timestamp); 
        let isToday = 
            saleDate.getFullYear() === today.getFullYear() &&
            saleDate.getMonth() === today.getMonth() &&
            saleDate.getDay() === today.getDay();
        return isToday? sum + (sale.quantity * sale.price) : sum;
    }, 0)
    todaySales.textContent = "Rs." + todayTotal.toLocaleString();
}
// ===== LOAD ITEMS =====
async function loadItems() {
    try {
        let result = await apiRequest("/api/items");
        let itemList = document.querySelector("#itemList");
        itemList.innerHTML = '';
        result.forEach(item => {
            let li = createItemElement(item);
            itemList.appendChild(li);
        });
        await updateStats();
        applyFilters();
    } catch (error) {
        console.log("Error loading items: ", error);
    }
}

// ===== LOAD SALES =====
async function loadSalesHistory() {
    try {
        let result = await apiRequest("/api/sales");
        let salesList = document.querySelector("#salesList");
        salesList.innerHTML = '';
        result.forEach(sale => {
            let li = document.createElement("li");
            li.className = "sale-entry";
            li.innerHTML = `
                ${sale.quantity}x ${sale.name} @ ${sale.price} each
                <div class="sale-time">${sale.timestamp}</div>
            `;
            salesList.appendChild(li);
            updateTodaySales(result);
        });
    } catch (error) {
        console.log("Error loading sales: ", error);
    }
}

// ===== TOAST =====
function showToast(message, type = "success") {
    let container = document.getElementById("toastContainer");
    let toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => toast.classList.add("show"), 10);
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 200);
    }, 2500);
}

// ===== SEARCH & FILTER =====
var searchInput = document.getElementById("searchInput");
var currentFilter = 'all';

function applyFilters() {
    if (!searchInput) return;
    var query = searchInput.value.trim().toLowerCase();
    var items = document.querySelectorAll("#itemList li");
    
    items.forEach(function(li) {
        var nameEl = li.querySelector(".itemNameValue");
        var stockPill = li.querySelector(".stock-pill");
        
        var name = nameEl ? nameEl.textContent.toLowerCase() : '';
        var isLowStock = stockPill && stockPill.classList.contains('stock-low');

        var matchesSearch = name.includes(query);
        var matchesFilter = (currentFilter === 'all') || (currentFilter === 'low' && isLowStock);

        li.style.display = (matchesSearch && matchesFilter) ? "" : "none";
    });
}

function filterItems(type) {
    currentFilter = type;
    document.querySelectorAll('.filter-btn').forEach(function(btn) {
        btn.classList.remove('active');
    });
    var buttons = document.querySelectorAll('.filter-btn');
    buttons.forEach(function(btn) {
        if (type === 'all' && btn.textContent.trim() === 'All') {
            btn.classList.add('active');
        } else if (type === 'low' && btn.textContent.includes('Low')) {
            btn.classList.add('active');
        }
    });
    applyFilters();
}

if (searchInput) {
    searchInput.addEventListener("input", function() {
        applyFilters();
    });
}

window.filterItems = filterItems;

// ===== AUTH =====
async function updateAuthLinks() {
    try {
        const response = await fetch("/api/session-status");
        const loginLink = document.getElementById("loginLink");
        const signupLink = document.getElementById("signupLink");
        const logoutLink = document.getElementById("logoutLink");
        const profileName = document.getElementById("profileName");
        const welcomeUser = document.getElementById("welcomeUser");
        const result = await response.json();
        
        if (result.logged_in) {
            if (loginLink) loginLink.style.display = "none";
            if (signupLink) signupLink.style.display = "none";
            if (logoutLink) logoutLink.style.display = "block";
            var profileCard = document.getElementById("profileCard");
            if (profileCard) profileCard.style.display = "flex";
            if (profileName) {
                profileName.style.display = "block";
                profileName.textContent = result.username;
            }
            if(welcomeUser){
                welcomeUser.textContent = result.username;
            }
        } else {
            if (loginLink) loginLink.style.display = "block";
            if (signupLink) signupLink.style.display = "block";
            if (logoutLink) logoutLink.style.display = "none";
            var profileCard = document.getElementById("profileCard");
            if (profileCard) profileCard.style.display = "none";
        }
    } catch (error) {
        console.log("couldn't check session status: ", error);
    }
}

// ===== INIT =====
document.addEventListener("DOMContentLoaded", function() {
    if (document.querySelector("#itemList")) {
        loadItems();
        loadSalesHistory();
    }
    updateAuthLinks();
});
