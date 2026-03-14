"""
============================================================
 Noisy Dataset Analysis + Comparison with Clean Results
 ─────────────────────────────────────────────────────────
 Generates a dataset with heavy environmental noise
 (uncontrolled field conditions), trains all models,
 saves results to results_noisy/, and creates cross-
 comparison graphs with the clean (controlled) results.
============================================================
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (classification_report, confusion_matrix,
                             precision_score, recall_score, f1_score,
                             accuracy_score, roc_curve, auc,
                             precision_recall_curve, average_precision_score,
                             silhouette_score)
from scipy.stats import mode
import warnings
warnings.filterwarnings('ignore')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.utils import to_categorical

# ─── Setup ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_NOISY = os.path.join(BASE_DIR, "results_noisy")
RESULTS_CLEAN = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_NOISY, exist_ok=True)

plt.rcParams.update({
    'figure.dpi': 150, 'font.size': 11, 'axes.titlesize': 13,
    'axes.labelsize': 11, 'figure.facecolor': 'white',
    'savefig.bbox': 'tight', 'savefig.pad_inches': 0.2
})
sns.set_style('whitegrid')
PALETTE = ['#2ecc71', '#f39c12', '#e74c3c']
CLASS_NAMES = ['Normal Water', 'Possible Contamination', 'Severe Contamination']
features = ['ph', 'turbidity', 'tds', 'temperature', 'humidity']

def save_fig(name):
    path = os.path.join(RESULTS_NOISY, f"{name}.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  ✓ {name}.png")

print("=" * 65)
print("  NOISY DATASET ANALYSIS — Uncontrolled Field Conditions")
print("=" * 65)

# ═══════════════════════════════════════════════════════════════
# SECTION 1: NOISY DATASET GENERATION
# ═══════════════════════════════════════════════════════════════
print("\n[1/6] Generating noisy dataset (uncontrolled conditions)...")
print("  Adding: sensor drift, random spikes, cross-interference,")
print("         temperature fluctuations, missing-value noise,")
print("         and Gaussian measurement noise.\n")

np.random.seed(42)
n_samples = 10000
n_normal = int(n_samples * 0.60)
n_possible = int(n_samples * 0.25)
n_severe = n_samples - n_normal - n_possible

def generate_noisy_class(n, ph_range, tds_range, turb_range, temp_range, hum_range, label):
    ph = np.random.uniform(*ph_range, n) + np.random.normal(0, 0.1, n)
    turbidity = np.random.uniform(*turb_range, n) + np.random.normal(0, 1, n)
    turbidity = np.clip(turbidity, 0, None)
    tds = np.random.uniform(*tds_range, n) + turbidity * np.random.uniform(1.5, 3.0, n) + np.random.normal(0, 10, n)
    temperature = np.random.uniform(*temp_range, n) + np.random.normal(0, 0.5, n)
    humidity = np.random.uniform(*hum_range, n) - (temperature - 25) * 0.8 + np.random.normal(0, 2, n)
    humidity = np.clip(humidity, 20, 100)

    # ──── ENVIRONMENTAL NOISE (Uncontrolled Conditions) ────

    # 1. Heavy Gaussian measurement noise (simulates cheap/uncalibrated sensors)
    ph += np.random.normal(0, 0.4, n)
    tds += np.random.normal(0, 50, n)
    turbidity += np.random.normal(0, 4, n)
    temperature += np.random.normal(0, 2.0, n)
    humidity += np.random.normal(0, 6, n)

    # 2. Random sensor spikes (simulates electrical interference, ~8% of readings)
    spike_mask = np.random.random(n) < 0.08
    ph[spike_mask] += np.random.choice([-2, 2], size=spike_mask.sum()) * np.random.uniform(0.5, 1.5, spike_mask.sum())
    tds[spike_mask] += np.random.uniform(-200, 300, spike_mask.sum())
    turbidity[spike_mask] += np.random.uniform(-10, 30, spike_mask.sum())

    # 3. Slow sensor drift over time (simulates probe fouling, aging)
    drift = np.linspace(0, 1, n)
    ph += drift * np.random.uniform(-0.3, 0.3)
    tds += drift * np.random.uniform(-30, 30)
    turbidity += drift * np.random.uniform(-3, 3)

    # 4. Environmental temperature fluctuations (day/night cycle simulation)
    time_of_day = np.sin(np.linspace(0, 4 * np.pi, n))  # 2 full day cycles
    temperature += time_of_day * 3.0  # ±3°C swing
    humidity -= time_of_day * 5.0     # Inverse relationship

    # 5. Cross-sensor interference (electromagnetic, proximity effects)
    ph += turbidity * np.random.uniform(-0.005, 0.005, n)
    tds += temperature * np.random.uniform(-1, 1, n)

    # 6. Occasional sensor saturation / clipping
    turbidity = np.clip(turbidity, 0, None)
    humidity = np.clip(humidity, 10, 100)
    ph = np.clip(ph, 0, 14)
    tds = np.clip(tds, 0, None)

    return pd.DataFrame({
        'ph': ph, 'turbidity': turbidity, 'tds': tds,
        'temperature': temperature, 'humidity': humidity,
        'pollution_class': label
    })

df_n = generate_noisy_class(n_normal,   (6.5,8.5), (50,300),  (0,5),   (20,35), (40,80), 0)
df_p = generate_noisy_class(n_possible, (5.8,9.0), (300,600), (5,30),  (20,35), (50,90), 1)
df_s = generate_noisy_class(n_severe,   (5.5,9.5), (400,800), (10,50), (20,35), (55,95), 2)

df_noisy = pd.concat([df_n, df_p, df_s], ignore_index=True)
df_noisy = df_noisy.sample(frac=1, random_state=42).reset_index(drop=True)

df_noisy.to_csv(os.path.join(RESULTS_NOISY, "dataset_noisy.csv"), index=False)
df_noisy.describe().round(3).to_csv(os.path.join(RESULTS_NOISY, "dataset_noisy_statistics.csv"))
print(f"  Dataset: {df_noisy.shape[0]} samples | Saved dataset_noisy.csv")

# Also load the clean dataset for comparison
df_clean = pd.read_csv(os.path.join(RESULTS_CLEAN, "dataset.csv"))

# ── Noise comparison visualization ──
fig, axes = plt.subplots(2, 5, figsize=(24, 8))
for i, col in enumerate(features):
    axes[0][i].hist(df_clean[col], bins=50, alpha=0.7, color='#3498db', edgecolor='white')
    axes[0][i].set_title(f'{col.upper()} (Clean)', fontweight='bold')
    axes[1][i].hist(df_noisy[col], bins=50, alpha=0.7, color='#e74c3c', edgecolor='white')
    axes[1][i].set_title(f'{col.upper()} (Noisy)', fontweight='bold')
plt.suptitle('Clean vs Noisy Dataset — Feature Distributions', fontsize=16, y=1.02)
plt.tight_layout()
save_fig("01_clean_vs_noisy_distributions")

# ── Noisy feature histograms by class ──
fig, axes = plt.subplots(1, 5, figsize=(22, 4.5))
for i, col in enumerate(features):
    for cls in [0, 1, 2]:
        axes[i].hist(df_noisy[df_noisy['pollution_class']==cls][col], bins=40, alpha=0.6,
                     label=CLASS_NAMES[cls], color=PALETTE[cls])
    axes[i].set_title(col.upper(), fontweight='bold')
    axes[i].set_ylabel('Frequency')
axes[0].legend(fontsize=7)
plt.suptitle('Noisy Dataset — Feature Distributions by Class', fontsize=15, y=1.02)
plt.tight_layout()
save_fig("02_noisy_feature_histograms")

# ── Correlation heatmap ──
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
cols = features + ['pollution_class']
mask = np.triu(np.ones((len(cols), len(cols)), dtype=bool))
sns.heatmap(df_clean[cols].corr(), mask=mask, annot=True, fmt='.2f', cmap='RdYlGn_r', center=0, ax=axes[0], square=True)
axes[0].set_title('Clean Data Correlations', fontsize=13)
sns.heatmap(df_noisy[cols].corr(), mask=mask, annot=True, fmt='.2f', cmap='RdYlGn_r', center=0, ax=axes[1], square=True)
axes[1].set_title('Noisy Data Correlations', fontsize=13)
plt.suptitle('Correlation Comparison — Clean vs Noisy', fontsize=15)
plt.tight_layout()
save_fig("03_correlation_comparison")

# ── Boxplots ──
fig, axes = plt.subplots(1, 5, figsize=(22, 5))
for i, col in enumerate(features):
    sns.boxplot(data=df_noisy, x='pollution_class', y=col, palette=PALETTE, ax=axes[i])
    axes[i].set_xticklabels(CLASS_NAMES, rotation=25, fontsize=7)
    axes[i].set_title(col.upper(), fontweight='bold')
plt.suptitle('Noisy Data — Sensor Readings by Pollution Class', fontsize=15, y=1.02)
plt.tight_layout()
save_fig("04_noisy_boxplots")

# ═══════════════════════════════════════════════════════════════
# SECTION 2: PREPROCESSING
# ═══════════════════════════════════════════════════════════════
print("\n[2/6] Preprocessing noisy data...")

X_noisy = df_noisy[features].values
y_noisy = df_noisy['pollution_class'].values

X_train, X_test, y_train, y_test = train_test_split(X_noisy, y_noisy, test_size=0.2, random_state=42, stratify=y_noisy)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)
print(f"  Train: {X_train_s.shape} | Test: {X_test_s.shape}")

# ═══════════════════════════════════════════════════════════════
# SECTION 3: ISOLATION FOREST
# ═══════════════════════════════════════════════════════════════
print("\n[3/6] Isolation Forest on noisy data...")

X_normal = X_train_s[y_train == 0]
iso_f = IsolationForest(n_estimators=200, contamination=0.1, random_state=42)
iso_f.fit(X_normal)

iso_pred = iso_f.predict(X_test_s)
iso_scores = iso_f.decision_function(X_test_s)
iso_binary = (iso_pred == -1).astype(int)
y_test_binary = (y_test > 0).astype(int)

n_iso_acc = accuracy_score(y_test_binary, iso_binary)
n_iso_prec = precision_score(y_test_binary, iso_binary)
n_iso_rec = recall_score(y_test_binary, iso_binary)
n_iso_f1 = f1_score(y_test_binary, iso_binary)

print(f"  Accuracy: {n_iso_acc:.4f} | Precision: {n_iso_prec:.4f} | Recall: {n_iso_rec:.4f} | F1: {n_iso_f1:.4f}")

# Anomaly score distribution
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(iso_scores[y_test_binary==0], bins=50, alpha=0.6, label='Normal', color=PALETTE[0])
ax.hist(iso_scores[y_test_binary==1], bins=50, alpha=0.6, label='Contaminated', color=PALETTE[2])
ax.axvline(x=0, color='black', linestyle='--', lw=1.5, label='Boundary')
ax.set_xlabel('Anomaly Score'); ax.set_ylabel('Frequency')
ax.set_title('Isolation Forest — Noisy Data Anomaly Scores'); ax.legend()
plt.tight_layout()
save_fig("05_noisy_anomaly_scores")

# Confusion matrix
cm = confusion_matrix(y_test_binary, iso_binary)
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Normal','Anomaly'], yticklabels=['Normal','Anomaly'], ax=ax)
ax.set_xlabel('Predicted'); ax.set_ylabel('Actual'); ax.set_title('Noisy — Iso. Forest Confusion Matrix')
plt.tight_layout()
save_fig("06_noisy_iso_confusion")

# PCA scatter
pca2 = PCA(n_components=2)
X_test_pca = pca2.fit_transform(X_test_s)
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for cls, name, c in zip([0,1], ['Normal','Contaminated'], [PALETTE[0], PALETTE[2]]):
    m = y_test_binary == cls
    axes[0].scatter(X_test_pca[m,0], X_test_pca[m,1], c=c, s=10, alpha=0.4, label=name)
axes[0].set_title('Ground Truth'); axes[0].legend()
for cls, name, c in zip([0,1], ['Normal','Anomaly'], [PALETTE[0], PALETTE[2]]):
    m = iso_binary == cls
    axes[1].scatter(X_test_pca[m,0], X_test_pca[m,1], c=c, s=10, alpha=0.4, label=name)
axes[1].set_title('Isolation Forest Predictions'); axes[1].legend()
for ax in axes: ax.set_xlabel('PC1'); ax.set_ylabel('PC2')
plt.suptitle('Noisy Data — Anomaly Detection PCA', fontsize=14)
plt.tight_layout()
save_fig("07_noisy_anomaly_pca")

# ═══════════════════════════════════════════════════════════════
# SECTION 4: K-MEANS CLUSTERING
# ═══════════════════════════════════════════════════════════════
print("\n[4/6] K-Means clustering on noisy data...")

inertias, sil = [], []
for k in range(2, 11):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_train_s)
    inertias.append(km.inertia_)
    sil.append(silhouette_score(X_train_s, km.labels_, sample_size=2000))

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(range(2,11), inertias, 'bo-', lw=2); axes[0].axvline(x=3, color='red', linestyle='--', alpha=0.7)
axes[0].set_xlabel('k'); axes[0].set_ylabel('Inertia'); axes[0].set_title('Elbow Method (Noisy)')
axes[1].plot(range(2,11), sil, 'go-', lw=2); axes[1].axvline(x=3, color='red', linestyle='--', alpha=0.7)
axes[1].set_xlabel('k'); axes[1].set_ylabel('Silhouette'); axes[1].set_title('Silhouette (Noisy)')
plt.suptitle('Noisy Data — Optimal Cluster Selection', fontsize=14)
plt.tight_layout()
save_fig("08_noisy_elbow_silhouette")

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
km_labels = kmeans.fit_predict(X_train_s)
km_test_labels = kmeans.predict(X_test_s)

pca3 = PCA(n_components=2)
X_train_pca = pca3.fit_transform(X_train_s)
centroids_pca = pca3.transform(kmeans.cluster_centers_)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for c in range(3):
    m = km_labels == c
    axes[0].scatter(X_train_pca[m,0], X_train_pca[m,1], s=8, alpha=0.3, label=f'Cluster {c}')
axes[0].scatter(centroids_pca[:,0], centroids_pca[:,1], c='black', marker='X', s=200, zorder=5, label='Centroids')
axes[0].set_title('K-Means Clusters (Noisy)'); axes[0].legend()
for c in range(3):
    m = y_train == c
    axes[1].scatter(X_train_pca[m,0], X_train_pca[m,1], s=8, alpha=0.3, color=PALETTE[c], label=CLASS_NAMES[c])
axes[1].set_title('Ground Truth (Noisy)'); axes[1].legend()
plt.suptitle('Noisy Data — K-Means vs Ground Truth', fontsize=14)
plt.tight_layout()
save_fig("09_noisy_kmeans_pca")

km_mapped = np.zeros_like(km_test_labels)
for c in range(3):
    m = km_test_labels == c
    if m.sum() > 0: km_mapped[m] = mode(y_test[m], keepdims=False).mode
n_km_acc = accuracy_score(y_test, km_mapped)
n_km_f1 = f1_score(y_test, km_mapped, average='weighted')

centroids_df = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=features)
centroids_df.index.name = 'Cluster'
centroids_df.round(2).to_csv(os.path.join(RESULTS_NOISY, "cluster_centroids_noisy.csv"))
print(f"  K-Means mapped accuracy: {n_km_acc:.4f}")

# ═══════════════════════════════════════════════════════════════
# SECTION 5: DEEP LEARNING
# ═══════════════════════════════════════════════════════════════
print("\n[5/6] Training Neural Network on noisy data...")

y_train_cat = to_categorical(y_train, 3)
y_test_cat = to_categorical(y_test, 3)

tf.random.set_seed(42)
model = Sequential([
    Dense(64, activation='relu', input_shape=(5,)),
    BatchNormalization(),
    Dropout(0.3),
    Dense(32, activation='relu'),
    BatchNormalization(),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(3, activation='softmax')
])
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

history = model.fit(X_train_s, y_train_cat, validation_data=(X_test_s, y_test_cat),
                    epochs=30, batch_size=32, verbose=1)

# Training curves
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(history.history['accuracy'], label='Train', lw=2, color='#3498db')
axes[0].plot(history.history['val_accuracy'], label='Validation', lw=2, color='#e74c3c')
axes[0].set_title('Noisy — Model Accuracy'); axes[0].set_xlabel('Epoch'); axes[0].set_ylabel('Accuracy'); axes[0].legend()
axes[1].plot(history.history['loss'], label='Train', lw=2, color='#3498db')
axes[1].plot(history.history['val_loss'], label='Validation', lw=2, color='#e74c3c')
axes[1].set_title('Noisy — Model Loss'); axes[1].set_xlabel('Epoch'); axes[1].set_ylabel('Loss'); axes[1].legend()
plt.suptitle('Neural Network Training — Noisy Data', fontsize=14)
plt.tight_layout()
save_fig("10_noisy_training_curves")

y_pred_proba = model.predict(X_test_s)
y_pred_nn = np.argmax(y_pred_proba, axis=1)

n_nn_acc = accuracy_score(y_test, y_pred_nn)
n_nn_prec = precision_score(y_test, y_pred_nn, average='weighted')
n_nn_rec = recall_score(y_test, y_pred_nn, average='weighted')
n_nn_f1 = f1_score(y_test, y_pred_nn, average='weighted')

print(f"\n  NN Accuracy: {n_nn_acc:.4f} | Precision: {n_nn_prec:.4f} | Recall: {n_nn_rec:.4f} | F1: {n_nn_f1:.4f}")

report = classification_report(y_test, y_pred_nn, target_names=CLASS_NAMES, output_dict=True)
pd.DataFrame(report).T.round(4).to_csv(os.path.join(RESULTS_NOISY, "nn_classification_report_noisy.csv"))

# Confusion matrix
cm_nn = confusion_matrix(y_test, y_pred_nn)
fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(cm_nn, annot=True, fmt='d', cmap='Purples', xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES, ax=ax)
ax.set_xlabel('Predicted'); ax.set_ylabel('Actual'); ax.set_title('Noisy — NN Confusion Matrix')
plt.tight_layout()
save_fig("11_noisy_nn_confusion")

# ROC curves
y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
fig, ax = plt.subplots(figsize=(8, 7))
for i in range(3):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_pred_proba[:, i])
    ax.plot(fpr, tpr, lw=2, label=f'{CLASS_NAMES[i]} (AUC={auc(fpr, tpr):.3f})')
ax.plot([0,1],[0,1],'k--', lw=1)
ax.set_xlabel('FPR'); ax.set_ylabel('TPR'); ax.set_title('Noisy — ROC Curves'); ax.legend(loc='lower right')
plt.tight_layout()
save_fig("12_noisy_roc_curves")

# Precision-Recall curves
fig, ax = plt.subplots(figsize=(8, 7))
for i in range(3):
    prec, rec, _ = precision_recall_curve(y_test_bin[:, i], y_pred_proba[:, i])
    ap = average_precision_score(y_test_bin[:, i], y_pred_proba[:, i])
    ax.plot(rec, prec, lw=2, label=f'{CLASS_NAMES[i]} (AP={ap:.3f})')
ax.set_xlabel('Recall'); ax.set_ylabel('Precision'); ax.set_title('Noisy — PR Curves'); ax.legend()
plt.tight_layout()
save_fig("13_noisy_pr_curves")

# Random Forest baseline
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_s, y_train)
rf_pred = rf.predict(X_test_s)
n_rf_acc = accuracy_score(y_test, rf_pred)
n_rf_f1 = f1_score(y_test, rf_pred, average='weighted')

# Feature importance
importances = rf.feature_importances_
sorted_idx = np.argsort(importances)[::-1]
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh([features[i] for i in sorted_idx], importances[sorted_idx],
        color=['#1abc9c','#3498db','#9b59b6','#e74c3c','#f39c12'])
ax.set_xlabel('Feature Importance'); ax.set_title('Noisy — RF Feature Importance'); ax.invert_yaxis()
plt.tight_layout()
save_fig("14_noisy_feature_importance")

# Save training history
pd.DataFrame(history.history).to_csv(os.path.join(RESULTS_NOISY, "training_history_noisy.csv"), index=False)

# Save noisy model comparison
noisy_results = pd.DataFrame({
    'Model': ['Isolation Forest', 'K-Means', 'Neural Network', 'Random Forest'],
    'Accuracy': [n_iso_acc, n_km_acc, n_nn_acc, n_rf_acc],
    'F1_Score': [n_iso_f1, n_km_f1, n_nn_f1, n_rf_f1]
})
noisy_results.to_csv(os.path.join(RESULTS_NOISY, "model_comparison_noisy.csv"), index=False)

# ═══════════════════════════════════════════════════════════════
# SECTION 6: CROSS-COMPARISON — CLEAN vs NOISY
# ═══════════════════════════════════════════════════════════════
print("\n[6/6] Generating cross-comparison graphs (Clean vs Noisy)...")

# Load clean results
clean_results = pd.read_csv(os.path.join(RESULTS_CLEAN, "model_comparison.csv"))
# Convert string columns to numeric (handles '-' entries)
for col in ['Accuracy', 'F1_Score', 'Precision', 'Recall']:
    if col in clean_results.columns:
        clean_results[col] = pd.to_numeric(clean_results[col], errors='coerce')

models = ['Isolation Forest', 'K-Means', 'Neural Network', 'Random Forest']
clean_acc = clean_results.set_index('Model').loc[models, 'Accuracy'].values.astype(float)
noisy_acc = noisy_results.set_index('Model').loc[models, 'Accuracy'].values.astype(float)
clean_f1 = clean_results.set_index('Model').loc[models, 'F1_Score'].values.astype(float)
noisy_f1 = noisy_results.set_index('Model').loc[models, 'F1_Score'].values.astype(float)

# ── 6.1 Accuracy comparison (grouped bar) ──
x = np.arange(len(models))
width = 0.35
fig, ax = plt.subplots(figsize=(12, 6))
bars1 = ax.bar(x - width/2, clean_acc, width, label='Controlled (Clean)', color='#3498db', edgecolor='white', linewidth=1.5)
bars2 = ax.bar(x + width/2, noisy_acc, width, label='Uncontrolled (Noisy)', color='#e74c3c', edgecolor='white', linewidth=1.5)
for b, v in zip(bars1, clean_acc): ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.01, f'{v:.3f}', ha='center', fontsize=10, fontweight='bold')
for b, v in zip(bars2, noisy_acc): ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.01, f'{v:.3f}', ha='center', fontsize=10, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(models, fontsize=11)
ax.set_ylim(0, 1.15); ax.set_ylabel('Accuracy', fontsize=12)
ax.set_title('Model Accuracy — Controlled vs Uncontrolled Conditions', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
save_fig("15_comparison_accuracy")

# ── 6.2 F1 Score comparison ──
fig, ax = plt.subplots(figsize=(12, 6))
bars1 = ax.bar(x - width/2, clean_f1, width, label='Controlled (Clean)', color='#2ecc71', edgecolor='white', linewidth=1.5)
bars2 = ax.bar(x + width/2, noisy_f1, width, label='Uncontrolled (Noisy)', color='#e67e22', edgecolor='white', linewidth=1.5)
for b, v in zip(bars1, clean_f1): ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.01, f'{v:.3f}', ha='center', fontsize=10, fontweight='bold')
for b, v in zip(bars2, noisy_f1): ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.01, f'{v:.3f}', ha='center', fontsize=10, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(models, fontsize=11)
ax.set_ylim(0, 1.15); ax.set_ylabel('F1 Score', fontsize=12)
ax.set_title('Model F1 Score — Controlled vs Uncontrolled Conditions', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
save_fig("16_comparison_f1")

# ── 6.3 Performance drop analysis ──
drops = ((clean_acc - noisy_acc) / clean_acc * 100)
fig, ax = plt.subplots(figsize=(10, 5))
colors_drop = ['#e74c3c' if d > 5 else '#f39c12' if d > 2 else '#2ecc71' for d in drops]
bars = ax.bar(models, drops, color=colors_drop, edgecolor='white', linewidth=1.5)
for b, v in zip(bars, drops): ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.2, f'{v:.1f}%', ha='center', fontsize=12, fontweight='bold')
ax.set_ylabel('Accuracy Drop (%)', fontsize=12)
ax.set_title('Performance Degradation Due to Environmental Noise', fontsize=14, fontweight='bold')
ax.axhline(y=5, color='red', linestyle='--', alpha=0.5, label='5% threshold')
ax.legend()
plt.tight_layout()
save_fig("17_performance_drop")

# ── 6.4 Radar comparison ──
clean_nn = pd.read_csv(os.path.join(RESULTS_CLEAN, "nn_classification_report.csv"), index_col=0)
noisy_nn = pd.read_csv(os.path.join(RESULTS_NOISY, "nn_classification_report_noisy.csv"), index_col=0)

metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
clean_nn_row = clean_results[clean_results['Model']=='Neural Network'].iloc[0]
clean_metrics = [
    float(clean_nn_row['Accuracy']),
    float(clean_nn.loc['weighted avg', 'precision']),
    float(clean_nn.loc['weighted avg', 'recall']),
    float(clean_nn.loc['weighted avg', 'f1-score'])
]
noisy_metrics = [float(n_nn_acc), float(n_nn_prec), float(n_nn_rec), float(n_nn_f1)]

angles = np.linspace(0, 2*np.pi, len(metric_labels), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
for vals, label, color in [(clean_metrics, 'NN (Clean)', '#3498db'), (noisy_metrics, 'NN (Noisy)', '#e74c3c')]:
    vals_p = vals + vals[:1]
    ax.plot(angles, vals_p, 'o-', lw=2.5, label=label, color=color)
    ax.fill(angles, vals_p, alpha=0.12, color=color)
ax.set_thetagrids(np.degrees(angles[:-1]), metric_labels, fontsize=12)
ax.set_ylim(0, 1.05)
ax.set_title('Neural Network — Clean vs Noisy Performance', fontsize=14, pad=25)
ax.legend(loc='lower right', fontsize=11)
plt.tight_layout()
save_fig("18_comparison_radar")

# ── 6.5 Per-class accuracy comparison ──
clean_per_class = [float(clean_nn.loc[c, 'f1-score']) for c in CLASS_NAMES]
noisy_per_class = [float(noisy_nn.loc[c, 'f1-score']) for c in CLASS_NAMES]

fig, ax = plt.subplots(figsize=(12, 6))
x2 = np.arange(len(CLASS_NAMES))
bars1 = ax.bar(x2 - width/2, clean_per_class, width, label='Controlled (Clean)', color='#3498db', edgecolor='white')
bars2 = ax.bar(x2 + width/2, noisy_per_class, width, label='Uncontrolled (Noisy)', color='#e74c3c', edgecolor='white')
for b, v in zip(bars1, clean_per_class): ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.01, f'{v:.3f}', ha='center', fontsize=11, fontweight='bold')
for b, v in zip(bars2, noisy_per_class): ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.01, f'{v:.3f}', ha='center', fontsize=11, fontweight='bold')
ax.set_xticks(x2); ax.set_xticklabels(CLASS_NAMES, fontsize=11)
ax.set_ylim(0, 1.15); ax.set_ylabel('F1 Score', fontsize=12)
ax.set_title('Per-Class F1 Score — Clean vs Noisy', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
save_fig("19_comparison_per_class_f1")

# ── 6.6 Noise impact on class separability (PCA) ──
scaler_clean = StandardScaler()
X_clean_s = scaler_clean.fit_transform(df_clean[features].values)
pca_compare = PCA(n_components=2)
X_clean_pca = pca_compare.fit_transform(X_clean_s)
X_noisy_pca = pca_compare.transform(scaler_clean.transform(df_noisy[features].values))

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for c in range(3):
    m_c = df_clean['pollution_class'].values == c
    m_n = df_noisy['pollution_class'].values == c
    axes[0].scatter(X_clean_pca[m_c, 0], X_clean_pca[m_c, 1], s=5, alpha=0.3, color=PALETTE[c], label=CLASS_NAMES[c])
    axes[1].scatter(X_noisy_pca[m_n, 0], X_noisy_pca[m_n, 1], s=5, alpha=0.3, color=PALETTE[c], label=CLASS_NAMES[c])
axes[0].set_title('Clean Data (PCA)', fontweight='bold'); axes[0].legend(fontsize=8)
axes[1].set_title('Noisy Data (PCA)', fontweight='bold'); axes[1].legend(fontsize=8)
for ax in axes: ax.set_xlabel('PC1'); ax.set_ylabel('PC2')
plt.suptitle('Class Separability — Clean vs Noisy (PCA Projection)', fontsize=15)
plt.tight_layout()
save_fig("20_comparison_pca_separability")

# ── 6.7 Comprehensive summary table ──
summary = pd.DataFrame({
    'Model': models + models,
    'Condition': ['Controlled']*4 + ['Uncontrolled']*4,
    'Accuracy': list(clean_acc) + list(noisy_acc),
    'F1_Score': list(clean_f1) + list(noisy_f1),
    'Accuracy_Drop_%': list(np.zeros(4)) + list(drops)
})
summary.to_csv(os.path.join(RESULTS_NOISY, "comprehensive_comparison.csv"), index=False)

# ═══════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("  ANALYSIS COMPLETE!")
print("=" * 65)

all_files = sorted(os.listdir(RESULTS_NOISY))
print(f"\n  Results saved to: {RESULTS_NOISY}")
print(f"  Total files: {len(all_files)}\n")
for f in all_files:
    size = os.path.getsize(os.path.join(RESULTS_NOISY, f))
    print(f"    {f:50s} ({size/1024:.0f} KB)")

print(f"\n  === MODEL PERFORMANCE SUMMARY ===")
print(f"  {'Model':<20s} {'Clean Acc':>10s} {'Noisy Acc':>10s} {'Drop':>8s}")
print(f"  {'-'*48}")
for i, m in enumerate(models):
    print(f"  {m:<20s} {clean_acc[i]:>10.3f} {noisy_acc[i]:>10.3f} {drops[i]:>7.1f}%")

print(f"\n{'=' * 65}")
print("  DONE!")
print(f"{'=' * 65}")
