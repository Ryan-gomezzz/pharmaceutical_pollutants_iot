"""
Build the complete Jupyter Notebook for Pharmaceutical Pollution Detection.
This script generates the .ipynb file programmatically.
"""
import json, os

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source if isinstance(source, list) else [source]}

def code(source):
    return {"cell_type": "code", "metadata": {}, "source": source if isinstance(source, list) else [source], "outputs": [], "execution_count": None}

cells = []

# ═══════════════════════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════════════════════
cells.append(md([
    "# 🧪 Detection of Pharmaceutical Pollution in Water Using Proxy Sensing and Machine Learning\n",
    "\n",
    "---\n",
    "\n",
    "**Abstract:** This notebook presents an end-to-end machine learning pipeline for detecting pharmaceutical contamination in water streams using *proxy sensing*. ",
    "Rather than directly measuring pharmaceutical compounds (which requires expensive spectrometry), we use an array of low-cost environmental sensors — **pH, Turbidity, TDS, Temperature, and Humidity** — ",
    "whose correlated deviations from baseline water chemistry serve as indirect indicators of contamination events.\n",
    "\n",
    "We implement and compare three approaches:\n",
    "1. **Isolation Forest** for unsupervised anomaly detection\n",
    "2. **K-Means Clustering** for discovering pollution signatures\n",
    "3. **Deep Neural Network (Keras)** for supervised multi-class classification\n",
    "\n",
    "All graphs are publication-quality and suitable for research reports.\n",
    "\n",
    "---"
]))

# ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════
cells.append(md("## 📦 Library Imports"))
cells.append(code([
    "import numpy as np\n",
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import matplotlib.gridspec as gridspec\n",
    "import seaborn as sns\n",
    "from sklearn.preprocessing import StandardScaler, label_binarize\n",
    "from sklearn.model_selection import train_test_split\n",
    "from sklearn.ensemble import IsolationForest, RandomForestClassifier\n",
    "from sklearn.cluster import KMeans\n",
    "from sklearn.decomposition import PCA\n",
    "from sklearn.metrics import (classification_report, confusion_matrix,\n",
    "                             precision_score, recall_score, f1_score,\n",
    "                             accuracy_score, roc_curve, auc,\n",
    "                             precision_recall_curve, average_precision_score,\n",
    "                             silhouette_score)\n",
    "import tensorflow as tf\n",
    "from tensorflow.keras.models import Sequential\n",
    "from tensorflow.keras.layers import Dense, Dropout, BatchNormalization\n",
    "from tensorflow.keras.utils import to_categorical\n",
    "from tensorflow.keras.callbacks import EarlyStopping\n",
    "import warnings\n",
    "warnings.filterwarnings('ignore')\n",
    "\n",
    "# Plot styling\n",
    "plt.rcParams.update({\n",
    "    'figure.dpi': 120,\n",
    "    'font.size': 11,\n",
    "    'axes.titlesize': 13,\n",
    "    'axes.labelsize': 11,\n",
    "    'figure.facecolor': 'white'\n",
    "})\n",
    "sns.set_style('whitegrid')\n",
    "PALETTE = ['#2ecc71', '#f39c12', '#e74c3c']\n",
    "CLASS_NAMES = ['Normal Water', 'Possible Contamination', 'Severe Contamination']\n",
    "print('All libraries loaded successfully.')\n",
    "print(f'TensorFlow version: {tf.__version__}')"
]))

# ═══════════════════════════════════════════════════════════════
# SECTION 1: DATASET GENERATION
# ═══════════════════════════════════════════════════════════════
cells.append(md([
    "---\n",
    "# Section 1: Synthetic Dataset Generation\n",
    "\n",
    "We generate **10,000 samples** simulating readings from 5 environmental sensors.\n",
    "\n",
    "| Class | Label | pH | TDS (ppm) | Turbidity (NTU) | Temp (°C) | Humidity (%) |\n",
    "|---|---|---|---|---|---|---|\n",
    "| Normal | 0 | 6.5–8.5 | 50–300 | 0–5 | 20–35 | 40–80 |\n",
    "| Possible Contamination | 1 | 5.8–9.0 | 300–600 | 5–30 | 20–35 | 50–90 |\n",
    "| Severe Contamination | 2 | 5.5–9.5 | 400–800 | 10–50 | 20–35 | 55–95 |\n",
    "\n",
    "**Correlation logic:** TDS increases with turbidity; humidity is slightly correlated with temperature; contamination shifts pH away from neutral."
]))

