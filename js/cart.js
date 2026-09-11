/**
 * KalaConnect AI - Customer Cart & Checkout Engine
 * Manages shopping cart state, impact calculations, artisan welfare fund, and checkout
 */

const Cart = {
  items: [],
  welfareContribution: true,
  welfareAmount: 50,
  isFirstTimeUser: true,
  discountPercent: 40,

  init() {
    // Load from localStorage if present
    const saved = localStorage.getItem('kalaconnectai_cart') || localStorage.getItem('kalaconneai_cart') || localStorage.getItem('virasat_cart');
    if (saved) {
      try {
        this.items = JSON.parse(saved);
      } catch (e) {
        this.items = [];
      }
    }

    // Sync first-time discount status with customer authentication/database
    this.syncWithUser();

    this.render();
    this.bindEvents();
  },

  syncWithUser() {
    if (window.Auth && window.Auth.currentUser) {
      // If user is registered and already placed orders, they are an old customer
      const isOldCustomer = (window.Auth.currentUser.ordersCount && window.Auth.currentUser.ordersCount > 0) || window.Auth.currentUser.isFirstTime === false;
      this.isFirstTimeUser = !isOldCustomer;
    } else {
      const hasOrderedBefore = localStorage.getItem('kalaconnectai_ordered_before') || localStorage.getItem('kalaconneai_ordered_before') || localStorage.getItem('virasat_ordered_before');
      this.isFirstTimeUser = (hasOrderedBefore !== 'true');
    }
    this.render();
  },

  save() {
    localStorage.setItem('kalaconnectai_cart', JSON.stringify(this.items));
    this.render();
  },

  addItem(productId, quantity = 1) {
    const product = window.ARTISAN_PRODUCTS.find(p => p.id === productId);
    if (!product) return;

    const existingIndex = this.items.findIndex(i => i.id === productId);
    if (existingIndex > -1) {
      this.items[existingIndex].quantity += quantity;
    } else {
      this.items.push({
        id: product.id,
        name: product.name,
        price: product.price,
        image: product.image,
        region: product.region,
        state: product.state,
        craftForm: product.craftForm,
        artisanName: product.artisan.name,
        artisanSharePercent: product.artisanSharePercent,
        quantity: quantity
      });
    }

    this.save();
    window.App.showToast(`Added "${product.name}" to your cart!`, 'success');
    this.openDrawer();
  },

  updateQuantity(productId, delta) {
    const item = this.items.find(i => i.id === productId);
    if (!item) return;

    item.quantity += delta;
    if (item.quantity <= 0) {
      this.items = this.items.filter(i => i.id !== productId);
      window.App.showToast(`Removed "${item.name}" from cart.`, 'info');
    }
    this.save();
  },

  toggleWelfare() {
    this.welfareContribution = !this.welfareContribution;
    this.render();
  },

  getSubtotal() {
    return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  },

  getDiscountAmount() {
    if (!this.isFirstTimeUser) return 0;
    return Math.round(this.getSubtotal() * (this.discountPercent / 100));
  },

  getTotal() {
    const subtotal = this.getSubtotal();
    if (subtotal === 0) return 0;
    const discount = this.getDiscountAmount();
    const welfare = this.welfareContribution ? this.welfareAmount : 0;
    return Math.max(0, subtotal - discount + welfare);
  },

  getTotalArtisanDirectEarning() {
    return this.items.reduce((sum, item) => {
      const share = item.price * (item.artisanSharePercent / 100);
      return sum + Math.round(share * item.quantity);
    }, 0);
  },

  getItemCount() {
    return this.items.reduce((sum, item) => sum + item.quantity, 0);
  },

  openDrawer() {
    const backdrop = document.getElementById('cartDrawerBackdrop');
    if (backdrop) backdrop.classList.add('active');
    document.body.style.overflow = 'hidden';
  },

  closeDrawer() {
    const backdrop = document.getElementById('cartDrawerBackdrop');
    if (backdrop) backdrop.classList.remove('active');
    document.body.style.overflow = '';
  },

  bindEvents() {
    const cartToggle = document.getElementById('cartToggleBtn');
    const cartClose = document.getElementById('cartCloseBtn');
    const backdrop = document.getElementById('cartDrawerBackdrop');
    const checkoutBtn = document.getElementById('checkoutBtn');

    if (cartToggle) cartToggle.addEventListener('click', () => this.openDrawer());
    if (cartClose) cartClose.addEventListener('click', () => this.closeDrawer());
    
    if (backdrop) {
      backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) this.closeDrawer();
      });
    }

    if (checkoutBtn) {
      checkoutBtn.addEventListener('click', () => this.handleCheckout());
    }
  },

  render() {
    const badge = document.getElementById('cartCountBadge');
    const count = this.getItemCount();
    if (badge) {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'flex' : 'none';
    }

    const drawerCount = document.getElementById('cartHeaderCount');
    if (drawerCount) drawerCount.textContent = `${count} ${count === 1 ? 'craft' : 'crafts'}`;

    const itemsContainer = document.getElementById('cartItemsList');
    const emptyState = document.getElementById('cartEmptyView');
    const footer = document.getElementById('cartFooter');

    if (!itemsContainer) return;

    if (this.items.length === 0) {
      itemsContainer.innerHTML = '';
      if (emptyState) emptyState.style.display = 'block';
      if (footer) footer.style.display = 'none';
      return;
    }

    if (emptyState) emptyState.style.display = 'none';
    if (footer) footer.style.display = 'block';

    itemsContainer.innerHTML = this.items.map(item => `
      <div class="cart-item">
        <img src="${item.image}" alt="${item.name}" class="cart-item-img" />
        <div class="cart-item-info">
          <h4 class="cart-item-title">${item.name}</h4>
          <p class="cart-item-origin">By ${item.artisanName} · ${item.craftForm}</p>
          <div class="cart-item-row">
            <span class="cart-item-price">₹${(item.price * item.quantity).toLocaleString('en-IN')}</span>
            <div class="qty-control">
              <button class="qty-btn" onclick="Cart.updateQuantity('${item.id}', -1)">−</button>
              <span class="qty-value">${item.quantity}</span>
              <button class="qty-btn" onclick="Cart.updateQuantity('${item.id}', 1)">+</button>
            </div>
          </div>
        </div>
      </div>
    `).join('');

    // Summary lines
    const subtotal = this.getSubtotal();
    const discount = this.getDiscountAmount();
    const total = this.getTotal();
    const artisanDirect = this.getTotalArtisanDirectEarning();

    const subtotalEl = document.getElementById('cartSubtotal');
    const totalEl = document.getElementById('cartTotal');
    const directEarningEl = document.getElementById('cartDirectEarning');
    const discountRow = document.getElementById('cartDiscountRow');
    const discountValEl = document.getElementById('cartDiscountValue');
    const firstTimeBanner = document.getElementById('cartFirstTimeBanner');

    if (subtotalEl) subtotalEl.textContent = `₹${subtotal.toLocaleString('en-IN')}`;
    if (totalEl) totalEl.textContent = `₹${total.toLocaleString('en-IN')}`;
    if (directEarningEl) directEarningEl.textContent = `₹${artisanDirect.toLocaleString('en-IN')}`;

    if (firstTimeBanner) {
      firstTimeBanner.style.display = (this.isFirstTimeUser && this.items.length > 0) ? 'flex' : 'none';
    }

    if (discountRow && discountValEl) {
      if (this.isFirstTimeUser && discount > 0) {
        discountRow.style.display = 'flex';
        discountValEl.textContent = `− ₹${discount.toLocaleString('en-IN')}`;
      } else {
        discountRow.style.display = 'none';
      }
    }
  },

  handleCheckout() {
    if (this.items.length === 0) return;

    const orderId = 'VIR-' + Math.floor(100000 + Math.random() * 900000);
    const subtotal = this.getSubtotal();
    const discount = this.getDiscountAmount();
    const total = this.getTotal();
    const artisanDirect = this.getTotalArtisanDirectEarning();
    const wasFirstTime = this.isFirstTimeUser;

    // Close cart drawer
    this.closeDrawer();

    const loggedInUser = window.Auth && window.Auth.currentUser;
    const recipientText = loggedInUser ? `for <strong>${loggedInUser.name}</strong> (${loggedInUser.city || 'India'})` : 'to your registered address';

    // Award Kala loyalty points & increment customer database order count
    if (loggedInUser) {
      loggedInUser.kalaPoints = (loggedInUser.kalaPoints || 100) + Math.round(total / 50);
      loggedInUser.ordersCount = (loggedInUser.ordersCount || 0) + 1;
      loggedInUser.isFirstTime = false;
      localStorage.setItem('kalaconnect_user', JSON.stringify(loggedInUser));
      if (window.Auth && window.Auth.updateUserInDatabase) {
        window.Auth.updateUserInDatabase(loggedInUser);
      }
      if (window.Auth.renderNavAuth) window.Auth.renderNavAuth();
    }

    // Mark customer as having completed an order
    localStorage.setItem('kalaconnectai_ordered_before', 'true');
    this.isFirstTimeUser = false;
    this.items = [];
    this.save();

    // Open Checkout Confirmation Modal with 40% discount highlight
    const modalContent = `
      <div class="order-success-content">
        <div class="success-icon-wrap">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
        </div>
        <h3>Order Placed Successfully!</h3>
        <p>Order ID: <strong>#${orderId}</strong>. We've notified the artisan collective to carefully pack and dispatch ${recipientText}.</p>

        ${wasFirstTime ? `
          <div style="background: #ECFDF5; border: 1px solid #10B981; border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; text-align: left;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <span style="font-weight: 700; color: #065F46; font-size: 0.9rem;">🎉 First-Time User 40% Discount Applied</span>
              <span style="background: #059669; color: white; padding: 2px 8px; border-radius: 999px; font-size: 0.72rem; font-weight: 800;">SAVED ₹${discount.toLocaleString('en-IN')}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #047857;">
              <span>Original Craft Value: <s>₹${subtotal.toLocaleString('en-IN')}</s></span>
              <span><strong>Final Amount Paid: ₹${total.toLocaleString('en-IN')}</strong></span>
            </div>
          </div>
        ` : ''}

        <div class="order-impact-card">
          <h5>🌿 Direct Social Impact Verified</h5>
          <p><strong>₹${artisanDirect.toLocaleString('en-IN')}</strong> will be disbursed directly to rural artisan bank accounts. The 40% promotional welcome subsidy is fully absorbed by the Market Linkage Grant so the makers receive 100% of their fair earnings.</p>
        </div>

        <div style="display: flex; gap: 10px; justify-content: center;">
          <button class="btn-primary-large" style="max-width: 240px;" onclick="window.App.closeModal()">
            Continue Exploring
          </button>
          <button class="btn-secondary-large" style="max-width: 180px; font-size: 0.82rem;" onclick="Cart.resetFirstTimeStatus(); window.App.closeModal();">
            ↺ Reset Test User
          </button>
        </div>
      </div>
    `;

    window.App.openModal(modalContent);

    // Record that first order was placed
    localStorage.setItem('kalaconnectai_ordered_before', 'true');
    this.isFirstTimeUser = false;

    // Clear cart
    this.items = [];
    this.save();
  },

  resetFirstTimeStatus() {
    localStorage.removeItem('kalaconnectai_ordered_before');
    localStorage.removeItem('kalaconneai_ordered_before');
    localStorage.removeItem('virasat_ordered_before');
    this.isFirstTimeUser = true;
    this.render();
    window.App.showToast('Reset status: You are now a First-Time User again with 40% OFF!', 'success');
  }
};

window.Cart = Cart;
