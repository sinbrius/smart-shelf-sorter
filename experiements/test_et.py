import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

# 1. PARAMETRELER VE MODELİ YÜKLEME
DATA_DIR = r"C:\Users\Feyzanur\OneDrive\Desktop\projeler\derinogrenme\archive (1)\data\testing_data"
IMG_SIZE = (28, 28)
CHAR_LIST = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

print("🧠 Eğitilen yapay zeka modeli hafızaya yükleniyor...")
model = tf.keras.models.load_model('kitap_ocr_cnn_model.keras')

# Testing_data klasöründen rastgele bir harf sınıfı seçelim
siniflar = [s for s in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, s))]
rastgele_sinif = np.random.choice(siniflar)
sinif_yolu = os.path.join(DATA_DIR, rastgele_sinif)

# Seçilen sınıftan rastgele bir resim alalım
rastgele_resim = np.random.choice(os.listdir(sinif_yolu))
resim_yolu = os.path.join(sinif_yolu, rastgele_resim)

# 2. GÖRÜNTÜYÜ MODELE HAZIRLAMA
img = cv2.imread(resim_yolu, cv2.IMREAD_GRAYSCALE)
img_resized = cv2.resize(img, IMG_SIZE)
img_normalized = img_resized.astype('float32') / 255.0
img_input = np.expand_dims(np.expand_dims(img_normalized, 0), -1) # (1, 28, 28, 1)

# 3. TAHMİN ETME
predictions = model.predict(img_input, verbose=0)
tahmin_indeksi = np.argmax(predictions)
tahmin_karakteri = CHAR_LIST[tahmin_indeksi]

# 4. EKRANA BASMA
print(f"\n📂 Seçilen Resim: {rastgele_resim} (Gerçek Sınıf: {rastgele_sinif})")
print(f"🎯 Yapay Zeka Tahmini: {tahmin_karakteri}")

plt.figure(figsize=(3, 3))
plt.imshow(img_resized, cmap='gray')
plt.title(f"Gerçek: {rastgele_sinif}\nTahmin: {tahmin_karakteri}", fontsize=12, color='green' if rastgele_sinif == tahmin_karakteri else 'red')
plt.axis('off')
plt.show()