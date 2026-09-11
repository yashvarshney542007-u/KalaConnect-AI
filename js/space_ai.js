/**
 * KalaConnect AI - AI Space Recommendation Studio
 * Member 5 Secondary Responsibility:
 * 1. Space & Aesthetic Harmony Recommender (Algorithmic Room Matcher)
 * 2. Interactive Room Visualizer & "Place-in-Space" Canvas
 */

const SpaceAI = {
  activeMode: 'stylist', // 'stylist' or 'visualizer'
  
  // Stylist state
  selectedRoom: 'living_room',
  selectedStyle: 'earthy_rustic',
  selectedColor: '#C85A32',

  // Visualizer state
  currentPresetIndex: 0,
  activeCanvasProduct: null,
  canvasScale: 1.0,
  isDragging: false,
  dragStart: { x: 0, y: 0 },
  itemPos: { x: 50, y: 48 }, // percentages

  init() {
    this.bindEvents();
    this.runStylistMatch();
    this.setupVisualizer();
  },

  bindEvents() {
    // Mode switcher buttons
    const stylistTabBtn = document.getElementById('tabModeStylist');
    const visualizerTabBtn = document.getElementById('tabModeVisualizer');

    if (stylistTabBtn) {
      stylistTabBtn.addEventListener('click', () => this.switchStudioMode('stylist'));
    }
    if (visualizerTabBtn) {
      visualizerTabBtn.addEventListener('click', () => this.switchStudioMode('visualizer'));
    }

    // Stylist Room Options
    document.querySelectorAll('.room-opt-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.room-opt-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        this.selectedRoom = btn.dataset.room;
        this.runStylistMatch();
      });
    });

    // Stylist Style Options
    document.querySelectorAll('.style-opt-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.style-opt-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        this.selectedStyle = btn.dataset.style;
        this.runStylistMatch();
      });
    });

    // Color Swatches
    document.querySelectorAll('.palette-swatch').forEach(swatch => {
      swatch.addEventListener('click', (e) => {
        document.querySelectorAll('.palette-swatch').forEach(s => s.classList.remove('selected'));
        swatch.classList.add('selected');
        this.selectedColor = swatch.dataset.color;
        this.runStylistMatch();
      });
    });

    // Preset Room Dropdown
    const presetSelect = document.getElementById('roomPresetSelect');
    if (presetSelect) {
      presetSelect.addEventListener('change', (e) => {
        this.currentPresetIndex = parseInt(e.target.value, 10) || 0;
        this.updateRoomBackground();
      });
    }

    // Room Photo File Upload
    const uploadInput = document.getElementById('customRoomUploadInput');
    if (uploadInput) {
      uploadInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (event) => {
            const bgImg = document.getElementById('canvasBgImage');
            if (bgImg) bgImg.src = event.target.result;
            window.App.showToast('Uploaded your room photo! Decorate it now.', 'success');
          };
          reader.readAsDataURL(file);
        }
      });
    }

    // Canvas Dragging and Scaling
    this.initCanvasInteraction();
  },

  switchStudioMode(mode) {
    this.activeMode = mode;
    const stylistView = document.getElementById('studioModeStylistView');
    const visualizerView = document.getElementById('studioModeVisualizerView');
    const stylistTab = document.getElementById('tabModeStylist');
    const visualizerTab = document.getElementById('tabModeVisualizer');

    if (mode === 'stylist') {
      if (stylistView) stylistView.style.display = 'grid';
      if (visualizerView) visualizerView.style.display = 'none';
      if (stylistTab) stylistTab.classList.add('active');
      if (visualizerTab) visualizerTab.classList.remove('active');
    } else {
      if (stylistView) stylistView.style.display = 'none';
      if (visualizerView) visualizerView.style.display = 'block';
      if (stylistTab) stylistTab.classList.remove('active');
      if (visualizerTab) visualizerTab.classList.add('active');
    }
  },

  // MODE 1: Space Stylist Match Algorithm
  runStylistMatch() {
    const products = window.ARTISAN_PRODUCTS || [];

    // Calculate score for each product
    const scoredProducts = products.map(p => {
      let score = 70; // baseline

      if (p.spaceCompatibility.rooms.includes(this.selectedRoom)) {
        score += 15;
      }
      if (p.spaceCompatibility.styles.includes(this.selectedStyle)) {
        score += 12;
      }
      if (p.giCertified) {
        score += 2;
      }

      // Add slight deterministic variation for aesthetic feel
      const charCodeSum = p.id.charCodeAt(p.id.length - 1);
      score += (charCodeSum % 4);

      return { product: p, score: Math.min(score, 99) };
    });

    // Sort by highest score
    scoredProducts.sort((a, b) => b.score - a.score);
    const topPicks = scoredProducts.slice(0, 4);

    // Update Average Harmony Display
    const avgScore = Math.round(topPicks.reduce((acc, curr) => acc + curr.score, 0) / topPicks.length);
    const scoreCircle = document.getElementById('harmonyScoreCircle');
    const scoreVal = document.getElementById('harmonyScoreValue');
    const rationale = document.getElementById('aiStylingRationale');

    if (scoreCircle) scoreCircle.style.setProperty('--score', avgScore);
    if (scoreVal) scoreVal.textContent = `${avgScore}%`;

    const roomNames = {
      living_room: 'Living Room',
      bedroom: 'Master Bedroom',
      foyer: 'Entry Foyer',
      study_desk: 'Work / Study Desk',
      dining_pooja: 'Dining or Sacred Space',
      balcony: 'Veranda & Balcony'
    };

    const styleNames = {
      earthy_rustic: 'Earthy Rustic & Terracotta',
      minimalist: 'Contemporary Warm Minimalist',
      royal_heritage: 'Royal Indian Heritage',
      bohemian: 'Artistic Bohemian Fusion'
    };

    if (rationale) {
      rationale.textContent = `Based on your ${roomNames[this.selectedRoom] || 'space'} with ${styleNames[this.selectedStyle] || 'aesthetic'}, our AI model selected authentic handcrafted pieces with earthy textural harmony, avoiding mass-produced synthetic clutter.`;
    }

    // Render Curated Grid
    const resultsContainer = document.getElementById('stylistResultsGrid');
    if (!resultsContainer) return;

    resultsContainer.innerHTML = topPicks.map(item => `
      <div class="product-card">
        <div class="card-image-wrap" onclick="Marketplace.showProductModal('${item.product.id}')">
          <img src="${item.product.image}" alt="${item.product.name}" />
          <div class="card-badge-container">
            <span class="badge badge-heritage">★ ${item.score}% Space Match</span>
          </div>
        </div>
        <div class="card-body">
          <span class="card-craft-type">${item.product.craftForm}</span>
          <h4 class="card-title" onclick="Marketplace.showProductModal('${item.product.id}')">${item.product.name}</h4>
          <p style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 12px;">
            💡 <em>${item.product.spaceCompatibility.placementSuggestion}</em>
          </p>
          <div class="card-price-row">
            <span class="price-current">₹${item.product.price.toLocaleString('en-IN')}</span>
            <span class="fair-share-pill">${item.product.artisanSharePercent}% to Artisan</span>
          </div>
          <div class="card-cta-row">
            <button class="btn-card-cart" onclick="Cart.addItem('${item.product.id}')">Add to Cart</button>
            <button class="btn-card-space" onclick="SpaceAI.selectCraftForCanvas('${item.product.id}')">Place on Wall</button>
          </div>
        </div>
      </div>
    `).join('');
  },

  // MODE 2: Visualizer & Canvas Setup
  setupVisualizer() {
    const presets = window.ROOM_PRESETS || [];
    const select = document.getElementById('roomPresetSelect');
    if (select && select.options.length === 0) {
      select.innerHTML = presets.map((preset, idx) => `
        <option value="${idx}">${preset.name} (${preset.paletteName})</option>
      `).join('');
    }

    // Default first product
    if (window.ARTISAN_PRODUCTS && window.ARTISAN_PRODUCTS.length > 0) {
      this.activeCanvasProduct = window.ARTISAN_PRODUCTS[0];
    }

    this.renderCraftTray();
    this.updateRoomBackground();
  },

  renderCraftTray() {
    const tray = document.getElementById('canvasCraftThumbnails');
    if (!tray) return;

    const products = window.ARTISAN_PRODUCTS || [];
    tray.innerHTML = products.map(p => `
      <div class="craft-thumb-card ${this.activeCanvasProduct && this.activeCanvasProduct.id === p.id ? 'active' : ''}" 
           onclick="SpaceAI.selectCraftForCanvas('${p.id}')">
        <img src="${p.image}" alt="${p.name}" />
        <h6>${p.name}</h6>
        <span>₹${p.price.toLocaleString('en-IN')}</span>
      </div>
    `).join('');
  },

  updateRoomBackground() {
    const presets = window.ROOM_PRESETS || [];
    const preset = presets[this.currentPresetIndex] || presets[0];
    const bgImg = document.getElementById('canvasBgImage');
    if (bgImg && preset) {
      bgImg.src = preset.image;
    }
  },

  selectCraftForCanvas(productId) {
    const product = (window.ARTISAN_PRODUCTS || []).find(p => p.id === productId);
    if (!product) return;

    this.activeCanvasProduct = product;
    this.switchStudioMode('visualizer');

    const decorImg = document.getElementById('canvasDecorItemImg');
    const decorContainer = document.getElementById('canvasDecorItem');

    if (decorImg) {
      decorImg.src = product.image;
      decorImg.alt = product.name;
    }
    if (decorContainer) {
      decorContainer.style.display = 'block';
    }

    this.renderCraftTray();
    window.App.showToast(`Placed "${product.name}" onto room canvas! Drag to reposition.`, 'info');
  },

  initCanvasInteraction() {
    const container = document.getElementById('canvasContainer');
    const item = document.getElementById('canvasDecorItem');

    if (!container || !item) return;

    // Mouse events
    item.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      const rect = container.getBoundingClientRect();
      this.dragStart = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
      e.preventDefault();
    });

    window.addEventListener('mousemove', (e) => {
      if (!this.isDragging) return;
      const rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const posX = Math.max(10, Math.min(90, (x / rect.width) * 100));
      const posY = Math.max(10, Math.min(90, (y / rect.height) * 100));

      this.itemPos = { x: posX, y: posY };
      item.style.left = `${posX}%`;
      item.style.top = `${posY}%`;
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    // Touch events for mobile
    item.addEventListener('touchstart', (e) => {
      this.isDragging = true;
      const rect = container.getBoundingClientRect();
      const touch = e.touches[0];
      this.dragStart = {
        x: touch.clientX - rect.left,
        y: touch.clientY - rect.top
      };
    }, { passive: false });

    window.addEventListener('touchmove', (e) => {
      if (!this.isDragging) return;
      const rect = container.getBoundingClientRect();
      const touch = e.touches[0];
      const x = touch.clientX - rect.left;
      const y = touch.clientY - rect.top;

      const posX = Math.max(10, Math.min(90, (x / rect.width) * 100));
      const posY = Math.max(10, Math.min(90, (y / rect.height) * 100));

      this.itemPos = { x: posX, y: posY };
      item.style.left = `${posX}%`;
      item.style.top = `${posY}%`;
    }, { passive: true });

    window.addEventListener('touchend', () => {
      this.isDragging = false;
    });
  },

  zoomDecor(factor) {
    this.canvasScale = Math.max(0.5, Math.min(2.0, this.canvasScale + factor));
    const item = document.getElementById('canvasDecorItem');
    if (item) {
      item.style.transform = `translate(-50%, -50%) scale(${this.canvasScale})`;
    }
  },

  resetDecor() {
    this.canvasScale = 1.0;
    this.itemPos = { x: 50, y: 48 };
    const item = document.getElementById('canvasDecorItem');
    if (item) {
      item.style.left = '50%';
      item.style.top = '48%';
      item.style.transform = `translate(-50%, -50%) scale(1)`;
    }
  },

  addActiveCanvasItemToCart() {
    if (this.activeCanvasProduct) {
      Cart.addItem(this.activeCanvasProduct.id);
    }
  }
};

window.SpaceAI = SpaceAI;
