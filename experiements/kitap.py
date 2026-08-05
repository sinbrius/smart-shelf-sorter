import os
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

# 1. AYARLAR VE MODEL YÜKLEME
IMG_SIZE = (28, 28)
CHAR_LIST = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

print("🧠 Karakter Tanıma Modeli Yükleniyor...")
model = tf.keras.models.load_model('kitap_ocr_cnn_model.keras')

MY_DATA_DIR = r"C:\Users\Feyzanur\OneDrive\Desktop\projeler\derinogrenme\egitim_verisi\egitim_verisi"
kitap_resimleri = [f for f in os.listdir(MY_DATA_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
secilen_kitap = np.random.choice(kitap_resimleri)
kitap_yolu = os.path.join(MY_DATA_DIR, secilen_kitap)

gercek_satirlar = [p.upper() for p in secilen_kitap.split('.')[0].split('_') if p]

# 2. RESMİ OKUMA VE ÖN İŞLEME
img_array = np.fromfile(kitap_yolu, np.uint8)
img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
org_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR) 

# Görüntüyü temizle ve arka planı siyah, harfleri BEYAZ yap (Kaggle Standartı)
thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 3)
# Eğer harfler hala siyah kaldıysa inversiyonu kontrol et
if np.mean(thresh) > 127:
    thresh = cv2.bitwise_not(thresh)

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

bounding_boxes = []
for c in contours:
    x, y, w, h = cv2.boundingRect(c)
    if w >= 1 and h >= 4:
        bounding_boxes.append((x, y, w, h))

bounding_boxes = sorted(bounding_boxes, key=lambda b: b[1])

satirlar = []
if bounding_boxes:
    mevcut_satir = [bounding_boxes[0]]
    satir_esigi = 15
    for box in bounding_boxes[1:]:
        if box[1] - mevcut_satir[-1][1] < satir_esigi:
            mevcut_satir.append(box)
        else:
            mevcut_satir = sorted(mevcut_satir, key=lambda b: b[0])
            satirlar.append(mevcut_satir)
            mevcut_satir = [box]
    mevcut_satir = sorted(mevcut_satir, key=lambda b: b[0])
    satirlar.append(mevcut_satir)

# 3. ORANTI KORUMALI (PADDING) GERÇEK TAHMİN DÖNGÜSÜ
print(f"\n📖 Analiz Edilen Kitap: {secilen_kitap}")
print("-" * 50)

final_yerlesim_kodlari = []

for i, satir in enumerate(satirlar): 
    satir_metni = ""
    for (x, y, w, h) in satir:
        char_crop = thresh[y:y+h, x:x+w]
        
        # 🔥 EN-BOY ORANI KORUMA (PADDING MANTIĞI)
        # Harfi ezip büzmek yerine etrafına siyah boşluk ekleyerek kare yapıyoruz
        h_crop, w_crop = char_crop.shape
        if h_crop > w_crop:
            pad = (h_crop - w_crop) // 2
            char_square = cv2.copyMakeBorder(char_crop, 0, 0, pad, pad, cv2.BORDER_CONSTANT, value=0)
        else:
            pad = (w_crop - h_crop) // 2
            char_square = cv2.copyMakeBorder(char_crop, pad, pad, 0, 0, cv2.BORDER_CONSTANT, value=0)
            
        char_resize = cv2.resize(char_square, IMG_SIZE)
        char_normalized = char_resize.astype('float32') / 255.0
        char_input = np.expand_dims(np.expand_dims(char_normalized, 0), -1)
        
        # Modelin maskesiz saf tahmini
        preds = model.predict(char_input, verbose=0)
        harf = CHAR_LIST[np.argmax(preds)]
        satir_metni += harf
        
    print(f"[Satır {i+1} Saf Tahmin]: {satir_metni}")
    final_yerlesim_kodlari.append(satir_metni)

print("-" * 50)
print(f"🎯 KÜTÜPHANE RAF YERLEŞİM KODU: {' '.join(final_yerlesim_kodlari)}")
print("="*60)

# 4. GÖRSELLEŞTİRME
plt.figure(figsize=(7, 5), dpi=100)
plt.imshow(cv2.cvtColor(org_img, cv2.COLOR_BGR2RGB), aspect='equal')

temiz_gercek = "".join(gercek_satirlar).strip().upper()
temiz_tahmin = "".join(final_yerlesim_kodlari).strip().upper()
baslik_rengi = "green" if temiz_gercek == temiz_tahmin else "red"

plt.title(
    f"📋 GERÇEK ETİKET: {' '.join(gercek_satirlar)}\n"
    f"🤖 SAF MODEL OCR: {' '.join(final_yerlesim_kodlari)}", 
    fontsize=11, fontweight='bold', color=baslik_rengi, pad=12
)
plt.axis("off")
plt.tight_layout()
plt.show()