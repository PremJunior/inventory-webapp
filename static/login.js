// static/js/login.js

const form = document.getElementById("loginForm");
const errorDiv = document.getElementById("loginError");
const errorText = errorDiv.querySelector("span:last-child");

// Clear error when user types
document.getElementById("uname")?.addEventListener("input", () => {
    errorDiv.classList.remove("show");
});

document.getElementById("pwd")?.addEventListener("input", () => {
    errorDiv.classList.remove("show");
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    
    // Get values
    const username = document.getElementById("uname").value.trim();
    const password = document.getElementById("pwd").value;

    // Validation
    if (!username || !password) {
        errorText.textContent = "Please enter both username and password";
        errorDiv.classList.add("show");
        return;
    }

    // Hide errors
    errorDiv.classList.remove("show");

    // ---------- LOADING ----------
    const submitBtn = document.getElementById("login-btn");
    const originalText = submitBtn.textContent;
    const spinner = document.getElementById("loginBtnSpinner");
    
    submitBtn.disabled = true;
    submitBtn.classList.add("btn-loading");
    submitBtn.textContent = "";
    spinner.style.display = "inline-block";

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                username: username, 
                password: password 
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            // ❌ Login failed - no ❌ emoji, just the message
            errorText.textContent = result.message || "Invalid username or password";
            errorDiv.classList.add("show");
            
            // Reset button
            submitBtn.disabled = false;
            submitBtn.classList.remove("btn-loading");
            submitBtn.textContent = originalText;
            spinner.style.display = "none";
            return;
        }
        
        // ✅ Login successful
        submitBtn.textContent = "✅ Welcome!";
        spinner.style.display = "none";
        
        // Redirect after brief delay
        setTimeout(() => {
            window.location.href = "/?login=success";
        }, 600);
        
    } catch (error) {
        console.error("Login error:", error);
        
        errorText.textContent = "Network error. Please check your connection.";
        errorDiv.classList.add("show");
        
        // Reset button on network error
        submitBtn.disabled = false;
        submitBtn.classList.remove("btn-loading");
        submitBtn.textContent = originalText;
        spinner.style.display = "none";
    }
});