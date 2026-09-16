 // Minimal auth for protected pages (reports / account setting / admin)
// Reports, Account Setting and Admin are protected — keep login/signup hidden,
// make Log Out work, and gate the Users link by role.
(async function () {
  try {
    const r = await fetch('/api/session-status');
    const j = await r.json();
    // auth.js pages are already page_login_required, but still hide Users for non-admins
    const adminLink = document.getElementById('adminLink');
    if (adminLink) adminLink.style.display = (j.logged_in && j.role === 'admin') ? 'block' : 'none';
    const roleEl = document.querySelector('.profile-role');
    if (roleEl) roleEl.textContent = j.role === 'admin' ? 'Administrator' : (j.logged_in ? 'Seller' : 'Administrator');
    const nameEl = document.getElementById('profileName');
    if (nameEl && j.username) nameEl.textContent = j.username;
  } catch (e) { console.log('auth check failed', e); }
})();

document.getElementById('logoutLink')?.addEventListener('click', async (event) => {
  event.preventDefault();
  try {
    await fetch('/api/logout', { method: 'POST' });
  } catch (e) {
    console.log('logout failed', e);
  }
  window.location.href = '/login';
});