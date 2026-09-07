// static/js/signup.js

const form = document.getElementById("signupForm");
const errorDiv = document.getElementById("signupError");
const errorText = document.getElementById("signupErrorText");

// Clear error when user types
form?.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', () => {
        errorDiv.classList.remove("show");
    });
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    
    // Get values
    const fullName = document.getElementById("fullName").value.trim();
    const dob = document.getElementById("dob").value;
    const email = document.getElementById("email").value.trim();
    const userName = document.getElementById("uname").value.trim();
    const password = document.getElementById("pwd").value;
    const confirmPassword = document.getElementById("confirmPwd").value;

    // Validation
    if (!fullName || !dob || !email || !userName || !password || !confirmPassword) {
        errorText.textContent = "Please fill all the fields";
        errorDiv.classList.add("show");
        return;
    }
    
    if (password !== confirmPassword) {
        errorText.textContent = "Passwords don't match";
        errorDiv.classList.add("show");
        return;
    }
    
    if (password.length < 8) {
        errorText.textContent = "Password must be at least 8 characters";
        errorDiv.classList.add("show");
        return;
    }
    
    // Hide errors
    errorDiv.classList.remove("show");

    // ---------- LOADING ----------
    const submitBtn = document.getElementById("signup-btn");
    const originalText = submitBtn.textContent;
    const spinner = document.getElementById("signupBtnSpinner");
    
    submitBtn.disabled = true;
    submitBtn.classList.add("btn-loading");
    submitBtn.textContent = "";
    spinner.style.display = "inline-block";

    try {
        const response = await fetch("/api/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                fullname: fullName,
                dob: dob,
                email: email,
                username: userName,
                password: password
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            // ❌ Signup failed - no ❌ emoji, just the message
            errorText.textContent = result.message || "Failed to create account";
            errorDiv.classList.add("show");
            
            // Reset button
            submitBtn.disabled = false;
            submitBtn.classList.remove("btn-loading");
            submitBtn.textContent = originalText;
            spinner.style.display = "none";
            return;
        }
        
        // ✅ Signup successful
        submitBtn.textContent = "✅ Account Created!";
        spinner.style.display = "none";
        
        // Redirect after brief delay
        setTimeout(() => {
            window.location.href = "/";
        }, 600);
        
    } catch (error) {
        console.error("Signup error:", error);
        
        errorText.textContent = "Network error. Please check your connection.";
        errorDiv.classList.add("show");
        
        // Reset button on network error
        submitBtn.disabled = false;
        submitBtn.classList.remove("btn-loading");
        submitBtn.textContent = originalText;
        spinner.style.display = "none";
    }
});