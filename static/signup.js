// static/js/signup.js

const form = document.getElementById("signupForm");
const errorDiv = document.getElementById("signupError");
const errorText = document.getElementById("signupErrorText");

form?.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', () => {
        errorDiv.classList.remove("show");
    });
});

function resetSignupButton(){
    const btn = document.getElementById("signup-btn");
    const spinner = document.getElementById("signupBtnSpinner");
    if(!btn) return;
    if(btn.dataset.originalText){
        Array.from(btn.childNodes).forEach(n=>{if(n.nodeType===3) n.remove();});
        btn.prepend(document.createTextNode(btn.dataset.originalText));
    }
    btn.disabled=false; btn.classList.remove("btn-loading");
    if(spinner){ spinner.style.display="none"; if(!btn.contains(spinner)) btn.appendChild(spinner); }
}
window.addEventListener("pageshow", ()=>{ resetSignupButton(); errorDiv.classList.remove("show"); });

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const fullName = document.getElementById("fullName").value.trim();
    const dob = document.getElementById("dob").value;
    const email = document.getElementById("email").value.trim();
    const userName = document.getElementById("uname").value.trim();
    const password = document.getElementById("pwd").value;
    const confirmPassword = document.getElementById("confirmPwd").value;
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
    errorDiv.classList.remove("show");
    const submitBtn = document.getElementById("signup-btn");
    const spinner = document.getElementById("signupBtnSpinner");
    if(!submitBtn.dataset.originalText){
        let _t=""; Array.from(submitBtn.childNodes).forEach(n=>{if(n.nodeType===3) _t+=n.textContent;});
        submitBtn.dataset.originalText=_t.trim()||"Create account";
    }
    submitBtn.disabled = true;
    submitBtn.classList.add("btn-loading");
    Array.from(submitBtn.childNodes).forEach(n=>{if(n.nodeType===3) n.textContent="";});
    if(spinner) spinner.style.display = "inline-block";
    try {
        const response = await fetch("/api/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({ fullname: fullName, dob: dob, email: email, username: userName, password: password })
        });
        const result = await response.json();
        if (!response.ok) {
            errorText.textContent = result.message || "Failed to create account";
            errorDiv.classList.add("show");
            resetSignupButton();
            return;
        }
        if(spinner) spinner.style.display = "none";
        Array.from(submitBtn.childNodes).forEach(n=>{if(n.nodeType===3) n.textContent="";});
        submitBtn.prepend(document.createTextNode("✅ Account Created!"));
        setTimeout(() => { window.location.replace("/inventory"); }, 600);
    } catch (error) {
        console.error("Signup error:", error);
        errorText.textContent = "Network error. Please check your connection.";
        errorDiv.classList.add("show");
        resetSignupButton();
    }
});