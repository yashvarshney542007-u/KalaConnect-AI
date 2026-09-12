/**
 * KalaConnect AI - Customer Marketplace Module
 * Products are loaded from Django -> Supabase
 */

const Marketplace = {
  products: [],
  filteredProducts: [],

  currentCategory: "all",
  currentRegion: "all",
  currentRoom: "all",
  searchQuery: "",


  // =========================================================
  // INITIALIZE MARKETPLACE
  // =========================================================

  async init() {
    console.log("Loading marketplace products...");

    try {
      const response = await fetch("/marketplace/products/");

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Failed to fetch marketplace products"
        );
      }

      /*
       * Supabase currently returns fields such as:
       *
       * id
       * artisan_id
       * name
       * description
       * price
       * image_url
       * created_at
       *
       * Existing marketplace UI expects some additional fields.
       * Safe defaults are added below so the old UI continues
       * working without changing the database schema.
       */

      this.products = (data.products || []).map((p) => {

        const price = Number(p.price || 0);

        return {
          ...p,

          // ---------------------------------------------------
          // Core database fields
          // ---------------------------------------------------

          id: p.id,

          artisan_id: p.artisan_id || "",

          name:
            p.name ||
            "Handmade Product",

          description:
            p.description ||
            "Traditional handmade product crafted by an Indian artisan.",

          price: price,

          image:
            p.image_url ||
            "/static/assets/images/logo.png",

          image_url:
            p.image_url ||
            "/static/assets/images/logo.png",

          created_at:
            p.created_at || null,


          // ---------------------------------------------------
          // Compatibility fields for existing marketplace UI
          // ---------------------------------------------------

          category:
            p.category ||
            "Handicraft",

          craft:
            p.craft ||
            "Handmade Craft",

          craftForm:
            p.craft ||
            p.category ||
            "Handmade Craft",

          material:
            p.material ||
            "Handcrafted Material",

          materials:
            p.material ||
            "Handcrafted Material",

          technique:
            p.technique ||
            "Traditional Craft Technique",

          state:
            p.state ||
            "",

          region:
            p.region ||
            p.state ||
            "India",

          isUT:
            p.isUT || false,

          dimensions:
            p.dimensions ||
            "Contact artisan for dimensions",


          // ---------------------------------------------------
          // Pricing compatibility
          // ---------------------------------------------------

          marketEstimate:
            Number(
              p.original_price ||
              p.marketEstimate ||
              price
            ),

          artisanSharePercent:
            Number(
              p.artisanSharePercent ||
              100
            ),


          // ---------------------------------------------------
          // GI compatibility
          // ---------------------------------------------------

          giCertified:
            Boolean(
              p.gi_tag ||
              p.giCertified
            ),


          // ---------------------------------------------------
          // Artisan information
          // ---------------------------------------------------

          artisan: {
            id:
              p.artisan_id || "",

            name:
              p.artisan_name ||
              "KalaConnect Artisan",

            avatar:
              p.artisan_avatar ||
              "/static/assets/images/logo.png",

            experience:
              p.artisan_experience ||
              "Independent Artisan",

            story:
              p.artisan_story ||
              "This product has been handcrafted by an artisan on KalaConnect."
          },


          // ---------------------------------------------------
          // Space Studio compatibility
          // ---------------------------------------------------

          spaceCompatibility: {
            rooms:
              Array.isArray(p.room_compatibility)
                ? p.room_compatibility
                : [],

            placementSuggestion:
              p.placement_suggestion ||
              "Suitable for thoughtfully styled spaces",

            lightingVibe:
              p.lighting_vibe ||
              "Natural or warm lighting"
          }
        };
      });


      /*
       * cart.js and space_ai.js already use
       * window.ARTISAN_PRODUCTS.
       *
       * Keeping this global means those modules continue
       * working while products now come from Supabase.
       */

      window.ARTISAN_PRODUCTS = this.products;

      this.filteredProducts = [...this.products];


      console.log(
        `Loaded ${this.products.length} products from Supabase`
      );


      this.renderCatalog();

    } catch (error) {

      console.error(
        "Marketplace database error:",
        error
      );

      this.products = [];
      this.filteredProducts = [];

      window.ARTISAN_PRODUCTS = [];

      this.renderCatalog();
    }


    // Bind filters/search AFTER products are initialized
    this.bindEvents();
  },


  // =========================================================
  // EVENT LISTENERS
  // =========================================================

  bindEvents() {

    // Search
    const searchInput =
      document.getElementById(
        "marketplaceSearchInput"
      );

    if (searchInput) {

      searchInput.addEventListener(
        "input",
        (e) => {

          this.searchQuery =
            e.target.value
              .toLowerCase()
              .trim();

          this.applyFilters();
        }
      );
    }


    // Category chips
    const chipsContainer =
      document.getElementById(
        "categoryChipsContainer"
      );

    if (chipsContainer) {

      chipsContainer.addEventListener(
        "click",
        (e) => {

          const chip =
            e.target.closest(
              ".chip-btn"
            );

          if (!chip) return;


          document
            .querySelectorAll(
              ".chip-btn"
            )
            .forEach((c) =>
              c.classList.remove(
                "active"
              )
            );


          chip.classList.add(
            "active"
          );


          this.currentCategory =
            chip.dataset.category ||
            "all";


          this.applyFilters();
        }
      );
    }


    // Region filter
    const regionSelect =
      document.getElementById(
        "regionFilterSelect"
      );

    if (regionSelect) {

      regionSelect.addEventListener(
        "change",
        (e) => {

          this.currentRegion =
            e.target.value;


          if (
            this.currentRegion !==
              "all" &&
            this.currentCategory !==
              "all"
          ) {

            const hasCatInRegion =
              this.products.some(
                (item) => {

                  const state =
                    item.state || "";

                  const region =
                    item.region || "";

                  return (
                    item.category ===
                      this.currentCategory &&

                    (
                      state
                        .toLowerCase() ===
                        this.currentRegion
                          .toLowerCase() ||

                      region
                        .toLowerCase()
                        .includes(
                          this.currentRegion
                            .toLowerCase()
                        )
                    )
                  );
                }
              );


            if (!hasCatInRegion) {

              this.currentCategory =
                "all";


              document
                .querySelectorAll(
                  ".chip-btn"
                )
                .forEach((c) => {

                  c.classList.toggle(
                    "active",
                    c.dataset.category ===
                      "all"
                  );
                });
            }
          }


          this.applyFilters();
        }
      );
    }


    // Room filter
    const roomSelect =
      document.getElementById(
        "roomFilterSelect"
      );

    if (roomSelect) {

      roomSelect.addEventListener(
        "change",
        (e) => {

          this.currentRoom =
            e.target.value;

          this.applyFilters();
        }
      );
    }
  },


  // =========================================================
  // FILTER PRODUCTS
  // =========================================================

  applyFilters() {

    this.filteredProducts =
      this.products.filter(
        (item) => {

          const category =
            item.category || "";

          const state =
            item.state || "";

          const region =
            item.region || "";

          const name =
            item.name || "";

          const craft =
            item.craftForm || "";

          const materials =
            item.materials || "";

          const artisanName =
            item.artisan?.name || "";


          // Category
          const matchCategory =
            this.currentCategory ===
              "all" ||
            category ===
              this.currentCategory;


          // Region
          const matchRegion =
            this.currentRegion ===
              "all" ||

            state
              .toLowerCase() ===
              this.currentRegion
                .toLowerCase() ||

            region
              .toLowerCase()
              .includes(
                this.currentRegion
                  .toLowerCase()
              );


          // Room
          const rooms =
            item.spaceCompatibility
              ?.rooms || [];


          const matchRoom =
            this.currentRoom ===
              "all" ||
            rooms.includes(
              this.currentRoom
            );


          // Search
          const q =
            this.searchQuery;


          const matchSearch =
            !q ||

            name
              .toLowerCase()
              .includes(q) ||

            craft
              .toLowerCase()
              .includes(q) ||

            state
              .toLowerCase()
              .includes(q) ||

            region
              .toLowerCase()
              .includes(q) ||

            artisanName
              .toLowerCase()
              .includes(q) ||

            materials
              .toLowerCase()
              .includes(q);


          return (
            matchCategory &&
            matchRegion &&
            matchRoom &&
            matchSearch
          );
        }
      );


    this.renderCatalog();
  },


  // =========================================================
  // RENDER PRODUCT CARDS
  // =========================================================

  renderCatalog() {

    const grid =
      document.getElementById(
        "productsGrid"
      );


    if (!grid) {
      console.warn(
        "productsGrid element not found"
      );

      return;
    }


    // No products
    if (
      this.filteredProducts.length ===
      0
    ) {

      grid.innerHTML = `
        <div class="empty-results">

          <div style="
            font-size:2.5rem;
            margin-bottom:10px;
          ">
            🎨
          </div>

          <h3>
            No Artisan Crafts Found
          </h3>

          <p>
            ${
              this.products.length === 0

                ? "No products are currently available in the marketplace."

                : "Try clearing the filters or searching for another craft."
            }
          </p>

          ${
            this.products.length > 0

              ? `
                <button
                  class="chip-btn active"
                  onclick="Marketplace.resetFilters()"
                >
                  Show All Crafts
                </button>
              `

              : ""
          }

        </div>
      `;

      return;
    }


    // Product cards
    grid.innerHTML =
      this.filteredProducts
        .map(
          (p) => `

      <article
        class="product-card"
        data-id="${p.id}"
      >

        <div
          class="card-image-wrap"
          onclick="
            Marketplace.showProductModal(
              '${p.id}'
            )
          "
        >

          <img
            src="${p.image}"
            alt="${p.name}"
            loading="lazy"

onerror="
    this.onerror=null;
    this.src='https://placehold.co/600x600?text=Product+Image';
"


          <div
            class="card-badge-container"
          >

            ${
              p.giCertified

                ? `
                  <span
                    class="badge badge-gi"
                  >
                    ✓ GI Tag Certified
                  </span>
                `

                : ""
            }

            <span
              class="badge badge-fairprice"
            >
              Direct Artisan
            </span>

          </div>


          <div
            class="card-action-overlay"
          >

            <button
              class="icon-action-btn"
              title="Quick View"

              onclick="
                event.stopPropagation();

                Marketplace.showProductModal(
                  '${p.id}'
                );
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
                  d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"
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

          <span
            class="card-craft-type"
          >
            ${p.craftForm}
            ${p.state || p.region
              ? ` · ${p.state || p.region}`
              : ""
            }
          </span>


          <h3
            class="card-title"

            onclick="
              Marketplace.showProductModal(
                '${p.id}'
              )
            "
          >
            ${p.name}
          </h3>


          <div
            class="card-artisan-line"
          >

            <img
              src="${p.artisan.avatar}"
              alt="${p.artisan.name}"

              onerror="
                this.onerror=null;
                this.src='/static/assets/images/logo.png';
              "
            />

            <span>
              Crafted by
              <strong>
                ${p.artisan.name}
              </strong>
            </span>

          </div>


          <div
            class="card-price-row"
          >

            <div class="price-box">

              <span
                class="price-current"
              >
                ₹${p.price.toLocaleString(
                  "en-IN"
                )}
              </span>


              ${
                p.marketEstimate >
                p.price

                  ? `
                    <span
                      class="price-market-cut"
                    >
                      ₹${p.marketEstimate.toLocaleString(
                        "en-IN"
                      )}
                      retail
                    </span>
                  `

                  : ""
              }

            </div>


            <span
              class="fair-share-pill"
            >
              Direct from Artisan
            </span>

          </div>


          <div
            class="card-cta-row"
          >

            <button
              class="btn-card-cart"

              onclick="
                Cart.addItem(
                  '${p.id}'
                )
              "
            >

              Add to Cart

            </button>


            <button
              class="btn-card-space"

              onclick="
                Marketplace.openInSpaceStudio(
                  '${p.id}'
                )
              "
            >

              Style in Space

            </button>

          </div>

        </div>

      </article>

    `
        )
        .join("");
  },


  // =========================================================
  // SHOW ALL PRODUCTS IN REGION
  // =========================================================

  showAllInCurrentRegion() {

    this.currentCategory =
      "all";

    this.currentRoom =
      "all";

    this.searchQuery =
      "";


    const searchInput =
      document.getElementById(
        "marketplaceSearchInput"
      );

    if (searchInput) {
      searchInput.value = "";
    }


    const roomSelect =
      document.getElementById(
        "roomFilterSelect"
      );

    if (roomSelect) {
      roomSelect.value = "all";
    }


    document
      .querySelectorAll(
        ".chip-btn"
      )
      .forEach((c) => {

        c.classList.toggle(
          "active",
          c.dataset.category ===
            "all"
        );
      });


    this.applyFilters();
  },


  // =========================================================
  // RESET FILTERS
  // =========================================================

  resetFilters() {

    this.currentCategory =
      "all";

    this.currentRegion =
      "all";

    this.currentRoom =
      "all";

    this.searchQuery =
      "";


    const searchInput =
      document.getElementById(
        "marketplaceSearchInput"
      );

    if (searchInput) {
      searchInput.value = "";
    }


    const regionSelect =
      document.getElementById(
        "regionFilterSelect"
      );

    if (regionSelect) {
      regionSelect.value = "all";
    }


    const roomSelect =
      document.getElementById(
        "roomFilterSelect"
      );

    if (roomSelect) {
      roomSelect.value = "all";
    }


    document
      .querySelectorAll(
        ".chip-btn"
      )
      .forEach((c) =>
        c.classList.remove(
          "active"
        )
      );


    const defaultChip =
      document.querySelector(
        '.chip-btn[data-category="all"]'
      );


    if (defaultChip) {
      defaultChip.classList.add(
        "active"
      );
    }


    this.applyFilters();
  },


  // =========================================================
  // PRODUCT DETAILS MODAL
  // =========================================================

  showProductModal(productId) {

    const p =
      this.products.find(
        (item) =>
          item.id === productId
      );


    if (!p) {
      console.error(
        "Product not found:",
        productId
      );

      return;
    }


    const modalContent = `

      <div class="pdp-grid">

        <div
          class="pdp-image-container"
        >

          <img
            src="${p.image}"
            alt="${p.name}"

            onerror="
              this.onerror=null;
              this.src='/static/assets/images/logo.png';
            "
          />

        </div>


        <div
          class="pdp-details"
        >

          <span
            class="pdp-craft-tag"
          >
            ${p.craftForm}
            ·
            ${p.state || p.region}
          </span>


          <h2
            class="pdp-title"
          >
            ${p.name}
          </h2>


          <div
            class="card-price-row"
            style="
              border:none;
              padding:0;
              margin-bottom:16px;
            "
          >

            <div
              class="price-box"
            >

              <span
                class="price-current"
                style="
                  font-size:1.8rem;
                "
              >
                ₹${p.price.toLocaleString(
                  "en-IN"
                )}
              </span>

            </div>


            ${
              p.giCertified

                ? `
                  <span
                    class="badge badge-gi"
                  >
                    ✓ GI Tag Certified
                  </span>
                `

                : ""
            }

          </div>


          <div
            class="pdp-artisan-card"
          >

            <img
              src="${p.artisan.avatar}"
              alt="${p.artisan.name}"

onerror="
    this.onerror=null;
    this.src='https://placehold.co/600x600?text=Product+Image';
"


            <div
              class="pdp-artisan-meta"
            >

              <h5>
                ${p.artisan.name}
              </h5>

              <p>
                <em>
                  "${p.artisan.story}"
                </em>
              </p>

            </div>

          </div>


          <p
            style="
              color:var(--text-muted);
              font-size:0.92rem;
              line-height:1.6;
              margin-bottom:14px;
            "
          >
            ${p.description}
          </p>


          <div
            class="pdp-meta-list"
          >

            <div
              class="pdp-meta-item"
            >

              <strong>
                Dimensions
              </strong>

              <span>
                ${p.dimensions}
              </span>

            </div>


            <div
              class="pdp-meta-item"
            >

              <strong>
                Materials
              </strong>

              <span>
                ${p.materials}
              </span>

            </div>


            <div
              class="pdp-meta-item"
            >

              <strong>
                Recommended Space
              </strong>

              <span>
                ${p.spaceCompatibility
                    .placementSuggestion}
              </span>

            </div>


            <div
              class="pdp-meta-item"
            >

              <strong>
                Vibe & Lighting
              </strong>

              <span>
                ${p.spaceCompatibility
                    .lightingVibe}
              </span>

            </div>

          </div>


          <div
            class="pdp-actions-row"
          >

            <button
              class="btn-primary-large"

              onclick="
                Cart.addItem(
                  '${p.id}'
                );

                window.App.closeModal();
              "
            >

              Add to Cart
              ·
              ₹${p.price.toLocaleString(
                "en-IN"
              )}

            </button>


            <button
              class="btn-secondary-large"

              onclick="
                Marketplace.openInSpaceStudio(
                  '${p.id}'
                );

                window.App.closeModal();
              "
            >

              Style in Space

            </button>

          </div>

        </div>

      </div>
    `;


    window.App.openModal(
      modalContent
    );
  },


  // =========================================================
  // SPACE STUDIO
  // =========================================================

  openInSpaceStudio(productId) {

    window.App.switchView(
      "space"
    );


    if (window.SpaceAI) {

      window.SpaceAI
        .selectCraftForCanvas(
          productId
        );
    }
  }
};


// Make available globally
window.Marketplace =
  Marketplace;