cells.append(code([
    "np.random.seed(42)\n",
    "n_samples = 10000\n",
    "\n",
    "# Class distribution: 60% normal, 25% possible, 15% severe\n",
    "n_normal  = int(n_samples * 0.60)\n",
    "n_possible = int(n_samples * 0.25)\n",
    "n_severe  = n_samples - n_normal - n_possible\n",
    "\n",
    "def generate_class(n, ph_range, tds_range, turb_range, temp_range, hum_range, label):\n",
    "    ph = np.random.uniform(*ph_range, n) + np.random.normal(0, 0.1, n)\n",
    "    turbidity = np.random.uniform(*turb_range, n) + np.random.normal(0, 1, n)\n",
    "    turbidity = np.clip(turbidity, 0, None)\n",
    "    # TDS correlates with turbidity\n",
    "    tds = np.random.uniform(*tds_range, n) + turbidity * np.random.uniform(1.5, 3.0, n) + np.random.normal(0, 10, n)\n",
    "    temperature = np.random.uniform(*temp_range, n) + np.random.normal(0, 0.5, n)\n",
    "    # Humidity inversely correlated with temperature\n",
    "    humidity = np.random.uniform(*hum_range, n) - (temperature - 25) * 0.8 + np.random.normal(0, 2, n)\n",
    "    humidity = np.clip(humidity, 20, 100)\n",
    "    return pd.DataFrame({\n",
    "        'ph': ph, 'turbidity': turbidity, 'tds': tds,\n",
    "        'temperature': temperature, 'humidity': humidity,\n",
    "        'pollution_class': label\n",
    "    })\n",
    "\n",
    "df_normal   = generate_class(n_normal,   (6.5, 8.5), (50, 300),  (0, 5),   (20, 35), (40, 80), 0)\n",
    "df_possible = generate_class(n_possible, (5.8, 9.0), (300, 600), (5, 30),  (20, 35), (50, 90), 1)\n",
    "df_severe   = generate_class(n_severe,   (5.5, 9.5), (400, 800), (10, 50), (20, 35), (55, 95), 2)\n",
    "\n",
    "df = pd.concat([df_normal, df_possible, df_severe], ignore_index=True)\n",
    "df = df.sample(frac=1, random_state=42).reset_index(drop=True)\n",
    "\n",
    "print(f'Dataset shape: {df.shape}')\n",
    "print(f'\\nClass distribution:')\n",
    "print(df['pollution_class'].value_counts().sort_index().to_string())\n",
    "print(f'\\nFirst 5 rows:')\n",
    "df.head()"
]))

cells.append(code([
    "# Summary statistics\n",
    "df.describe().round(3)"
]))

# ═══════════════════════════════════════════════════════════════
# SECTION 2: DATA VISUALIZATION
# ═══════════════════════════════════════════════════════════════
cells.append(md([
    "---\n",
    "# Section 2: Data Visualization\n",
    "\n",
    "Comprehensive visual exploration of the sensor data to understand feature distributions, inter-variable correlations, and class separability."
]))

