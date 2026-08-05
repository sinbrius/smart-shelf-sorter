import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split

# 1. PARAMETRELER VE KLASÖR AYARLARI
DATASET_PATH = "egitim_verisi_2"
IMG_SIZE = (28, 28) # CNN için özellikleri daha iyi yakalaması adına 28x28 yapıyoruz

print("="*60)
print("🚀 TÜRKÇE KARAKTER DESTEKLİ DERİN ÖĞRENME (CNN) MOTORU BAŞLATILDI... 🚀")
print("="*60)

CHAR_LIST = "0123456789ABCÇDEFGHIİJKLMNOÖPRSŞTUÜVYZ"
NUM_CLASSES = len(CHAR_LIST)
char_to_num = {char: idx for idx, char in enumerate(CHAR_LIST)}

X_data = []
y_data = []

if not os.path.exists(DATASET_PATH):
    print(f"❌ HATA: '{DATASET_PATH}' klasörü bulunamadı!")
    exit()

all_images = [f for f in os.listdir(DATASET_PATH) if f.endswith(('.png', '.jpg', '.jpeg'))]
print(f"📂 {len(all_images)} adet sentetik resim CNN için işleniyor...")
clahe= cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
# 2. GÖRÜNTÜ İŞLEME VE VERİ HAZIRLAMA
for filename in all_images:
    image_path = os.path.join(DATASET_PATH, filename)
    
    try:
        img_array = np.fromfile(image_path, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
    except:
        continue

    if img is None:
        continue
        
    clahe_img = clahe.apply(img)
    # Basit küresel binarizasyon (CNN gürültüyü kendi temizleyeceği için normal threshold yeterli)
    _, thresh = cv2.threshold(clahe_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Dosya adından temiz etiketi ayıkla
    isim_parçası = filename.split('.')[0]
    parts = isim_parçası.split('_')[:-1] 
    clean_label_str = "".join(parts).upper()
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_chars = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > 2 and h > 6:
            detected_chars.append((x, y, w, h))
            
    detected_chars = sorted(detected_chars, key=lambda b: (b[1] // 20, b[0]))
    
    if len(detected_chars) == len(clean_label_str):
        for idx, (x, y, w, h) in enumerate(detected_chars):
            char_crop = thresh[y:y+h, x:x+w]
            char_resize = cv2.resize(char_crop, IMG_SIZE)
            
            char_actual = clean_label_str[idx]
            if char_actual in char_to_num:
                # Görüntüyü 0-1 arasına normalize ederek CNN'e ekliyoruz
                X_data.append(char_resize / 255.0)
                y_data.append(char_to_num[char_actual])

X_data = np.array(X_data, dtype=np.float32)
y_data = np.array(y_data, dtype=np.int32)

# CNN için boyut genişletme: (Veri_Sayısı, 28, 28, 1) -> Son parametre tek kanal (grayscale) olduğunu belirtir
X_data = np.expand_dims(X_data, axis=-1)

# Veriyi %80 Eğitim, %20 Test olarak bölüyoruz
X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2, random_state=42)

print(f"✅ Eğitim seti boyutu: {X_train.shape}")
print(f"✅ Test seti boyutu: {X_test.shape}")

# 3. CNN MİMARİSİNİN KURULMASI
model = models.Sequential([
    # 1. Evrişim Katmanı: Özellikleri yakalar (Kenar, köşe tespiti)
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
    layers.MaxPooling2D((2, 2)),
    
    # 2. Evrişim Katmanı: Daha karmaşık kalıpları çözer
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    
    # Matrisi düzleştirip tam bağlantılı katmana aktarma
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3), # Overfitting'i önlemek için %30 nöronu rastgele kapatır
    layers.Dense(NUM_CLASSES, activation='softmax') # Çıktı katmanı (Harf olasılıkları)
])

# 4. MODELİN DERLENMESİ VE EĞİTİLMESİ
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

print("\n🚀 CNN Modeli eğitiliyor... (Bu işlem bilgisayarına göre 1-2 dakika sürebilir)")
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

# 5. MODELİN DEĞERLENDİRİLMESİ VE KAYDEDİLMESİ
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=2)
print(f"\n📊 CNN Modelinin Gerçek Başarı Oranı (Test Accuracy): %{test_acc*100:.2f}")

model.save("kutuphane_cnn_model_2.h5")
print("💾 Model 'kutuphane_cnn_model_2.h5' adıyla başarıyla kaydedildi!")
print("="*60)