 // Minimal auth for protected pages (reports / account setting / admin)
// Reports, Account Setting and Admin are protected — keep login/signup hidden,
// make Log Out work, and gate the Users link by role.
(async function () {
    try {
      const res = await fetch('/api/session-status');
      if (!res.ok) return;

      const data = await res.json();

      const adminLink = document.getElementById('adminLink');
      if (adminLink) {
        const isAdmin = data.logged_in && data.role === 'admin';
        adminLink.style.display = isAdmin ? 'block' : 'none';
      }

      const roleEl = document.querySelector('.profile-role');
      if (roleEl) {
        roleEl.textContent = data.role === 'admin' ? 'Administrator' : (data.logged_in ? 'Seller' : 'Administrator');
      }

      const nameEl = document.getElementById('profileName');
      if (nameEl && data.username) {
        nameEl.textContent = data.username;
      }
    } catch (err) {
      console.log('auth check failed', err);
    }
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