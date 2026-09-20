// Shared session UI for every page that has navigation links or a profile card.
async function initializeAuth() {
  try {
    const response = await fetch('/api/session-status');
    if (!response.ok) return;

    const user = await response.json();
    const isLoggedIn = user.logged_in;
    const isAdmin = isLoggedIn && user.role === 'admin';
    const profileRole = isAdmin ? 'Administrator' : 'Seller';

    const loginLink = document.getElementById('loginLink');
    const signupLink = document.getElementById('signupLink');
    const logoutLink = document.getElementById('logoutLink');
    const adminLink = document.getElementById('adminLink');
    const profileCard = document.getElementById('profileCard');
    const profileName = document.getElementById('profileName');
    const roleElement = document.querySelector('.profile-role');

    if (loginLink) loginLink.style.display = isLoggedIn ? 'none' : 'block';
    if (signupLink) signupLink.style.display = isLoggedIn ? 'none' : 'block';
    if (logoutLink) logoutLink.style.display = isLoggedIn ? 'block' : 'none';
    if (adminLink) adminLink.style.display = isAdmin ? 'block' : 'none';
    if (profileCard) profileCard.style.display = isLoggedIn ? 'flex' : 'none';
    if (profileName && isLoggedIn) profileName.textContent = user.username;
    if (roleElement) roleElement.textContent = profileRole;

    return user;
  } catch (error) {
    console.log('auth check failed', error);
    return null;
  }
}

// Other page scripts can await this instead of requesting session status again.
window.authReady = initializeAuth();

document.getElementById('logoutLink')?.addEventListener('click', async (event) => {
  event.preventDefault();
  try {
    await fetch('/api/logout', { method: 'POST' });
  } catch (e) {
    console.log('logout failed', e);
  }
  window.location.href = '/login';
});
