const Marketplace = {
  products: [],
  filteredProducts: [],
  currentCategory: 'all',
  currentRegion: 'all',
  currentRoom: 'all',
  searchQuery: '',

  
  async init() {
    try {
      const response = await fetch('/marketplace/products/');

      if (!response.ok) {
        throw new Error(`Marketplace API returned ${response.status}`);
      }

      const data = await response.json();

      this.products = (data.products || []).map(product =>
        this.normalizeProduct(product)
      );

      
      window.ARTISAN_PRODUCTS = this.products;

      this.filteredProducts = [...this.products];

      this.renderCatalog();
      this.bindEvents();

      console.log(
        '✅ Marketplace loaded from Django API:',
        this.products
      );
    } catch (error) {
      console.error(
        '❌ Failed to load marketplace products:',
        error
      );

      this.products = [];
      this.filteredProducts = [];

      
      window.ARTISAN_PRODUCTS = [];

      this.renderCatalog();

      if (window.App && window.App.showToast) {
        window.App.showToast(
          'Could not load products from the server.',
          'error'
        );
      }
    }
  },

  
  normalizeProduct(product) {
    const price = Number(product.price) || 0;
    const image = product.image_url || '';

    return {
      // Real database/API fields
      id: product.id,
      name: product.name || 'Unnamed Product',
      description: product.description || '',
      price: price,
      image: image,

      // Existing marketplace UI fields
      category: 'Handicraft',
      craftForm: 'Handicraft',
      region: 'India',
      state: '',
      isUT: false,

      // Artisan information
      artisan: {
        name: 'KalaConnect Artisan',
        avatar: image,
        experience: '',
        story: 'Handcrafted through KalaConnect.'
      },

      // Pricing presentation
      artisanSharePercent: 100,
      marketEstimate: price,

      // Certification
      giCertified: false,

      // Product metadata not currently stored
      // in the final products table
      materials: '',
      dimensions: '',

      // Space Studio compatibility defaults
      spaceCompatibility: {
        rooms: [],
        placementSuggestion: 'Suitable for home decoration',
        lightingVibe: ''
      }
    };
  },

  bindEvents() {
    // Search input
    const searchInput = document.getElementById(
      'marketplaceSearchInput'
    );

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value
          .toLowerCase()
          .trim();

        this.applyFilters();
      });
    }

    // Category chips
    const chipsContainer = document.getElementById(
      'categoryChipsContainer'
    );

    if (chipsContainer) {
      chipsContainer.addEventListener('click', (e) => {
        const chip = e.target.closest('.chip-btn');

        if (!chip) return;

        document
          .querySelectorAll('.chip-btn')
          .forEach(c => c.classList.remove('active'));

        chip.classList.add('active');

        this.currentCategory =
          chip.dataset.category || 'all';

        this.applyFilters();
      });
    }

    // Region dropdown
    const regionSelect = document.getElementById(
      'regionFilterSelect'
    );

    if (regionSelect) {
      regionSelect.addEventListener('change', (e) => {
        this.currentRegion = e.target.value;

        /*
         * If a specific region is chosen, check whether
         * the current category contains products in that region.
         */
        if (
          this.currentRegion !== 'all' &&
          this.currentCategory !== 'all'
        ) {
          const hasCatInRegion = this.products.some(item =>
            item.category === this.currentCategory &&
            (
              (
                item.state &&
                item.state.toLowerCase() ===
                  this.currentRegion.toLowerCase()
              ) ||
              (
                item.region &&
                item.region
                  .toLowerCase()
                  .includes(
                    this.currentRegion.toLowerCase()
                  )
              )
            )
          );

          if (!hasCatInRegion) {
            this.currentCategory = 'all';

            document
              .querySelectorAll('.chip-btn')
              .forEach(c => {
                c.classList.toggle(
                  'active',
                  c.dataset.category === 'all'
                );
              });
          }
        }

        this.applyFilters();
      });
    }

    // Room dropdown
    const roomSelect = document.getElementById(
      'roomFilterSelect'
    );

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
      const matchCategory =
        this.currentCategory === 'all' ||
        item.category === this.currentCategory;

      // Region / State / UT match
      const matchRegion =
        this.currentRegion === 'all' ||
        (
          item.state &&
          item.state.toLowerCase() ===
            this.currentRegion.toLowerCase()
        ) ||
        (
          item.region &&
          item.region
            .toLowerCase()
            .includes(this.currentRegion.toLowerCase())
        );

      // Room suitability match
      const matchRoom =
        this.currentRoom === 'all' ||
        (
          item.spaceCompatibility &&
          Array.isArray(item.spaceCompatibility.rooms) &&
          item.spaceCompatibility.rooms.includes(
            this.currentRoom
          )
        );

      // Search match
      const searchFields = [
        item.name,
        item.craftForm,
        item.state,
        item.artisan && item.artisan.name,
        item.materials,
        item.region
      ];

      const matchSearch =
        !this.searchQuery ||
        searchFields.some(value =>
          String(value || '')
            .toLowerCase()
            .includes(this.searchQuery)
        );

      return (
        matchCategory &&
        matchRegion &&
        matchRoom &&
        matchSearch
      );
    });

    this.renderCatalog();
  },

  renderCatalog() {
    const grid = document.getElementById('productsGrid');

    if (!grid) return;

    if (this.filteredProducts.length === 0) {
      const isStateFilter =
        this.currentRegion !== 'all';

      const regionCrafts = isStateFilter
        ? this.products.filter(item =>
            (
              item.state &&
              item.state.toLowerCase() ===
                this.currentRegion.toLowerCase()
            ) ||
            (
              item.region &&
              item.region
                .toLowerCase()
                .includes(
                  this.currentRegion.toLowerCase()
                )
            )
          )
        : [];

      // If region has crafts but not in this specific category/filter
      if (
        isStateFilter &&
        regionCrafts.length > 0
      ) {
        const availableCategories = [
          ...new Set(
            regionCrafts.map(p => p.category)
          )
        ].join(', ');

        grid.innerHTML = `
          <div class="empty-results">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">
              🎨
            </div>

            <h3>
              No "${this.currentCategory}"
              Currently in ${this.currentRegion}
            </h3>

            <p style="max-width: 540px; margin: 0 auto 20px;">
              We have
              <strong>
                ${regionCrafts.length}
                GI-certified artisan crafts
              </strong>
              from
              <strong>${this.currentRegion}</strong>
              in:
              <em>${availableCategories}</em>.
            </p>

            <div
              style="
                display: flex;
                gap: 10px;
                justify-content: center;
                flex-wrap: wrap;
              "
            >
              <button
                class="chip-btn active"
                onclick="Marketplace.showAllInCurrentRegion()"
              >
                View All ${regionCrafts.length}
                Crafts in ${this.currentRegion}
              </button>

              <button
                class="chip-btn"
                onclick="Marketplace.resetFilters()"
              >
                Show All Indian Crafts
              </button>
            </div>
          </div>
        `;

        return;
      }

      grid.innerHTML = `
        <div class="empty-results">
          <div style="font-size: 2.5rem; margin-bottom: 10px;">
            🇮🇳
          </div>

          <h3>
            ${
              isStateFilter
                ? `Artisan Clusters in ${this.currentRegion} Onboarding`
                : 'No Artisan Crafts Found'
            }
          </h3>

          <p style="max-width: 540px; margin: 0 auto 20px;">
            ${
              isStateFilter
                ? `
                  We are currently validating and digitizing
                  GI-tagged marginalized artisan cooperatives in
                  <strong>${this.currentRegion}</strong>
                  through Member 2 & 3's pipeline.
                  Check back shortly or explore neighboring
                  craft clusters!
                `
                : `
                  Try clearing some filters or searching for
                  terms like "Madhubani", "Pottery", or "Brass".
                `
            }
          </p>

          <div
            style="
              display: flex;
              gap: 10px;
              justify-content: center;
            "
          >
            <button
              class="chip-btn active"
              onclick="Marketplace.resetFilters()"
            >
              Show All Indian Crafts
            </button>

            ${
              isStateFilter
                ? `
                  <button
                    class="chip-btn"
                    onclick="
                      window.App.showToast(
                        'Subscribed for artisan launches in ${this.currentRegion}!',
                        'success'
                      )
                    "
                  >
                    🔔 Notify Me for ${this.currentRegion}
                  </button>
                `
                : ''
            }
          </div>
        </div>
      `;

      return;
    }

    grid.innerHTML = this.filteredProducts
      .map(p => `
        <article
          class="product-card"
          data-id="${p.id}"
        >
          <div
            class="card-image-wrap"
            onclick="
              Marketplace.showProductModal('${p.id}')
            "
          >
            <img
              src="${p.image}"
              alt="${p.name}"
              loading="lazy"
            />

            <div class="card-badge-container">
              ${
                p.giCertified
                  ? `
                    <span class="badge badge-gi">
                      ✓ GI Tag Certified
                    </span>
                  `
                  : ''
              }

              <span class="badge badge-fairprice">
                Fair Margin: ${p.artisanSharePercent}%
              </span>
            </div>

            <div class="card-action-overlay">
              <button
                class="icon-action-btn"
                title="Quick View & Artisan Story"
                onclick="
                  event.stopPropagation();
                  Marketplace.showProductModal('${p.id}')
                "
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    d="
                      M1 12s4-8 11-8
                      11 8 11 8-4 8-11 8
                      -11-8-11-8z
                    "
                  ></path>

                  <circle
                    cx="12"
                    cy="12"
                    r="3"
                  ></circle>
                </svg>
              </button>
            </div>
          </div>

          <div class="card-body">

            <span class="card-craft-type">
              ${p.craftForm}
              ·
              ${p.state || p.region}
              ${p.isUT ? '(UT)' : ''}
            </span>

            <h3
              class="card-title"
              onclick="
                Marketplace.showProductModal('${p.id}')
              "
            >
              ${p.name}
            </h3>

            <div class="card-artisan-line">
              <img
                src="${p.artisan.avatar}"
                alt="${p.artisan.name}"
              />

              <span>
                Crafted by
                <strong>${p.artisan.name}</strong>
              </span>
            </div>

            <div class="card-price-row">
              <div class="price-box">

                <span class="price-current">
                  ₹${p.price.toLocaleString('en-IN')}
                </span>

                <span class="price-market-cut">
                  ₹${p.marketEstimate.toLocaleString('en-IN')}
                  retail
                </span>

              </div>

              <span
                class="fair-share-pill"
                title="Fair Pricing Model (Member 4 Integration)"
              >
                Direct to Artisan:
                ${p.artisanSharePercent}%
              </span>
            </div>

            <div class="card-cta-row">

              <button
                class="btn-card-cart"
                onclick="Cart.addItem('${p.id}')"
              >
                <svg
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle
                    cx="9"
                    cy="21"
                    r="1"
                  ></circle>

                  <circle
                    cx="20"
                    cy="21"
                    r="1"
                  ></circle>

                  <path
                    d="
                      M1 1h4l2.68 13.39
                      a2 2 0 0 0 2 1.61
                      h9.72a2 2 0 0 0 2-1.61
                      L23 6H6
                    "
                  ></path>
                </svg>

                Add to Cart
              </button>

              <button
                class="btn-card-space"
                onclick="
                  Marketplace.openInSpaceStudio('${p.id}')
                "
              >
                <svg
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    d="
                      M3 9l9-7 9 7v11
                      a2 2 0 0 1-2 2H5
                      a2 2 0 0 1-2-2z
                    "
                  ></path>

                  <polyline
                    points="9 22 9 12 15 12 15 22"
                  ></polyline>
                </svg>

                Style in Space
              </button>

            </div>
          </div>
        </article>
      `)
      .join('');
  },

  showAllInCurrentRegion() {
    this.currentCategory = 'all';
    this.currentRoom = 'all';
    this.searchQuery = '';

    const searchInput = document.getElementById(
      'marketplaceSearchInput'
    );

    if (searchInput) {
      searchInput.value = '';
    }

    const roomSelect = document.getElementById(
      'roomFilterSelect'
    );

    if (roomSelect) {
      roomSelect.value = 'all';
    }

    document
      .querySelectorAll('.chip-btn')
      .forEach(c => {
        c.classList.toggle(
          'active',
          c.dataset.category === 'all'
        );
      });

    this.applyFilters();
  },

  resetFilters() {
    this.currentCategory = 'all';
    this.currentRegion = 'all';
    this.currentRoom = 'all';
    this.searchQuery = '';

    const searchInput = document.getElementById(
      'marketplaceSearchInput'
    );

    if (searchInput) {
      searchInput.value = '';
    }

    const regionSelect = document.getElementById(
      'regionFilterSelect'
    );

    if (regionSelect) {
      regionSelect.value = 'all';
    }

    const roomSelect = document.getElementById(
      'roomFilterSelect'
    );

    if (roomSelect) {
      roomSelect.value = 'all';
    }

    document
      .querySelectorAll('.chip-btn')
      .forEach(c => c.classList.remove('active'));

    const defaultChip = document.querySelector(
      '.chip-btn[data-category="all"]'
    );

    if (defaultChip) {
      defaultChip.classList.add('active');
    }

    this.applyFilters();
  },

  showProductModal(productId) {
    const p = this.products.find(
      item => item.id === productId
    );

    if (!p) return;

    const modalContent = `
      <div class="pdp-grid">

        <div class="pdp-image-container">
          <img
            src="${p.image}"
            alt="${p.name}"
          />
        </div>

        <div class="pdp-details">

          <span class="pdp-craft-tag">
            ${p.craftForm} · ${p.region}
          </span>

          <h2 class="pdp-title">
            ${p.name}
          </h2>

          <div
            class="card-price-row"
            style="
              border: none;
              padding: 0;
              margin-bottom: 16px;
            "
          >
            <div class="price-box">

              <span
                class="price-current"
                style="font-size: 1.8rem;"
              >
                ₹${p.price.toLocaleString('en-IN')}
              </span>

              <span class="price-market-cut">
                Commercial Retail Est:
                ₹${p.marketEstimate.toLocaleString('en-IN')}
              </span>

            </div>

            ${
              p.giCertified
                ? `
                  <span
                    class="badge badge-gi"
                    style="font-size: 0.82rem;"
                  >
                    ✓ GI Tag Authenticity Certified
                  </span>
                `
                : ''
            }
          </div>

          <!-- Artisan Heritage Profile -->
          <div class="pdp-artisan-card">

            <img
              src="${p.artisan.avatar}"
              alt="${p.artisan.name}"
            />

            <div class="pdp-artisan-meta">

              <h5>
                ${p.artisan.name}
                ${
                  p.artisan.experience
                    ? `(${p.artisan.experience})`
                    : ''
                }
              </h5>

              <p>
                <em>
                  "${p.artisan.story}"
                </em>
              </p>

            </div>
          </div>

          <!-- Fair Trade Transparency -->
          <div class="fair-pricing-box">

            <h6>
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path
                  d="
                    M12 2v20
                    M17 5H9.5
                    a3.5 3.5 0 0 0 0 7
                    h5
                    a3.5 3.5 0 0 1 0 7
                    H6
                  "
                ></path>
              </svg>

              Fair Price Transparency Guarantee
            </h6>

            <p>
              Direct Artisan Earning:
              <strong>
                ${p.artisanSharePercent}%
                (
                  ₹${Math.round(
                    p.price *
                    p.artisanSharePercent /
                    100
                  ).toLocaleString('en-IN')}
                )
              </strong>.

              Eliminates middlemen commissions,
              providing 3.4x higher net income
              to the maker.
            </p>

          </div>

          <p
            style="
              color: var(--text-muted);
              font-size: 0.92rem;
              line-height: 1.6;
              margin-bottom: 14px;
            "
          >
            ${p.description}
          </p>

          <div class="pdp-meta-list">

            <div class="pdp-meta-item">
              <strong>Dimensions</strong>
              <span>${p.dimensions || 'Not specified'}</span>
            </div>

            <div class="pdp-meta-item">
              <strong>Materials</strong>
              <span>${p.materials || 'Not specified'}</span>
            </div>

            <div class="pdp-meta-item">
              <strong>Recommended Space</strong>
              <span>
                ${
                  p.spaceCompatibility
                    ? p.spaceCompatibility
                        .placementSuggestion
                    : 'Suitable for home decoration'
                }
              </span>
            </div>

            <div class="pdp-meta-item">
              <strong>Vibe & Lighting</strong>
              <span>
                ${
                  p.spaceCompatibility
                    ? (
                        p.spaceCompatibility.lightingVibe ||
                        'Not specified'
                      )
                    : 'Not specified'
                }
              </span>
            </div>

          </div>

          <div class="pdp-actions-row">

            <button
              class="btn-primary-large"
              onclick="
                Cart.addItem('${p.id}');
                window.App.closeModal();
              "
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <circle
                  cx="9"
                  cy="21"
                  r="1"
                ></circle>

                <circle
                  cx="20"
                  cy="21"
                  r="1"
                ></circle>

                <path
                  d="
                    M1 1h4l2.68 13.39
                    a2 2 0 0 0 2 1.61
                    h9.72a2 2 0 0 0 2-1.61
                    L23 6H6
                  "
                ></path>
              </svg>

              Add to Cart ·
              ₹${p.price.toLocaleString('en-IN')}
            </button>

            <button
              class="btn-secondary-large"
              onclick="
                Marketplace.openInSpaceStudio('${p.id}');
                window.App.closeModal();
              "
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  d="
                    M3 9l9-7 9 7v11
                    a2 2 0 0 1-2 2H5
                    a2 2 0 0 1-2-2z
                  "
                ></path>

                <polyline
                  points="9 22 9 12 15 12 15 22"
                ></polyline>
              </svg>

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