# -*- coding: utf-8 -*-
"""PREDIKSI PENYAKIT PARU-PARU.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1MQ42pw-T7JPNnTGzRLdkNONZ6uSLqk-I

**IMPORT LIBRARY**
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_auc_score, roc_curve, precision_recall_curve
from sklearn.decomposition import PCA
import joblib

# Business Understanding
print("Tujuan: Memprediksi penyakit paru-paru berdasarkan gaya hidup dan penyakit bawaan.")

"""**LOAD DATASET**"""

# 1. Load Dataset
df = pd.read_csv('/content/predic_tabel.csv')

"""**EDA**"""

import seaborn as sns
plt.figure(figsize=(12, 6))
sns.boxplot(data=df)
plt.title("Boxplot Distribusi Data")
plt.xticks(rotation=45)  # Memutar label sumbu x jika panjang
plt.show()

print(df.head())

print(df.info())

print(df.describe())

print(df.isnull().sum())

# Daftar fitur gaya hidup
lifestyle_features = ['Usia', 'Jenis_Kelamin', 'Merokok', 'Aktivitas_Begadang', 'Aktivitas_Olahraga', 'Bekerja', 'Penyakit_Bawaan']

# Loop untuk setiap fitur
for feature in lifestyle_features:
    plt.figure(figsize=(6, 4))

    # Buat count plot
    ax = sns.countplot(data=df, x=feature, hue='Hasil', palette='Set2')

    # Tambahkan nilai di atas setiap bar
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}',
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=6, color='black', fontweight='bold')

    # Atur judul dan label
    plt.title(f'{feature}')
    plt.xlabel(feature)
    plt.ylabel('Jumlah')
    plt.legend(title='Hasil', labels=['Tidak', 'Ya'])

    # Tampilkan plot
    plt.show()

"""**PREPROCESSING DATA**

*Data Cleaning*
"""

# - Tangani nilai yang hilang
df.dropna(inplace=True)

print(df.isnull().sum())

"""*Data Duplication*"""

# Menampilkan duplikasi (baris yang berulang)
df.duplicated().sum()

"""*Data Transformation*"""

from sklearn.preprocessing import LabelEncoder
# Mengubah tipe data non-numerik sebelum korelasi
for col in df.select_dtypes(include=['object']).columns:
    df[col], _ = pd.factorize(df[col])

print(df.head())

"""*Feature Selection*"""

# Atribut relevan
kolom_kategorikal = ['Usia', 'Jenis_Kelamin', 'Merokok', 'Aktivitas_Begadang', 'Aktivitas_Olahraga', 'Penyakit_Bawaan']

# Hapus atribut yang tidak relevan
df.drop(columns=['No', 'Asuransi', 'Rumah_Tangga', 'Bekerja'], inplace=True, errors='ignore')

# Hitung korelasi antara fitur
plt.figure(figsize=(8, 6))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.show()

"""*Splitting Data*"""

# Pisahkan fitur (X) dan target (y)
X = df.drop(columns=['Hasil'])
y = df['Hasil']

# Split data: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

"""*Feature Scaling (Normalisasi/Standarisasi Data)*"""

# Standarisasi fitur
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

"""*PCA*"""

# Terapkan PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_train_scaled)

# Konversi hasil PCA ke DataFrame
df_pca = pd.DataFrame(X_pca, columns=["PC1", "PC2"])
df_pca["Hasil"] = y  # Tambahkan label target

# Cek kontribusi setiap komponen utama
explained_variance = pca.explained_variance_ratio_
print(f"Variansi yang dijelaskan oleh PC1: {explained_variance[0]:.2%}")
print(f"Variansi yang dijelaskan oleh PC2: {explained_variance[1]:.2%}")
print(f"Total variansi yang dijelaskan oleh 2 PC: {sum(explained_variance):.2%}")

# Visualisasi hasil PCA
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df_pca, x="PC1", y="PC2", hue="Hasil", palette="coolwarm", alpha=0.7)
plt.title("Visualisasi PCA (2 Komponen Utama)")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.legend(title="Hasil")
plt.show()

# Visualisasi Scree Plot (Elbow Method)
plt.figure(figsize=(8, 5))
plt.plot(range(1, len(pca.explained_variance_ratio_) + 1), pca.explained_variance_ratio_, marker='o', linestyle='--')
plt.xlabel("Jumlah Principal Components")
plt.ylabel("Variansi yang Dijelaskan")
plt.title("Scree Plot PCA")
plt.show()

"""**DATA MINING/MODELING**

*Model Training*
"""

# Inisialisasi model Logistic Regression
logistic_model = LogisticRegression()

# Melatih model dengan data training yang sudah di-scale
logistic_model.fit(X_train_scaled, y_train)

"""*Model Predictions*"""

# Model Prediction
y_pred = logistic_model.predict(X_test_scaled)
y_prob = logistic_model.predict_proba(X_test_scaled)[:, 1]

"""**EVALUATION**

