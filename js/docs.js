// Docs page specific JavaScript

function showPage(pageId, navId, clickedElement) {
    // Hide all page content
    document.querySelectorAll('.page-content').forEach(page => {
        page.classList.add('hidden');
    });
    
    // Show the target page
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.remove('hidden');
    }

    // Update active state in sidebar
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.classList.remove('sidebar-active');
    });
    
    // Find the corresponding link in the sidebar and activate it
    const activeSidebarLink = document.querySelector(`.sidebar-link[data-page-id="${pageId}"]`);
    if (activeSidebarLink) {
        activeSidebarLink.classList.add('sidebar-active');
        
        // If it's in a submenu, make sure the submenu is open
        const submenu = activeSidebarLink.closest('div[id^="submenu-"]');
        if (submenu && submenu.classList.contains('hidden')) {
            // Find the button that controls this submenu
            const parentButton = document.querySelector(`button[onclick*="'${submenu.id}'"]`);
            if (parentButton) {
                submenu.classList.remove('hidden');
                parentButton.classList.add('sidebar-active');
                parentButton.querySelector('.submenu-chevron').classList.add('rotate-180');
                parentButton.setAttribute('aria-expanded', 'true');
            }
        }
    }

    // Close mobile menu on navigation
    if (window.innerWidth < 768) {
        toggleMobileMenu(false);
    }
    
    // Close all top-nav dropdowns
    closeAllDropdowns();

    // Scroll to top
    document.getElementById('content-area').scrollTop = 0;
    window.scrollTo(0, 0);
    
    // Prevent default link behavior
    if (clickedElement && clickedElement.preventDefault) {
        clickedElement.preventDefault();
    }
}

// Initialize the docs page
document.addEventListener('DOMContentLoaded', () => {
    // Show installation page by default
    showPage('page-installation', 'nav-docs', document.querySelector('.sidebar-link[data-page-id="page-installation"]'));
});