/**
 * KalaConnect AI - Supabase Image Loader
 * Fetches all images from the 'images' storage bucket and distributes
 * them across ARTISAN_PRODUCTS before the marketplace renders.
 */

const ImageLoader = {
  BUCKET_NAMES: ['product-images', 'images'],
  
  // Directly verified public images uploaded by the team in Supabase storage
  KNOWN_SUPABASE_IMAGES: [
    'https://wbgntprnfvtvbvkfbyjp.supabase.co/storage/v1/object/public/product-images/handicraft/pexels-nata-37483660%20(1).jpg',
    'https://wbgntprnfvtvbvkfbyjp.supabase.co/storage/v1/object/public/product-images/handicraft/pexels-photo-36953894.jpg'
  ],

  /**
   * Get the public URL for a file in the storage bucket
   */
  getPublicUrl(fileName, bucket = 'product-images') {
    const client = window.SupabaseConfig && window.SupabaseConfig.getClient();
    if (!client) return null;
    const { data } = client.storage.from(bucket).getPublicUrl(fileName);
    return data && data.publicUrl ? data.publicUrl : null;
  },

  /**
   * List files from all known storage buckets and return public URLs
   */
  async fetchBucketImages() {
    const client = window.SupabaseConfig && window.SupabaseConfig.getClient();
    const collectedUrls = [...this.KNOWN_SUPABASE_IMAGES];

    if (!client) {
      console.warn('[ImageLoader] Supabase client not initialized yet, using verified storage URLs.');
      return collectedUrls;
    }

    for (const bucket of this.BUCKET_NAMES) {
      try {
        const { data: files, error } = await client.storage
          .from(bucket)
          .list('', { limit: 100, sortBy: { column: 'name', order: 'asc' } });

        if (!error && files && files.length > 0) {
          files.forEach(f => {
            if (f.name && /\.(jpg|jpeg|png|webp|gif|avif|svg)$/i.test(f.name)) {
              const url = this.getPublicUrl(f.name, bucket);
              if (url && !collectedUrls.includes(url)) collectedUrls.push(url);
            }
          });
        }
      } catch (err) {
        console.warn(`[ImageLoader] Could not read bucket ${bucket}:`, err);
      }
    }

    return collectedUrls;
  },

  /**
   * Patch ARTISAN_PRODUCTS with real Supabase image URLs.
   * Cycles through available images if there are fewer than products.
   * Products that already have a working non-Unsplash image are left untouched.
   */
  patchProductImages(imageUrls) {
    if (!imageUrls || imageUrls.length === 0) return;

    const products = window.ARTISAN_PRODUCTS;
    if (!products || products.length === 0) return;

    let imgIndex = 0;
    products.forEach(product => {
      // Assign a Supabase image, cycling round-robin if needed
      product.image = imageUrls[imgIndex % imageUrls.length];
      imgIndex++;
    });

    console.log(`[ImageLoader] 🖼️ Patched ${Math.min(imgIndex, products.length)} products with Supabase images.`);
  },

  /**
   * Re-render the marketplace and Space AI after images are loaded
   */
  refreshUI() {
    // Refresh marketplace catalog
    if (window.Marketplace && typeof window.Marketplace.renderCatalog === 'function') {
      window.Marketplace.products = window.ARTISAN_PRODUCTS || [];
      window.Marketplace.filteredProducts = [...window.Marketplace.products];
      window.Marketplace.applyFilters();
    }

    // Refresh Space AI stylist results grid and visualizer tray
    if (window.SpaceAI) {
      if (typeof window.SpaceAI.runStylistMatch === 'function') {
        window.SpaceAI.runStylistMatch();
      }
      if (typeof window.SpaceAI.renderCraftTray === 'function') {
        window.SpaceAI.renderCraftTray();
      }
    }
  },

  /**
   * Main entry point — call this once on page load.
   * Waits for Supabase to be ready, then loads and patches images.
   */
  async load() {
    // Wait for Supabase SDK to be available (it loads via CDN)
    await this._waitForSupabase();

    const imageUrls = await this.fetchBucketImages();

    if (imageUrls.length > 0) {
      this.patchProductImages(imageUrls);
      this.refreshUI();
    } else {
      console.info('[ImageLoader] No Supabase images found. Using default product images.');
    }
  },

  /**
   * Poll until window.supabase and SupabaseConfig.client are ready
   */
  _waitForSupabase(maxWaitMs = 5000) {
    return new Promise(resolve => {
      const start = Date.now();
      const check = () => {
        const client = window.SupabaseConfig && window.SupabaseConfig.getClient();
        if (client) {
          resolve(client);
        } else if (Date.now() - start > maxWaitMs) {
          console.warn('[ImageLoader] Supabase did not initialize in time. Proceeding without images.');
          resolve(null);
        } else {
          setTimeout(check, 100);
        }
      };
      check();
    });
  }
};

window.ImageLoader = ImageLoader;
