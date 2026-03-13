"""
============================================================
 Pharmaceutical Pollution Detection — Full Analysis Runner
 Saves ALL graphs (PNG) and data (CSV) to results/ folder.
============================================================
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving
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

# TF import
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.utils import to_categorical

# ─── Setup ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

plt.rcParams.update({
    'figure.dpi': 150,
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.facecolor': 'white',
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.2
})
sns.set_style('whitegrid')
PALETTE = ['#2ecc71', '#f39c12', '#e74c3c']
CLASS_NAMES = ['Normal Water', 'Possible Contamination', 'Severe Contamination']
features = ['ph', 'turbidity', 'tds', 'temperature', 'humidity']

def save_fig(name):
    path = os.path.join(RESULTS_DIR, f"{name}.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  ✓ Saved {name}.png")

print("=" * 60)
print("  PHARMACEUTICAL POLLUTION DETECTION — FULL ANALYSIS")
print("=" * 60)

# ═══════════════════════════════════════════════════════════════
# SECTION 1: DATASET GENERATION
# ═══════════════════════════════════════════════════════════════
print("\n[1/8] Generating synthetic dataset...")

np.random.seed(42)
n_samples = 10000
n_normal = int(n_samples * 0.60)
n_possible = int(n_samples * 0.25)
n_severe = n_samples - n_normal - n_possible

def generate_class(n, ph_range, tds_range, turb_range, temp_range, hum_range, label):
    ph = np.random.uniform(*ph_range, n) + np.random.normal(0, 0.1, n)
    turbidity = np.random.uniform(*turb_range, n) + np.random.normal(0, 1, n)
    turbidity = np.clip(turbidity, 0, None)
    tds = np.random.uniform(*tds_range, n) + turbidity * np.random.uniform(1.5, 3.0, n) + np.random.normal(0, 10, n)
    temperature = np.random.uniform(*temp_range, n) + np.random.normal(0, 0.5, n)
    humidity = np.random.uniform(*hum_range, n) - (temperature - 25) * 0.8 + np.random.normal(0, 2, n)
    humidity = np.clip(humidity, 20, 100)
    return pd.DataFrame({
        'ph': ph, 'turbidity': turbidity, 'tds': tds,
        'temperature': temperature, 'humidity': humidity,
        'pollution_class': label
    })

df_normal = generate_class(n_normal, (6.5,8.5), (50,300), (0,5), (20,35), (40,80), 0)
df_possible = generate_class(n_possible, (5.8,9.0), (300,600), (5,30), (20,35), (50,90), 1)
df_severe = generate_class(n_severe, (5.5,9.5), (400,800), (10,50), (20,35), (55,95), 2)

df = pd.concat([df_normal, df_possible, df_severe], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save dataset
df.to_csv(os.path.join(RESULTS_DIR, "dataset.csv"), index=False)
print(f"  ✓ Dataset: {df.shape[0]} samples, {df.shape[1]} columns")
print(f"  ✓ Saved dataset.csv")

# Save summary stats
stats = df.describe().round(3)
stats.to_csv(os.path.join(RESULTS_DIR, "dataset_statistics.csv"))
print(f"  ✓ Saved dataset_statistics.csv")

# ═══════════════════════════════════════════════════════════════
# SECTION 2: DATA VISUALIZATION
# ═══════════════════════════════════════════════════════════════
print("\n[2/8] Generating visualizations...")

# 2.1 Feature distribution histograms
fig, axes = plt.subplots(1, 5, figsize=(22, 4.5))
for i, col in enumerate(features):
    for cls in [0, 1, 2]:
        axes[i].hist(df[df['pollution_class']==cls][col], bins=40, alpha=0.6,
                     label=CLASS_NAMES[cls], color=PALETTE[cls])
    axes[i].set_title(col.upper(), fontweight='bold')
    axes[i].set_xlabel(col)
    axes[i].set_ylabel('Frequency')
axes[0].legend(fontsize=7)
plt.suptitle('Feature Distributions by Pollution Class', fontsize=15, y=1.02)
plt.tight_layout()
save_fig("01_feature_histograms")

# 2.2 Correlation heatmap
fig, ax = plt.subplots(figsize=(8, 6))
corr = df[features + ['pollution_class']].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn_r',
            center=0, square=True, linewidths=1, ax=ax)
ax.set_title('Correlation Matrix of Sensor Features', fontsize=14)
plt.tight_layout()
save_fig("02_correlation_heatmap")

# 2.3 Pairplot
g = sns.pairplot(df.sample(2000, random_state=42), hue='pollution_class',
                 vars=features, palette=PALETTE, diag_kind='kde',
                 plot_kws={'alpha': 0.5, 's': 12})
g.figure.suptitle('Pairwise Feature Relationships', y=1.01, fontsize=15)
g.savefig(os.path.join(RESULTS_DIR, "03_pairplot.png"), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved 03_pairplot.png")

# 2.4 Boxplots
fig, axes = plt.subplots(1, 5, figsize=(22, 5))
for i, col in enumerate(features):
    sns.boxplot(data=df, x='pollution_class', y=col, palette=PALETTE, ax=axes[i])
    axes[i].set_xticklabels(CLASS_NAMES, rotation=25, fontsize=7)
    axes[i].set_title(col.upper(), fontweight='bold')
plt.suptitle('Sensor Readings by Pollution Class', fontsize=15, y=1.02)
plt.tight_layout()
save_fig("04_boxplots")

# 2.5 Time-series simulation
fig, axes = plt.subplots(5, 1, figsize=(16, 12), sharex=True)
time_slice = df.head(500)
colors_ts = [PALETTE[int(c)] for c in time_slice['pollution_class']]
for i, col in enumerate(features):
    axes[i].scatter(range(len(time_slice)), time_slice[col], c=colors_ts, s=4, alpha=0.7)
    axes[i].plot(time_slice[col].rolling(20).mean().values, color='black', lw=1.2, alpha=0.7)
    axes[i].set_ylabel(col.upper(), fontsize=10)
axes[-1].set_xlabel('Sample Index (simulated time)')
fig.suptitle('Simulated Time-Series of Sensor Readings', fontsize=15)
plt.tight_layout()
save_fig("05_timeseries_simulation")

# ═══════════════════════════════════════════════════════════════
# SECTION 3: PREPROCESSING
# ═══════════════════════════════════════════════════════════════
print("\n[3/8] Preprocessing data...")

X = df[features].values
y = df['pollution_class'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"  Training: {X_train_scaled.shape}, Testing: {X_test_scaled.shape}")

# Scaled vs Raw
fig, axes = plt.subplots(2, 5, figsize=(22, 7))
for i, col in enumerate(features):
    axes[0][i].hist(X_train[:, i], bins=40, color='#3498db', alpha=0.7, edgecolor='white')
    axes[0][i].set_title(f'{col} (Raw)', fontweight='bold')
    axes[1][i].hist(X_train_scaled[:, i], bins=40, color='#e74c3c', alpha=0.7, edgecolor='white')
    axes[1][i].set_title(f'{col} (Scaled)', fontweight='bold')
plt.suptitle('Raw vs. StandardScaler Normalized Features', fontsize=15, y=1.02)
plt.tight_layout()
save_fig("06_raw_vs_scaled")

# ═══════════════════════════════════════════════════════════════
# SECTION 4: ANOMALY DETECTION
# ═══════════════════════════════════════════════════════════════
print("\n[4/8] Running Isolation Forest anomaly detection...")

X_normal = X_train_scaled[y_train == 0]
iso_forest = IsolationForest(n_estimators=200, contamination=0.1, random_state=42)
iso_forest.fit(X_normal)

iso_pred = iso_forest.predict(X_test_scaled)
iso_scores = iso_forest.decision_function(X_test_scaled)

iso_binary = (iso_pred == -1).astype(int)
y_test_binary = (y_test > 0).astype(int)

iso_precision = precision_score(y_test_binary, iso_binary)
iso_recall = recall_score(y_test_binary, iso_binary)
iso_f1 = f1_score(y_test_binary, iso_binary)
iso_accuracy = accuracy_score(y_test_binary, iso_binary)

print(f"  Accuracy:  {iso_accuracy:.4f}")
print(f"  Precision: {iso_precision:.4f}")
print(f"  Recall:    {iso_recall:.4f}")
print(f"  F1 Score:  {iso_f1:.4f}")

# 4.1 Anomaly score distribution
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(iso_scores[y_test_binary==0], bins=50, alpha=0.6, label='Normal', color=PALETTE[0])
ax.hist(iso_scores[y_test_binary==1], bins=50, alpha=0.6, label='Contaminated', color=PALETTE[2])
ax.axvline(x=0, color='black', linestyle='--', lw=1.5, label='Decision Boundary')
ax.set_xlabel('Anomaly Score')
ax.set_ylabel('Frequency')
ax.set_title('Isolation Forest Anomaly Score Distribution')
ax.legend()
plt.tight_layout()
save_fig("07_anomaly_score_distribution")

# 4.2 PCA scatter
pca_2d = PCA(n_components=2)
X_test_pca = pca_2d.fit_transform(X_test_scaled)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for cls, name, c in zip([0,1], ['Normal','Contaminated'], [PALETTE[0], PALETTE[2]]):
    mask = y_test_binary == cls
    axes[0].scatter(X_test_pca[mask,0], X_test_pca[mask,1], c=c, s=10, alpha=0.5, label=name)
axes[0].set_title('Ground Truth')
axes[0].legend()
for cls, name, c in zip([0,1], ['Normal','Anomaly'], [PALETTE[0], PALETTE[2]]):
    mask = iso_binary == cls
    axes[1].scatter(X_test_pca[mask,0], X_test_pca[mask,1], c=c, s=10, alpha=0.5, label=name)
axes[1].set_title('Isolation Forest Predictions')
axes[1].legend()
for ax in axes:
    ax.set_xlabel('PC1'); ax.set_ylabel('PC2')
plt.suptitle('Anomaly Detection — PCA Projection', fontsize=14)
plt.tight_layout()
save_fig("08_anomaly_scatter_pca")

# 4.3 Decision boundary (2D PCA projection)
pca_2d_train = PCA(n_components=2)
X_normal_pca = pca_2d_train.fit_transform(X_normal)
iso_2d = IsolationForest(n_estimators=200, contamination=0.1, random_state=42)
iso_2d.fit(X_normal_pca)

xx, yy = np.meshgrid(
    np.linspace(X_normal_pca[:,0].min()-1, X_normal_pca[:,0].max()+1, 200),
    np.linspace(X_normal_pca[:,1].min()-1, X_normal_pca[:,1].max()+1, 200)
)
Z = iso_2d.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

fig, ax = plt.subplots(figsize=(10, 8))
ax.contourf(xx, yy, Z, levels=np.linspace(Z.min(), Z.max(), 25), cmap='RdYlGn')
ax.contour(xx, yy, Z, levels=[0], linewidths=2, colors='black')
ax.scatter(X_normal_pca[:,0], X_normal_pca[:,1], s=5, c='white', alpha=0.3, edgecolors='black', linewidths=0.1)
ax.set_title('Isolation Forest Decision Boundary (2D PCA)', fontsize=14)
ax.set_xlabel('PC1'); ax.set_ylabel('PC2')
plt.tight_layout()
save_fig("09_decision_boundary")

# 4.4 Confusion matrix
cm = confusion_matrix(y_test_binary, iso_binary)
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Normal', 'Anomaly'], yticklabels=['Normal', 'Anomaly'], ax=ax)
ax.set_xlabel('Predicted'); ax.set_ylabel('Actual')
ax.set_title('Isolation Forest — Confusion Matrix')
plt.tight_layout()
save_fig("10_iso_confusion_matrix")

# ═══════════════════════════════════════════════════════════════
# SECTION 5: CLUSTERING
# ═══════════════════════════════════════════════════════════════
print("\n[5/8] Running K-Means clustering...")

# 5.1 Elbow + Silhouette
inertias = []
sil_scores = []
K_range = range(2, 11)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_train_scaled)
    inertias.append(km.inertia_)
    sil_scores.append(silhouette_score(X_train_scaled, km.labels_, sample_size=2000))

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(list(K_range), inertias, 'bo-', lw=2)
axes[0].set_xlabel('Number of Clusters (k)'); axes[0].set_ylabel('Inertia')
axes[0].set_title('Elbow Method')
axes[0].axvline(x=3, color='red', linestyle='--', alpha=0.7, label='k=3')
axes[0].legend()
axes[1].plot(list(K_range), sil_scores, 'go-', lw=2)
axes[1].set_xlabel('Number of Clusters (k)'); axes[1].set_ylabel('Silhouette Score')
axes[1].set_title('Silhouette Analysis')
axes[1].axvline(x=3, color='red', linestyle='--', alpha=0.7, label='k=3')
axes[1].legend()
plt.suptitle('Optimal Cluster Selection', fontsize=14)
plt.tight_layout()
save_fig("11_elbow_silhouette")

# 5.2 K-Means k=3
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
km_labels = kmeans.fit_predict(X_train_scaled)
km_test_labels = kmeans.predict(X_test_scaled)

pca3 = PCA(n_components=2)
X_train_pca = pca3.fit_transform(X_train_scaled)
centroids_pca = pca3.transform(kmeans.cluster_centers_)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for c in range(3):
    mask = km_labels == c
    axes[0].scatter(X_train_pca[mask,0], X_train_pca[mask,1], s=8, alpha=0.4, label=f'Cluster {c}')
axes[0].scatter(centroids_pca[:,0], centroids_pca[:,1], c='black', marker='X', s=200, zorder=5, label='Centroids')
axes[0].set_title('K-Means Clusters (PCA)'); axes[0].legend()
for c in range(3):
    mask = y_train == c
    axes[1].scatter(X_train_pca[mask,0], X_train_pca[mask,1], s=8, alpha=0.4, color=PALETTE[c], label=CLASS_NAMES[c])
axes[1].set_title('Ground Truth Classes (PCA)'); axes[1].legend()
for ax in axes:
    ax.set_xlabel('PC1'); ax.set_ylabel('PC2')
plt.suptitle('K-Means Clustering vs Ground Truth', fontsize=14)
plt.tight_layout()
save_fig("12_kmeans_clusters_pca")

# 5.3 Cluster scatter plots (feature pairs)
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
pairs = [(0,1),(0,2),(1,2),(2,3),(3,4),(0,4)]
for idx, (i, j) in enumerate(pairs):
    ax = axes[idx//3][idx%3]
    for c in range(3):
        mask = km_labels == c
        ax.scatter(X_train[mask, i], X_train[mask, j], s=8, alpha=0.3, label=f'Cluster {c}')
    ax.set_xlabel(features[i].upper()); ax.set_ylabel(features[j].upper())
    ax.set_title(f'{features[i]} vs {features[j]}')
axes[0][0].legend(fontsize=8)
plt.suptitle('K-Means Cluster Scatter Plots', fontsize=14)
plt.tight_layout()
save_fig("13_cluster_scatter_plots")

# 5.4 Centroids
centroids_df = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=features)
centroids_df.index.name = 'Cluster'
centroids_df.round(2).to_csv(os.path.join(RESULTS_DIR, "cluster_centroids.csv"))
print(f"  ✓ Saved cluster_centroids.csv")
print(centroids_df.round(2).to_string())

# ═══════════════════════════════════════════════════════════════
# SECTION 6: DEEP LEARNING
# ═══════════════════════════════════════════════════════════════
print("\n[6/8] Training Deep Learning model...")

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
model.summary()

history = model.fit(
    X_train_scaled, y_train_cat,
    validation_data=(X_test_scaled, y_test_cat),
    epochs=30, batch_size=32, verbose=1
)

# 6.1 Training curves
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(history.history['accuracy'], label='Train', lw=2, color='#3498db')
axes[0].plot(history.history['val_accuracy'], label='Validation', lw=2, color='#e74c3c')
axes[0].set_title('Model Accuracy', fontweight='bold'); axes[0].set_xlabel('Epoch'); axes[0].set_ylabel('Accuracy'); axes[0].legend()
axes[1].plot(history.history['loss'], label='Train', lw=2, color='#3498db')
axes[1].plot(history.history['val_loss'], label='Validation', lw=2, color='#e74c3c')
axes[1].set_title('Model Loss', fontweight='bold'); axes[1].set_xlabel('Epoch'); axes[1].set_ylabel('Loss'); axes[1].legend()
plt.suptitle('Neural Network Training History', fontsize=14)
plt.tight_layout()
save_fig("14_training_curves")

# Predictions
y_pred_proba = model.predict(X_test_scaled)
y_pred_nn = np.argmax(y_pred_proba, axis=1)

nn_accuracy = accuracy_score(y_test, y_pred_nn)
nn_precision = precision_score(y_test, y_pred_nn, average='weighted')
nn_recall = recall_score(y_test, y_pred_nn, average='weighted')
nn_f1 = f1_score(y_test, y_pred_nn, average='weighted')

print(f"\n  === Neural Network Results ===")
print(f"  Accuracy:  {nn_accuracy:.4f}")
print(f"  Precision: {nn_precision:.4f}")
print(f"  Recall:    {nn_recall:.4f}")
print(f"  F1 Score:  {nn_f1:.4f}")

report = classification_report(y_test, y_pred_nn, target_names=CLASS_NAMES, output_dict=True)
pd.DataFrame(report).T.round(4).to_csv(os.path.join(RESULTS_DIR, "nn_classification_report.csv"))
print(f"  ✓ Saved nn_classification_report.csv")

# 6.2 Confusion matrix
cm_nn = confusion_matrix(y_test, y_pred_nn)
fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(cm_nn, annot=True, fmt='d', cmap='Purples',
            xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES, ax=ax)
ax.set_xlabel('Predicted'); ax.set_ylabel('Actual')
ax.set_title('Neural Network — Confusion Matrix')
plt.tight_layout()
save_fig("15_nn_confusion_matrix")

# 6.3 ROC curve
y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
fig, ax = plt.subplots(figsize=(8, 7))
for i in range(3):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_pred_proba[:, i])
    roc_auc = auc(fpr, tpr)
    ax.plot(fpr, tpr, lw=2, label=f'{CLASS_NAMES[i]} (AUC={roc_auc:.3f})')
ax.plot([0,1],[0,1],'k--', lw=1)
ax.set_xlabel('False Positive Rate'); ax.set_ylabel('True Positive Rate')
ax.set_title('ROC Curves (One-vs-Rest)'); ax.legend(loc='lower right')
plt.tight_layout()
save_fig("16_roc_curves")

# 6.4 Precision-Recall curve
fig, ax = plt.subplots(figsize=(8, 7))
for i in range(3):
    prec, rec, _ = precision_recall_curve(y_test_bin[:, i], y_pred_proba[:, i])
    ap = average_precision_score(y_test_bin[:, i], y_pred_proba[:, i])
    ax.plot(rec, prec, lw=2, label=f'{CLASS_NAMES[i]} (AP={ap:.3f})')
ax.set_xlabel('Recall'); ax.set_ylabel('Precision')
ax.set_title('Precision-Recall Curves'); ax.legend()
plt.tight_layout()
save_fig("17_precision_recall_curves")

# Save training history
hist_df = pd.DataFrame(history.history)
hist_df.to_csv(os.path.join(RESULTS_DIR, "training_history.csv"), index=False)
print(f"  ✓ Saved training_history.csv")

# ═══════════════════════════════════════════════════════════════
# SECTION 7: MODEL COMPARISON
# ═══════════════════════════════════════════════════════════════
print("\n[7/8] Comparing models...")

# Random Forest baseline
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_scaled, y_train)
rf_pred = rf.predict(X_test_scaled)
rf_accuracy = accuracy_score(y_test, rf_pred)
rf_f1 = f1_score(y_test, rf_pred, average='weighted')

# K-Means mapped accuracy
km_mapped = np.zeros_like(km_test_labels)
for c in range(3):
    mask = km_test_labels == c
    if mask.sum() > 0:
        km_mapped[mask] = mode(y_test[mask], keepdims=False).mode
km_accuracy = accuracy_score(y_test, km_mapped)
km_f1 = f1_score(y_test, km_mapped, average='weighted')

results_df = pd.DataFrame({
    'Model': ['Isolation Forest', 'K-Means', 'Neural Network', 'Random Forest'],
    'Accuracy': [iso_accuracy, km_accuracy, nn_accuracy, rf_accuracy],
    'F1_Score': [iso_f1, km_f1, nn_f1, rf_f1],
    'Precision': [iso_precision, '-', nn_precision, precision_score(y_test, rf_pred, average='weighted')],
    'Recall': [iso_recall, '-', nn_recall, recall_score(y_test, rf_pred, average='weighted')]
})
results_df.to_csv(os.path.join(RESULTS_DIR, "model_comparison.csv"), index=False)
print(f"  ✓ Saved model_comparison.csv")

# 7.1 Accuracy bar chart
fig, ax = plt.subplots(figsize=(10, 5))
colors_bar = ['#3498db', '#e67e22', '#9b59b6', '#2ecc71']
models = ['Isolation Forest', 'K-Means', 'Neural Network', 'Random Forest']
accs = [iso_accuracy, km_accuracy, nn_accuracy, rf_accuracy]
bars = ax.bar(models, accs, color=colors_bar, edgecolor='white', linewidth=1.5)
for bar, val in zip(bars, accs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{val:.3f}', ha='center', fontsize=12, fontweight='bold')
ax.set_ylim(0, 1.15); ax.set_ylabel('Accuracy')
ax.set_title('Model Accuracy Comparison', fontsize=14)
plt.tight_layout()
save_fig("18_accuracy_comparison")

# 7.2 Radar chart
metrics_nn = [nn_accuracy, nn_precision, nn_recall, nn_f1]
metrics_iso = [iso_accuracy, iso_precision, iso_recall, iso_f1]
metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1 Score']

angles = np.linspace(0, 2*np.pi, len(metric_labels), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
for vals, label, color in [(metrics_nn, 'Neural Network', '#9b59b6'),
                            (metrics_iso, 'Isolation Forest', '#3498db')]:
    vals_plot = vals + vals[:1]
    ax.plot(angles, vals_plot, 'o-', lw=2, label=label, color=color)
    ax.fill(angles, vals_plot, alpha=0.15, color=color)
ax.set_thetagrids(np.degrees(angles[:-1]), metric_labels)
ax.set_ylim(0, 1.05)
ax.set_title('Model Performance Radar', fontsize=14, pad=20)
ax.legend(loc='lower right')
plt.tight_layout()
save_fig("19_radar_chart")

# 7.3 Feature importance
importances = rf.feature_importances_
sorted_idx = np.argsort(importances)[::-1]
fig, ax = plt.subplots(figsize=(10, 5))
colors_fi = ['#1abc9c','#3498db','#9b59b6','#e74c3c','#f39c12']
ax.barh([features[i] for i in sorted_idx], importances[sorted_idx],
        color=[colors_fi[i] for i in range(5)])
ax.set_xlabel('Feature Importance')
ax.set_title('Random Forest Feature Importance', fontsize=14)
ax.invert_yaxis()
plt.tight_layout()
save_fig("20_feature_importance")

# 7.4 Classification distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].pie(df['pollution_class'].value_counts().sort_index(),
            labels=CLASS_NAMES, colors=PALETTE, autopct='%1.1f%%',
            startangle=90, explode=(0.02,0.02,0.02))
axes[0].set_title('Dataset Distribution')
pred_counts = pd.Series(y_pred_nn).value_counts().sort_index()
axes[1].pie(pred_counts, labels=[CLASS_NAMES[i] for i in pred_counts.index],
            colors=[PALETTE[i] for i in pred_counts.index], autopct='%1.1f%%',
            startangle=90, explode=(0.02,0.02,0.02))
axes[1].set_title('NN Predicted Distribution')
plt.suptitle('Pollution Classification Distribution', fontsize=14)
plt.tight_layout()
save_fig("21_classification_distribution")

# ═══════════════════════════════════════════════════════════════
# SECTION 8: REAL-TIME SIMULATION
# ═══════════════════════════════════════════════════════════════
print("\n[8/8] Running real-time sensor simulation...")

np.random.seed(99)
n_steps = 300
sim_data = []
for t in range(n_steps):
    if 80 <= t <= 120:
        ph = np.random.uniform(5.8, 9.0) + np.random.normal(0, 0.1)
        turb = np.random.uniform(8, 25) + np.random.normal(0, 1)
        tds = np.random.uniform(350, 550) + turb * 2.0
        temp = np.random.uniform(22, 30)
        hum = np.random.uniform(55, 85)
    elif 180 <= t <= 220:
        ph = np.random.uniform(5.5, 9.5) + np.random.normal(0, 0.15)
        turb = np.random.uniform(15, 45) + np.random.normal(0, 2)
        tds = np.random.uniform(450, 750) + turb * 2.5
        temp = np.random.uniform(22, 32)
        hum = np.random.uniform(60, 92)
    else:
        ph = np.random.uniform(6.5, 8.5) + np.random.normal(0, 0.05)
        turb = np.random.uniform(0, 4) + np.random.normal(0, 0.5)
        tds = np.random.uniform(60, 280) + max(turb, 0) * 2.0
        temp = np.random.uniform(22, 30)
        hum = np.random.uniform(42, 75)
    sim_data.append([ph, max(turb, 0), tds, temp, hum])

sim_array = np.array(sim_data)
sim_scaled = scaler.transform(sim_array)
sim_preds = np.argmax(model.predict(sim_scaled), axis=1)

# Save simulation data
sim_df = pd.DataFrame(sim_array, columns=features)
sim_df['predicted_class'] = sim_preds
sim_df['class_name'] = [CLASS_NAMES[p] for p in sim_preds]
sim_df.to_csv(os.path.join(RESULTS_DIR, "realtime_simulation.csv"), index=False)
print(f"  ✓ Saved realtime_simulation.csv")

# 8.1 Full detection timeline
fig, axes = plt.subplots(6, 1, figsize=(18, 16), sharex=True,
                         gridspec_kw={'height_ratios': [1, 1, 1, 1, 1, 1.5]})
sensor_labels = ['pH', 'Turbidity (NTU)', 'TDS (ppm)', 'Temperature (°C)', 'Humidity (%)']
for i in range(5):
    axes[i].plot(sim_array[:, i], color='#2c3e50', lw=1, alpha=0.8)
    axes[i].axvspan(80, 120, alpha=0.15, color='orange', label='Event 1' if i==0 else '')
    axes[i].axvspan(180, 220, alpha=0.15, color='red', label='Event 2' if i==0 else '')
    axes[i].set_ylabel(sensor_labels[i], fontsize=10)
axes[0].legend(loc='upper right', fontsize=9)

color_map = {0: PALETTE[0], 1: PALETTE[1], 2: PALETTE[2]}
for t in range(n_steps):
    axes[5].axvspan(t, t+1, color=color_map[sim_preds[t]], alpha=0.8)
axes[5].set_ylabel('Detection'); axes[5].set_yticks([])
legend_patches = [mpatches.Patch(color=PALETTE[i], label=CLASS_NAMES[i]) for i in range(3)]
axes[5].legend(handles=legend_patches, loc='upper right', fontsize=9)
axes[5].set_xlabel('Time Step')
fig.suptitle('Real-Time Pollution Detection Simulation', fontsize=16, y=1.01)
plt.tight_layout()
save_fig("22_realtime_detection_timeline")

# 8.2 Sensor trend graphs with rolling averages
fig, axes = plt.subplots(5, 1, figsize=(16, 14), sharex=True)
for i in range(5):
    axes[i].plot(sim_array[:, i], color='#bdc3c7', lw=0.8, alpha=0.7, label='Raw')
    axes[i].plot(pd.Series(sim_array[:, i]).rolling(15).mean(), color='#2c3e50', lw=2, label='Trend (MA-15)')
    axes[i].set_ylabel(sensor_labels[i])
    axes[i].legend(loc='upper right', fontsize=8)
axes[-1].set_xlabel('Time Step')
fig.suptitle('Sensor Reading Trends with Rolling Average', fontsize=15)
plt.tight_layout()
save_fig("23_sensor_trends")

# 8.3 Anomaly markers on timeline
fig, ax = plt.subplots(figsize=(18, 5))
colors_timeline = [PALETTE[p] for p in sim_preds]
ax.scatter(range(n_steps), sim_array[:, 2], c=colors_timeline, s=20, alpha=0.8, zorder=2)  # TDS
anomaly_mask = sim_preds > 0
ax.scatter(np.where(anomaly_mask)[0], sim_array[anomaly_mask, 2],
           facecolors='none', edgecolors='red', s=80, linewidths=1.5, zorder=3, label='Anomaly Detected')
ax.plot(pd.Series(sim_array[:, 2]).rolling(15).mean(), color='black', lw=1.5, alpha=0.5, label='TDS Trend')
ax.set_xlabel('Time Step'); ax.set_ylabel('TDS (ppm)')
ax.set_title('Detected Anomaly Markers on TDS Timeline', fontsize=14)
legend_patches2 = [mpatches.Patch(color=PALETTE[i], label=CLASS_NAMES[i]) for i in range(3)]
legend_patches2.append(plt.Line2D([0],[0], marker='o', color='w', markerfacecolor='none', markeredgecolor='red', markersize=10, label='Anomaly Marker'))
ax.legend(handles=legend_patches2, loc='upper left', fontsize=9)
plt.tight_layout()
save_fig("24_anomaly_markers_timeline")

# ═══════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("  ALL ANALYSIS COMPLETE!")
print("=" * 60)

# List all saved files
all_files = sorted(os.listdir(RESULTS_DIR))
print(f"\n  Results saved to: {RESULTS_DIR}")
print(f"  Total files: {len(all_files)}\n")
for f in all_files:
    size = os.path.getsize(os.path.join(RESULTS_DIR, f))
    print(f"    {f:45s} ({size/1024:.0f} KB)")

print(f"\n{'=' * 60}")
print("  DONE!")
print(f"{'=' * 60}")
