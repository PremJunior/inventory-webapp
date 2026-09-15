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

function resetLoginButton() {
    const btn = document.getElementById("login-btn");
    const spinner = document.getElementById("loginBtnSpinner");
    if (!btn) return;
    if (btn.dataset.originalText) {
        Array.from(btn.childNodes).forEach(n => { if (n.nodeType === 3) n.remove(); });
        btn.prepend(document.createTextNode(btn.dataset.originalText));
    }
    btn.disabled = false;
    btn.classList.remove("btn-loading");
    if (spinner) {
        spinner.style.display = "none";
        if (!btn.contains(spinner)) btn.appendChild(spinner);
    }
}
window.addEventListener("pageshow", () => {
    resetLoginButton();
    errorDiv.classList.remove("show");
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const username = document.getElementById("uname").value.trim();
    const password = document.getElementById("pwd").value;
    if (!username || !password) {
        errorText.textContent = "Please enter both username and password";
        errorDiv.classList.add("show");
        return;
    }
    errorDiv.classList.remove("show");
    const submitBtn = document.getElementById("login-btn");
    const spinner = document.getElementById("loginBtnSpinner");
    if (!submitBtn.dataset.originalText) {
        let t = "";
        submitBtn.childNodes.forEach(n => { if(n.nodeType===3) t+=n.textContent; });
        submitBtn.dataset.originalText = t.trim() || "Log in";
    }
    submitBtn.disabled = true;
    submitBtn.classList.add("btn-loading");
    Array.from(submitBtn.childNodes).forEach(n => { if(n.nodeType===3) n.textContent=""; });
    if (spinner) spinner.style.display = "inline-block";
    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({ username: username, password: password })
        });
        const result = await response.json();
        if (!response.ok) {
            errorText.textContent = result.message || "Invalid username or password";
            errorDiv.classList.add("show");
            resetLoginButton();
            return;
        }
        if (spinner) spinner.style.display = "none";
        Array.from(submitBtn.childNodes).forEach(n => { if(n.nodeType===3) n.textContent=""; });
        submitBtn.prepend(document.createTextNode("✅ Welcome!"));
        setTimeout(() => { window.location.replace("/inventory?login=success"); }, 600);
    } catch (error) {
        console.error("Login error:", error);
        errorText.textContent = "Network error. Please check your connection.";
        errorDiv.classList.add("show");
        resetLoginButton();
    }
});
