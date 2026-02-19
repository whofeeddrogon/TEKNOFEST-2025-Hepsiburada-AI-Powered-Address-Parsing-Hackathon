# TEKNOFEST 2025: Hepsiburada AI-Powered Address Parsing Hackathon

![Banner](https://img.shields.io/badge/TEKNOFEST-2025-blue?style=for-the-badge&logo=rocket)
![Rank-Kaggle](https://img.shields.io/badge/Kaggle_Stage-1st_Place-gold?style=for-the-badge)
![Rank-Hackathon](https://img.shields.io/badge/Hackathon_Stage-2nd_Place-silver?style=for-the-badge)
![Model](https://img.shields.io/badge/Model-BERTürk-green?style=for-the-badge)

This repository contains the solution developed by **Team Atom** for the **TEKNOFEST 2025 Hepsiburada AI-Powered Address Parsing Hackathon**. Our solution achieved **1st Place** among 256 teams in the Kaggle stage and **2nd Place** in the final hackathon stage held at the Hepsiburada HQ.

🔗 **[Read our success story on LinkedIn](https://www.linkedin.com/posts/berkaybicer_im-incredibly-proud-to-announce-that-our-activity-7375892313794990080-FXL6)**

## 🚀 Project Overview

The core objective of the competition was to match approximately **1 million** noisy, handwritten, and unformatted Turkish address strings with **~10,390** unique ground-truth address labels. Our approach combined state-of-the-art NLP models with advanced geospatial clustering to ensure high-precision address resolution.

### 🏆 Achievements
*   **Ranked #1** in the Kaggle evaluation stage (out of 256 teams).
*   **Ranked #2** in the final Hackathon presentation and implementation phase.
*   Developed a robust Two-Pass DBSCAN clustering algorithm for geocoordinate validation.

---

## 📸 Visuals

Analysis and visualization of our results:

<div align="center">
  <img src="assets/Ekran görüntüsü 2026-02-19 204247.png" width="400" alt="Interactive Map Analysis">
  <p><i>Figure 1: Interactive map interface visualizing address clusters and centroids across Turkey.</i></p>
</div>

<div align="center">
  <img src="assets/Ekran görüntüsü 2026-02-19 204206.png" width="800" alt="Model Error Analysis">
  <p><i>Figure 2: Model error analysis and performance visualization.</i></p>
</div>

<div align="center">
  <img src="assets/Ekran görüntüsü 2026-02-19 204223.png" width="500" alt="Confidence Metrics">
</div>

---

## 🛠️ Technical Methodology

### 1. Advanced Turkish Address Preprocessing
To maximize the performance of the BERTürk model, we implemented a custom preprocessing pipeline:
*   **Normalization:** Context-aware lowercasing and character standardization (specifically for Turkish characters).
*   **Abbreviation Expansion:** Standardized 50+ common Turkish address abbreviations (e.g., "Mah." → "mahallesi", "Sk." → "sokak").
*   **Feature Engineering:** Extracted and tagged specific address components like Door Numbers, Floor Info, and Postal Codes as secondary signals for the model.

### 2. Model Architecture: BERTürk Fine-Tuning
*   **Base Model:** We utilized `dbmdz/bert-base-turkish-cased` as our foundation.
*   **Optimization:** The model was fine-tuned on the massive 1M dataset, handling significant class imbalance across the 10k unique labels.

### 3. Geospatial Validation & Clustering
Following the model's predictions, we implemented a validation layer:
*   **Confidence Filtering:** We performed a forward pass on all data and selected the Top-10 address strings for each label based on confidence values.
*   **Geocoding:** These top addresses were mapped to coordinates using the Google Maps API.
*   **Two-Pass DBSCAN:** 
    1.  *Macro-Clustering:* Removed inter-city outliers with a 25km radius.
    2.  *Micro-Clustering:* Applied a fine-tuned density search to identify the most probable geographic center for each label.
*   **Centroid Positioning:** The center of the densest cluster became the ground truth center for that label.

---

## 🗺️ Interactive Dashboard

We built a geospatial dashboard to visually inspect our model's performance. It allowed us to:
*   Identify problematic labels where addresses were geographically dispersed.
*   Validate the accuracy of cluster centers in real-time.
*   Visualize the relationship between raw address strings and their resolved locations.

---

## 👥 Team Atom

*   **Berkay Biçer**
*   **Çağlar Kabaca**
*   **Yiğit Alıcıkuş**

---
<div align="center">
  <b>Hepsiburada AI-Powered Address Parsing Hackathon 2025</b>
</div>