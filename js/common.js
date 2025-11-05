// Common JavaScript functions for LIPID+ website

// Set current year in footer
document.addEventListener('DOMContentLoaded', () => {
    const yearElement = document.getElementById('current-year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
    
    // Set active navigation based on current page
    setActiveNav();
    
    // Initialize dark mode icons
    updateDarkModeIcons();
});

// --- Dark Mode Functions ---
function toggleDarkMode() {
    const html = document.documentElement;
    const isDark = html.classList.contains('dark');
    
    if (isDark) {
        // Switch to light mode
        html.classList.remove('dark');
        localStorage.setItem('theme', 'light');
    } else {
        // Switch to dark mode
        html.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    }
    
    updateDarkModeIcons();
}

function updateDarkModeIcons() {
    const themeIconLight = document.getElementById('theme-icon-light');
    const themeIconDark = document.getElementById('theme-icon-dark');
    const isDark = document.documentElement.classList.contains('dark');
    
    if (themeIconLight && themeIconDark) {
        if (isDark) {
            // Currently in dark mode, show moon icon (dark icon)
            themeIconLight.classList.add('hidden');
            themeIconDark.classList.remove('hidden');
        } else {
            // Currently in light mode, show sun icon (light icon)
            themeIconLight.classList.remove('hidden');
            themeIconDark.classList.add('hidden');
        }
    }
}

// --- Navigation Functions ---
function setActiveNav() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    // Remove all active classes
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('nav-active');
    });
    
    // Set active based on current page
    if (currentPage === 'index.html' || currentPage === '') {
        const homeNav = document.getElementById('nav-home');
        if (homeNav) homeNav.classList.add('nav-active');
    } else if (currentPage === 'docs.html') {
        const docsNav = document.getElementById('nav-docs');
        if (docsNav) docsNav.classList.add('nav-active');
    } else if (currentPage === 'about.html') {
        const aboutNav = document.getElementById('nav-about');
        if (aboutNav) aboutNav.classList.add('nav-active');
    }
}

// --- Dropdown Functions ---
function toggleDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    if (!dropdown) return;

    const isOpen = !dropdown.classList.contains('hidden');
    
    // Close all dropdowns first
    closeAllDropdowns();
    
    // If it was closed, open it
    if (!isOpen) {
        dropdown.classList.remove('hidden');
    }
}

function closeAllDropdowns() {
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        menu.classList.add('hidden');
    });
}

// Close dropdowns if clicking outside
window.addEventListener('click', function(event) {
    if (!event.target.closest('[onclick^="toggleDropdown"]')) {
        closeAllDropdowns();
    }
});

// --- Search Functions ---
function showSearchModal(message) {
    const modal = document.getElementById('search-modal');
    const messageEl = document.getElementById('search-modal-message');
    if (modal && messageEl) {
        messageEl.textContent = message;
        modal.classList.remove('hidden');
    }
}

function closeSearchModal() {
    const modal = document.getElementById('search-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function handleSearch(event) {
    event.preventDefault();
    const input = document.getElementById('search-input');
    const query = input ? input.value.trim() : '';
    
    if (query) {
        showSearchModal(`Search functionality for "${query}" is not implemented in this demo.`);
    } else {
        showSearchModal('Please enter a search term.');
    }
}

// --- Mobile Menu Functions ---
function toggleMobileMenu(forceState) {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    
    if (!sidebar) return;
    
    let open;
    if (typeof forceState === 'boolean') {
        open = forceState;
    } else {
        open = sidebar.classList.contains('-translate-x-full');
    }

    if (open) {
        sidebar.classList.remove('-translate-x-full');
        sidebar.classList.add('translate-x-0');
        if (overlay) overlay.classList.remove('hidden');
        if (mobileMenuBtn) {
            mobileMenuBtn.innerHTML = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>`;
        }
    } else {
        sidebar.classList.add('-translate-x-full');
        sidebar.classList.remove('translate-x-0');
        if (overlay) overlay.classList.add('hidden');
        if (mobileMenuBtn) {
            mobileMenuBtn.innerHTML = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>`;
        }
    }
}

// --- Sidebar Submenu ---
function toggleSidebarMenu(submenuId, element) {
    const submenu = document.getElementById(submenuId);
    const chevron = element.querySelector('.submenu-chevron');
    if (submenu) {
        submenu.classList.toggle('hidden');
        if (chevron) chevron.classList.toggle('rotate-180');
        element.setAttribute('aria-expanded', !submenu.classList.contains('hidden'));
    }
}