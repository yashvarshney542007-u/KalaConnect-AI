/**
 * KalaConnect AI - User Authentication & Supabase Integration
 * Supports Supabase Auth (Email & Password) with session persistence,
 * while maintaining the old vs. new customer check and "No Customer Found" screen.
 */

const Auth = {
  currentUser: null,
  authMethod: 'email', // 'email' or 'phone'
  phoneState: { fullPhone: '', timerInterval: null },
  STORAGE_KEY_SESSION: 'kalaconnect_user',
  STORAGE_KEY_DB: 'kalaconnect_registered_users_db',

  // Initial Registered Customers Seed Database (fallback / local demo)
  DEFAULT_DATABASE: [
    {
      id: "usr-reg-1",
      name: "Priya Sharma",
      email: "priya.sharma@example.com",
      password: "password123",
      avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
      city: "Mumbai, Maharashtra",
      kalaPoints: 240,
      isFirstTime: false,
      memberSince: "August 2026",
      ordersCount: 2
    },
    {
      id: "usr-reg-2",
      name: "Arjun Mehta",
      email: "arjun.mehta@example.com",
      password: "password123",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
      city: "Bengaluru, Karnataka",
      kalaPoints: 180,
      isFirstTime: false,
      memberSince: "July 2026",
      ordersCount: 1
    },
    {
      id: "usr-reg-3",
      name: "Kavita Nair",
      email: "kavita.nair@example.com",
      password: "password123",
      avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80",
      city: "Kochi, Kerala",
      kalaPoints: 310,
      isFirstTime: false,
      memberSince: "June 2026",
      ordersCount: 3
    }
  ],

  async init() {
    this.ensureDatabaseInitialized();

    // 1. Initialize Supabase Client if configured
    if (window.SupabaseConfig) {
      window.SupabaseConfig.initClient();
      const sbClient = window.SupabaseConfig.getClient();

      if (sbClient) {
        // Listen to active Supabase auth state changes (login, logout, token refresh)
        try {
          sbClient.auth.onAuthStateChange(async (event, session) => {
            if (session && session.user) {
              this.currentUser = this.formatSupabaseUser(session.user);
              localStorage.setItem(this.STORAGE_KEY_SESSION, JSON.stringify(this.currentUser));
              this.renderNavAuth();
              if (window.Cart && window.Cart.syncWithUser) window.Cart.syncWithUser();
            } else if (event === 'SIGNED_OUT') {
              this.currentUser = null;
              localStorage.removeItem(this.STORAGE_KEY_SESSION);
              this.renderNavAuth();
              if (window.Cart && window.Cart.syncWithUser) window.Cart.syncWithUser();
            }
          });

          // Check if existing Supabase session exists
          const { data } = await sbClient.auth.getSession();
          if (data && data.session && data.session.user) {
            this.currentUser = this.formatSupabaseUser(data.session.user);
            localStorage.setItem(this.STORAGE_KEY_SESSION, JSON.stringify(this.currentUser));
          }
        } catch (e) {
          console.warn('Supabase session lookup note:', e);
        }
      }
    }

    // 2. Fallback: Restore active session from localStorage if not already set
    if (!this.currentUser) {
      const savedUser = localStorage.getItem(this.STORAGE_KEY_SESSION);
      if (savedUser) {
        try {
          this.currentUser = JSON.parse(savedUser);
        } catch (e) {
          this.currentUser = null;
        }
      }
    }

    this.renderNavAuth();
    this.bindEvents();
  },

  formatSupabaseUser(sbUser) {
    const meta = sbUser.user_metadata || {};
    const phone = sbUser.phone || '';
    const name = meta.full_name || (sbUser.email ? sbUser.email.split('@')[0] : (phone ? `Member ${phone.slice(-4)}` : 'Conscious Buyer'));
    return {
      id: sbUser.id,
      name: name,
      email: sbUser.email || (phone ? `${phone.replace('+', '')}@mobile.kalaconnect.ai` : ''),
      phone: phone,
      avatar: meta.avatar_url || "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80",
      city: meta.city || "India",
      kalaPoints: meta.kala_points || 120,
      isFirstTime: meta.is_first_time !== false,
      memberSince: "Verified Customer",
      ordersCount: meta.orders_count || 0,
      isSupabase: true
    };
  },

  // Database Management
  ensureDatabaseInitialized() {
    const existing = localStorage.getItem(this.STORAGE_KEY_DB);
    if (!existing) {
      localStorage.setItem(this.STORAGE_KEY_DB, JSON.stringify(this.DEFAULT_DATABASE));
    }
  },

  getAllUsers() {
    this.ensureDatabaseInitialized();
    try {
      return JSON.parse(localStorage.getItem(this.STORAGE_KEY_DB)) || this.DEFAULT_DATABASE;
    } catch (e) {
      return this.DEFAULT_DATABASE;
    }
  },

  saveUserToDatabase(user) {
    const users = this.getAllUsers();
    users.push(user);
    localStorage.setItem(this.STORAGE_KEY_DB, JSON.stringify(users));
  },

  updateUserInDatabase(updatedUser) {
    if (!updatedUser) return;
    const users = this.getAllUsers();
    const idx = users.findIndex(u => (u.id && u.id === updatedUser.id) || (u.email && u.email.toLowerCase() === updatedUser.email.toLowerCase()));
    if (idx > -1) {
      users[idx] = { ...users[idx], ...updatedUser };
      localStorage.setItem(this.STORAGE_KEY_DB, JSON.stringify(users));
    }
  },

  findUserByEmail(email) {
    if (!email) return null;
    const cleanEmail = email.trim().toLowerCase();
    const users = this.getAllUsers();
    return users.find(u => u.email.toLowerCase() === cleanEmail) || null;
  },

  bindEvents() {
    document.addEventListener('click', (e) => {
      const dropdown = document.getElementById('userDropdownMenu');
      const pill = document.getElementById('userProfilePill');
      if (dropdown && pill && !pill.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.remove('show');
        pill.classList.remove('active');
      }
    });
  },

  isLoggedIn() {
    return !!this.currentUser;
  },

  renderNavAuth() {
    const authContainer = document.getElementById('authNavContainer');
    if (!authContainer) return;

    if (this.isLoggedIn()) {
      authContainer.innerHTML = `
        <div class="auth-nav-wrap">
          <div class="user-profile-pill" id="userProfilePill" onclick="Auth.toggleDropdown()">
            <img src="${this.currentUser.avatar}" alt="${this.currentUser.name}" class="user-avatar-img" />
            <span class="user-pill-name">${this.currentUser.name.split(' ')[0]}</span>
            <svg class="user-dropdown-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </div>

          <!-- Dropdown Menu -->
          <div class="user-dropdown-menu" id="userDropdownMenu">
            <div class="dropdown-user-header">
              <h5>${this.currentUser.name}</h5>
              <p>${this.currentUser.email}</p>
              <div style="display: flex; gap: 4px; align-items: center; margin-top: 4px;">
                <span class="dropdown-badge">🪙 ${this.currentUser.kalaPoints || 120} Kala Points</span>
              </div>
            </div>

            <button class="dropdown-item" onclick="Auth.showOrdersModal()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line></svg>
              My Orders & Impact
            </button>

            <button class="dropdown-item" onclick="App.switchView('space'); Auth.toggleDropdown();">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
              My Styled Spaces
            </button>

            <button class="dropdown-item" onclick="Auth.showProfilePhotoModal()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
              Change Profile Photo
            </button>

            <button class="dropdown-item logout-item" onclick="Auth.logout()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
              Sign Out
            </button>
          </div>
        </div>
      `;
    } else {
      authContainer.innerHTML = `
        <button class="auth-login-btn" onclick="Auth.openAuthModal('signin')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          Sign In
        </button>
      `;
    }
  },

  toggleDropdown() {
    const dropdown = document.getElementById('userDropdownMenu');
    const pill = document.getElementById('userProfilePill');
    if (dropdown && pill) {
      dropdown.classList.toggle('show');
      pill.classList.toggle('active');
    }
  },

  openAuthModal(defaultTab = 'signin', prefillEmail = '', defaultMethod = 'email') {
    this.authMethod = defaultMethod;
    this.stopResendCountdown();

    const isEmail = this.authMethod === 'email';

    const modalContent = `
      <div class="auth-modal-wrap" id="authModalContainer">
        <div class="auth-modal-header">
          <img src="assets/logo.png" alt="KalaConnect AI" class="auth-modal-logo" />
          <h3>Welcome to KalaConnect AI</h3>
          <p>Direct fair-market linkage empowering India's marginalized artisans</p>
        </div>

        <!-- Auth Method Switcher (Email vs Mobile OTP) -->
        <div class="auth-method-bar" id="authMethodBar">
          <button type="button" class="auth-method-btn ${isEmail ? 'active' : ''}" id="btnMethodEmail" onclick="Auth.switchAuthMethod('email')">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
            Email & Password
          </button>
          <button type="button" class="auth-method-btn ${!isEmail ? 'active' : ''}" id="btnMethodPhone" onclick="Auth.switchAuthMethod('phone')">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
            Mobile Number (OTP)
          </button>
        </div>

        <!-- Quick Pre-Registered Demo Customers (for offline/demo fallback) -->
        <div class="demo-accounts-card" id="demoAccountsCard" style="${isEmail && defaultTab === 'signin' ? 'display: block;' : 'display: none;'}">
          <h6>⚡ Existing Registered Customers (Click to test):</h6>
          <div class="demo-btn-row">
            <button class="demo-user-btn" onclick="Auth.loginAsRegisteredDemo(0)">
              <span>👤 Priya (Mumbai)</span>
            </button>
            <button class="demo-user-btn" onclick="Auth.loginAsRegisteredDemo(1)">
              <span>👤 Arjun (Bengaluru)</span>
            </button>
          </div>
        </div>

        <!-- Tabs (for Email flow) -->
        <div class="auth-tabs" id="authTabsBar" style="${isEmail ? 'display: grid;' : 'display: none;'}">
          <button class="auth-tab-btn ${defaultTab === 'signin' ? 'active' : ''}" id="tabBtnSignIn" onclick="Auth.switchModalTab('signin')">
            Sign In (Existing Customer)
          </button>
          <button class="auth-tab-btn ${defaultTab === 'signup' ? 'active' : ''}" id="tabBtnSignUp" onclick="Auth.switchModalTab('signup')">
            Create Account (New Customer)
          </button>
        </div>

        <!-- Dynamic Container for Form or "No Customer Found" or OTP screen -->
        <div id="authDynamicContent">
          ${isEmail ? (defaultTab === 'signin' ? this.getSignInFormHTML(prefillEmail) : this.getSignUpFormHTML(prefillEmail)) : this.getPhoneRequestOtpHTML()}
        </div>

        <p class="auth-footnote">
          🔒 Secure authentication. Your purchases directly empower 840+ rural artisan families across 28 States & 8 Union Territories.
        </p>
      </div>
    `;

    window.App.openModal(modalContent);
  },

  switchAuthMethod(method, prefillPhone = '') {
    this.authMethod = method;
    this.stopResendCountdown();

    const btnEmail = document.getElementById('btnMethodEmail');
    const btnPhone = document.getElementById('btnMethodPhone');
    const demoCard = document.getElementById('demoAccountsCard');
    const tabsBar = document.getElementById('authTabsBar');
    const content = document.getElementById('authDynamicContent');

    if (method === 'email') {
      if (btnEmail) btnEmail.classList.add('active');
      if (btnPhone) btnPhone.classList.remove('active');
      if (tabsBar) tabsBar.style.display = 'grid';
      if (demoCard) demoCard.style.display = 'block';
      if (content) content.innerHTML = this.getSignInFormHTML();
    } else {
      if (btnPhone) btnPhone.classList.add('active');
      if (btnEmail) btnEmail.classList.remove('active');
      if (tabsBar) tabsBar.style.display = 'none';
      if (demoCard) demoCard.style.display = 'none';
      if (content) content.innerHTML = this.getPhoneRequestOtpHTML(prefillPhone);
    }
  },

  getPhoneRequestOtpHTML(prefillPhone = '') {
    return `
      <form id="formPhoneRequest" onsubmit="Auth.handleSendPhoneOtp(event)">
        <div id="phoneAlertBox"></div>

        <div style="text-align: center; margin-bottom: 16px;">
          <p style="font-size: 0.86rem; color: var(--text-muted); margin: 0;">
            Sign in or register with your mobile number. We'll send a 6-digit verification code.
          </p>
        </div>

        <div class="auth-form-group">
          <label>Mobile Phone Number</label>
          <div class="phone-input-wrap">
            <div class="phone-prefix-box">
              <span>🇮🇳</span>
              <span>+91</span>
            </div>
            <input type="tel" id="inputPhoneNumber" class="auth-form-input phone-input-field" placeholder="98765 43210" maxlength="10" pattern="[0-9]{10}" required value="${prefillPhone}" />
          </div>
        </div>

        <button type="submit" class="auth-submit-btn" id="btnSendPhoneOtp">
          Get Verification OTP
        </button>
      </form>
    `;
  },

  getPhoneVerifyOtpHTML(fullPhone) {
    const rawPhone = fullPhone.replace('+91', '');
    const isProviderDisabled = this.phoneState.providerDisabled;

    return `
      <div class="otp-verify-card">
        <div id="otpAlertBox"></div>

        <div class="otp-icon-wrap">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
        </div>

        <h4 style="font-size: 1.25rem; margin-bottom: 4px;">Verify Mobile Number</h4>
        <div class="otp-target-chip">
          <span>${fullPhone}</span>
          <button type="button" class="otp-edit-btn" onclick="Auth.switchAuthMethod('phone', '${rawPhone}')">Edit</button>
        </div>

        <p style="font-size: 0.84rem; color: var(--text-muted); margin-bottom: 16px;">
          Please enter the 6-digit verification code sent to your phone messaging box.
        </p>

        ${isProviderDisabled ? `
          <div class="auth-notice-banner" style="background: #FFF8E6; border: 1px solid #FFE08A; border-radius: var(--radius-md); padding: 12px; margin-bottom: 16px; text-align: left; font-size: 0.8rem; color: #7A5600;">
            <div style="font-weight: 700; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
              <span>⚠️ Supabase SMS Gateway Setup Required</span>
            </div>
            <span>To send real cellular text messages to your phone's SMS inbox, Supabase requires an SMS Provider (e.g., <strong>Twilio</strong> or <strong>MessageBird</strong>) enabled in your Supabase dashboard.</span>
            <div style="margin-top: 8px;">
              <a href="https://supabase.com/dashboard/project/tsithhzabhsapspzcbcv/auth/providers" target="_blank" rel="noopener noreferrer" style="color: #C25927; font-weight: 700; text-decoration: underline;">
                🔗 Open Supabase Phone Provider Settings →
              </a>
            </div>
          </div>
        ` : ''}

        <form id="formPhoneVerify" onsubmit="Auth.handleVerifyPhoneOtp(event)">
          <input type="text" id="inputOtpCode" class="otp-input-field" maxlength="6" pattern="[0-9]{6}" placeholder="••••••" required autofocus />

          <button type="submit" class="auth-submit-btn" id="btnVerifyOtp">
            Verify & Sign In
          </button>

          <div class="otp-resend-row">
            <span>Didn't receive SMS?</span>
            <button type="button" id="btnResendOtp" class="otp-resend-btn" disabled onclick="Auth.handleResendPhoneOtp('${fullPhone}')">
              Resend in <span id="resendCountdown">30</span>s
            </button>
          </div>
        </form>
      </div>
    `;
  },

  showSmsPushNotification(fullPhone, otpCode) {
    const existing = document.getElementById('smsHeadsUpBanner');
    if (existing) existing.remove();

    const banner = document.createElement('div');
    banner.id = 'smsHeadsUpBanner';
    banner.className = 'sms-heads-up-toast';
    banner.onclick = () => this.autoFillOtp(otpCode);
    banner.innerHTML = `
      <div class="sms-toast-icon">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
      </div>
      <div class="sms-toast-content">
        <div class="sms-toast-header">
          <span>💬 SMS Notification</span>
          <span>Just Now</span>
        </div>
        <div class="sms-toast-title">KalaConnect AI Verification</div>
        <div class="sms-toast-body">
          Your mobile OTP is <strong>${otpCode}</strong>. Valid for 5 mins. Tap to auto-fill.
        </div>
      </div>
      <button type="button" class="sms-toast-action">
        ✨ Auto-Fill
      </button>
    `;

    document.body.appendChild(banner);

    setTimeout(() => {
      if (banner && banner.parentNode) {
        banner.style.opacity = '0';
        banner.style.transform = 'translateX(-50%) translateY(-30px)';
        setTimeout(() => banner.remove(), 250);
      }
    }, 9000);
  },

  autoFillOtp(code) {
    const input = document.getElementById('inputOtpCode');
    const alertBox = document.getElementById('otpAlertBox');
    if (input) {
      input.value = code;
      input.focus();
    }
    if (alertBox) alertBox.innerHTML = '';
    const banner = document.getElementById('smsHeadsUpBanner');
    if (banner) banner.remove();
    window.App.showToast(`Code ${code} filled! Click 'Verify & Sign In' to complete.`, 'info');
  },

  async handleSendPhoneOtp(e) {
    e.preventDefault();
    const phoneInput = document.getElementById('inputPhoneNumber');
    const alertBox = document.getElementById('phoneAlertBox');
    const submitBtn = document.getElementById('btnSendPhoneOtp');

    if (!phoneInput) return;
    const rawPhone = phoneInput.value.trim().replace(/\D/g, '');

    if (rawPhone.length !== 10) {
      if (alertBox) {
        alertBox.innerHTML = `
          <div class="auth-error-banner">
            <span>Please enter a valid 10-digit Indian mobile number.</span>
          </div>
        `;
      }
      return;
    }

    const fullPhone = `+91${rawPhone}`;
    this.phoneState.fullPhone = fullPhone;

    // Generate fresh dynamic 6-digit OTP
    const generatedOtp = Math.floor(100000 + Math.random() * 900000).toString();
    this.phoneState.generatedOtp = generatedOtp;

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending OTP...';
    }

    const sbClient = window.SupabaseConfig && window.SupabaseConfig.getClient();

    this.phoneState.providerDisabled = false;

    if (sbClient) {
      try {
        const { data, error } = await sbClient.auth.signInWithOtp({
          phone: fullPhone
        });

        if (error) {
          console.warn('Supabase signInWithOtp (SMS provider pending):', error.message || error);
          this.phoneState.providerDisabled = true;
        }
      } catch (err) {
        console.warn('Supabase phone auth note:', err);
        this.phoneState.providerDisabled = true;
      }
    } else {
      this.phoneState.providerDisabled = true;
    }

    // Transition to OTP verification screen
    const content = document.getElementById('authDynamicContent');
    if (content) {
      content.innerHTML = this.getPhoneVerifyOtpHTML(fullPhone);
      this.startResendCountdown();
    }
  },

  async handleVerifyPhoneOtp(e) {
    e.preventDefault();
    const otpInput = document.getElementById('inputOtpCode');
    const alertBox = document.getElementById('otpAlertBox');
    const submitBtn = document.getElementById('btnVerifyOtp');

    if (!otpInput) return;
    const otpCode = otpInput.value.trim();
    const fullPhone = this.phoneState.fullPhone;
    const expectedOtp = this.phoneState.generatedOtp;

    if (otpCode.length !== 6) {
      if (alertBox) {
        alertBox.innerHTML = `
          <div class="auth-error-banner">
            <span>Please enter the full 6-digit OTP code.</span>
          </div>
        `;
      }
      return;
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Verifying...';
    }

    const sbClient = window.SupabaseConfig && window.SupabaseConfig.getClient();
    let verifiedUser = null;

    if (sbClient) {
      try {
        const { data, error } = await sbClient.auth.verifyOtp({
          phone: fullPhone,
          token: otpCode,
          type: 'sms'
        });

        if (!error && data && data.user) {
          verifiedUser = this.formatSupabaseUser(data.user);
        }
      } catch (err) {
        console.warn('Supabase verifyOtp check:', err);
      }
    }

    // Check if entered code matches dynamically generated OTP or dev code
    const isCodeValid = (
      otpCode === expectedOtp ||
      otpCode === '123456' ||
      otpCode === '000000' ||
      verifiedUser !== null
    );

    if (isCodeValid) {
      if (!verifiedUser) {
        verifiedUser = {
          id: "usr-ph-" + fullPhone.slice(-6),
          name: `Member ${fullPhone.slice(-4)}`,
          phone: fullPhone,
          email: `${fullPhone.replace('+', '')}@mobile.kalaconnect.ai`,
          avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80",
          city: "India",
          kalaPoints: 120,
          isFirstTime: true,
          memberSince: "Verified Member",
          ordersCount: 0,
          isSupabase: true
        };
      }

      // Save session and sync state
      this.currentUser = verifiedUser;
      localStorage.setItem(this.STORAGE_KEY_SESSION, JSON.stringify(this.currentUser));
      this.updateUserInDatabase(this.currentUser);
      this.renderNavAuth();
      if (window.Cart && window.Cart.syncWithUser) window.Cart.syncWithUser();
      this.stopResendCountdown();

      const banner = document.getElementById('smsHeadsUpBanner');
      if (banner) banner.remove();

      window.App.closeModal();
      window.App.showToast(`🎉 Welcome, ${this.currentUser.name}! Phone verified and 40% discount unlocked.`, 'success');
      return;
    }

    // Invalid code entered
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Verify & Sign In';
    }
    if (alertBox) {
      alertBox.innerHTML = `
        <div class="auth-error-banner">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          <span>Invalid OTP code. Please enter the 6-digit code sent to your mobile. (Test code: <code>123456</code>)</span>
        </div>
      `;
    }
  },

  async handleResendPhoneOtp(fullPhone) {
    const sbClient = window.SupabaseConfig && window.SupabaseConfig.getClient();
    if (sbClient) {
      try {
        await sbClient.auth.signInWithOtp({ phone: fullPhone });
      } catch (e) {}
    }
    this.startResendCountdown();
    window.App.showToast(`New verification code requested for ${fullPhone}!`, 'success');
  },

  startResendCountdown() {
    this.stopResendCountdown();
    let seconds = 30;
    const countdownEl = document.getElementById('resendCountdown');
    const resendBtn = document.getElementById('btnResendOtp');

    if (countdownEl) countdownEl.textContent = seconds;
    if (resendBtn) resendBtn.disabled = true;

    this.phoneState.timerInterval = setInterval(() => {
      seconds--;
      const el = document.getElementById('resendCountdown');
      const btn = document.getElementById('btnResendOtp');
      if (el) el.textContent = seconds;

      if (seconds <= 0) {
        this.stopResendCountdown();
        if (btn) {
          btn.disabled = false;
          btn.textContent = 'Resend OTP';
        }
      }
    }, 1000);
  },

  stopResendCountdown() {
    if (this.phoneState.timerInterval) {
      clearInterval(this.phoneState.timerInterval);
      this.phoneState.timerInterval = null;
    }
  },

  getSignInFormHTML(prefillEmail = '') {
    return `
      <form id="formSignIn" onsubmit="Auth.handleSignIn(event)">
        <div id="signInAlertBox"></div>
        <div class="auth-form-group">
          <label>Registered Customer Email</label>
          <input type="email" id="signInEmail" class="auth-form-input" placeholder="e.g. priya.sharma@example.com" required value="${prefillEmail || ''}" />
        </div>
        <div class="auth-form-group">
          <label>Password</label>
          <input type="password" id="signInPassword" class="auth-form-input" placeholder="••••••••" required />
        </div>
        <button type="submit" class="auth-submit-btn" id="btnSubmitSignIn">
          Sign In to KalaConnect
        </button>
      </form>
    `;
  },

  getSignUpFormHTML(prefillEmail = '') {
    const defaultAvatar = "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80";
    return `
      <form id="formSignUp" onsubmit="Auth.handleSignUp(event)">
        <div id="signUpAlertBox"></div>

        <!-- Profile Photo Selection / Upload -->
        <div class="avatar-section-wrap">
          <div class="avatar-section-title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
            Choose or Upload Profile Photo (Optional)
          </div>
          <div class="avatar-picker-row">
            <div class="avatar-preview-container">
              <img src="${defaultAvatar}" id="signUpAvatarPreview" class="avatar-preview-img" alt="Profile Preview" />
              <label for="signUpAvatarFile" class="avatar-upload-badge" title="Upload from device">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"></path></svg>
              </label>
            </div>
            <div class="avatar-picker-controls">
              <input type="file" id="signUpAvatarFile" class="file-input-hidden" accept="image/*" onchange="Auth.handleAvatarFileUpload(event, 'signUpAvatarPreview', 'signUpAvatarValue')" />
              <label for="signUpAvatarFile" class="btn-upload-avatar">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                Upload Photo
              </label>
              <div class="avatar-presets-grid">
                <button type="button" class="avatar-preset-btn active" onclick="Auth.selectPresetAvatar('https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80', 'signUpAvatarPreview', 'signUpAvatarValue', this)" title="Jaipur Royal">
                  <img src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&auto=format&fit=crop&q=80" alt="Preset 1" />
                </button>
                <button type="button" class="avatar-preset-btn" onclick="Auth.selectPresetAvatar('https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80', 'signUpAvatarPreview', 'signUpAvatarValue', this)" title="Mithila Lover">
                  <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&auto=format&fit=crop&q=80" alt="Preset 2" />
                </button>
                <button type="button" class="avatar-preset-btn" onclick="Auth.selectPresetAvatar('https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80', 'signUpAvatarPreview', 'signUpAvatarValue', this)" title="Craft Explorer">
                  <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&auto=format&fit=crop&q=80" alt="Preset 3" />
                </button>
                <button type="button" class="avatar-preset-btn" onclick="Auth.selectPresetAvatar('https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80', 'signUpAvatarPreview', 'signUpAvatarValue', this)" title="Heritage Patron">
                  <img src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=80&auto=format&fit=crop&q=80" alt="Preset 4" />
                </button>
              </div>
            </div>
          </div>
          <input type="hidden" id="signUpAvatarValue" value="${defaultAvatar}" />
        </div>

        <div class="auth-form-group">
          <label>Full Name</label>
          <input type="text" id="signUpName" class="auth-form-input" placeholder="e.g. Aditi Rao" required />
        </div>
        <div class="auth-form-group">
          <label>Email Address</label>
          <input type="email" id="signUpEmail" class="auth-form-input" placeholder="e.g. aditi@example.com" required value="${prefillEmail || ''}" />
        </div>
        <div class="auth-form-group">
          <label>Delivery City / State</label>
          <input type="text" id="signUpCity" class="auth-form-input" placeholder="e.g. Jaipur, Rajasthan" required />
        </div>
        <div class="auth-form-group">
          <label>Create Password</label>
          <input type="password" id="signUpPassword" class="auth-form-input" placeholder="•••••••• (Min. 6 chars)" minlength="6" required />
        </div>
        <button type="submit" class="auth-submit-btn" id="btnSubmitSignUp">
          Create Account & Claim Flat 40% OFF
        </button>
      </form>
    `;
  },

  switchModalTab(tab, prefillEmail = '') {
    const content = document.getElementById('authDynamicContent');
    const tabSignIn = document.getElementById('tabBtnSignIn');
    const tabSignUp = document.getElementById('tabBtnSignUp');
    const tabsBar = document.getElementById('authTabsBar');
    const demoCard = document.getElementById('demoAccountsCard');

    if (tabsBar) tabsBar.style.display = 'grid';

    if (tab === 'signin') {
      if (demoCard) demoCard.style.display = 'block';
      if (tabSignIn) tabSignIn.classList.add('active');
      if (tabSignUp) tabSignUp.classList.remove('active');
      if (content) {
        content.innerHTML = this.getSignInFormHTML(prefillEmail);
      }
    } else {
      if (demoCard) demoCard.style.display = 'none';
      if (tabSignIn) tabSignIn.classList.remove('active');
      if (tabSignUp) tabSignUp.classList.add('active');
      if (content) {
        content.innerHTML = this.getSignUpFormHTML(prefillEmail);
      }
    }
  },

  // 1-Click Demo Login (fallback)
  loginAsRegisteredDemo(index) {
    const users = this.getAllUsers();
    const user = users[index] || users[0];
    this.currentUser = { ...user };
    localStorage.setItem(this.STORAGE_KEY_SESSION, JSON.stringify(this.currentUser));
    this.renderNavAuth();
    if (window.Cart && window.Cart.syncWithUser) window.Cart.syncWithUser();
    window.App.closeModal();
    window.App.showToast(`Welcome back, ${this.currentUser.name}! Customer verified in database.`, 'success');
  },

  // SIGN IN: Authenticates with Supabase or fallback database
  async handleSignIn(e) {
    e.preventDefault();
    const emailInput = document.getElementById('signInEmail');
    const passwordInput = document.getElementById('signInPassword');
    const alertBox = document.getElementById('signInAlertBox');
    const submitBtn = document.getElementById('btnSubmitSignIn');

    if (!emailInput) return;
    const email = emailInput.value.trim();
    const password = passwordInput ? passwordInput.value : '';

    if (!email || !password) {
      if (alertBox) {
        alertBox.innerHTML = `
          <div class="auth-error-banner">
            <span>Please enter both email and password.</span>
          </div>
        `;
      }
      return;
    }

    // A. Check if Supabase client is configured
    const sbClient = window.SupabaseConfig && window.SupabaseConfig.getClient();

    if (sbClient) {
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Connecting to Supabase...';
      }

      try {
        const { data, error } = await sbClient.auth.signInWithPassword({
          email: email,
          password: password
        });

        if (error) {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Sign In to KalaConnect';
          }

          const errMsg = (error.message || '').toLowerCase();

          // Check if email confirmation is pending
          if (errMsg.includes('email not confirmed')) {
            if (alertBox) {
              alertBox.innerHTML = `
                <div class="auth-error-banner" style="background: #FEF3C7; border-color: #FCD34D; color: #92400E;">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                  <span>Your email <strong>${email}</strong> has not been confirmed yet. Please verify via the email sent by Supabase.</span>
                </div>
              `;
            }
            return;
          }

          // Incorrect email or password banner inside the Sign In form
          if (alertBox) {
            alertBox.innerHTML = `
              <div class="auth-error-banner">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                <div style="text-align: left;">
                  <span><strong>Incorrect email or password.</strong> Please check your credentials and try again.</span>
                  <div style="margin-top: 4px; font-size: 0.78rem; opacity: 0.95;">
                    New customer? <a href="javascript:void(0)" onclick="Auth.switchModalTab('signup', '${email}')" style="text-decoration: underline; font-weight: 700; color: inherit;">Create an account here</a> to claim flat 40% OFF.
                  </div>
                </div>
              </div>
            `;
          }
          return;
        }

        // Supabase sign-in success!
        if (data && data.user) {
          this.currentUser = this.formatSupabaseUser(data.user);
          localStorage.setItem(this.STORAGE_KEY_SESSION, JSON.stringify(this.currentUser));
          this.renderNavAuth();
          if (window.Cart && window.Cart.syncWithUser) window.Cart.syncWithUser();
          window.App.closeModal();
          window.App.showToast(`Welcome back, ${this.currentUser.name}! Authenticated via Supabase.`, 'success');
          return;
        }
      } catch (err) {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Sign In to KalaConnect';
        }
        console.error('Supabase sign-in exception:', err);
      }
    }

    // B. Fallback: Local database verification if Supabase not configured
    const existingUser = this.findUserByEmail(email);

    if (!existingUser) {
      // NEW CUSTOMER TRIED SIGNING IN: Show "No Customer Found" Screen!
      this.showNoCustomerFoundScreen(email);
      return;
    }

    // Existing customer found -> Check password
    if (existingUser.password && password && password !== existingUser.password) {
      if (alertBox) {
        alertBox.innerHTML = `
          <div class="auth-error-banner">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            <span><strong>Incorrect email or password.</strong> Please check your credentials and try again.</span>
          </div>
        `;
      }
      return;
    }

    // Successfully verified customer
    this.currentUser = { ...existingUser };
    localStorage.setItem(this.STORAGE_KEY_SESSION, JSON.stringify(this.currentUser));
    this.renderNavAuth();
    if (window.Cart && window.Cart.syncWithUser) window.Cart.syncWithUser();
    window.App.closeModal();
    window.App.showToast(`Welcome back, ${this.currentUser.name}! Logged in successfully.`, 'success');
  },

  // SCREEN: "No Customer Found"
  showNoCustomerFoundScreen(searchedEmail) {
    const content = document.getElementById('authDynamicContent');
    const tabsBar = document.getElementById('authTabsBar');
    const demoCard = document.getElementById('demoAccountsCard');

    if (tabsBar) tabsBar.style.display = 'none';
    if (demoCard) demoCard.style.display = 'none';

    if (content) {
      content.innerHTML = `
        <div class="no-customer-card">
          <div class="no-customer-icon-wrap">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>
          </div>

          <h4>No Customer Account Found</h4>
          <span class="searched-email-chip">${searchedEmail}</span>

          <p class="no-customer-desc">
            We searched our registered customer database, but there is no existing KalaConnect account associated with this email.
            <br/><br/>
            <strong>It looks like you're a new customer!</strong> Please create an account to unlock your <strong>Flat 40% First-Time Buyer Discount</strong> and direct artisan linkage.
          </p>

          <div class="no-customer-actions">
            <button class="btn-goto-signup" onclick="Auth.switchModalTab('signup', '${searchedEmail}')">
              Create New Customer Account (40% OFF)
            </button>
            <button class="btn-back-signin" onclick="Auth.switchModalTab('signin', '${searchedEmail}')">
              ← Try Another Email or Sign In
            </button>
          </div>
        </div>
      `;
    }
  },

  // SIGN UP: Registers new customer in Supabase or fallback database
  async handleSignUp(e) {
    e.preventDefault();
    const name = document.getElementById('signUpName').value.trim();
    const email = document.getElementById('signUpEmail').value.trim();
    const city = document.getElementById('signUpCity').value.trim();
    const password = document.getElementById('signUpPassword').value;
    const alertBox = document.getElementById('signUpAlertBox');
    const submitBtn = document.getElementById('btnSubmitSignUp');
    const avatarInput = document.getElementById('signUpAvatarValue');
    const avatar = (avatarInput && avatarInput.value) ? avatarInput.value : 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80';

    if (!email || !password || !name) return;

    // A. Check if Supabase client is configured
    const sbClient = window.SupabaseConfig && window.SupabaseConfig.getClient();

    if (sbClient) {
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Registering on Supabase...';
      }

      try {
        const { data, error } = await sbClient.auth.signUp({
          email: email,
          password: password,
          options: {
            data: {
              full_name: name,
              city: city || 'India',
              avatar_url: avatar,
              kala_points: 100,
              is_first_time: true,
              orders_count: 0
            }
          }
        });

        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Create Account & Claim Flat 40% OFF';
        }

        if (error) {
          if (alertBox) {
            alertBox.innerHTML = `
              <div class="auth-error-banner">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                <span>${error.message || 'Error signing up with Supabase.'}</span>
              </div>
            `;
          }
          return;
        }

        // If email confirmation is enabled in Supabase, session is null until user confirms link
        if (data.user && !data.session) {
          if (alertBox) {
            alertBox.innerHTML = `
              <div class="auth-error-banner" style="background: #ECFDF5; border-color: #10B981; color: #065F46; text-align: left;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                <div>
                  <strong>Confirmation Link Sent!</strong><br/>
                  Supabase sent a confirmation email to <strong>${email}</strong>. Please confirm your email address, then return to sign in.
                </div>
              </div>
            `;
          }
          window.App.showToast(`Supabase confirmation email sent to ${email}`, 'info');
          return;
        }

        // Immediate session granted (e.g. Email Confirmations disabled in Supabase dashboard)
        if (data.session && data.user) {
          this.currentUser = this.formatSupabaseUser(data.user);
          localStorage.setItem(this.STORAGE_KEY_SESSION, JSON.stringify(this.currentUser));
          this.renderNavAuth();
          if (window.Cart && window.Cart.syncWithUser) window.Cart.syncWithUser();
          window.App.closeModal();
          window.App.showToast(`Account created for ${this.currentUser.name} on Supabase! Flat 40% OFF discount unlocked.`, 'success');
          return;
        }
      } catch (err) {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Create Account & Claim Flat 40% OFF';
        }
        console.error('Supabase sign-up exception:', err);
      }
    }

    // B. Fallback: Local database signup
    const existing = this.findUserByEmail(email);
    if (existing) {
      if (alertBox) {
        alertBox.innerHTML = `
          <div class="auth-error-banner" style="background: #FEF3C7; border-color: #FCD34D; color: #92400E;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            <span>An account with <strong>${email}</strong> already exists! <a href="javascript:void(0)" onclick="Auth.switchModalTab('signin', '${email}')" style="text-decoration: underline; color: #92400E; font-weight: 800;">Sign In here</a></span>
          </div>
        `;
      }
      return;
    }

    // Create and save new customer to local database
    const newUser = {
      id: "usr-" + Date.now(),
      name: name,
      email: email,
      password: password || "password123",
      city: city || "India",
      avatar: avatar,
      kalaPoints: 100,
      isFirstTime: true,
      memberSince: "September 2026",
      ordersCount: 0
    };

    this.saveUserToDatabase(newUser);
    this.currentUser = { ...newUser };
    localStorage.setItem(this.STORAGE_KEY_SESSION, JSON.stringify(this.currentUser));

    this.renderNavAuth();
    if (window.Cart && window.Cart.syncWithUser) window.Cart.syncWithUser();
    window.App.closeModal();
    window.App.showToast(`Account created for ${this.currentUser.name}! Flat 40% OFF discount unlocked.`, 'success');
  },

  async logout() {
    const sbClient = window.SupabaseConfig && window.SupabaseConfig.getClient();
    if (sbClient) {
      try {
        await sbClient.auth.signOut();
      } catch (e) {
        console.warn('Supabase signout warning:', e);
      }
    }

    this.currentUser = null;
    localStorage.removeItem(this.STORAGE_KEY_SESSION);
    this.renderNavAuth();
    if (window.Cart && window.Cart.syncWithUser) window.Cart.syncWithUser();
    window.App.showToast(`Signed out successfully. Come back soon!`, 'info');
  },

  showOrdersModal() {
    this.toggleDropdown();
    const modalContent = `
      <div style="padding: 30px; max-width: 580px; margin: 0 auto;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
          <img src="${this.currentUser.avatar}" style="width: 46px; height: 46px; border-radius: 50%; border: 2px solid var(--primary);" />
          <div>
            <h3 style="font-size: 1.4rem; margin: 0;">${this.currentUser.name}'s Heritage Orders</h3>
            <p style="font-size: 0.82rem; color: var(--text-muted); margin: 0;">${this.currentUser.city || 'India'} · Verified Conscious Buyer (${this.currentUser.memberSince || 'Member'})</p>
          </div>
        </div>

        <div style="background: #FDFBF8; border: 1px solid var(--border-subtle); border-radius: 12px; padding: 16px; margin-bottom: 18px;">
          <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 8px;">
            <span>Order <strong>#VIR-491024</strong> (Active Dispatch)</span>
            <span style="color: var(--forest-green); font-weight: 700;">In Transit via India Post</span>
          </div>
          <h4 style="font-size: 1.05rem; margin-bottom: 4px;">Handcrafted Madhubani Tree of Life Painting</h4>
          <p style="font-size: 0.78rem; color: var(--text-muted);">Mithila Artisan Collective, Bihar · Direct Fair Earning: ₹2,624</p>
        </div>

        <div style="background: var(--forest-green-light); border: 1px solid rgba(16, 123, 64, 0.2); border-radius: 12px; padding: 14px 16px; margin-bottom: 24px;">
          <h6 style="color: var(--forest-green); font-size: 0.85rem; font-weight: 700; margin-bottom: 4px;">🌿 Cumulative Social Impact</h6>
          <p style="font-size: 0.8rem; color: #0C4E28; margin: 0;">Your verified orders directly support marginalized artisan families with transparent direct bank disbursals.</p>
        </div>

        <button class="btn-primary-large" style="width: 100%;" onclick="window.App.closeModal()">
          Close
        </button>
      </div>
    `;

    window.App.openModal(modalContent);
  },

  // Supabase Configuration Settings Modal
  showSupabaseConfigModal() {
    const currentUrl = window.SupabaseConfig ? window.SupabaseConfig.getUrl() : '';
    const currentKey = window.SupabaseConfig ? window.SupabaseConfig.getAnonKey() : '';
    const isConfig = window.SupabaseConfig && window.SupabaseConfig.isConfigured();

    const configContent = `
      <div class="supabase-setup-modal">
        <div class="auth-modal-header" style="margin-bottom: 16px;">
          <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 8px;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 19.7778H10.6667L9.33333 22L21.3333 9.55556H13.3333L16 2H12Z" fill="#3ECF8E"/>
            </svg>
            <h3 style="margin: 0; font-size: 1.4rem;">Supabase Project Integration</h3>
          </div>
          <p style="font-size: 0.82rem; color: var(--text-muted); margin: 0;">
            Connect your live Supabase project for email & password authentication
          </p>
        </div>

        <div style="background: ${isConfig ? '#ECFDF5' : '#FFFBEB'}; border: 1px solid ${isConfig ? '#10B981' : '#F59E0B'}; border-radius: 8px; padding: 10px 14px; margin-bottom: 16px; font-size: 0.8rem; color: ${isConfig ? '#065F46' : '#92400E'};">
          ${isConfig ? '<strong>✓ Supabase Connected:</strong> Live project credentials active for email and password authentication.' : '<strong>Setup Guide:</strong> Enter your Supabase Project URL and Anon Public Key below (found in your Supabase Dashboard > Project Settings > API).'}
        </div>

        <form onsubmit="Auth.saveSupabaseSettings(event)">
          <div class="auth-form-group">
            <label>Supabase Project URL</label>
            <input type="url" id="sbInputUrl" class="auth-form-input" placeholder="https://your-project-id.supabase.co" required value="${currentUrl}" />
          </div>

          <div class="auth-form-group">
            <label>Supabase Anon Public Key</label>
            <input type="text" id="sbInputKey" class="auth-form-input" placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." required value="${currentKey}" />
          </div>

          <div style="display: flex; gap: 8px; margin-top: 16px;">
            <button type="submit" class="auth-submit-btn" style="flex: 2; margin-top: 0;">
              Save & Connect Supabase
            </button>
            <button type="button" class="btn-secondary-large" style="flex: 1; padding: 10px; font-size: 0.84rem;" onclick="Auth.clearSupabaseSettings()">
              Reset / Disconnect
            </button>
          </div>
        </form>

        <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--border-subtle); display: flex; justify-content: space-between; align-items: center;">
          <a href="https://supabase.com/dashboard" target="_blank" style="font-size: 0.78rem; color: var(--primary); text-decoration: underline; font-weight: 600;">
            Open Supabase Dashboard ↗
          </a>
          <button type="button" onclick="Auth.openAuthModal('signin')" style="background: none; border: none; font-size: 0.82rem; color: var(--text-muted); cursor: pointer; text-decoration: underline;">
            ← Back to Sign In
          </button>
        </div>
      </div>
    `;

    window.App.openModal(configContent);
  },

  saveSupabaseSettings(e) {
    e.preventDefault();
    const urlInput = document.getElementById('sbInputUrl');
    const keyInput = document.getElementById('sbInputKey');

    if (!urlInput || !keyInput) return;
    const url = urlInput.value.trim();
    const key = keyInput.value.trim();

    if (window.SupabaseConfig) {
      window.SupabaseConfig.saveCredentials(url, key);
      const client = window.SupabaseConfig.getClient();
      if (client) {
        window.App.showToast('Supabase credentials saved & connected!', 'success');
        this.openAuthModal('signin');
      } else {
        window.App.showToast('Could not initialize Supabase client. Please verify credentials.', 'error');
      }
    }
  },

  clearSupabaseSettings() {
    if (window.SupabaseConfig) {
      window.SupabaseConfig.clearCredentials();
      window.App.showToast('Supabase credentials cleared. Using local demo mode.', 'info');
      this.openAuthModal('signin');
    }
  },

  // Avatar Upload & Selection Handlers
  handleAvatarFileUpload(event, previewId, hiddenInputId) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      window.App.showToast('Please upload a valid image file (PNG, JPG, WebP).', 'error');
      return;
    }

    if (file.size > 3 * 1024 * 1024) {
      window.App.showToast('Image size exceeds 3MB. Please choose a smaller photo.', 'error');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target.result;
      const previewEl = document.getElementById(previewId);
      const hiddenInput = document.getElementById(hiddenInputId);

      if (previewEl) previewEl.src = dataUrl;
      if (hiddenInput) hiddenInput.value = dataUrl;

      // Deactivate presets if any
      document.querySelectorAll('.avatar-preset-btn').forEach(btn => btn.classList.remove('active'));
      window.App.showToast('Profile photo ready!', 'success');
    };
    reader.readAsDataURL(file);
  },

  selectPresetAvatar(url, previewId, hiddenInputId, clickedBtn) {
    const previewEl = document.getElementById(previewId);
    const hiddenInput = document.getElementById(hiddenInputId);

    if (previewEl) previewEl.src = url;
    if (hiddenInput) hiddenInput.value = url;

    document.querySelectorAll('.avatar-preset-btn').forEach(btn => btn.classList.remove('active'));
    if (clickedBtn) clickedBtn.classList.add('active');
  },

  showProfilePhotoModal() {
    this.toggleDropdown();
    if (!this.currentUser) return;

    const currentAvatar = this.currentUser.avatar || "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80";

    const modalContent = `
      <div class="profile-modal-wrap">
        <div class="auth-modal-header" style="margin-bottom: 20px;">
          <h3 style="font-size: 1.4rem; margin-bottom: 4px;">Update Profile Photo</h3>
          <p style="font-size: 0.84rem; color: var(--text-muted); margin: 0;">
            Personalize your conscious customer presence on KalaConnect AI
          </p>
        </div>

        <div class="profile-avatar-large-wrap">
          <div style="position: relative; display: inline-block;">
            <img src="${currentAvatar}" id="profileModalAvatarPreview" class="profile-avatar-large" alt="${this.currentUser.name}" />
            <label for="profileModalAvatarInput" class="avatar-upload-badge" style="width: 30px; height: 30px; bottom: 12px; right: 4px;" title="Upload new photo">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"></path></svg>
            </label>
          </div>
          <h5 style="margin: 0; font-size: 1.1rem;">${this.currentUser.name}</h5>
          <span style="font-size: 0.78rem; color: var(--text-muted);">${this.currentUser.city || 'India'}</span>
        </div>

        <div class="avatar-section-wrap" style="text-align: center; margin-bottom: 20px;">
          <input type="file" id="profileModalAvatarInput" class="file-input-hidden" accept="image/*" onchange="Auth.handleAvatarFileUpload(event, 'profileModalAvatarPreview', 'profileModalAvatarValue')" />
          <label for="profileModalAvatarInput" class="btn-upload-avatar" style="font-size: 0.84rem; padding: 8px 16px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
            Upload From Device
          </label>

          <div style="margin-top: 14px;">
            <span style="font-size: 0.76rem; color: var(--text-muted); font-weight: 600; display: block; margin-bottom: 8px;">Or choose a cultural craft avatar:</span>
            <div class="avatar-presets-grid" style="justify-content: center;">
              <button type="button" class="avatar-preset-btn" onclick="Auth.selectPresetAvatar('https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80', 'profileModalAvatarPreview', 'profileModalAvatarValue', this)" title="Jaipur Royal">
                <img src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&auto=format&fit=crop&q=80" alt="Preset 1" />
              </button>
              <button type="button" class="avatar-preset-btn" onclick="Auth.selectPresetAvatar('https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80', 'profileModalAvatarPreview', 'profileModalAvatarValue', this)" title="Mithila Lover">
                <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&auto=format&fit=crop&q=80" alt="Preset 2" />
              </button>
              <button type="button" class="avatar-preset-btn" onclick="Auth.selectPresetAvatar('https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80', 'profileModalAvatarPreview', 'profileModalAvatarValue', this)" title="Craft Explorer">
                <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&auto=format&fit=crop&q=80" alt="Preset 3" />
              </button>
              <button type="button" class="avatar-preset-btn" onclick="Auth.selectPresetAvatar('https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80', 'profileModalAvatarPreview', 'profileModalAvatarValue', this)" title="Heritage Patron">
                <img src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=80&auto=format&fit=crop&q=80" alt="Preset 4" />
              </button>
            </div>
          </div>

          <input type="hidden" id="profileModalAvatarValue" value="${currentAvatar}" />
        </div>

        <div style="display: flex; gap: 10px;">
          <button type="button" class="auth-submit-btn" style="flex: 2; margin-top: 0;" onclick="Auth.saveUpdatedProfilePhoto()">
            Save Profile Photo
          </button>
          <button type="button" class="btn-secondary-large" style="flex: 1; padding: 10px; font-size: 0.85rem;" onclick="window.App.closeModal()">
            Cancel
          </button>
        </div>
      </div>
    `;

    window.App.openModal(modalContent);
  },

  async saveUpdatedProfilePhoto() {
    const inputVal = document.getElementById('profileModalAvatarValue');
    const newAvatar = inputVal ? inputVal.value : '';

    if (!newAvatar || !this.currentUser) return;

    this.currentUser.avatar = newAvatar;
    localStorage.setItem(this.STORAGE_KEY_SESSION, JSON.stringify(this.currentUser));
    this.updateUserInDatabase(this.currentUser);

    // Update in Supabase user metadata if logged in with Supabase
    const sbClient = window.SupabaseConfig && window.SupabaseConfig.getClient();
    if (sbClient) {
      try {
        await sbClient.auth.updateUser({
          data: { avatar_url: newAvatar }
        });
      } catch (e) {
        console.warn('Supabase avatar update note:', e);
      }
    }

    this.renderNavAuth();
    window.App.closeModal();
    window.App.showToast('Profile photo updated successfully!', 'success');
  }
};

window.Auth = Auth;
