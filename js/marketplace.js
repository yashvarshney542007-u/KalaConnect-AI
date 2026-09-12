/**
 * KalaConnect AI - Customer Marketplace Module
 * Catalog rendering, multi-facet filtering, search, and artisan story modal
 */

const Marketplace = {
  products: [],
  filteredProducts: [],
  currentCategory: 'all',
  currentRegion: 'all',
  currentRoom: 'all',
  searchQuery: '',

  init() {
    this.products = window.ARTISAN_PRODUCTS || [];
    this.filteredProducts = [...this.products];
    this.renderCatalog();
    this.bindEvents();
  },

  bindEvents() {
    // Search input
    const searchInput = document.getElementById('marketplaceSearchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value.toLowerCase().trim();
        this.applyFilters();
      });
    }

    // Category chips
    const chipsContainer = document.getElementById('categoryChipsContainer');
    if (chipsContainer) {
      chipsContainer.addEventListener('click', (e) => {
        const chip = e.target.closest('.chip-btn');
        if (!chip) return;
        
        document.querySelectorAll('.chip-btn').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        this.currentCategory = chip.dataset.category || 'all';
        this.applyFilters();
      });
    }

    // Region dropdown
    const regionSelect = document.getElementById('regionFilterSelect');
    if (regionSelect) {
      regionSelect.addEventListener('change', (e) => {
        this.currentRegion = e.target.value;

        // If a specific region is chosen, check if current category has crafts in that region.
        // If not, auto-switch to 'all' so the user immediately sees the region's crafts!
        if (this.currentRegion !== 'all' && this.currentCategory !== 'all') {
          const hasCatInRegion = this.products.some(item => 
            item.category === this.currentCategory &&
            ((item.state && item.state.toLowerCase() === this.currentRegion.toLowerCase()) ||
             (item.region && item.region.toLowerCase().includes(this.currentRegion.toLowerCase())))
          );
          if (!hasCatInRegion) {
            this.currentCategory = 'all';
            document.querySelectorAll('.chip-btn').forEach(c => {
              c.classList.toggle('active', c.dataset.category === 'all');
            });
          }
        }
        this.applyFilters();
      });
    }

    // Room dropdown
    const roomSelect = document.getElementById('roomFilterSelect');
    if (roomSelect) {
      roomSelect.addEventListener('change', (e) => {
        this.currentRoom = e.target.value;
        this.applyFilters();
      });
    }
  },

  applyFilters() {
    this.filteredProducts = this.products.filter(item => {
      // Category match
      const matchCategory = this.currentCategory === 'all' || item.category === this.currentCategory;

      // Region / State / UT match
      const matchRegion = this.currentRegion === 'all' || 
        (item.state && item.state.toLowerCase() === this.currentRegion.toLowerCase()) ||
        item.region.toLowerCase().includes(this.currentRegion.toLowerCase());

      // Room suitability match
      const matchRoom = this.currentRoom === 'all' || (item.spaceCompatibility && item.spaceCompatibility.rooms.includes(this.currentRoom));

      // Search match
      const matchSearch = !this.searchQuery || 
        item.name.toLowerCase().includes(this.searchQuery) ||
        item.craftForm.toLowerCase().includes(this.searchQuery) ||
        (item.state && item.state.toLowerCase().includes(this.searchQuery)) ||
        item.artisan.name.toLowerCase().includes(this.searchQuery) ||
        item.materials.toLowerCase().includes(this.searchQuery) ||
        item.region.toLowerCase().includes(this.searchQuery);

      return matchCategory && matchRegion && matchRoom && matchSearch;
    });

    this.renderCatalog();
  },

  renderCatalog() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    if (this.filteredProducts.length === 0) {
      const isStateFilter = this.currentRegion !== 'all';
      const regionCrafts = isStateFilter ? this.products.filter(item => 
        (item.state && item.state.toLowerCase() === this.currentRegion.toLowerCase()) ||
        (item.region && item.region.toLowerCase().includes(this.currentRegion.toLowerCase()))
      ) : [];

      // If region has crafts but not in this specific category/filter
      if (isStateFilter && regionCrafts.length > 0) {
        const availableCategories = [...new Set(regionCrafts.map(p => p.category))].join(', ');
        grid.innerHTML = `
          <div class="empty-results">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">🎨</div>
            <h3>No "${this.currentCategory}" Currently in ${this.currentRegion}</h3>
            <p style="max-width: 540px; margin: 0 auto 20px;">
              We have <strong>${regionCrafts.length} GI-certified artisan crafts</strong> from <strong>${this.currentRegion}</strong> in: <em>${availableCategories}</em>.
            </p>
            <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
              <button class="chip-btn active" onclick="Marketplace.showAllInCurrentRegion()">
                View All ${regionCrafts.length} Crafts in ${this.currentRegion}
              </button>
              <button class="chip-btn" onclick="Marketplace.resetFilters()">
                Show All Indian Crafts
              </button>
            </div>
          </div>
        `;
        return;
      }

      grid.innerHTML = `
        <div class="empty-results">
          <div style="font-size: 2.5rem; margin-bottom: 10px;">🇮🇳</div>
          <h3>${isStateFilter ? `Artisan Clusters in ${this.currentRegion} Onboarding` : 'No Artisan Crafts Found'}</h3>
          <p style="max-width: 540px; margin: 0 auto 20px;">
            ${isStateFilter 
              ? `We are currently validating and digitizing GI-tagged marginalized artisan cooperatives in <strong>${this.currentRegion}</strong> through Member 2 & 3's pipeline. Check back shortly or explore neighboring craft clusters!`
              : 'Try clearing some filters or searching for terms like "Madhubani", "Pottery", or "Brass".'}
          </p>
          <div style="display: flex; gap: 10px; justify-content: center;">
            <button class="chip-btn active" onclick="Marketplace.resetFilters()">
              Show All Indian Crafts
            </button>
            ${isStateFilter ? `
              <button class="chip-btn" onclick="window.App.showToast('Subscribed for artisan launches in ${this.currentRegion}!', 'success')">
                🔔 Notify Me for ${this.currentRegion}
              </button>
            ` : ''}
          </div>
        </div>
      `;
      return;
    }

    grid.innerHTML = this.filteredProducts.map(p => `
      <article class="product-card" data-id="${p.id}">
        <div class="card-image-wrap" onclick="Marketplace.showProductModal('${p.id}')">
          <img src="${p.image}" alt="${p.name}" loading="lazy" onerror="this.onerror=null; this.src='https://wbgntprnfvtvbvkfbyjp.supabase.co/storage/v1/object/public/product-images/handicraft/pexels-nata-37483660%20(1).jpg';" />
          <div class="card-badge-container">
            ${p.giCertified ? `<span class="badge badge-gi">✓ GI Tag Certified</span>` : ''}
            <span class="badge badge-fairprice">Fair Margin: ${p.artisanSharePercent}%</span>
          </div>
          <div class="card-action-overlay">
            <button class="icon-action-btn" title="Quick View & Artisan Story" onclick="event.stopPropagation(); Marketplace.showProductModal('${p.id}')">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
            </button>
          </div>
        </div>

        <div class="card-body">
          <span class="card-craft-type">${p.craftForm} · ${p.state || p.region} ${p.isUT ? '(UT)' : ''}</span>
          <h3 class="card-title" onclick="Marketplace.showProductModal('${p.id}')">${p.name}</h3>
          
          <div class="card-artisan-line">
            <img src="${p.artisan.avatar}" alt="${p.artisan.name}" />
            <span>Crafted by <strong>${p.artisan.name}</strong></span>
          </div>

          <div class="card-price-row">
            <div class="price-box">
              <span class="price-current">₹${p.price.toLocaleString('en-IN')}</span>
              <span class="price-market-cut">₹${p.marketEstimate.toLocaleString('en-IN')} retail</span>
            </div>
            <span class="fair-share-pill" title="Fair Pricing Model (Member 4 Integration)">Direct to Artisan: ${p.artisanSharePercent}%</span>
          </div>

          <div class="card-cta-row">
            <button class="btn-card-cart" onclick="Cart.addItem('${p.id}')">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>
              Add to Cart
            </button>
            <button class="btn-card-space" onclick="Marketplace.openInSpaceStudio('${p.id}')">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
              Style in Space
            </button>
          </div>
        </div>
      </article>
    `).join('');
  },

  showAllInCurrentRegion() {
    this.currentCategory = 'all';
    this.currentRoom = 'all';
    this.searchQuery = '';

    const searchInput = document.getElementById('marketplaceSearchInput');
    if (searchInput) searchInput.value = '';

    const roomSelect = document.getElementById('roomFilterSelect');
    if (roomSelect) roomSelect.value = 'all';

    document.querySelectorAll('.chip-btn').forEach(c => {
      c.classList.toggle('active', c.dataset.category === 'all');
    });

    this.applyFilters();
  },

  resetFilters() {
    this.currentCategory = 'all';
    this.currentRegion = 'all';
    this.currentRoom = 'all';
    this.searchQuery = '';

    const searchInput = document.getElementById('marketplaceSearchInput');
    if (searchInput) searchInput.value = '';

    const regionSelect = document.getElementById('regionFilterSelect');
    if (regionSelect) regionSelect.value = 'all';

    const roomSelect = document.getElementById('roomFilterSelect');
    if (roomSelect) roomSelect.value = 'all';

    document.querySelectorAll('.chip-btn').forEach(c => c.classList.remove('active'));
    const defaultChip = document.querySelector('.chip-btn[data-category="all"]');
    if (defaultChip) defaultChip.classList.add('active');

    this.applyFilters();
  },

  showProductModal(productId) {
    const p = this.products.find(item => item.id === productId);
    if (!p) return;

    // ── Compute tentative delivery date (mirrors Cart.getDeliveryDate logic) ──
    const remoteStates = [
      'Arunachal Pradesh', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland',
      'Sikkim', 'Tripura', 'Assam', 'Jammu and Kashmir', 'Ladakh',
      'Andaman and Nicobar', 'Lakshadweep', 'Himachal Pradesh', 'Uttarakhand'
    ];
    const isRemote   = remoteStates.includes(p.state);
    const isDelicate = ['Handloom', 'Weaving', 'Embroidery', 'Zari'].some(
      k => (p.craftForm || '').includes(k)
    );
    const minDays = isRemote ? 5 : 3;
    const maxDays = (isRemote ? 8 : 6) + (isDelicate ? 1 : 0);
    const today   = new Date();
    const minDate = new Date(today); minDate.setDate(today.getDate() + minDays);
    const maxDate = new Date(today); maxDate.setDate(today.getDate() + maxDays);
    const fmtD    = (d) => d.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' });
    const deliveryLabel = `${fmtD(minDate)} – ${fmtD(maxDate)}`;
    const deliveryNote  = isRemote
      ? 'Remote region — allow extra transit time.'
      : isDelicate
        ? 'Delicate craft — carefully packed by artisan.'
        : 'Standard artisan-direct shipping.';

    const modalContent = `
      <div class="pdp-grid">
        <div class="pdp-image-container">
          <img src="${p.image}" alt="${p.name}" onerror="this.onerror=null; this.src='https://wbgntprnfvtvbvkfbyjp.supabase.co/storage/v1/object/public/product-images/handicraft/pexels-nata-37483660%20(1).jpg';" />
        </div>

        <div class="pdp-details">
          <span class="pdp-craft-tag">${p.craftForm} · ${p.region}</span>
          <h2 class="pdp-title">${p.name}</h2>
          
          <div class="card-price-row" style="border: none; padding: 0; margin-bottom: 16px;">
            <div class="price-box">
              <span class="price-current" style="font-size: 1.8rem;">₹${p.price.toLocaleString('en-IN')}</span>
              <span class="price-market-cut">Commercial Retail Est: ₹${p.marketEstimate.toLocaleString('en-IN')}</span>
            </div>
            ${p.giCertified ? `<span class="badge badge-gi" style="font-size: 0.82rem;">✓ GI Tag Authenticity Certified</span>` : ''}
          </div>

          <!-- Artisan Heritage Profile -->
          <div class="pdp-artisan-card">
            <img src="${p.artisan.avatar}" alt="${p.artisan.name}" />
            <div class="pdp-artisan-meta">
              <h5>${p.artisan.name} (${p.artisan.experience})</h5>
              <p><em>"${p.artisan.story}"</em></p>
            </div>
          </div>

          <!-- Fair Trade Transparency (Member 4 Integration) -->
          <div class="fair-pricing-box">
            <h6>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
              Fair Price Transparency Guarantee
            </h6>
            <p>Direct Artisan Earning: <strong>${p.artisanSharePercent}% (₹${Math.round(p.price * p.artisanSharePercent / 100).toLocaleString('en-IN')})</strong>. Eliminates middlemen commissions, providing 3.4x higher net income to the maker.</p>
          </div>

          <!-- Tentative Delivery Date -->
          <div class="pdp-delivery-box">
            <div class="pdp-delivery-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <rect x="1" y="3" width="15" height="13" rx="1"></rect>
                <path d="M16 8h4l3 5v3h-7V8z"></path>
                <circle cx="5.5" cy="18.5" r="2.5"></circle>
                <circle cx="18.5" cy="18.5" r="2.5"></circle>
              </svg>
              Tentative Delivery Date
            </div>
            <div class="pdp-delivery-date">${deliveryLabel}</div>
            <div class="pdp-delivery-note">${deliveryNote}</div>
            <div class="pdp-delivery-meta">
              <span>🚚 FREE artisan-direct delivery</span>
              <span>📦 ${minDays}–${maxDays} business days</span>
            </div>
          </div>

          <p style="color: var(--text-muted); font-size: 0.92rem; line-height: 1.6; margin-bottom: 14px;">
            ${p.description}
          </p>

          <div class="pdp-meta-list">
            <div class="pdp-meta-item">
              <strong>Dimensions</strong>
              <span>${p.dimensions}</span>
            </div>
            <div class="pdp-meta-item">
              <strong>Materials</strong>
              <span>${p.materials}</span>
            </div>
            <div class="pdp-meta-item">
              <strong>Recommended Space</strong>
              <span>${p.spaceCompatibility.placementSuggestion}</span>
            </div>
            <div class="pdp-meta-item">
              <strong>Vibe &amp; Lighting</strong>
              <span>${p.spaceCompatibility.lightingVibe}</span>
            </div>
          </div>

          <div class="pdp-actions-row">
            <button class="btn-primary-large" onclick="Cart.addItem('${p.id}'); window.App.closeModal();">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>
              Add to Cart · ₹${p.price.toLocaleString('en-IN')}
            </button>
            <button class="btn-secondary-large" onclick="Marketplace.openInSpaceStudio('${p.id}'); window.App.closeModal();">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
              Style in Space
            </button>
          </div>
        </div>
      </div>
    `;

    window.App.openModal(modalContent);
  },

  openInSpaceStudio(productId) {
    window.App.switchView('space');
    if (window.SpaceAI) {
      window.SpaceAI.selectCraftForCanvas(productId);
    }
  }
};

window.Marketplace = Marketplace;
