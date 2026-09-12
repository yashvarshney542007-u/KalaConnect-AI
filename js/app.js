/**
 * KalaConnect AI - Main Application Controller
 * Handles view routing, modal management, toast feedback, and startup initialization
 */

const App = {
  currentView: 'marketplace', // 'marketplace' or 'space'

  init() {
    this.bindGlobalEvents();
    
    // Initialize child modules
    if (window.Auth) window.Auth.init();
    if (window.Cart) window.Cart.init();
    if (window.Marketplace) window.Marketplace.init();
    if (window.SpaceAI) window.SpaceAI.init();

    // Load real product images from Supabase Storage bucket asynchronously
    // This runs after the initial render so the page feels instant,
    // then silently swaps in the real images once fetched.
    if (window.ImageLoader) {
      window.ImageLoader.load().catch(err => {
        console.warn('[App] ImageLoader failed gracefully:', err);
      });
    }

    console.log('✨ KalaConnect AI Marketplace & AI Space Studio ready!');
  },

  bindGlobalEvents() {
    // Navigation view tabs
    const navMarketplace = document.getElementById('navBtnMarketplace');
    const navSpace = document.getElementById('navBtnSpace');

    if (navMarketplace) {
      navMarketplace.addEventListener('click', () => this.switchView('marketplace'));
    }
    if (navSpace) {
      navSpace.addEventListener('click', () => this.switchView('space'));
    }

    // Modal Close buttons & overlay click
    const modalOverlay = document.getElementById('globalModalOverlay');
    const modalCloseBtn = document.getElementById('globalModalCloseBtn');

    if (modalOverlay) {
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) this.closeModal();
      });
    }

    if (modalCloseBtn) {
      modalCloseBtn.addEventListener('click', () => this.closeModal());
    }

    // Escape key
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeModal();
        if (window.Cart) window.Cart.closeDrawer();
      }
    });
  },

  switchView(viewName) {
    this.currentView = viewName;

    const marketplaceSection = document.getElementById('viewMarketplaceSection');
    const spaceSection = document.getElementById('viewSpaceSection');
    const navMarketplace = document.getElementById('navBtnMarketplace');
    const navSpace = document.getElementById('navBtnSpace');

    if (viewName === 'marketplace') {
      if (marketplaceSection) marketplaceSection.style.display = 'block';
      if (spaceSection) spaceSection.style.display = 'none';
      if (navMarketplace) navMarketplace.classList.add('active');
      if (navSpace) navSpace.classList.remove('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      if (marketplaceSection) marketplaceSection.style.display = 'none';
      if (spaceSection) spaceSection.style.display = 'block';
      if (navMarketplace) navMarketplace.classList.remove('active');
      if (navSpace) navSpace.classList.add('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  },

  openModal(htmlContent) {
    const modalOverlay = document.getElementById('globalModalOverlay');
    const modalContainer = document.getElementById('globalModalContainer');
    
    if (modalOverlay && modalContainer) {
      modalContainer.innerHTML = htmlContent;
      modalOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  },

  closeModal() {
    const modalOverlay = document.getElementById('globalModalOverlay');
    if (modalOverlay) {
      modalOverlay.classList.remove('active');
      document.body.style.overflow = '';
    }
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconSvg = '';
    if (type === 'success') {
      iconSvg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>';
    } else {
      iconSvg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
    }

    toast.innerHTML = `
      ${iconSvg}
      <span>${message}</span>
    `;

    container.appendChild(toast);

    // Trigger animate in
    requestAnimationFrame(() => toast.classList.add('show'));

    // Remove after 3.5s
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 400);
    }, 3500);
  }
};

window.App = App;

// Bootstrap when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
