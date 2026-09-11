/**
 * KalaConnect AI - Supabase Configuration & Client Initializer
 * Connected to live Supabase project for Email & Password authentication.
 */

const SupabaseConfig = {
  // Default storage keys for dynamic configuration in browser
  STORAGE_KEY_URL: 'kalaconnect_supabase_url',
  STORAGE_KEY_ANON_KEY: 'kalaconnect_supabase_anon_key',

  // Configured Live Supabase Credentials
  DEFAULT_URL: 'https://tsithhzabhsapspzcbcv.supabase.co',
  DEFAULT_ANON_KEY: 'sb_publishable_C88Ca81o61i0rzYPhKYxWQ_p5Fb_TOE',

  client: null,

  getUrl() {
    const raw = localStorage.getItem(this.STORAGE_KEY_URL) || this.DEFAULT_URL;
    return (raw || '').trim().replace(/\/+$/, '');
  },

  getAnonKey() {
    const raw = localStorage.getItem(this.STORAGE_KEY_ANON_KEY) || this.DEFAULT_ANON_KEY;
    return (raw || '').trim();
  },

  isConfigured() {
    const url = this.getUrl();
    const key = this.getAnonKey();
    return !!(url && key && url.startsWith('http') && key.length > 15);
  },

  saveCredentials(url, anonKey) {
    if (url) localStorage.setItem(this.STORAGE_KEY_URL, url.trim().replace(/\/+$/, ''));
    if (anonKey) localStorage.setItem(this.STORAGE_KEY_ANON_KEY, anonKey.trim());
    this.initClient();
  },

  clearCredentials() {
    localStorage.removeItem(this.STORAGE_KEY_URL);
    localStorage.removeItem(this.STORAGE_KEY_ANON_KEY);
    this.client = null;
  },

  initClient() {
    const url = this.getUrl();
    const anonKey = this.getAnonKey();

    if (this.isConfigured() && window.supabase && typeof window.supabase.createClient === 'function') {
      try {
        this.client = window.supabase.createClient(url, anonKey, {
          auth: {
            persistSession: true,
            autoRefreshToken: true,
            detectSessionInUrl: true,
            storage: window.localStorage
          }
        });
        console.log('⚡ Supabase Client initialized successfully with:', url);
        return this.client;
      } catch (err) {
        console.error('Failed to initialize Supabase client:', err);
        this.client = null;
        return null;
      }
    } else {
      this.client = null;
      return null;
    }
  },

  getClient() {
    if (!this.client && this.isConfigured()) {
      this.initClient();
    }
    return this.client;
  }
};

window.SupabaseConfig = SupabaseConfig;
