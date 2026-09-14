// Minimal auth for protected pages (reports / account setting)
// Reports & Account Setting are @page_login_required so logout must always be visible.
// This keeps the commented login/signup hidden and makes Log Out work without needing the full script.js.
document.getElementById("logoutLink")?.addEventListener("click", async (event) => {
  event.preventDefault();
  try {
    await fetch("/api/logout", { method: "POST" });
  } catch (e) {
    console.log("logout failed", e);
  }
  window.location.href = "/login";
});