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

    // Check signed in user status for checkout button and prompt
    const loggedInUser = window.Auth && window.Auth.currentUser;
    const checkoutBtn = document.getElementById('checkoutBtn');
    const signInNotice = document.getElementById('cartSignInNotice');

    if (signInNotice) {
      signInNotice.style.display = (!loggedInUser && this.items.length > 0) ? 'flex' : 'none';
    }

    if (checkoutBtn) {
      if (!loggedInUser) {
        checkoutBtn.innerHTML = `
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" style="margin-right: 6px; vertical-align: -2px;"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
          Sign In to Place Order
        `;
        checkoutBtn.style.background = '#8F4F24';
      } else {
        checkoutBtn.innerHTML = `Proceed to Order (Fair Trade Link)`;
        checkoutBtn.style.background = '';
      }
    }
  },

  // ── Delivery date estimator ─────────────────────────────────────────────────
  getDeliveryDate(item) {
    // Remote / far-flung states get extra days
    const remoteStates = [
      'Arunachal Pradesh', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland',
      'Sikkim', 'Tripura', 'Assam', 'Jammu and Kashmir', 'Ladakh',
      'Andaman and Nicobar', 'Lakshadweep', 'Himachal Pradesh', 'Uttarakhand'
    ];
    const isRemote = remoteStates.includes(item.state);
    // Handloom / textile crafts take 1 extra day to pack
    const isDelicate = ['Handloom', 'Weaving', 'Embroidery', 'Zari'].some(
      k => (item.craftForm || '').includes(k)
    );
    const minDays = isRemote ? 5 : 3;
    const maxDays = (isRemote ? 8 : 6) + (isDelicate ? 1 : 0);

    const today = new Date();
    const minDate = new Date(today); minDate.setDate(today.getDate() + minDays);
    const maxDate = new Date(today); maxDate.setDate(today.getDate() + maxDays);

    const fmt = (d) => d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    return { minDays, maxDays, label: `${fmt(minDate)} – ${fmt(maxDate)}`, minDate, maxDate };
  },

  // ── UPI QR URL builder (uses free QR Server API — no JS lib required) ──────
  getUpiQrImgUrl(total) {
    const upiId = 'kalaconnect@okaxis';
    const upiLink = `upi://pay?pa=${upiId}&pn=KalaConnect%20AI&am=${total}&cu=INR&tn=ArtisanCraft`;
    const encoded = encodeURIComponent(upiLink);
    return `https://api.qrserver.com/v1/create-qr-code/?size=180x180&margin=8&data=${encoded}`;
  },

  handleCheckout() {
    if (this.items.length === 0) return;

    // MANDATORY REQUIREMENT: Must be signed in to place an order
    const loggedInUser = window.Auth && window.Auth.currentUser;
    if (!loggedInUser) {
      this.closeDrawer();
      window.App.showToast('Please sign in or create an account to place your order.', 'warning');
      if (window.Auth && window.Auth.openAuthModal) {
        window.Auth.openAuthModal('signin');
      }
      return;
    }

    // Close cart drawer and open Address & Payment Checkout Modal
    this.closeDrawer();
    this.openCheckoutModal();
  },

  checkoutState: {
    paymentMethod: 'card', // 'card', 'upi', 'netbanking', 'cod'
    selectedBank: 'hdfc',
    selectedUpiApp: 'gpay',
    // Cached totals — set when modal opens so tab switching never loses them
    cachedTotal: 0,
    cachedSubtotal: 0,
    cachedDiscount: 0,
    cachedArtisanDirect: 0,
    cachedWasFirstTime: false,
    cachedItemsSnapshot: []
  },

  openCheckoutModal() {
    const loggedInUser = window.Auth && window.Auth.currentUser;
    if (!loggedInUser) return;

    const subtotal = this.getSubtotal();
    const discount = this.getDiscountAmount();
    const total = this.getTotal();
    const artisanDirect = this.getTotalArtisanDirectEarning();
    const wasFirstTime = this.isFirstTimeUser;
    const isCodAvailable = total >= 1000;

    // Cache everything for use by switchPaymentTab & confirmOrderPlacement
    this.checkoutState.cachedTotal = total;
    this.checkoutState.cachedSubtotal = subtotal;
    this.checkoutState.cachedDiscount = discount;
    this.checkoutState.cachedArtisanDirect = artisanDirect;
    this.checkoutState.cachedWasFirstTime = wasFirstTime;
    this.checkoutState.cachedItemsSnapshot = JSON.parse(JSON.stringify(this.items));

    // If COD was active but order < 1000, fallback to Card
    if (this.checkoutState.paymentMethod === 'cod' && !isCodAvailable) {
      this.checkoutState.paymentMethod = 'card';
    }

    const INDIAN_STATES = [
      "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
      "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
      "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
      "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
      "Andaman and Nicobar", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi",
      "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
    ];

    const stateOptionsHTML = INDIAN_STATES.map(st => {
      const isSelected = (loggedInUser.city && loggedInUser.city.toLowerCase().includes(st.toLowerCase())) ? 'selected' : '';
      return `<option value="${st}" ${isSelected}>${st}</option>`;
    }).join('');

    const miniItemsHTML = this.items.map(item => {
      const delivery = this.getDeliveryDate(item);
      return `
      <div class="checkout-mini-item">
        <img src="${item.image}" alt="${item.name}" />
        <div class="checkout-mini-item-info">
          <h6>${item.name}</h6>
          <span>${item.quantity} × ₹${item.price.toLocaleString('en-IN')} (${item.craftForm})</span>
          <span class="delivery-date-badge">🚚 Est. ${delivery.label}</span>
        </div>
        <strong>₹${(item.price * item.quantity).toLocaleString('en-IN')}</strong>
      </div>
    `;
    }).join('');

    const modalHTML = `
      <div class="checkout-modal-container">
        <div class="checkout-header">
          <h3>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
            Secure Checkout & Artisan Linkage
          </h3>
          <p>Complete your delivery address and payment to directly empower rural artisan families.</p>
        </div>

        <form id="checkoutMainForm" onsubmit="Cart.confirmOrderPlacement(event)">
          <div class="checkout-main-grid">
            <!-- Left Column: Address & Payment Selection -->
            <div class="checkout-left-col">
              
              <!-- STEP 1: DELIVERY ADDRESS -->
              <div class="checkout-section-box">
                <div class="checkout-section-title">
                  <span class="step-num">1</span>
                  <span>Shipping & Delivery Address</span>
                </div>

                <div class="address-form-grid">
                  <div class="form-group-item">
                    <label>Full Name</label>
                    <input type="text" id="chkFullName" required value="${loggedInUser.name || ''}" placeholder="e.g. Priya Sharma" />
                  </div>

                  <div class="form-group-item">
                    <label>Contact Phone</label>
                    <input type="tel" id="chkPhone" required pattern="[0-9]{10}" maxlength="10" value="${(loggedInUser.phone || '').replace('+91', '')}" placeholder="10-digit mobile" />
                  </div>

                  <div class="form-group-item full-span">
                    <label>Flat, House No., Street Address</label>
                    <input type="text" id="chkStreet" required placeholder="House/Flat No., Apartment, Street, Locality" value="Sector 4, Cultural Artisan Enclave" />
                  </div>

                  <div class="form-group-item">
                    <label>City / Town</label>
                    <input type="text" id="chkCity" required value="${(loggedInUser.city || 'Varanasi').split(',')[0].trim()}" placeholder="City" />
                  </div>

                  <div class="form-group-item">
                    <label>State / UT (All 28+8)</label>
                    <select id="chkState" required>
                      ${stateOptionsHTML}
                    </select>
                  </div>

                  <div class="form-group-item">
                    <label>PIN Code</label>
                    <input type="text" id="chkPinCode" required pattern="[0-9]{6}" maxlength="6" value="221001" placeholder="6-digit PIN" />
                  </div>

                  <div class="form-group-item">
                    <label>Landmark (Optional)</label>
                    <input type="text" id="chkLandmark" placeholder="Near Temple / Metro / Market" />
                  </div>
                </div>
              </div>

              <!-- STEP 2: PAYMENT METHOD SELECTION -->
              <div class="checkout-section-box">
                <div class="checkout-section-title">
                  <span class="step-num">2</span>
                  <span>Select Payment Method</span>
                </div>

                <!-- Payment Tabs Switcher -->
                <div class="payment-tabs-bar">
                  <button type="button" class="payment-tab-btn ${this.checkoutState.paymentMethod === 'card' ? 'active' : ''}" onclick="Cart.switchPaymentTab('card')">
                    💳 Card
                  </button>
                  <button type="button" class="payment-tab-btn ${this.checkoutState.paymentMethod === 'upi' ? 'active' : ''}" onclick="Cart.switchPaymentTab('upi')">
                    ⚡ UPI
                  </button>
                  <button type="button" class="payment-tab-btn ${this.checkoutState.paymentMethod === 'netbanking' ? 'active' : ''}" onclick="Cart.switchPaymentTab('netbanking')">
                    🏦 NetBanking
                  </button>
                  <button type="button" class="payment-tab-btn ${this.checkoutState.paymentMethod === 'cod' ? 'active' : ''}" onclick="Cart.switchPaymentTab('cod')">
                    💵 COD
                  </button>
                </div>

                <!-- Dynamic Payment Method Content Area -->
                <div id="checkoutPaymentDynamicArea">
                  ${this.getPaymentAreaHTML(isCodAvailable, total)}
                </div>
              </div>
            </div>

            <!-- Right Column: Order Summary & Pay Button -->
            <div class="checkout-right-col">
              <div class="checkout-summary-sidebar">
                <h4>Order Summary</h4>

                <div class="checkout-mini-items">
                  ${miniItemsHTML}
                </div>

                <div style="border-top: 1px solid var(--border-subtle); padding-top: 10px; margin-top: 10px;">
                  <div class="cart-summary-line" style="font-size: 0.85rem;">
                    <span>Subtotal</span>
                    <span>₹${subtotal.toLocaleString('en-IN')}</span>
                  </div>

                  ${wasFirstTime ? `
                    <div class="cart-summary-line" style="font-size: 0.85rem; color: #10B981; font-weight: 700;">
                      <span>First-Time 40% OFF</span>
                      <span>− ₹${discount.toLocaleString('en-IN')}</span>
                    </div>
                  ` : ''}

                  ${this.welfareContribution ? `
                    <div class="cart-summary-line" style="font-size: 0.85rem;">
                      <span>Artisan Welfare Fund</span>
                      <span>+ ₹${this.welfareAmount}</span>
                    </div>
                  ` : ''}

                  <div class="cart-summary-line" style="font-size: 0.85rem;">
                    <span>Delivery</span>
                    <span style="color: var(--forest-green); font-weight: 700;">FREE (Artisan Direct)</span>
                  </div>

                  <div class="cart-summary-total" style="font-size: 1.15rem; margin: 12px 0;">
                    <span>Total Amount</span>
                    <span style="color: var(--primary);">₹${total.toLocaleString('en-IN')}</span>
                  </div>

                  <div class="subsidy-note" style="margin-bottom: 12px; font-size: 0.74rem;">
                    🌱 <strong>₹${artisanDirect.toLocaleString('en-IN')}</strong> directly disbursed to rural artisan bank accounts.
                  </div>

                  <button type="submit" class="btn-confirm-pay" id="btnConfirmPay">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    Place Order (₹${total.toLocaleString('en-IN')})
                  </button>

                  <div style="text-align: center; margin-top: 10px;">
                    <span style="font-size: 0.72rem; color: var(--text-muted);">
                      🔒 256-Bit Bank Grade SSL Encrypted Checkout
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    `;

    window.App.openModal(modalHTML);
  },

  getPaymentAreaHTML(isCodAvailable, total) {
    const method = this.checkoutState.paymentMethod;

    if (method === 'card') {
      return `
        <div class="card-payment-panel">
          <div class="bank-selection-header">Choose Your Bank & Card Provider</div>
          <div class="bank-badges-grid">
            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'hdfc' ? 'active' : ''}" onclick="Cart.selectBank('hdfc')">
              <div class="bank-logo-box bank-hdfc">HDFC</div>
              <div class="bank-badge-name">HDFC Bank</div>
            </div>

            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'sbi' ? 'active' : ''}" onclick="Cart.selectBank('sbi')">
              <div class="bank-logo-box bank-sbi">SBI</div>
              <div class="bank-badge-name">State Bank of India</div>
            </div>

            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'icici' ? 'active' : ''}" onclick="Cart.selectBank('icici')">
              <div class="bank-logo-box bank-icici">ICICI</div>
              <div class="bank-badge-name">ICICI Bank</div>
            </div>

            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'axis' ? 'active' : ''}" onclick="Cart.selectBank('axis')">
              <div class="bank-logo-box bank-axis">AXIS</div>
              <div class="bank-badge-name">Axis Bank</div>
            </div>

            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'kotak' ? 'active' : ''}" onclick="Cart.selectBank('kotak')">
              <div class="bank-logo-box bank-kotak">KOTAK</div>
              <div class="bank-badge-name">Kotak Mahindra</div>
            </div>

            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'other' ? 'active' : ''}" onclick="Cart.selectBank('other')">
              <div class="bank-logo-box" style="background: #475569;">CARD</div>
              <div class="bank-badge-name">Other Debit / Credit</div>
            </div>
          </div>

          <div class="address-form-grid" style="margin-top: 10px;">
            <div class="form-group-item full-span">
              <label>Card Number</label>
              <input type="text" id="chkCardNumber" required maxlength="19" placeholder="4532 •••• •••• 8921" value="4532 8812 3901 8921" />
            </div>

            <div class="form-group-item">
              <label>Valid Thru (MM/YY)</label>
              <input type="text" id="chkCardExpiry" required maxlength="5" placeholder="MM/YY" value="08/29" />
            </div>

            <div class="form-group-item">
              <label>CVV / CVC</label>
              <input type="password" id="chkCardCvv" required maxlength="4" placeholder="•••" value="782" />
            </div>
          </div>
        </div>
      `;
    }

    if (method === 'upi') {
      const qrImgUrl = this.getUpiQrImgUrl(total);
      return `
        <div class="upi-payment-panel">
          <div class="bank-selection-header">Select Your UPI App</div>
          <div class="upi-apps-row">
            <div class="upi-app-chip ${this.checkoutState.selectedUpiApp === 'gpay' ? 'active' : ''}" onclick="Cart.selectUpiApp('gpay')">
              <span>🔵</span> Google Pay
            </div>
            <div class="upi-app-chip ${this.checkoutState.selectedUpiApp === 'phonepe' ? 'active' : ''}" onclick="Cart.selectUpiApp('phonepe')">
              <span>🟣</span> PhonePe
            </div>
            <div class="upi-app-chip ${this.checkoutState.selectedUpiApp === 'paytm' ? 'active' : ''}" onclick="Cart.selectUpiApp('paytm')">
              <span>🔷</span> Paytm
            </div>
            <div class="upi-app-chip ${this.checkoutState.selectedUpiApp === 'bhim' ? 'active' : ''}" onclick="Cart.selectUpiApp('bhim')">
              <span>🇮🇳</span> BHIM
            </div>
          </div>

          <!-- UPI QR Code — reliable img via QR Server API, no JS lib needed -->
          <div class="upi-qr-box">
            <div class="upi-qr-label">Scan &amp; Pay via any UPI App</div>
            <img
              src="${qrImgUrl}"
              alt="UPI QR Code"
              width="180" height="180"
              style="border-radius:8px; border:2px solid #E7E0D6; display:block;"
            />
            <div class="upi-qr-amount">₹${total.toLocaleString('en-IN')}</div>
            <div class="upi-qr-id">kalaconnect@okaxis</div>
          </div>

          <div class="upi-qr-divider"><span>or enter UPI ID manually</span></div>

          <div class="form-group-item" style="margin-top: 10px;">
            <label>UPI Virtual ID (VPA)</label>
            <input type="text" id="chkUpiId" required placeholder="mobile@upi / yourname@oksbi" value="artisan.buyer@okhdfcbank" />
          </div>
          <p style="font-size: 0.74rem; color: var(--text-muted); margin-top: 6px;">
            A payment request will be sent to your UPI app for authorization.
          </p>
        </div>
      `;
    }

    if (method === 'netbanking') {
      return `
        <div class="netbanking-panel">
          <div class="bank-selection-header">Choose Your Registered Net Banking Portal</div>
          <div class="bank-badges-grid">
            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'sbi' ? 'active' : ''}" onclick="Cart.selectBank('sbi')">
              <div class="bank-logo-box bank-sbi">SBI</div>
              <div class="bank-badge-name">State Bank of India</div>
            </div>

            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'hdfc' ? 'active' : ''}" onclick="Cart.selectBank('hdfc')">
              <div class="bank-logo-box bank-hdfc">HDFC</div>
              <div class="bank-badge-name">HDFC Bank</div>
            </div>

            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'icici' ? 'active' : ''}" onclick="Cart.selectBank('icici')">
              <div class="bank-logo-box bank-icici">ICICI</div>
              <div class="bank-badge-name">ICICI Bank</div>
            </div>

            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'axis' ? 'active' : ''}" onclick="Cart.selectBank('axis')">
              <div class="bank-logo-box bank-axis">AXIS</div>
              <div class="bank-badge-name">Axis Bank</div>
            </div>

            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'kotak' ? 'active' : ''}" onclick="Cart.selectBank('kotak')">
              <div class="bank-logo-box bank-kotak">KOTAK</div>
              <div class="bank-badge-name">Kotak Bank</div>
            </div>

            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'pnb' ? 'active' : ''}" onclick="Cart.selectBank('pnb')">
              <div class="bank-logo-box bank-pnb">PNB</div>
              <div class="bank-badge-name">Punjab National Bank</div>
            </div>

            <div class="bank-badge-btn ${this.checkoutState.selectedBank === 'bob' ? 'active' : ''}" onclick="Cart.selectBank('bob')">
              <div class="bank-logo-box bank-bob">BOB</div>
              <div class="bank-badge-name">Bank of Baroda</div>
            </div>
          </div>
          <p style="font-size: 0.74rem; color: var(--text-muted);">
            You will be redirected to your bank's secure net banking authorization gateway.
          </p>
        </div>
      `;
    }

    if (method === 'cod') {
      if (!isCodAvailable) {
        return `
          <div class="cod-alert-disabled">
            <h6>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
              Cash on Delivery (COD) Cancelled / Unavailable
            </h6>
            <p>
              To prevent fraudulent and rejected dispatches to remote artisan villages, Cash on Delivery is strictly restricted to orders of <strong>₹1,000 and above</strong>.
            </p>
            <p style="margin-top: 6px; font-weight: 700;">
              Your current order total is ₹${total.toLocaleString('en-IN')}. Please select <strong>Credit/Debit Card, UPI, or Net Banking</strong> above, or add more crafts to reach ₹1,000.
            </p>
          </div>
        `;
      }

      return `
        <div class="cod-allowed-box">
          <h6>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            Cash on Delivery Eligible (Orders Over ₹1,000)
          </h6>
          <p style="font-size: 0.84rem; margin: 0; line-height: 1.4;">
            Pay <strong>₹${total.toLocaleString('en-IN')}</strong> in cash upon doorstep delivery by our verified courier partner.
          </p>
          <p style="font-size: 0.74rem; color: #15803D; margin-top: 6px;">
            💡 Note: Please keep exact change ready to assist the courier representative.
          </p>
        </div>
      `;
    }

    return '';
  },

  switchPaymentTab(tabName, evObj) {
    this.checkoutState.paymentMethod = tabName;
    // Always use the cached total from when the modal opened — never recompute
    // from Cart.items here, as that can return 0 if state drifts between renders.
    const total = this.checkoutState.cachedTotal || this.getTotal();
    const isCodAvailable = total >= 1000;

    // Update active class on tab buttons
    document.querySelectorAll('.payment-tab-btn').forEach(btn => btn.classList.remove('active'));
    const activeBtn = (evObj && evObj.currentTarget) || (evObj && evObj.target) ||
                      (typeof event !== 'undefined' && event && event.target);
    if (activeBtn) activeBtn.classList.add('active');

    // Update dynamic area
    const area = document.getElementById('checkoutPaymentDynamicArea');
    if (area) {
      area.innerHTML = this.getPaymentAreaHTML(isCodAvailable, total);
    }

    // Enable/disable submit button based on COD availability
    const submitBtn = document.getElementById('btnConfirmPay');
    if (submitBtn) {
      if (tabName === 'cod' && !isCodAvailable) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'COD Unavailable (< ₹1,000)';
      } else {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          Place Order (₹${total.toLocaleString('en-IN')})
        `;
      }
    }
  },

  selectBank(bankId) {
    this.checkoutState.selectedBank = bankId;
    document.querySelectorAll('.bank-badge-btn').forEach(btn => btn.classList.remove('active'));
    if (event && event.currentTarget) {
      event.currentTarget.classList.add('active');
    }
  },

  selectUpiApp(appId) {
    this.checkoutState.selectedUpiApp = appId;
    document.querySelectorAll('.upi-app-chip').forEach(btn => btn.classList.remove('active'));
    if (event && event.currentTarget) {
      event.currentTarget.classList.add('active');
    }
  },

  confirmOrderPlacement(e) {
    e.preventDefault();

    // Use cached snapshot from modal open — items may have been cleared by re-renders
    const itemsToProcess = this.items.length > 0
      ? this.items
      : this.checkoutState.cachedItemsSnapshot;

    if (!itemsToProcess || itemsToProcess.length === 0) {
      window.App.showToast('Your cart appears empty. Please add items and try again.', 'error');
      return;
    }

    // Restore items if they drifted empty
    if (this.items.length === 0 && itemsToProcess.length > 0) {
      this.items = itemsToProcess;
    }

    const loggedInUser = window.Auth && window.Auth.currentUser;
    if (!loggedInUser) {
      window.App.showToast('Please sign in to place your order.', 'warning');
      return;
    }

    // Use cached values from modal open — safe even if Cart.items drifted empty.
    // IMPORTANT: use explicit check, not || (since 0 is a valid falsy total that breaks ||)
    const total        = (this.checkoutState.cachedTotal > 0)  ? this.checkoutState.cachedTotal  : this.getTotal();
    const subtotal     = (this.checkoutState.cachedSubtotal > 0) ? this.checkoutState.cachedSubtotal : this.getSubtotal();
    const discount     = this.checkoutState.cachedDiscount  !== undefined ? this.checkoutState.cachedDiscount  : this.getDiscountAmount();
    const artisanDirect = this.checkoutState.cachedArtisanDirect > 0 ? this.checkoutState.cachedArtisanDirect : this.getTotalArtisanDirectEarning();
    const wasFirstTime = this.checkoutState.cachedWasFirstTime;
    const isCodAvailable = total >= 1000;

    // Strict COD check
    if (this.checkoutState.paymentMethod === 'cod' && !isCodAvailable) {
      window.App.showToast('Cash on Delivery is cancelled for orders under ₹1,000. Please choose Card, UPI, or Net Banking.', 'error');
      return;
    }

    // Collect Address
    const address = {
      fullName: (document.getElementById('chkFullName')?.value || loggedInUser.name).trim(),
      phone: (document.getElementById('chkPhone')?.value || loggedInUser.phone || '').trim(),
      street: (document.getElementById('chkStreet')?.value || '').trim(),
      city: (document.getElementById('chkCity')?.value || '').trim(),
      state: (document.getElementById('chkState')?.value || '').trim(),
      pinCode: (document.getElementById('chkPinCode')?.value || '').trim(),
      landmark: (document.getElementById('chkLandmark')?.value || '').trim()
    };

    // Formatted payment method string for receipt
    let paymentSummaryText = 'Credit / Debit Card';
    const bankNames = {
      hdfc: 'HDFC Bank',
      sbi: 'State Bank of India',
      icici: 'ICICI Bank',
      axis: 'Axis Bank',
      kotak: 'Kotak Mahindra Bank',
      pnb: 'Punjab National Bank',
      bob: 'Bank of Baroda',
      other: 'Bank Card'
    };

    if (this.checkoutState.paymentMethod === 'card') {
      const bankName = bankNames[this.checkoutState.selectedBank] || 'Bank Card';
      paymentSummaryText = `💳 ${bankName} Card (Ending in 8921)`;
    } else if (this.checkoutState.paymentMethod === 'upi') {
      const upiId = document.getElementById('chkUpiId')?.value || 'artisan.buyer@upi';
      paymentSummaryText = `⚡ UPI Payment (${upiId})`;
    } else if (this.checkoutState.paymentMethod === 'netbanking') {
      const bankName = bankNames[this.checkoutState.selectedBank] || 'Net Banking';
      paymentSummaryText = `🏦 ${bankName} Net Banking`;
    } else if (this.checkoutState.paymentMethod === 'cod') {
      paymentSummaryText = `💵 Cash on Delivery (Pay upon delivery)`;
    }

    const orderId = 'KALA-' + Math.floor(100000 + Math.random() * 900000);

    // Award loyalty points
    loggedInUser.kalaPoints = (loggedInUser.kalaPoints || 100) + Math.round(total / 50);
    loggedInUser.ordersCount = (loggedInUser.ordersCount || 0) + 1;
    loggedInUser.isFirstTime = false;
    localStorage.setItem('kalaconnect_user', JSON.stringify(loggedInUser));
    if (window.Auth && window.Auth.updateUserInDatabase) {
      window.Auth.updateUserInDatabase(loggedInUser);
    }
    if (window.Auth.renderNavAuth) window.Auth.renderNavAuth();

    // Mark customer as completed order
    localStorage.setItem('kalaconnectai_ordered_before', 'true');
    this.isFirstTimeUser = false;

    // Snapshot items before clearing (for receipt display)
    window._lastOrderItems = JSON.parse(JSON.stringify(this.items));

    // Clear cart
    const purchasedItemsCount = this.getItemCount();
    this.items = [];
    this.save();

    // ── Build per-item delivery info ──────────────────────────────────────────
    // Use the snapshot saved just before cart was cleared
    const orderItemsSnapshot = window._lastOrderItems || [];

    const itemReceiptRows = orderItemsSnapshot.map(item => {
      const del = this.getDeliveryDate(item);
      return `
        <div class="order-receipt-item">
          <img src="${item.image}" alt="${item.name}" />
          <div class="order-receipt-item-info">
            <strong>${item.name}</strong>
            <span>${item.quantity} × ₹${item.price.toLocaleString('en-IN')}</span>
          </div>
          <div class="delivery-date-badge order-receipt-date">🚚 ${del.label}</div>
        </div>
      `;
    }).join('');

    // ── Tracking timeline dates ────────────────────────────────────────────────
    const now = new Date();
    const addDays = (d, n) => { const r = new Date(d); r.setDate(r.getDate() + n); return r; };
    const fmtFull = (d) => d.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' });
    const fmtTime = (d) => d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

    const t0 = now;
    const t1 = addDays(now, 1);
    const t2 = addDays(now, 2);
    const t3 = addDays(now, 4);
    const t4 = addDays(now, 5);
    // Overall estimated delivery = max delivery date across items
    const maxDaysAll = orderItemsSnapshot.length > 0
      ? Math.max(...orderItemsSnapshot.map(it => this.getDeliveryDate(it).maxDays))
      : 6;
    const tDelivered = addDays(now, maxDaysAll);

    // ── Open Confirmation Receipt Modal ────────────────────────────────────────
    const modalContent = `
      <div class="order-success-content">
        <div class="success-icon-wrap">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
        </div>
        <h3 style="font-family: var(--font-serif); color: var(--secondary);">Order Confirmed! 🎉</h3>
        <p style="margin-bottom: 18px;">
          Order ID: <strong>#${orderId}</strong>. We've notified our rural artisan collective to carefully pack and ship your craft items.
        </p>

        <!-- Delivery Address Details Box -->
        <div style="background: #FDFBF8; border: 1.5px solid #E5DFD5; border-radius: 12px; padding: 14px 18px; text-align: left; margin-bottom: 16px; font-size: 0.86rem;">
          <div style="font-weight: 800; color: var(--secondary); margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
            <span>📍 Delivery Address</span>
          </div>
          <div><strong>${address.fullName}</strong> (${address.phone})</div>
          <div style="color: var(--text-muted);">${address.street}${address.landmark ? ', ' + address.landmark : ''}</div>
          <div style="color: var(--text-muted);">${address.city}, ${address.state} – <strong>${address.pinCode}</strong></div>
          <div style="margin-top: 8px; font-size: 0.82rem; color: var(--text-main); font-weight: 700;">
            Payment: <span style="color: var(--primary);">${paymentSummaryText}</span>
          </div>
        </div>

        ${wasFirstTime ? `
          <div style="background: #ECFDF5; border: 1px solid #10B981; border-radius: 12px; padding: 14px 18px; margin-bottom: 16px; text-align: left;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <span style="font-weight: 700; color: #065F46; font-size: 0.9rem;">🎉 First-Time 40% Discount Applied</span>
              <span style="background: #059669; color: white; padding: 2px 8px; border-radius: 999px; font-size: 0.72rem; font-weight: 800;">SAVED ₹${discount.toLocaleString('en-IN')}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #047857;">
              <span>Original: <s>₹${subtotal.toLocaleString('en-IN')}</s></span>
              <span><strong>Paid: ₹${total.toLocaleString('en-IN')}</strong></span>
            </div>
          </div>
        ` : ''}

        <!-- Order Tracking Timeline -->
        <div class="order-tracking-section">
          <div class="tracking-section-title">📦 Live Order Tracking</div>
          <div class="tracking-timeline">
            <div class="tracking-step done">
              <div class="tracking-dot"></div>
              <div class="tracking-content">
                <div class="tracking-label">✅ Order Placed</div>
                <div class="tracking-date">${fmtFull(t0)}, ${fmtTime(t0)}</div>
              </div>
            </div>
            <div class="tracking-step done">
              <div class="tracking-dot"></div>
              <div class="tracking-content">
                <div class="tracking-label">🧵 Artisan Packing</div>
                <div class="tracking-date">Expected by ${fmtFull(t1)}</div>
              </div>
            </div>
            <div class="tracking-step active">
              <div class="tracking-dot"></div>
              <div class="tracking-content">
                <div class="tracking-label">🚚 In Transit</div>
                <div class="tracking-date">Est. ${fmtFull(t2)} – ${fmtFull(t3)}</div>
              </div>
            </div>
            <div class="tracking-step">
              <div class="tracking-dot"></div>
              <div class="tracking-content">
                <div class="tracking-label">🏠 Out for Delivery</div>
                <div class="tracking-date">Est. ${fmtFull(t4)}</div>
              </div>
            </div>
            <div class="tracking-step">
              <div class="tracking-dot"></div>
              <div class="tracking-content">
                <div class="tracking-label">🎁 Delivered</div>
                <div class="tracking-date">Est. by ${fmtFull(tDelivered)}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Per-item delivery dates -->
        ${orderItemsSnapshot.length > 0 ? `
          <div class="order-items-receipt">
            <div class="tracking-section-title" style="margin-bottom: 10px;">🛍️ Item-wise Delivery Estimates</div>
            ${itemReceiptRows}
          </div>
        ` : ''}

        <div class="order-impact-card">
          <h5>🌿 Direct Social Impact Verified</h5>
          <p><strong>₹${artisanDirect.toLocaleString('en-IN')}</strong> will be disbursed directly to rural artisan bank accounts.</p>
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
    window.App.showToast(`Order #${orderId} placed! Estimated delivery by ${fmtFull(tDelivered)}.`, 'success');
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