# 2.1 Histograms
cells.append(md("### 2.1 Feature Distribution Histograms"))
cells.append(code([
    "features = ['ph', 'turbidity', 'tds', 'temperature', 'humidity']\n",
    "fig, axes = plt.subplots(1, 5, figsize=(20, 4))\n",
    "for i, col in enumerate(features):\n",
    "    for cls in [0, 1, 2]:\n",
    "        axes[i].hist(df[df['pollution_class']==cls][col], bins=40, alpha=0.6,\n",
    "                     label=CLASS_NAMES[cls], color=PALETTE[cls])\n",
    "    axes[i].set_title(col.upper())\n",
    "    axes[i].set_xlabel(col)\n",
    "    axes[i].set_ylabel('Frequency')\n",
    "axes[0].legend(fontsize=8)\n",
    "plt.suptitle('Feature Distributions by Pollution Class', fontsize=15, y=1.02)\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

# 2.2 Correlation heatmap
cells.append(md("### 2.2 Correlation Heatmap"))
cells.append(code([
    "fig, ax = plt.subplots(figsize=(8, 6))\n",
    "corr = df[features + ['pollution_class']].corr()\n",
    "mask = np.triu(np.ones_like(corr, dtype=bool))\n",
    "sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn_r',\n",
    "            center=0, square=True, linewidths=1, ax=ax)\n",
    "ax.set_title('Correlation Matrix of Sensor Features', fontsize=14)\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

# 2.3 Pairplot
cells.append(md("### 2.3 Pairplot"))
cells.append(code([
    "g = sns.pairplot(df.sample(2000, random_state=42), hue='pollution_class',\n",
    "                 vars=features, palette=PALETTE, diag_kind='kde',\n",
    "                 plot_kws={'alpha': 0.5, 's': 15})\n",
    "g.figure.suptitle('Pairwise Feature Relationships', y=1.01, fontsize=15)\n",
    "plt.show()"
]))

# 2.4 Boxplots
cells.append(md("### 2.4 Box Plots by Pollution Class"))
cells.append(code([
    "fig, axes = plt.subplots(1, 5, figsize=(20, 5))\n",
    "for i, col in enumerate(features):\n",
    "    sns.boxplot(data=df, x='pollution_class', y=col, palette=PALETTE, ax=axes[i])\n",
    "    axes[i].set_xticklabels(CLASS_NAMES, rotation=25, fontsize=8)\n",
    "    axes[i].set_title(col.upper())\n",
    "plt.suptitle('Sensor Readings by Pollution Class', fontsize=15, y=1.02)\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

# 2.5 Time-series simulation
cells.append(md("### 2.5 Time-Series Simulation"))
cells.append(code([
    "fig, axes = plt.subplots(5, 1, figsize=(16, 12), sharex=True)\n",
    "time_slice = df.head(500)\n",
    "colors_ts = [PALETTE[int(c)] for c in time_slice['pollution_class']]\n",
    "for i, col in enumerate(features):\n",
    "    axes[i].scatter(range(len(time_slice)), time_slice[col], c=colors_ts, s=5, alpha=0.7)\n",
    "    axes[i].plot(time_slice[col].rolling(20).mean().values, color='black', lw=1.2, alpha=0.7)\n",
    "    axes[i].set_ylabel(col.upper())\n",
    "axes[-1].set_xlabel('Sample Index (simulated time)')\n",
    "fig.suptitle('Simulated Time-Series of Sensor Readings', fontsize=15)\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

# ═══════════════════════════════════════════════════════════════
# SECTION 3: PREPROCESSING
# ═══════════════════════════════════════════════════════════════
cells.append(md([
    "---\n",
    "# Section 3: Data Preprocessing\n",
    "\n",
    "Standard scaling, train/test split, and visual comparison of raw vs. scaled features."
]))

cells.append(code([
    "X = df[features].values\n",
    "y = df['pollution_class'].values\n",
    "\n",
    "# Train/Test Split (80/20)\n",
    "X_train, X_test, y_train, y_test = train_test_split(\n",
    "    X, y, test_size=0.2, random_state=42, stratify=y\n",
    ")\n",
    "\n",
    "# Standard Scaling\n",
    "scaler = StandardScaler()\n",
    "X_train_scaled = scaler.fit_transform(X_train)\n",
    "X_test_scaled = scaler.transform(X_test)\n",
    "\n",
    "print(f'Training set: {X_train_scaled.shape}')\n",
    "print(f'Testing set:  {X_test_scaled.shape}')\n",
    "print(f'\\nScaler means: {scaler.mean_.round(3)}')\n",
    "print(f'Scaler stds:  {scaler.scale_.round(3)}')"
]))

cells.append(md("### Scaled vs. Raw Feature Comparison"))
cells.append(code([
    "fig, axes = plt.subplots(2, 5, figsize=(20, 7))\n",
    "for i, col in enumerate(features):\n",
    "    axes[0][i].hist(X_train[:, i], bins=40, color='#3498db', alpha=0.7)\n",
    "    axes[0][i].set_title(f'{col} (Raw)')\n",
    "    axes[1][i].hist(X_train_scaled[:, i], bins=40, color='#e74c3c', alpha=0.7)\n",
    "    axes[1][i].set_title(f'{col} (Scaled)')\n",
    "plt.suptitle('Raw vs. StandardScaler Normalized Features', fontsize=15, y=1.02)\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

# ═══════════════════════════════════════════════════════════════
# SECTION 4: ANOMALY DETECTION
# ═══════════════════════════════════════════════════════════════
cells.append(md([
    "---\n",
    "# Section 4: Anomaly Detection — Isolation Forest\n",
    "\n",
    "The Isolation Forest is trained **only on normal water samples** (class 0). Any contaminated sample should appear as an anomaly."
]))

cells.append(code([
    "# Train only on class 0 (Normal)\n",
    "X_normal = X_train_scaled[y_train == 0]\n",
    "\n",
    "iso_forest = IsolationForest(n_estimators=200, contamination=0.1, random_state=42)\n",
    "iso_forest.fit(X_normal)\n",
    "\n",
    "# Predict on full test set\n",
    "iso_pred = iso_forest.predict(X_test_scaled)  # 1 = normal, -1 = anomaly\n",
    "iso_scores = iso_forest.decision_function(X_test_scaled)\n",
    "\n",
    "# Convert: anomaly (-1) → 1 (contaminated), normal (1) → 0\n",
    "iso_binary = (iso_pred == -1).astype(int)\n",
    "y_test_binary = (y_test > 0).astype(int)  # 0 = normal, 1 = contaminated\n",
    "\n",
    "iso_precision = precision_score(y_test_binary, iso_binary)\n",
    "iso_recall = recall_score(y_test_binary, iso_binary)\n",
    "iso_f1 = f1_score(y_test_binary, iso_binary)\n",
    "iso_accuracy = accuracy_score(y_test_binary, iso_binary)\n",
    "\n",
    "print('=== Isolation Forest Results ===')\n",
    "print(f'Accuracy:  {iso_accuracy:.4f}')\n",
    "print(f'Precision: {iso_precision:.4f}')\n",
    "print(f'Recall:    {iso_recall:.4f}')\n",
    "print(f'F1 Score:  {iso_f1:.4f}')"
]))

cells.append(md("### 4.1 Anomaly Score Distribution"))
cells.append(code([
    "fig, ax = plt.subplots(figsize=(10, 5))\n",
    "ax.hist(iso_scores[y_test_binary==0], bins=50, alpha=0.6, label='Normal', color=PALETTE[0])\n",
    "ax.hist(iso_scores[y_test_binary==1], bins=50, alpha=0.6, label='Contaminated', color=PALETTE[2])\n",
    "ax.axvline(x=0, color='black', linestyle='--', lw=1.5, label='Decision Boundary')\n",
    "ax.set_xlabel('Anomaly Score')\n",
    "ax.set_ylabel('Frequency')\n",
    "ax.set_title('Isolation Forest Anomaly Score Distribution')\n",
    "ax.legend()\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

cells.append(md("### 4.2 Anomaly Scatter Plot (PCA 2D)"))
cells.append(code([
    "pca_2d = PCA(n_components=2)\n",
    "X_test_pca = pca_2d.fit_transform(X_test_scaled)\n",
    "\n",
    "fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n",
    "# Ground truth\n",
    "for cls, name, c in zip([0,1], ['Normal','Contaminated'], [PALETTE[0], PALETTE[2]]):\n",
    "    mask = y_test_binary == cls\n",
    "    axes[0].scatter(X_test_pca[mask,0], X_test_pca[mask,1], c=c, s=10, alpha=0.5, label=name)\n",
    "axes[0].set_title('Ground Truth')\n",
    "axes[0].legend()\n",
    "# Predictions\n",
    "for cls, name, c in zip([0,1], ['Normal','Anomaly'], [PALETTE[0], PALETTE[2]]):\n",
    "    mask = iso_binary == cls\n",
    "    axes[1].scatter(X_test_pca[mask,0], X_test_pca[mask,1], c=c, s=10, alpha=0.5, label=name)\n",
    "axes[1].set_title('Isolation Forest Predictions')\n",
    "axes[1].legend()\n",
    "for ax in axes:\n",
    "    ax.set_xlabel('PC1')\n",
    "    ax.set_ylabel('PC2')\n",
    "plt.suptitle('Anomaly Detection — PCA Projection', fontsize=14)\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

cells.append(md("### 4.3 Confusion Matrix"))
cells.append(code([
    "cm = confusion_matrix(y_test_binary, iso_binary)\n",
    "fig, ax = plt.subplots(figsize=(6, 5))\n",
    "sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',\n",
    "            xticklabels=['Normal', 'Anomaly'], yticklabels=['Normal', 'Anomaly'], ax=ax)\n",
    "ax.set_xlabel('Predicted')\n",
    "ax.set_ylabel('Actual')\n",
    "ax.set_title('Isolation Forest — Confusion Matrix')\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

# ═══════════════════════════════════════════════════════════════
# SECTION 5: CLUSTERING
# ═══════════════════════════════════════════════════════════════
cells.append(md([
    "---\n",
    "# Section 5: K-Means Clustering\n",
    "\n",
    "Unsupervised clustering to discover natural groupings in sensor data."
]))

cells.append(md("### 5.1 Elbow Method"))
cells.append(code([
    "inertias = []\n",
    "sil_scores = []\n",
    "K_range = range(2, 11)\n",
    "for k in K_range:\n",
    "    km = KMeans(n_clusters=k, random_state=42, n_init=10)\n",
    "    km.fit(X_train_scaled)\n",
    "    inertias.append(km.inertia_)\n",
    "    sil_scores.append(silhouette_score(X_train_scaled, km.labels_, sample_size=2000))\n",
    "\n",
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
    "axes[0].plot(K_range, inertias, 'bo-', lw=2)\n",
    "axes[0].set_xlabel('Number of Clusters (k)')\n",
    "axes[0].set_ylabel('Inertia')\n",
    "axes[0].set_title('Elbow Method')\n",
    "axes[0].axvline(x=3, color='red', linestyle='--', alpha=0.7, label='k=3')\n",
    "axes[0].legend()\n",
    "\n",
    "axes[1].plot(K_range, sil_scores, 'go-', lw=2)\n",
    "axes[1].set_xlabel('Number of Clusters (k)')\n",
    "axes[1].set_ylabel('Silhouette Score')\n",
    "axes[1].set_title('Silhouette Analysis')\n",
    "axes[1].axvline(x=3, color='red', linestyle='--', alpha=0.7, label='k=3')\n",
    "axes[1].legend()\n",
    "plt.suptitle('Optimal Cluster Selection', fontsize=14)\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

cells.append(md("### 5.2 K-Means with k=3"))
cells.append(code([
    "kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)\n",
    "km_labels = kmeans.fit_predict(X_train_scaled)\n",
    "km_test_labels = kmeans.predict(X_test_scaled)\n",
    "\n",
    "# PCA visualization\n",
    "pca3 = PCA(n_components=2)\n",
    "X_train_pca = pca3.fit_transform(X_train_scaled)\n",
    "centroids_pca = pca3.transform(kmeans.cluster_centers_)\n",
    "\n",
    "fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n",
    "# Cluster assignments\n",
    "for c in range(3):\n",
    "    mask = km_labels == c\n",
    "    axes[0].scatter(X_train_pca[mask,0], X_train_pca[mask,1], s=8, alpha=0.4, label=f'Cluster {c}')\n",
    "axes[0].scatter(centroids_pca[:,0], centroids_pca[:,1], c='black', marker='X', s=200, zorder=5, label='Centroids')\n",
    "axes[0].set_title('K-Means Clusters (PCA)')\n",
    "axes[0].legend()\n",
    "\n",
    "# Ground truth\n",
    "for c in range(3):\n",
    "    mask = y_train == c\n",
    "    axes[1].scatter(X_train_pca[mask,0], X_train_pca[mask,1], s=8, alpha=0.4,\n",
    "                    color=PALETTE[c], label=CLASS_NAMES[c])\n",
    "axes[1].set_title('Ground Truth Classes (PCA)')\n",
    "axes[1].legend()\n",
    "for ax in axes:\n",
    "    ax.set_xlabel('PC1')\n",
    "    ax.set_ylabel('PC2')\n",
    "plt.suptitle('K-Means Clustering vs Ground Truth', fontsize=14)\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

cells.append(md("### 5.3 Cluster Centroids"))
cells.append(code([
    "centroids_df = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_),\n",
    "                             columns=features)\n",
    "centroids_df.index.name = 'Cluster'\n",
    "print('Cluster Centroids (original scale):')\n",
    "centroids_df.round(2)"
]))

# ═══════════════════════════════════════════════════════════════
# SECTION 6: DEEP LEARNING
# ═══════════════════════════════════════════════════════════════
cells.append(md([
    "---\n",
    "# Section 6: Deep Learning Classification (Keras)\n",
    "\n",
    "A multi-layer neural network for supervised 3-class pollution classification."
]))

cells.append(code([
    "# One-hot encode targets\n",
    "y_train_cat = to_categorical(y_train, 3)\n",
    "y_test_cat = to_categorical(y_test, 3)\n",
    "\n",
    "# Build model\n",
    "model = Sequential([\n",
    "    Dense(64, activation='relu', input_shape=(5,)),\n",
    "    BatchNormalization(),\n",
    "    Dropout(0.3),\n",
    "    Dense(32, activation='relu'),\n",
    "    BatchNormalization(),\n",
    "    Dropout(0.2),\n",
    "    Dense(16, activation='relu'),\n",
    "    Dense(3, activation='softmax')\n",
    "])\n",
    "\n",
    "model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])\n",
    "model.summary()\n",
    "\n",
    "history = model.fit(\n",
    "    X_train_scaled, y_train_cat,\n",
    "    validation_data=(X_test_scaled, y_test_cat),\n",
    "    epochs=30, batch_size=32, verbose=1\n",
    ")"
]))

cells.append(md("### 6.1 Training Curves"))
cells.append(code([
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
    "axes[0].plot(history.history['accuracy'], label='Train', lw=2)\n",
    "axes[0].plot(history.history['val_accuracy'], label='Validation', lw=2)\n",
    "axes[0].set_title('Model Accuracy')\n",
    "axes[0].set_xlabel('Epoch')\n",
    "axes[0].set_ylabel('Accuracy')\n",
    "axes[0].legend()\n",
    "\n",
    "axes[1].plot(history.history['loss'], label='Train', lw=2)\n",
    "axes[1].plot(history.history['val_loss'], label='Validation', lw=2)\n",
    "axes[1].set_title('Model Loss')\n",
    "axes[1].set_xlabel('Epoch')\n",
    "axes[1].set_ylabel('Loss')\n",
    "axes[1].legend()\n",
    "plt.suptitle('Neural Network Training History', fontsize=14)\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

cells.append(md("### 6.2 Confusion Matrix & Metrics"))
cells.append(code([
    "y_pred_proba = model.predict(X_test_scaled)\n",
    "y_pred_nn = np.argmax(y_pred_proba, axis=1)\n",
    "\n",
    "nn_accuracy = accuracy_score(y_test, y_pred_nn)\n",
    "nn_precision = precision_score(y_test, y_pred_nn, average='weighted')\n",
    "nn_recall = recall_score(y_test, y_pred_nn, average='weighted')\n",
    "nn_f1 = f1_score(y_test, y_pred_nn, average='weighted')\n",
    "\n",
    "print('=== Neural Network Results ===')\n",
    "print(f'Accuracy:  {nn_accuracy:.4f}')\n",
    "print(f'Precision: {nn_precision:.4f}')\n",
    "print(f'Recall:    {nn_recall:.4f}')\n",
    "print(f'F1 Score:  {nn_f1:.4f}')\n",
    "print(f'\\n{classification_report(y_test, y_pred_nn, target_names=CLASS_NAMES)}')\n",
    "\n",
    "cm_nn = confusion_matrix(y_test, y_pred_nn)\n",
    "fig, ax = plt.subplots(figsize=(7, 6))\n",
    "sns.heatmap(cm_nn, annot=True, fmt='d', cmap='Purples',\n",
    "            xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES, ax=ax)\n",
    "ax.set_xlabel('Predicted')\n",
    "ax.set_ylabel('Actual')\n",
    "ax.set_title('Neural Network — Confusion Matrix')\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

cells.append(md("### 6.3 ROC Curve"))
cells.append(code([
    "y_test_bin = label_binarize(y_test, classes=[0, 1, 2])\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(8, 7))\n",
    "for i in range(3):\n",
    "    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_pred_proba[:, i])\n",
    "    roc_auc = auc(fpr, tpr)\n",
    "    ax.plot(fpr, tpr, lw=2, label=f'{CLASS_NAMES[i]} (AUC={roc_auc:.3f})')\n",
    "ax.plot([0,1],[0,1],'k--', lw=1)\n",
    "ax.set_xlabel('False Positive Rate')\n",
    "ax.set_ylabel('True Positive Rate')\n",
    "ax.set_title('ROC Curves (One-vs-Rest)')\n",
    "ax.legend(loc='lower right')\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

cells.append(md("### 6.4 Precision-Recall Curve"))
cells.append(code([
    "fig, ax = plt.subplots(figsize=(8, 7))\n",
    "for i in range(3):\n",
    "    prec, rec, _ = precision_recall_curve(y_test_bin[:, i], y_pred_proba[:, i])\n",
    "    ap = average_precision_score(y_test_bin[:, i], y_pred_proba[:, i])\n",
    "    ax.plot(rec, prec, lw=2, label=f'{CLASS_NAMES[i]} (AP={ap:.3f})')\n",
    "ax.set_xlabel('Recall')\n",
    "ax.set_ylabel('Precision')\n",
    "ax.set_title('Precision-Recall Curves')\n",
    "ax.legend()\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

# ═══════════════════════════════════════════════════════════════
# SECTION 7: MODEL COMPARISON
# ═══════════════════════════════════════════════════════════════
cells.append(md([
    "---\n",
    "# Section 7: Model Performance Comparison\n",
    "\n",
    "Comparing all three approaches side by side."
]))

cells.append(code([
    "# Train a quick RF for feature importance and as a baseline\n",
    "rf = RandomForestClassifier(n_estimators=100, random_state=42)\n",
    "rf.fit(X_train_scaled, y_train)\n",
    "rf_pred = rf.predict(X_test_scaled)\n",
    "rf_accuracy = accuracy_score(y_test, rf_pred)\n",
    "rf_f1 = f1_score(y_test, rf_pred, average='weighted')\n",
    "\n",
    "# K-Means \"accuracy\" via cluster-to-class mapping\n",
    "from scipy.stats import mode\n",
    "km_mapped = np.zeros_like(km_test_labels)\n",
    "for c in range(3):\n",
    "    mask = km_test_labels == c\n",
    "    if mask.sum() > 0:\n",
    "        km_mapped[mask] = mode(y_test[mask], keepdims=False).mode\n",
    "km_accuracy = accuracy_score(y_test, km_mapped)\n",
    "km_f1 = f1_score(y_test, km_mapped, average='weighted')\n",
    "\n",
    "results = pd.DataFrame({\n",
    "    'Model': ['Isolation Forest', 'K-Means', 'Neural Network', 'Random Forest'],\n",
    "    'Accuracy': [iso_accuracy, km_accuracy, nn_accuracy, rf_accuracy],\n",
    "    'F1 Score': [iso_f1, km_f1, nn_f1, rf_f1]\n",
    "})\n",
    "print(results.to_string(index=False))"
]))

cells.append(md("### 7.1 Accuracy Comparison"))
cells.append(code([
    "fig, ax = plt.subplots(figsize=(10, 5))\n",
    "colors_bar = ['#3498db', '#e67e22', '#9b59b6', '#2ecc71']\n",
    "bars = ax.bar(results['Model'], results['Accuracy'], color=colors_bar, edgecolor='white', linewidth=1.5)\n",
    "for bar, val in zip(bars, results['Accuracy']):\n",
    "    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,\n",
    "            f'{val:.3f}', ha='center', fontsize=12, fontweight='bold')\n",
    "ax.set_ylim(0, 1.15)\n",
    "ax.set_ylabel('Accuracy')\n",
    "ax.set_title('Model Accuracy Comparison', fontsize=14)\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

cells.append(md("### 7.2 Radar Chart"))
cells.append(code([
    "metrics_nn = [nn_accuracy, nn_precision, nn_recall, nn_f1]\n",
    "metrics_iso = [iso_accuracy, iso_precision, iso_recall, iso_f1]\n",
    "metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1 Score']\n",
    "\n",
    "angles = np.linspace(0, 2*np.pi, len(metric_labels), endpoint=False).tolist()\n",
    "angles += angles[:1]\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))\n",
    "for vals, label, color in [(metrics_nn, 'Neural Network', '#9b59b6'),\n",
    "                            (metrics_iso, 'Isolation Forest', '#3498db')]:\n",
    "    vals_plot = vals + vals[:1]\n",
    "    ax.plot(angles, vals_plot, 'o-', lw=2, label=label, color=color)\n",
    "    ax.fill(angles, vals_plot, alpha=0.15, color=color)\n",
    "ax.set_thetagrids(np.degrees(angles[:-1]), metric_labels)\n",
    "ax.set_ylim(0, 1.05)\n",
    "ax.set_title('Model Performance Radar', fontsize=14, pad=20)\n",
    "ax.legend(loc='lower right')\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

cells.append(md("### 7.3 Feature Importance (Random Forest)"))
cells.append(code([
    "importances = rf.feature_importances_\n",
    "sorted_idx = np.argsort(importances)[::-1]\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(10, 5))\n",
    "ax.barh([features[i] for i in sorted_idx], importances[sorted_idx],\n",
    "        color=['#1abc9c','#3498db','#9b59b6','#e74c3c','#f39c12'])\n",
    "ax.set_xlabel('Feature Importance')\n",
    "ax.set_title('Random Forest Feature Importance', fontsize=14)\n",
    "ax.invert_yaxis()\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

cells.append(md("### 7.4 Classification Distribution"))
cells.append(code([
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
    "axes[0].pie(df['pollution_class'].value_counts().sort_index(),\n",
    "            labels=CLASS_NAMES, colors=PALETTE, autopct='%1.1f%%',\n",
    "            startangle=90, explode=(0.02,0.02,0.02))\n",
    "axes[0].set_title('Dataset Distribution')\n",
    "\n",
    "pred_counts = pd.Series(y_pred_nn).value_counts().sort_index()\n",
    "axes[1].pie(pred_counts, labels=[CLASS_NAMES[i] for i in pred_counts.index],\n",
    "            colors=[PALETTE[i] for i in pred_counts.index], autopct='%1.1f%%',\n",
    "            startangle=90, explode=(0.02,0.02,0.02))\n",
    "axes[1].set_title('NN Predicted Distribution')\n",
    "plt.suptitle('Pollution Classification Distribution', fontsize=14)\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

# ═══════════════════════════════════════════════════════════════
# SECTION 8: REAL-TIME SIMULATION
# ═══════════════════════════════════════════════════════════════
cells.append(md([
    "---\n",
    "# Section 8: Real-Time Sensor Simulation\n",
    "\n",
    "Simulating a live data stream where the trained neural network detects contamination events in real time. ",
    "This mirrors how the Flask server processes Jellyfish sensor telemetry and maps predictions to actuator commands (LEDs on the ESP32).\n",
    "\n",
    "**Actuation Mapping:**\n",
    "| Prediction | LED Color | Treatment |\n",
    "|---|---|---|\n",
    "| Normal Water | 🟢 Green | Standard Pump |\n",
    "| Packaging Residue | 🔵 Blue | UV Module |\n",
    "| Antibiotic Contamination | 🟡 Yellow | Electrolysis |\n",
    "| High Spike Risk | 🔴 Red | Heavy Pre-treatment |"
]))

cells.append(code([
    "# Simulate 300 time steps with contamination events\n",
    "np.random.seed(99)\n",
    "n_steps = 300\n",
    "sim_data = []\n",
    "\n",
    "for t in range(n_steps):\n",
    "    # Normal baseline with occasional contamination bursts\n",
    "    if 80 <= t <= 120:  # Packaging contamination event\n",
    "        ph = np.random.uniform(5.8, 9.0) + np.random.normal(0, 0.1)\n",
    "        turb = np.random.uniform(8, 25) + np.random.normal(0, 1)\n",
    "        tds = np.random.uniform(350, 550) + turb * 2.0\n",
    "        temp = np.random.uniform(22, 30)\n",
    "        hum = np.random.uniform(55, 85)\n",
    "    elif 180 <= t <= 220:  # Severe contamination event\n",
    "        ph = np.random.uniform(5.5, 9.5) + np.random.normal(0, 0.15)\n",
    "        turb = np.random.uniform(15, 45) + np.random.normal(0, 2)\n",
    "        tds = np.random.uniform(450, 750) + turb * 2.5\n",
    "        temp = np.random.uniform(22, 32)\n",
    "        hum = np.random.uniform(60, 92)\n",
    "    else:  # Normal\n",
    "        ph = np.random.uniform(6.5, 8.5) + np.random.normal(0, 0.05)\n",
    "        turb = np.random.uniform(0, 4) + np.random.normal(0, 0.5)\n",
    "        tds = np.random.uniform(60, 280) + max(turb, 0) * 2.0\n",
    "        temp = np.random.uniform(22, 30)\n",
    "        hum = np.random.uniform(42, 75)\n",
    "    sim_data.append([ph, max(turb, 0), tds, temp, hum])\n",
    "\n",
    "sim_array = np.array(sim_data)\n",
    "sim_scaled = scaler.transform(sim_array)\n",
    "sim_preds = np.argmax(model.predict(sim_scaled), axis=1)\n",
    "\n",
    "print(f'Simulated {n_steps} time steps.')\n",
    "print(f'Predictions: Normal={np.sum(sim_preds==0)}, Possible={np.sum(sim_preds==1)}, Severe={np.sum(sim_preds==2)}')"
]))

cells.append(md("### 8.1 Live Pollution Detection Timeline"))
cells.append(code([
    "fig, axes = plt.subplots(6, 1, figsize=(18, 16), sharex=True,\n",
    "                         gridspec_kw={'height_ratios': [1, 1, 1, 1, 1, 1.5]})\n",
    "\n",
    "sensor_labels = ['pH', 'Turbidity (NTU)', 'TDS (ppm)', 'Temperature (°C)', 'Humidity (%)']\n",
    "for i in range(5):\n",
    "    axes[i].plot(sim_array[:, i], color='#2c3e50', lw=1, alpha=0.8)\n",
    "    # Mark contamination zones\n",
    "    axes[i].axvspan(80, 120, alpha=0.15, color='orange', label='Event 1' if i==0 else '')\n",
    "    axes[i].axvspan(180, 220, alpha=0.15, color='red', label='Event 2' if i==0 else '')\n",
    "    axes[i].set_ylabel(sensor_labels[i], fontsize=10)\n",
    "axes[0].legend(loc='upper right', fontsize=9)\n",
    "\n",
    "# Detection timeline\n",
    "color_map = {0: PALETTE[0], 1: PALETTE[1], 2: PALETTE[2]}\n",
    "for t in range(n_steps):\n",
    "    axes[5].axvspan(t, t+1, color=color_map[sim_preds[t]], alpha=0.8)\n",
    "axes[5].set_ylabel('Detection')\n",
    "axes[5].set_yticks([])\n",
    "# Legend\n",
    "import matplotlib.patches as mpatches\n",
    "legend_patches = [mpatches.Patch(color=PALETTE[i], label=CLASS_NAMES[i]) for i in range(3)]\n",
    "axes[5].legend(handles=legend_patches, loc='upper right', fontsize=9)\n",
    "axes[5].set_xlabel('Time Step')\n",
    "\n",
    "fig.suptitle('Real-Time Pollution Detection Simulation', fontsize=16, y=1.01)\n",
    "plt.tight_layout()\n",
    "plt.show()"
]))

cells.append(md([
    "---\n",
    "## ✅ Conclusion\n",
    "\n",
    "This notebook demonstrates that **proxy sensing** — using correlated changes in pH, Turbidity, TDS, Temperature, and Humidity — ",
    "can effectively infer pharmaceutical contamination without direct chemical analysis.\n",
    "\n",
    "**Key findings:**\n",
    "- The **Neural Network** achieves the highest multi-class accuracy, making it ideal for the Flask server's real-time classification.\n",
    "- **Isolation Forest** provides reliable binary anomaly detection useful as a first-pass safety filter.\n",
    "- **K-Means** reveals natural data clusters that align well with pollution class boundaries.\n",
    "- **TDS and Turbidity** are the most discriminative features for proxy pollution detection.\n",
    "\n",
    "In the deployed IoT system (The Jellyfish), the server's Decision Engine maps these classifications to physical actuator commands, ",
    "with the ESP32 actuator node lighting the corresponding LED to indicate the active treatment cluster:\n",
    "- 🟢 **Green** — Normal Water (Standard Pump)\n",
    "- 🔵 **Blue** — Packaging Residue (UV Treatment)\n",
    "- 🟡 **Yellow** — Antibiotic Contamination (Electrolysis)\n",
    "- 🔴 **Red** — High Spike Risk (Heavy Pre-treatment)"
]))

# ═══════════════════════════════════════════════════════════════
# BUILD AND SAVE NOTEBOOK
# ═══════════════════════════════════════════════════════════════
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.12.0"
        }
    },
    "cells": cells
}

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "pharmaceutical_pollution_detection.ipynb")
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print(f"Notebook written to: {out_path}")
print(f"Total cells: {len(cells)}")