*Cross Validation*
"""

# Cross Validation dengan 5 lipatan
cv_scores = cross_val_score(logistic_model, X, y, cv=5, scoring='accuracy')
print("Cross-Validation Scores:", cv_scores)
print("Mean CV Accuracy:", np.mean(cv_scores))

"""*Best* *Hyperparameters*"""

# Set parameter yang akan disesuaikan
param_grid = {'C': [0.001, 0.01, 0.1, 1, 10, 100]}

# Inisialisasi model
logistic_model_tuned = LogisticRegression()

# GridSearchCV untuk penyetelan hiperparameter
grid_search = GridSearchCV(logistic_model_tuned, param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)

# Parameter terbaik
best_params = grid_search.best_params_
print("Best Hyperparameters:", best_params)

# Model dengan parameter terbaik
logistic_model_best = grid_search.best_estimator_

"""*Classification Report*"""

# Model Evaluation
akurasi = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)
print("Akurasi:", akurasi)
print("ROC-AUC Score:", roc_auc)
print("Laporan Klasifikasi:")
print(classification_report(y_test, y_pred))

report = classification_report(y_test, y_pred, output_dict=True)
report_df = pd.DataFrame(report).transpose()
plt.figure(figsize=(8, 4))
sns.heatmap(report_df.iloc[:-1, :-1], annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Laporan Klasifikasi')
plt.show()

"""2.	Seberapa efektif algoritma logistic regression dalam memprediksi risiko penyakit paru-paru berdasarkan variabel gaya hidup dan penyakit bawaan?

*Confusion Matrix Visualization*
"""

conf_matrix = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 4))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Tidak Terkena', 'Terkena'], yticklabels=['Tidak Terkena', 'Terkena'])
plt.xlabel('Prediksi')
plt.ylabel('Aktual')
plt.title('Confusion Matrix')
plt.show()

"""*ROC AUC*"""

# Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_test, y_prob)
plt.figure(figsize=(8, 6))
plt.plot(recall, precision, marker='.', label='Logistic Regression')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.legend()
plt.title("Precision-Recall Curve")
plt.grid()
plt.show()

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, marker='.', label='Logistic Regression')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()
plt.title("ROC Curve")
plt.grid()
plt.show()

"""1.	Apa saja variabel yang paling signifikan dalam memprediksi penyakit paru-paru menggunakan algoritma logistic regression?"""

# Visualisasi Variabel Pa ling Signifikan (Koefisien Model)
coefficients = pd.DataFrame({'Fitur': X.columns, 'Koefisien': logistic_model.coef_[0]})
coefficients = coefficients.sort_values(by='Koefisien', ascending=False)
plt.figure(figsize=(10,7))
sns.barplot(x=coefficients['Koefisien'], y=coefficients['Fitur'], palette='viridis')
plt.axvline(0, color='black', linestyle='--')
plt.xlabel('Koefisien')
plt.ylabel('Fitur')
plt.title('Variabel Paling Signifikan dalam Prediksi Penyakit Paru-Paru')
plt.show()

"""3.	Bagaimana pengaruh penyakit bawaan terhadap kemungkinan seseorang menderita penyakit paru-paru?"""

# Bar plot for Penyakit_Bawaan vs Hasil
plt.figure(figsize=(6, 4))
sns.countplot(data=df, x='Penyakit_Bawaan', hue='Hasil', palette='Set2')
plt.title('Penyakit Bawaan vs Penyakit Paru-Paru')
plt.xlabel('Penyakit Bawaan')
plt.ylabel('Jumlah')
plt.legend(title='Hasil', labels=['Tidak Ada Penyakit', 'Ada Penyakit'])
plt.show()
# Tambahkan nilai di atas setiap bar
for p in ax.patches:
  ax.annotate(f'{int(p.get_height())}',
  (p.get_x() + p.get_width() / 2., p.get_height()),
  ha='center', va='bottom', fontsize=6, color='black', fontweight='bold')

import matplotlib.pyplot as plt

# Hitung distribusi kelas
class_counts = y.value_counts()
total_samples = len(y)  # Total jumlah baris

# Buat pie chart
plt.figure(figsize=(6, 6))
wedges, texts, autotexts = plt.pie(
    class_counts,
    labels=class_counts.index,
    autopct=lambda p: '{:.1f}%\n({:,.0f})'.format(p, p * sum(class_counts) / 100),  # Persentase + jumlah
    colors=['#3674B5','#FF9D23'],
    startangle=90,
    textprops={'fontsize': 8, 'weight': 'bold'}
)

# Tambahkan judul
plt.title("Distribusi Kelas Target", fontsize=14, fontweight='bold')

# Tambahkan jumlah baris per kelas di luar chart
for i, (label, count) in enumerate(class_counts.items()):
    print(f"Kelas {label}: {count} baris ({(count/total_samples)*100:.1f}%)")

# Tampilkan pie chart
plt.show()

"""**SAVE MODEL**"""

# Simpan model menggunakan joblib
joblib.dump(logistic_model, "logistic_regression_model.sav")
print("✅ Model berhasil disimpan!")