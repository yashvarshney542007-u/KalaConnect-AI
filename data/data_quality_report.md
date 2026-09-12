# Indian Handicraft Price Dataset — Data Quality & Validation Report

**Generated Date:** 2026-09-12  
**Dataset Path:** `data/processed/indian_handicraft_price_dataset.csv`  
**Evaluation Scope:** Complete synthetic catalog of authentic Indian crafts  

---

## 1. Executive Summary

| Quality Metric | Measured Value | Standard Target | Status |
|----------------|----------------|-----------------|--------|
| **Total Records** | 16,000 | 10,000 – 25,000 | ✅ PASS |
| **Total Features** | 30 | 30 | ✅ PASS |
| **Unique Crafts** | 32 | ≥ 30 | ✅ PASS |
| **Unique States** | 16 | ≥ 10 | ✅ PASS (Covering 16 Indian States) |
| **Missing Values** | 0 (0.00%) | 0.00% | ✅ PASS |
| **Exact Duplicates** | 0 | 0 | ✅ PASS |
| **Constraint Violations** | 0 | 0 | ✅ PASS |
| **Geographic Mismatches** | 0 | 0 | ✅ PASS |

---

## 2. Price Distribution Sanity

| Statistic | Value (INR) |
|-----------|-------------|
| **Minimum Price** | ₹755.00 |
| **Median Price** | ₹13,361.51 |
| **Mean Price** | ₹32,176.44 |
| **Standard Deviation** | ₹68,817.24 |
| **Maximum Price** | ₹1,395,645.15 |
| **Distribution Skewness** | 7.22 (Right-skewed, authentic to luxury/bridal mastercraft items) |

### Price Tiers
- **Budget Crafts (< ₹2,000):** Channapatna wooden toys, tea coasters, small terracotta figurines, block print stoles.
- **Mid-Range Crafts (₹2,000 – ₹10,000):** Dhokra sculptures, Madhubani paintings, Jaipur Blue Pottery planters, Kolhapuri chappals, Chikankari kurtas.
- **Premium / Bridal Crafts (> ₹10,000):** Banarasi Katan silk sarees, Kanjeevaram Korvai sarees, Tanjore 22K gold leaf frames, Kashmiri silk hand-knotted carpets.

---

## 3. Economic & Domain Constraint Audit

- **Production Cost Floor Check:** 100% of rows have `price_inr >= material_cost + labor_cost + overhead_cost`. Minimum artisan profit margin is preserved.
- **Labor Coherence:** Average work day corresponds to 7.2–8.5 labor hours. No fractional negative or inflated labor values.
- **Dimensional Fidelity:** Length, width, height, and weight are physically proportional and positive across all craft categories.
- **Geographical Integrity:** 100% of records preserve authentic State, Region, and District alignments grounded in statutory GI Registry data and Ministry of Textiles clusters.

---

## 4. Key Feature Correlations with Price

| Feature Pair | Pearson Correlation ($r$) | Domain Interpretation |
|--------------|---------------------------|-----------------------|
| `labor_cost_inr` vs `price_inr` | +0.946 | Strong positive correlation reflecting labor-intensive artistry |
| `material_cost_inr` vs `price_inr` | +0.836 | Strong positive correlation reflecting precious inputs (silk, zari, gold foil) |
| `complexity_score` vs `price_inr` | +0.391 | Intricacy directly increases craft market valuation |

---

## 5. Craft Representation Breakdown

| Craft Name | State | District | Sample Rows | Price Median (INR) |
|------------|-------|----------|-------------|--------------------|
| Ajrakh | Gujarat | Kutch | 500 | ₹25,040.31 |
| Bamboo Craft | Assam | Barpeta | 500 | ₹4,190.23 |
| Banarasi Handloom | Uttar Pradesh | Varanasi | 500 | ₹51,538.34 |
| Bastar Art | Chhattisgarh | Kondagaon | 500 | ₹6,361.75 |
| Bell Metal Craft | Assam | Barpeta | 500 | ₹9,846.40 |
| Bidriware | Karnataka | Bidar | 500 | ₹14,471.21 |
| Blue Pottery | Rajasthan | Jaipur | 500 | ₹4,329.01 |
| Brass Craft | Uttar Pradesh | Moradabad | 500 | ₹8,807.33 |
| Cane Craft | Assam | Dibrugarh | 500 | ₹10,738.20 |
| Channapatna Toys | Karnataka | Ramanagara | 500 | ₹2,014.20 |
| Chikankari | Uttar Pradesh | Lucknow | 500 | ₹22,208.53 |
| Dhokra | Chhattisgarh | Bastar | 500 | ₹9,910.24 |
| Handloom Products | Madhya Pradesh | Ashoknagar | 500 | ₹22,386.58 |
| Handwoven Textiles | Odisha | Bargarh | 500 | ₹30,610.28 |
| Kalamkari | Andhra Pradesh | Tirupati | 500 | ₹16,399.60 |
| Kanjeevaram Silk | Tamil Nadu | Kanchipuram | 500 | ₹70,277.21 |
| Kantha | West Bengal | Birbhum | 500 | ₹34,609.11 |
| Kashmiri Carpets | Jammu & Kashmir | Srinagar | 500 | ₹244,868.50 |
| Kashmiri Papier-Mâché | Jammu & Kashmir | Srinagar | 500 | ₹14,872.51 |
| Kutch Embroidery | Gujarat | Kutch | 500 | ₹14,825.85 |
| Leather Craft | Maharashtra | Kolhapur | 500 | ₹3,786.76 |
| Madhubani Painting | Bihar | Madhubani | 500 | ₹18,295.28 |
| Metalware | Telangana | Jangaon | 500 | ₹15,561.61 |
| Pattachitra | Odisha | Puri | 500 | ₹10,547.48 |
| Phulkari | Punjab | Patiala | 500 | ₹24,345.06 |
| Pottery | Uttar Pradesh | Bulandshahr | 500 | ₹8,807.80 |
| Rajasthani Block Printing | Rajasthan | Jaipur | 500 | ₹7,155.35 |
| Stone Carving | Odisha | Puri | 500 | ₹18,492.72 |
| Tanjore Painting | Tamil Nadu | Thanjavur | 500 | ₹28,288.15 |
| Terracotta | West Bengal | Bankura | 500 | ₹4,030.90 |
| Warli Painting | Maharashtra | Palghar | 500 | ₹3,579.14 |
| Wood Carving | Karnataka | Mysuru | 500 | ₹19,374.22 |

---

## 6. Conclusion
The dataset passes all domain constraints, structural checks, and geographical validations with zero missing values or impossible records. It is verified ML-ready for regression modeling.
