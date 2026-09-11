/**
 * KalaConnect AI - Artisan Catalog Dataset
 * Curated for marginalized Indian artisans across all 28 States & 8 Union Territories
 * Includes heritage metadata, fair pricing breakdowns (Member 4), and room/space compatibility tags (Member 5).
 */

const ALL_INDIAN_STATES_AND_UTS = {
  states: [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal"
  ],
  unionTerritories: [
    "Andaman and Nicobar", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
  ]
};

const ARTISAN_PRODUCTS = [
  // 1. BIHAR
  {
    id: "art-101",
    name: "Handcrafted Madhubani Tree of Life Painting",
    category: "Paintings & Folk Art",
    craftForm: "Madhubani (Mithila)",
    state: "Bihar",
    isUT: false,
    region: "Jitwarpur, Madhubani, Bihar",
    price: 3200,
    marketEstimate: 5800,
    artisanSharePercent: 82,
    giCertified: true,
    rating: 4.9,
    reviewCount: 47,
    image: "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=800&auto=format&fit=crop&q=80",
    dimensions: "18 x 24 inches (Framed)",
    materials: "Handmade Lokta Paper, Natural Vegetable Pigments, Twig Nib",
    description: "Intricately detailed Madhubani folk painting depicting the sacred Kalpavriksha (Tree of Life) surrounded by birds and fish, symbolizing fertility and harmony with nature.",
    artisan: {
      name: "Sita Devi & Geeta Kumari",
      community: "Mithila Women Artisan Collective",
      experience: "24 years",
      village: "Jitwarpur, Madhubani, Bihar",
      avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&auto=format&fit=crop&q=80",
      story: "Sita Devi learned ritual wall-painting from her grandmother. Today, her collective trains 18 young rural women, securing financial independence."
    },
    spaceCompatibility: {
      rooms: ["living_room", "foyer", "study_desk", "dining_pooja"],
      styles: ["earthy_rustic", "royal_heritage", "bohemian"],
      dominantColors: ["#D97736", "#2D4059", "#F7B731"],
      lightingVibe: "Warm ambient or accent spotlight",
      placementSuggestion: "Statement centerpiece on neutral living room wall or entry foyer."
    }
  },

  // 2. RAJASTHAN
  {
    id: "art-102",
    name: "Jaipur Hand-Turned Blue Pottery Floral Vase",
    category: "Pottery & Ceramics",
    craftForm: "Blue Pottery",
    state: "Rajasthan",
    isUT: false,
    region: "Kot Jewar, Jaipur, Rajasthan",
    price: 1850,
    marketEstimate: 3400,
    artisanSharePercent: 79,
    giCertified: true,
    rating: 4.8,
    reviewCount: 38,
    image: "https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?w=800&auto=format&fit=crop&q=80",
    dimensions: "10 inches H x 5 inches W",
    materials: "Quartz Stone Powder, Fullers Earth, Cobalt Blue Glaze (Clay-free)",
    description: "Authentic Jaipur Blue Pottery vase crafted without clay, fired at low temperatures with an iconic cobalt blue and turquoise hand-painted Mughal motif.",
    artisan: {
      name: "Kailash Chand Kumhar",
      community: "Kripal Blue Pottery Guild",
      experience: "31 years",
      village: "Kot Jewar, Jaipur, Rajasthan",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80",
      story: "A 4th-generation master potter preserving the Persian-origin quartz craft revival."
    },
    spaceCompatibility: {
      rooms: ["living_room", "dining_pooja", "study_desk", "bedroom"],
      styles: ["minimalist", "royal_heritage", "bohemian"],
      dominantColors: ["#1B4965", "#62B6CB", "#F4F1DE"],
      lightingVibe: "Natural daylight or soft warm lamp",
      placementSuggestion: "Place on light-wood coffee table or sunlit window shelf with dry botanicals."
    }
  },

  // 3. CHHATTISGARH
  {
    id: "art-103",
    name: "Bastar Dhokra Lost-Wax Bell Metal Elephant Figurine",
    category: "Metalcraft & Brass",
    craftForm: "Dhokra Lost-Wax Casting",
    state: "Chhattisgarh",
    isUT: false,
    region: "Kondagaon, Bastar, Chhattisgarh",
    price: 2600,
    marketEstimate: 4900,
    artisanSharePercent: 84,
    giCertified: true,
    rating: 4.95,
    reviewCount: 62,
    image: "https://images.unsplash.com/photo-1567653418876-5bb0e566e1c2?w=800&auto=format&fit=crop&q=80",
    dimensions: "7 x 6 x 3.5 inches",
    materials: "Recycled Brass, Beeswax, Clay Mold, River Sand",
    description: "Cast using a 4,000-year-old non-ferrous lost-wax metal casting technique dating back to Mohenjo-daro. Every casting requires breaking the earthen mold.",
    artisan: {
      name: "Ghasiram Ghadwa",
      community: "Ghadwa Tribal Metal Smiths",
      experience: "28 years",
      village: "Kondagaon, Bastar, Chhattisgarh",
      avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80",
      story: "Ghasiram and his tribal kin preserve indigenous metallurgical secrets passed down orally for millennia."
    },
    spaceCompatibility: {
      rooms: ["living_room", "study_desk", "foyer", "bedroom"],
      styles: ["earthy_rustic", "minimalist", "royal_heritage"],
      dominantColors: ["#B8860B", "#4A3E3D", "#D4AF37"],
      lightingVibe: "Warm accent spotlight",
      placementSuggestion: "Bookshelf, dark oak study desk, or console table beside warm lighting."
    }
  },

  // 4. KARNATAKA
  {
    id: "art-104",
    name: "Channapatna Lacquered Wooden Stacking Toy & Bird",
    category: "Woodcraft & Toys",
    craftForm: "Channapatna Wooden Craft",
    state: "Karnataka",
    isUT: false,
    region: "Channapatna, Ramanagara, Karnataka",
    price: 1100,
    marketEstimate: 2100,
    artisanSharePercent: 80,
    giCertified: true,
    rating: 4.7,
    reviewCount: 29,
    image: "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=800&auto=format&fit=crop&q=80",
    dimensions: "8 inches H x 4 inches Base",
    materials: "Ivory Wood (Wrightia Tinctoria), Natural Vegetable Dyes",
    description: "Handcrafted in the 'Toy Town of India' on traditional lathes, buffed with non-toxic natural lac made with turmeric and indigo pigments.",
    artisan: {
      name: "Syed Noorulla",
      community: "Channapatna Toy Artisans Welfare Trust",
      experience: "19 years",
      village: "Channapatna, Karnataka",
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&auto=format&fit=crop&q=80",
      story: "Syed creates eco-friendly wooden toys, keeping traditional craftsmanship vibrant for modern nurseries."
    },
    spaceCompatibility: {
      rooms: ["bedroom", "study_desk", "living_room"],
      styles: ["minimalist", "bohemian"],
      dominantColors: ["#E63946", "#F1FAEE", "#A8DADC"],
      lightingVibe: "Bright natural light",
      placementSuggestion: "Kids room bookshelf, floating display shelf, or cheerful study desk."
    }
  },

  // 5. GUJARAT
  {
    id: "art-105",
    name: "Kutch Rogan Hand-Painted Silk Wall Tapestry",
    category: "Paintings & Folk Art",
    craftForm: "Rogan Art",
    state: "Gujarat",
    isUT: false,
    region: "Nirona, Kutch, Gujarat",
    price: 4800,
    marketEstimate: 9200,
    artisanSharePercent: 86,
    giCertified: true,
    rating: 5.0,
    reviewCount: 33,
    image: "https://images.unsplash.com/photo-1582561424760-0321d75e81fa?w=800&auto=format&fit=crop&q=80",
    dimensions: "20 x 20 inches (Silk Mounted)",
    materials: "Boiled Castor Oil Paste, Natural Earth Pigments, Raw Silk",
    description: "An ultra-rare craft practiced in Nirona. Boiled castor oil paste is blended with pigments and drawn onto cloth using a metal stylus without touching the fabric.",
    artisan: {
      name: "Rizwan Khatri",
      community: "Khatri Rogan Heritage",
      experience: "17 years",
      village: "Nirona, Kutch, Gujarat",
      avatar: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&auto=format&fit=crop&q=80",
      story: "Preserving an art form once on the brink of extinction, now empowering apprentice craftswomen."
    },
    spaceCompatibility: {
      rooms: ["living_room", "foyer", "dining_pooja"],
      styles: ["royal_heritage", "earthy_rustic"],
      dominantColors: ["#C84B31", "#D9B48F", "#2D4263"],
      lightingVibe: "Warm museum spotlight",
      placementSuggestion: "Feature wall above headboard or main dining room wall."
    }
  },

  // 6. UTTAR PRADESH
  {
    id: "art-106",
    name: "Terracotta Relief Wall Hanging - Dancing Deities",
    category: "Pottery & Ceramics",
    craftForm: "Gorakhpur Terracotta",
    state: "Uttar Pradesh",
    isUT: false,
    region: "Gorakhpur, Uttar Pradesh",
    price: 1500,
    marketEstimate: 2900,
    artisanSharePercent: 78,
    giCertified: true,
    rating: 4.8,
    reviewCount: 51,
    image: "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=800&auto=format&fit=crop&q=80",
    dimensions: "12 x 12 inches",
    materials: "Alluvial Clay, Rice Husk, Wood Kiln Fired",
    description: "Sun-dried and wood-fired terracotta relief tile with folk figures, crafted with alluvial clay cured in indigenous village earthen kilns.",
    artisan: {
      name: "Ram Kumar Prajapati",
      community: "Gramin Mitti Shilp Sangh",
      experience: "26 years",
      village: "Aurangabad, Gorakhpur, UP",
      avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80",
      story: "Ram Kumar leads a village potter cooperative that turns traditional clay work into modern home decor."
    },
    spaceCompatibility: {
      rooms: ["balcony", "foyer", "living_room", "dining_pooja"],
      styles: ["earthy_rustic", "bohemian"],
      dominantColors: ["#A0522D", "#CD853F", "#F5DEB3"],
      lightingVibe: "Natural sunlight or terrace lantern",
      placementSuggestion: "Veranda wall, garden nook, or foyer accent wall paired with greens."
    }
  },

  // 7. JAMMU AND KASHMIR (UT)
  {
    id: "art-107",
    name: "Kashmir Hand-Carved Walnut Wood Dry Fruit Box",
    category: "Woodcraft & Toys",
    craftForm: "Kashmiri Walnut Wood Carving",
    state: "Jammu and Kashmir",
    isUT: true,
    region: "Rainawari, Srinagar, Jammu and Kashmir",
    price: 3400,
    marketEstimate: 6500,
    artisanSharePercent: 81,
    giCertified: true,
    rating: 4.9,
    reviewCount: 42,
    image: "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=800&auto=format&fit=crop&q=80",
    dimensions: "9 x 6 x 4 inches (Velvet Lined)",
    materials: "Seasoned Himalayan Walnut Wood, Organic Wax Polish",
    description: "Chiselled from mature walnut tree roots with Kashmiri chinar leaf and vine lattice work made entirely by hand.",
    artisan: {
      name: "Ghulam Mohammad Mir",
      community: "Kashmir Crafts Guild",
      experience: "35 years",
      village: "Rainawari, Srinagar, J&K",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80",
      story: "Master woodworker who preserves heritage fretwork techniques passed down across 3 centuries."
    },
    spaceCompatibility: {
      rooms: ["living_room", "dining_pooja", "bedroom", "study_desk"],
      styles: ["royal_heritage", "minimalist"],
      dominantColors: ["#5C4033", "#8B5A2B", "#D2B48C"],
      lightingVibe: "Soft warm table lamp",
      placementSuggestion: "Center of dark dining table or living room glass coffee table."
    }
  },

  // 8. ODISHA
  {
    id: "art-108",
    name: "Sambalpuri Ikat Handwoven Cotton Throw & Cushion Set",
    category: "Handloom & Textiles",
    craftForm: "Sambalpuri Ikat",
    state: "Odisha",
    isUT: false,
    region: "Barpali, Bargarh, Odisha",
    price: 2200,
    marketEstimate: 4100,
    artisanSharePercent: 85,
    giCertified: true,
    rating: 4.85,
    reviewCount: 39,
    image: "https://images.unsplash.com/photo-1606744837616-56c9a5c6a6eb?w=800&auto=format&fit=crop&q=80",
    dimensions: "Throw: 60 x 50 inches, 2 Cushions: 16 x 16 inches",
    materials: "100% Organic Cotton Yarn, Eco-friendly Reactive Dyes",
    description: "Woven on village pit looms using Bandhakala (tie-and-dye) precision weaving with sacred conch and fish tribal motifs.",
    artisan: {
      name: "Meenakshi Meher",
      community: "Bargarh Weavers Cooperative",
      experience: "21 years",
      village: "Barpali, Bargarh, Odisha",
      avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&auto=format&fit=crop&q=80",
      story: "Meenakshi weaves on pit looms in her mud house; direct market linkage has doubled her family income."
    },
    spaceCompatibility: {
      rooms: ["living_room", "bedroom", "balcony"],
      styles: ["bohemian", "minimalist", "earthy_rustic"],
      dominantColors: ["#8B0000", "#FFD700", "#1A1A1D"],
      lightingVibe: "Natural airy sunlight",
      placementSuggestion: "Draped over a neutral beige sofa or armchair with matching textured cushions."
    }
  },

  // 9. WEST BENGAL
  {
    id: "art-109",
    name: "Bankura Panchmura Sacred Terracotta Horse Sculpture",
    category: "Pottery & Ceramics",
    craftForm: "Bankura Terracotta Craft",
    state: "West Bengal",
    isUT: false,
    region: "Panchmura, Bankura, West Bengal",
    price: 1950,
    marketEstimate: 3800,
    artisanSharePercent: 83,
    giCertified: true,
    rating: 4.92,
    reviewCount: 44,
    image: "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?w=800&auto=format&fit=crop&q=80",
    dimensions: "16 inches H x 7 inches W",
    materials: "Local Alluvial Riverbed Clay, Wood Fired Kiln",
    description: "The renowned Bankura horse with erect ears and elongated neck, standing as the official symbol of Indian handicrafts. Hand-thrown on the potter's wheel in separate sections and assembled.",
    artisan: {
      name: "Bikash Kumbhakar",
      community: "Panchmura Shilpi Samity",
      experience: "27 years",
      village: "Panchmura, Bankura, West Bengal",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80",
      story: "Bikash crafts these iconic folk figures from locally dug river clay, maintaining ancient tribal aesthetic symmetry."
    },
    spaceCompatibility: {
      rooms: ["living_room", "foyer", "study_desk"],
      styles: ["earthy_rustic", "minimalist", "royal_heritage"],
      dominantColors: ["#A0522D", "#8B4513", "#F5DEB3"],
      lightingVibe: "Warm ambient glow",
      placementSuggestion: "Floor stand beside entryway or console table accent piece."
    }
  },

  // 10. ASSAM
  {
    id: "art-110",
    name: "Assam Golden Muga Silk & Bamboo Wall Scroll",
    category: "Handloom & Textiles",
    craftForm: "Muga Silk Weaving & Bamboo Craft",
    state: "Assam",
    isUT: false,
    region: "Sualkuchi, Kamrup, Assam",
    price: 3600,
    marketEstimate: 7200,
    artisanSharePercent: 86,
    giCertified: true,
    rating: 4.95,
    reviewCount: 31,
    image: "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800&auto=format&fit=crop&q=80",
    dimensions: "36 x 14 inches",
    materials: "Pure Wild Muga Golden Silk, River Reed Bamboo, Natural Lac",
    description: "Woven in Sualkuchi, the 'Manchester of Assam', using rare golden Muga silk known for durability and natural golden luster that increases with every wash.",
    artisan: {
      name: "Pabitra Das & Jonali",
      community: "Brahmaputra Weavers Trust",
      experience: "22 years",
      village: "Sualkuchi, Kamrup, Assam",
      avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&auto=format&fit=crop&q=80",
      story: "Pabitra preserves organic cocoon rearing in the Brahmaputra valley, weaving heirlooms with zero synthetic treatments."
    },
    spaceCompatibility: {
      rooms: ["living_room", "bedroom", "study_desk"],
      styles: ["minimalist", "royal_heritage"],
      dominantColors: ["#D4AF37", "#8B5A2B", "#FDF5E6"],
      lightingVibe: "Natural morning light",
      placementSuggestion: "Vertical wall accent between tall windows or beside dining area."
    }
  },

  // 11. TAMIL NADU
  {
    id: "art-111",
    name: "Thanjavur Sacred 22K Gold Foil Painting",
    category: "Paintings & Folk Art",
    craftForm: "Tanjore Painting",
    state: "Tamil Nadu",
    isUT: false,
    region: "Thanjavur, Tamil Nadu",
    price: 6200,
    marketEstimate: 12000,
    artisanSharePercent: 88,
    giCertified: true,
    rating: 5.0,
    reviewCount: 58,
    image: "https://images.unsplash.com/photo-1582561424760-0321d75e81fa?w=800&auto=format&fit=crop&q=80",
    dimensions: "16 x 20 inches (Teak Framed)",
    materials: "Pure 22-Karat Gold Leaf, Semi-Precious Jaipur Stones, Teak Wood Board",
    description: "Classical South Indian painting characterized by rich, flat colors, embossed gesso work, and glittering 22K gold foil with semi-precious stone embellishments.",
    artisan: {
      name: "Murugesan Sthapathi",
      community: "Chola Traditional Arts Guild",
      experience: "33 years",
      village: "Thanjavur, Tamil Nadu",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80",
      story: "Trained under temple sthapatis, Murugesan uses centuries-old gesso formulas made of chalk powder and Arabic gum."
    },
    spaceCompatibility: {
      rooms: ["dining_pooja", "living_room", "foyer"],
      styles: ["royal_heritage"],
      dominantColors: ["#D4AF37", "#8B0000", "#1A1A1A"],
      lightingVibe: "Dedicated warm golden picture spotlight",
      placementSuggestion: "Pooja room altar backdrop or living room royal heritage focal wall."
    }
  },

  // 12. TELANGANA
  {
    id: "art-112",
    name: "Cheriyal Folk Painting Wall Mask & Scroll Plaque",
    category: "Paintings & Folk Art",
    craftForm: "Cheriyal Scroll Art",
    state: "Telangana",
    isUT: false,
    region: "Cheriyal, Siddipet, Telangana",
    price: 2400,
    marketEstimate: 4600,
    artisanSharePercent: 82,
    giCertified: true,
    rating: 4.88,
    reviewCount: 36,
    image: "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=800&auto=format&fit=crop&q=80",
    dimensions: "14 x 9 x 4 inches",
    materials: "Tamarind Seed Paste, Sawdust Mold, Natural Vegetable Dyes",
    description: "Folk storytellers' art form unique to Telangana. Hand-molded masks made of tamarind paste and sawdust, painted with vibrant primary colors portraying rural folklore.",
    artisan: {
      name: "D. Vaikuntam Nakash",
      community: "Nakashi Artisan Family",
      experience: "30 years",
      village: "Cheriyal, Siddipet, Telangana",
      avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80",
      story: "One of only three surviving master Nakash families keeping the 500-year-old Cheriyal scroll narrative tradition alive."
    },
    spaceCompatibility: {
      rooms: ["living_room", "foyer", "study_desk"],
      styles: ["bohemian", "earthy_rustic"],
      dominantColors: ["#DC143C", "#FFD700", "#000080"],
      lightingVibe: "Warm ambient wall wash",
      placementSuggestion: "Gallery wall cluster or entrance foyer accent art."
    }
  },

  // 13. KERALA
  {
    id: "art-113",
    name: "Aranmula Metal Mirror & Brass Nilavilakku Oil Lamp",
    category: "Metalcraft & Brass",
    craftForm: "Aranmula Kannadi & Bell Metal",
    state: "Kerala",
    isUT: false,
    region: "Aranmula, Pathanamthitta, Kerala",
    price: 4900,
    marketEstimate: 9800,
    artisanSharePercent: 87,
    giCertified: true,
    rating: 4.96,
    reviewCount: 50,
    image: "https://images.unsplash.com/photo-1567653418876-5bb0e566e1c2?w=800&auto=format&fit=crop&q=80",
    dimensions: "12 inches H x 5 inches W",
    materials: "Copper-Tin Speculum Alloy, Pure Brass Casing",
    description: "A front-surface reflection mirror made from a secret alloy of copper and tin—unlike standard glass mirrors, it eliminates secondary reflections and refractive distortions.",
    artisan: {
      name: "A. G. Gopakumar",
      community: "Aranmula Viswakarma Guild",
      experience: "25 years",
      village: "Aranmula, Pathanamthitta, Kerala",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80",
      story: "Custodians of a metallurgical wonder known to only a single family guild in Aranmula."
    },
    spaceCompatibility: {
      rooms: ["living_room", "dining_pooja", "foyer"],
      styles: ["royal_heritage", "minimalist"],
      dominantColors: ["#D4AF37", "#C5A059", "#2F2B26"],
      lightingVibe: "Warm candlelight or soft spotlight",
      placementSuggestion: "Sacred prayer altar or royal entryway vanity credenza."
    }
  },

  // 14. MAHARASHTRA
  {
    id: "art-114",
    name: "Palghar Warli Tribal Canvas Art - Tarpa Dance",
    category: "Paintings & Folk Art",
    craftForm: "Warli Painting",
    state: "Maharashtra",
    isUT: false,
    region: "Dahanu, Palghar, Maharashtra",
    price: 1750,
    marketEstimate: 3500,
    artisanSharePercent: 82,
    giCertified: true,
    rating: 4.87,
    reviewCount: 65,
    image: "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=800&auto=format&fit=crop&q=80",
    dimensions: "16 x 20 inches",
    materials: "Handmade Cow Dung & Mud Canvas, Rice Flour White Paste, Bamboo Nib",
    description: "Geometric tribal art expressing harmony with nature through basic geometric shapes: circle (sun/moon), triangle (mountains/trees), and square (sacred enclosure).",
    artisan: {
      name: "Anil Wangad",
      community: "Warli Tribal Adivasi Sangha",
      experience: "20 years",
      village: "Ganjad, Dahanu, Maharashtra",
      avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80",
      story: "Anil uses organic rice paste to tell contemporary tribal stories while honoring ritual art traditions."
    },
    spaceCompatibility: {
      rooms: ["living_room", "study_desk", "bedroom"],
      styles: ["earthy_rustic", "minimalist", "bohemian"],
      dominantColors: ["#8B4513", "#FFFFFF", "#3E2723"],
      lightingVibe: "Natural daylight",
      placementSuggestion: "Living room study nook, minimalist hallway, or above sofa."
    }
  },

  // 15. MADHYA PRADESH
  {
    id: "art-115",
    name: "Dindori Gond Tribal Painting - Forest Deer & Bird",
    category: "Paintings & Folk Art",
    craftForm: "Gond Art",
    state: "Madhya Pradesh",
    isUT: false,
    region: "Patangarh, Dindori, Madhya Pradesh",
    price: 2800,
    marketEstimate: 5400,
    artisanSharePercent: 84,
    giCertified: true,
    rating: 4.93,
    reviewCount: 41,
    image: "https://images.unsplash.com/photo-1582561424760-0321d75e81fa?w=800&auto=format&fit=crop&q=80",
    dimensions: "18 x 24 inches (Framed)",
    materials: "Handmade Canvas, Natural Mineral & Charcoal Pigments, Ink Fine Nib",
    description: "Created by the Pardhan Gond tribal community, renowned for intricate dots, dashes, and fine lines that breathe motion into forest folklore.",
    artisan: {
      name: "Roshni Shyam",
      community: "Patangarh Gond Artists Cooperative",
      experience: "16 years",
      village: "Patangarh, Dindori, Madhya Pradesh",
      avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&auto=format&fit=crop&q=80",
      story: "Roshni's family carries forward Jangarh Singh Shyam's celebrated Gond art style to international acclaim."
    },
    spaceCompatibility: {
      rooms: ["living_room", "bedroom", "study_desk"],
      styles: ["bohemian", "earthy_rustic"],
      dominantColors: ["#2E8B57", "#FFA500", "#4B0082"],
      lightingVibe: "Soft warm spotlight",
      placementSuggestion: "Living room accent wall or master bedroom serene art feature."
    }
  },

  // 16. ANDHRA PRADESH
  {
    id: "art-116",
    name: "Srikalahasti Hand-Painted Tree of Life Kalamkari Tapestry",
    category: "Handloom & Textiles",
    craftForm: "Kalamkari (Srikalahasti Style)",
    state: "Andhra Pradesh",
    isUT: false,
    region: "Srikalahasti, Tirupati, Andhra Pradesh",
    price: 3800,
    marketEstimate: 7400,
    artisanSharePercent: 85,
    giCertified: true,
    rating: 4.91,
    reviewCount: 37,
    image: "https://images.unsplash.com/photo-1606744837616-56c9a5c6a6eb?w=800&auto=format&fit=crop&q=80",
    dimensions: "40 x 30 inches",
    materials: "100% Cotton Milled Fabric, Bamboo Kalam Pen, Cow Milk & Myrobalan Curing",
    description: "Completely hand-drawn with bamboo pens and processed through 17 rigorous organic steps using river water, alum, and fermented jaggery.",
    artisan: {
      name: "K. Mohan Rao",
      community: "Srikalahasti Kalamkari Guild",
      experience: "29 years",
      village: "Srikalahasti, Andhra Pradesh",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80",
      story: "Mohan continues the pen-drawn tradition of temple hangings, resisting synthetic screen-printed duplicates."
    },
    spaceCompatibility: {
      rooms: ["living_room", "foyer", "dining_pooja"],
      styles: ["earthy_rustic", "royal_heritage"],
      dominantColors: ["#8B0000", "#DAA520", "#1E3A8A"],
      lightingVibe: "Warm ambient wash",
      placementSuggestion: "Dining room focal wall or grand entryway textile hanging."
    }
  },

  // 17. PUNJAB
  {
    id: "art-117",
    name: "Patiala Hand-Embroidered Phulkari Silk Hanging",
    category: "Handloom & Textiles",
    craftForm: "Phulkari Embroidery",
    state: "Punjab",
    isUT: false,
    region: "Tripuri, Patiala, Punjab",
    price: 2900,
    marketEstimate: 5600,
    artisanSharePercent: 83,
    giCertified: true,
    rating: 4.89,
    reviewCount: 35,
    image: "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800&auto=format&fit=crop&q=80",
    dimensions: "36 x 36 inches",
    materials: "Khaddar Cotton Base, Untwisted Pure Silk Floss (Pat)",
    description: "'Phul-Kari' literally translates to flower work. Embroidered from the reverse side of coarse cotton fabric using darn stitch counted thread work.",
    artisan: {
      name: "Harjeet Kaur",
      community: "Malwa Women Artisans Society",
      experience: "23 years",
      village: "Patiala, Punjab",
      avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&auto=format&fit=crop&q=80",
      story: "Harjeet leads a cooperative of 30 village women who weave heritage Bagh and Phulkari heirlooms."
    },
    spaceCompatibility: {
      rooms: ["bedroom", "living_room"],
      styles: ["bohemian", "royal_heritage"],
      dominantColors: ["#FF4500", "#FFD700", "#800080"],
      lightingVibe: "Bright natural light",
      placementSuggestion: "Draped over living room settee or framed as vibrant textile art."
    }
  },

  // 18. HIMACHAL PRADESH
  {
    id: "art-118",
    name: "Kullu Handspun Merino Wool Throw & Cushion Set",
    category: "Handloom & Textiles",
    craftForm: "Kullu Handloom Weaving",
    state: "Himachal Pradesh",
    isUT: false,
    region: "Bhuttico, Kullu Valley, Himachal Pradesh",
    price: 3100,
    marketEstimate: 6100,
    artisanSharePercent: 85,
    giCertified: true,
    rating: 4.94,
    reviewCount: 46,
    image: "https://images.unsplash.com/photo-1606744837616-56c9a5c6a6eb?w=800&auto=format&fit=crop&q=80",
    dimensions: "Throw: 60 x 48 inches, Cushion: 16 x 16 inches",
    materials: "100% Himalayan Merino Wool, Eco-friendly Vegetable Dyes",
    description: "Famous for its vibrant geometric border patterns woven with fine interlock tapestry techniques on mountain handlooms.",
    artisan: {
      name: "Tenzin Choden",
      community: "Kullu Valley Weavers Union",
      experience: "21 years",
      village: "Shamshi, Kullu, Himachal Pradesh",
      avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80",
      story: "Tenzin hand-spins wool during high-altitude winters, crafting warm geometric throws for sustainable living."
    },
    spaceCompatibility: {
      rooms: ["living_room", "bedroom", "study_desk"],
      styles: ["earthy_rustic", "minimalist"],
      dominantColors: ["#8B0000", "#D2B48C", "#2F4F4F"],
      lightingVibe: "Cozy warm fireplace or reading lamp",
      placementSuggestion: "Living room armchair throw or bedside runner."
    }
  },

  // 19. LADAKH (UT)
  {
    id: "art-119",
    name: "Changthangi Hand-Spun Pure Pashmina & Yak Wool Stole",
    category: "Handloom & Textiles",
    craftForm: "Ladakhi Pashmina (Lena) Weaving",
    state: "Ladakh",
    isUT: true,
    region: "Changthang Plateau, Leh, Ladakh",
    price: 5900,
    marketEstimate: 11500,
    artisanSharePercent: 88,
    giCertified: true,
    rating: 4.98,
    reviewCount: 39,
    image: "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=800&auto=format&fit=crop&q=80",
    dimensions: "80 x 28 inches",
    materials: "Pure Changra Goat Down Feather Undercoat (Pashmina), Yak Fiber",
    description: "Sourced at 14,000 ft altitude from Changpa nomads. Spun on traditional wooden takli spindles and woven on Ladakhi pit looms with feather-light warmth.",
    artisan: {
      name: "Stanzin Angmo",
      community: "Looms of Ladakh Cooperative",
      experience: "18 years",
      village: "Chushul, Leh, Ladakh",
      avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&auto=format&fit=crop&q=80",
      story: "Stanzin leads a women-owned cooperative empowering nomad herders to capture direct fair retail value."
    },
    spaceCompatibility: {
      rooms: ["living_room", "bedroom"],
      styles: ["minimalist", "royal_heritage"],
      dominantColors: ["#E8E3DF", "#C2B29F", "#544B3D"],
      lightingVibe: "Natural airy sunlight",
      placementSuggestion: "Living room chaise lounge drape or luxury bedroom throw."
    }
  },

  // 20. DELHI (UT)
  {
    id: "art-120",
    name: "Old Delhi Mughal Lattice Meenakari Brass Lantern",
    category: "Metalcraft & Brass",
    craftForm: "Mughal Jaali & Meenakari Brass",
    state: "Delhi",
    isUT: true,
    region: "Ballimaran, Chandni Chowk, Delhi",
    price: 2700,
    marketEstimate: 5200,
    artisanSharePercent: 81,
    giCertified: true,
    rating: 4.86,
    reviewCount: 48,
    image: "https://images.unsplash.com/photo-1567653418876-5bb0e566e1c2?w=800&auto=format&fit=crop&q=80",
    dimensions: "12 inches H x 6.5 inches Dia",
    materials: "Sheet Brass, Glass Insets, Chased Filigree",
    description: "Hand-pierced Mughal geometric lattice (Jaali) lamp that casts dramatic floral shadows on walls when lit with warm tea lights.",
    artisan: {
      name: "Mohammad Yusuf",
      community: "Purani Dilli Thathera Guild",
      experience: "28 years",
      village: "Ballimaran, Old Delhi",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80",
      story: "Preserving intricate metal fretwork in Old Delhi's historic alleys amidst rapid industrialization."
    },
    spaceCompatibility: {
      rooms: ["foyer", "balcony", "living_room", "dining_pooja"],
      styles: ["royal_heritage", "bohemian"],
      dominantColors: ["#B8860B", "#D4AF37", "#1A1A1A"],
      lightingVibe: "Intimate shadow-casting candlelight",
      placementSuggestion: "Balcony garden nook, entrance console, or dining centerpiece."
    }
  },

  // 21. MANIPUR
  {
    id: "art-121",
    name: "Longpi Black Stone Pottery Teapot & Cup Set",
    category: "Pottery & Ceramics",
    craftForm: "Longpi (Hampai) Black Stone Pottery",
    state: "Manipur",
    isUT: false,
    region: "Longpi, Ukhrul, Manipur",
    price: 3300,
    marketEstimate: 6600,
    artisanSharePercent: 85,
    giCertified: true,
    rating: 4.97,
    reviewCount: 34,
    image: "https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?w=800&auto=format&fit=crop&q=80",
    dimensions: "Teapot: 6.5 inches H, 4 Cups: 3 inches H",
    materials: "Weathered Serpentine Rock Powder, Alluvial Clay, Chiron-Na Leaf Polish",
    description: "Crafted without a potter's wheel by Tangkhul Naga artisans. Polished with local tree leaves that impart its distinctive matte graphite-black luster.",
    artisan: {
      name: "Wungreingam Shirik",
      community: "Tangkhul Longpi Crafts Alliance",
      experience: "19 years",
      village: "Longpi, Ukhrul, Manipur",
      avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80",
      story: "Wungreingam crushes mountain rock by hand to craft non-toxic cookware admired by global minimalist chefs."
    },
    spaceCompatibility: {
      rooms: ["dining_pooja", "living_room", "study_desk"],
      styles: ["minimalist", "earthy_rustic"],
      dominantColors: ["#23201D", "#4A4643", "#C5BDB6"],
      lightingVibe: "Soft natural morning light",
      placementSuggestion: "Dining credenza, open kitchen shelving, or tea table centerpiece."
    }
  }
];

