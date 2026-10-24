/**
 * Smart Building Monitoring System - Navigation & Shared UI Components
 * Handles sidebar rendering/activation, theme toggle, mobile drawers,
 * and user role authentication guards.
 */

(function () {
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initUserSession();
    initMobileNav();
    highlightActiveNav();
    bindHeaderActions();
  });

  function initTheme() {
    const savedTheme = localStorage.getItem('smart_building_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
  }

  window.toggleTheme = function () {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('smart_building_theme', next);
    updateThemeIcon(next);
  };

  function updateThemeIcon(theme) {
    const themeBtns = document.querySelectorAll('.theme-toggle-btn i');
    themeBtns.forEach(icon => {
      if (theme === 'light') {
        icon.className = 'fa-solid fa-moon';
      } else {
        icon.className = 'fa-solid fa-sun';
      }
    });
  }

  function initUserSession() {
    // Check if on login page index.html
    const isLoginPage = window.location.pathname.endsWith('index.html') || window.location.pathname.endsWith('/') || window.location.pathname.endsWith('/frontend/');
    const auth = window.SmartBuildingStore ? window.SmartBuildingStore.getAuth() : null;

    if (!auth && !isLoginPage) {
      window.location.href = 'index.html';
      return;
    }

    if (auth) {
      const nameEl = document.getElementById('nav-user-name');
      const roleEl = document.getElementById('nav-user-role');
      const avatarEl = document.getElementById('nav-user-avatar');
      
      if (nameEl) nameEl.textContent = auth.name || 'Jordan Smith';
      if (roleEl) roleEl.textContent = 'BUILDING MANAGER';
      if (avatarEl) avatarEl.textContent = 'JS';
    }
  }

  function initMobileNav() {
    const toggleBtn = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (toggleBtn && sidebar) {
      toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
      });
    }

    // Close sidebar on outer click on mobile
    document.addEventListener('click', (e) => {
      if (sidebar && sidebar.classList.contains('open')) {
        if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
          sidebar.classList.remove('open');
        }
      }
    });
  }

  function highlightActiveNav() {
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-item');
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href && (href === currentPath || (currentPath === '' && href === 'dashboard.html'))) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  function bindHeaderActions() {
    const logoutBtn = document.getElementById('nav-logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (confirm('Are you sure you want to log out of the Building Management System?')) {
          if (window.SmartBuildingStore) {
            window.SmartBuildingStore.logout();
          } else {
            localStorage.removeItem('smart_tower_building_auth_v3');
            window.location.href = 'index.html';
          }
        }
      });
    }
  }
})();
