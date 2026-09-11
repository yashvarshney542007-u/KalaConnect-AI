# Member 5 Team Integration & API Specification Guide

**Project Title:** AI-Driven Market Linkage and Smart Cataloging Mobile/Web Application for Marginalized Artisans  
**Role:** Member 5  
**Primary Ownership:** Customer Marketplace  
**Secondary Responsibility:** AI Space Recommendation  

---

## 1. Overview of Member 5 Deliverables

Member 5 delivers the customer-facing interface and recommendation intelligence where buyers discover, visualize, and purchase artisan crafts:

1. **Customer Marketplace (`index.html`, `js/marketplace.js`, `css/marketplace.css`)**:
   - Cultural heritage discovery catalog with search and multi-filtering (by category, region, room suitability, and price).
   - Detailed Artisan Story Modal with GI Tag authenticity and transparency breakdown.
   - Interactive Cart, Artisan Welfare Fund toggle, and simulated checkout flow (`js/cart.js`, `css/cart.css`).
2. **AI Space Recommendation Studio (`js/space_ai.js`, `css/space_ai.css`)**:
   - **Mode 1 (Smart Space Stylist):** Algorithmic room match score, palette harmony, and placement advice.
   - **Mode 2 (Room Visualizer & "Place on Wall" Canvas):** Interactive drag, scale, and preview canvas on preset or user-uploaded room photos.

---

## 2. API Contract with Member 1 (Django Backend + DB + Auth)

Currently, the marketplace uses mock data in `js/products.js`. When Member 1's Django REST Framework (DRF) backend is ready, replace local data with these API endpoints:

### A. User Authentication APIs (Member 1 Collaboration)
* **Login Endpoint:** `POST /api/v1/auth/login/`
  * Body: `{"email": "priya.sharma@example.com", "password": "..."}`
  * Success Response (`200 OK` - Old/Registered Customer):
    `{"token": "jwt-token-string", "user": {"id": "usr-1", "name": "Priya Sharma", "email": "...", "avatar_url": "...", "city": "Mumbai", "kala_points": 240, "is_first_time": false, "orders_count": 2}}`
  * Unregistered User Response (`404 Not Found` - New Customer attempting Sign In):
    `{"status": 404, "error": "CUSTOMER_NOT_FOUND", "message": "No registered customer found with this email"}`
    *Frontend Behavior:* Triggers the dedicated **"No Customer Account Found" screen**, pre-fills their email, and guides them to register and claim their Flat 40% First-Time Buyer Discount.
* **Registration Endpoint:** `POST /api/v1/auth/register/`
  * Body: `{"name": "Aditi Rao", "email": "aditi@example.com", "password": "...", "city": "Jaipur"}`
  * Response: `{"token": "jwt-token-string", "user": {"id": "usr-new", "name": "Aditi Rao", "is_first_time": true, "orders_count": 0, "kala_points": 100}}`
* **Current User Session:** `GET /api/v1/auth/me/` (Headers: `Authorization: Bearer <jwt-token>`)

### B. Fetch Marketplace Products
* **Endpoint:** `GET /api/v1/products/`
* **Query Parameters:** `?category=pottery&region=Rajasthan&room=living_room&search=vase`
* **Response Schema:**
```json
[
  {
    "id": "art-101",
    "name": "Handcrafted Madhubani Tree of Life Painting",
    "category": "Paintings & Folk Art",
    "craft_form": "Madhubani (Mithila)",
    "region": "Jitwarpur, Bihar",
    "price": 3200,
    "market_estimate": 5800,
    "artisan_share_percent": 82,
    "gi_certified": true,
    "rating": 4.9,
    "review_count": 47,
    "image_url": "https://...",
    "dimensions": "18 x 24 inches (Framed)",
    "materials": "Handmade Lokta Paper, Natural Vegetable Pigments",
    "description": "...",
    "artisan": {
      "id": "artisan-44",
      "name": "Sita Devi",
      "community": "Mithila Women Artisan Collective",
      "experience": "24 years",
      "village": "Jitwarpur, Bihar",
      "avatar_url": "https://...",
      "story": "..."
    },
    "space_compatibility": {
      "rooms": ["living_room", "foyer", "study_desk"],
      "styles": ["earthy_rustic", "royal_heritage"],
      "dominant_colors": ["#D97736", "#2D4059"],
      "placement_suggestion": "Statement centerpiece on living room wall."
    }
  }
]
```

### B. Submit Customer Order
* **Endpoint:** `POST /api/v1/orders/`
* **Request Body:**
```json
{
  "customer_name": "Priya Sharma",
  "email": "priya@example.com",
  "phone": "+91 9876543210",
  "shipping_address": "Flat 402, Green Glen Layout, Bengaluru, Karnataka",
  "welfare_contribution": true,
  "welfare_amount": 50,
  "items": [
    {
      "product_id": "art-101",
      "quantity": 1,
      "unit_price": 3200
    }
  ],
  "total_amount": 3250
}
```
* **Response:**
```json
{
  "status": "success",
  "order_id": "VIR-491024",
  "artisan_payout_amount": 2624,
  "estimated_delivery": "2026-09-18"
}
```

### C. AI Space Match Backend API (Optional Server-Side Engine)
* **Endpoint:** `POST /api/v1/ai/space-recommend/`
* **Payload:**
```json
{
  "room_type": "living_room",
  "aesthetic_style": "earthy_rustic",
  "accent_color": "#C85A32"
}
```
* **Response:** Top 4 matching products with harmony scores and styling rationale.

---

## 3. Collaboration with Member 2 (Artisan Frontend)
* Ensure Member 2's craft listing form asks the artisan for:
  - Craft form & Region
  - Dimensions & Materials
  - Recommended room or placement (e.g., Tabletop, Wall Hanging, Floor Accent)

---

## 4. Collaboration with Member 3 (Image AI & Voice AI)
* Member 3's AI attribute extraction pipeline can automatically populate:
  - `dominant_colors` extracted from craft photos
  - `room_compatibility` tags inferred by image classification / Gemini Vision
  - Transcribed artisan audio stories into the `artisan.story` field.

---

## 5. Collaboration with Member 4 (Price Prediction ML)
* Member 4 supplies:
  - `market_estimate`: Traditional retail estimate calculated by ML
  - `artisan_share_percent`: Fair direct share percentage (e.g. 82%)
  - Member 5 renders the "Fair Price Transparency Guarantee" badge on the product card and modal.

---

## 6. Collaboration with Member 6 (Admin Dashboard & QA)
* Member 6's Admin Dashboard can track:
  - Total items added to cart & checkout completion rate from Member 5
  - Most viewed crafts in the AI Space Visualizer
  - Direct money disbursed to rural artisans.