// Room Presets for AI Space Visualizer
const ROOM_PRESETS = [
  {
    id: "room-living-minimal",
    name: "Contemporary Neutral Living Room",
    type: "living_room",
    style: "minimalist",
    image: "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=1000&auto=format&fit=crop&q=80",
    dominantColors: ["#E8E3DF", "#C2B29F", "#544B3D"],
    paletteName: "Warm Travertine & Linen",
    suitableSpots: ["Above Sofa Wall", "Coffee Table", "Side Console"]
  },
  {
    id: "room-living-earthy",
    name: "Bohemian Earth & Wood Lounge",
    type: "living_room",
    style: "earthy_rustic",
    image: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1000&auto=format&fit=crop&q=80",
    dominantColors: ["#935937", "#DFBD99", "#3E2E20"],
    paletteName: "Terracotta & Natural Teak",
    suitableSpots: ["Accent Wall Center", "Rattan Sideboard", "Corner Nook"]
  },
  {
    id: "room-study-desk",
    name: "Mindful Study & Work Desk",
    type: "study_desk",
    style: "minimalist",
    image: "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=1000&auto=format&fit=crop&q=80",
    dominantColors: ["#D4C5B9", "#3A3845", "#8E806A"],
    paletteName: "Matte Charcoal & Oak",
    suitableSpots: ["Desk Centerpiece", "Bookshelf Tier", "Study Wall Pinboard"]
  },
  {
    id: "room-foyer-heritage",
    name: "Royal Heritage Entry Foyer",
    type: "foyer",
    style: "royal_heritage",
    image: "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=1000&auto=format&fit=crop&q=80",
    dominantColors: ["#3A2E39", "#C5A880", "#E0D7C6"],
    paletteName: "Antique Brass & Sandstone",
    suitableSpots: ["Entryway Console", "Grand Hall Wall", "Pedestal Stand"]
  }
];

// Export to window
window.ALL_INDIAN_STATES_AND_UTS = ALL_INDIAN_STATES_AND_UTS;
window.ARTISAN_PRODUCTS = ARTISAN_PRODUCTS;
window.ROOM_PRESETS = ROOM_PRESETS;
