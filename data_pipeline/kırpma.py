import os
import cv2
import numpy as np
from ultralytics import YOLO

# 1. PARAMETRELER VE KLASÖR AYARLARI
MODEL_PATH = 'kitap-beyni.pt'
INPUT_DIR = 'kirpilacak'      # Raf fotoğraflarını koyacağın klasör
OUTPUT_DIR = 'kirpilmis_etiketler'    # Sonuçların çıkacağı ana klasör

print("="*60)
print("🤖 TOPLU YOLOCROP BARKOD AYRIŞTIRICI BAŞLATILDI... 🤖")
print("="*60)

# Gerekli klasör kontrolleri
if not os.path.exists(INPUT_DIR):
    os.makedirs(INPUT_DIR)
    print(f"📂 '{INPUT_DIR}' klasörü otomatik oluşturuldu. Lütfen içine raf fotoğraflarını atıp kodu tekrar çalıştır!")
    exit()

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Modeli yükle
if not os.path.exists(MODEL_PATH):
    print(f"❌ HATA: Model dosyası '{MODEL_PATH}' dizinde bulunamadı!")
    exit()

model = YOLO(MODEL_PATH)
print("✅ YOLO kitap-beyni modeli başarıyla yüklendi.")

# Klasördeki tüm resimleri listele (.png, .jpg, .jpeg)
valid_extensions = ('.png', '.jpg', '.jpeg', '.JPG', '.PNG', '.JPEG')
images_to_process = [f for f in os.listdir(INPUT_DIR) if f.endswith(valid_extensions)]

print(f"📂 Toplam işlenecek raf fotoğrafı sayısı: {len(images_to_process)}")
print("-" * 60)

# 2. ANA FOTOĞRAF TARAMA DÖNGÜSÜ
for img_name in images_to_process:
    img_path = os.path.join(INPUT_DIR, img_name)
    raw_name = os.path.splitext(img_name)[0] # Uzantısız dosya adı (Örn: IMG_5600)
    
    print(f"📸 İşleniyor: {img_name}")
    
    # 🔥 Türkçe karakter güvenli resim okuma yöntemi
    try:
        img_array = np.fromfile(img_path, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"   ❌ Resim okunamadı (Dosya hasarlı veya yol hatalı): {img_name}")
        continue

    if img is None:
        continue

    # YOLO Tahmini yap
    results = model.predict(source=img, conf=0.25, verbose=False) # verbose=False terminal kalabalığını önler
    
    # Her bir ana resim için özel bir alt klasör oluştur
    image_output_dir = os.path.join(OUTPUT_DIR, raw_name)
    if not os.path.exists(image_output_dir):
        os.makedirs(image_output_dir)

    for r in results:
        # Kutuları soldan sağa X koordinatına göre sırala (Raf düzenini korumak için hayati!)
        boxes = sorted(r.boxes, key=lambda b: b.xyxy[0][0])
        print(f"   🎯 {len(boxes)} adet kitap barkodu tespit edildi. Kırpılıyor...")
        
        for i, box in enumerate(boxes):
            # Koordinatları al ve tam sayıya çevir
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Koordinatların resim sınırları içinde kaldığından emin ol (Sistem çökme koruması)
            y1, y2 = max(0, y1), min(img.shape[0], y2)
            x1, x2 = max(0, x1), min(img.shape[1], x2)
            
            # OpenCV Matris Kırpma [y, x]
            etiket_resmi = img[y1:y2, x1:x2]
            
            # Eğer kırpılan bölge boş değilse kaydet
            if etiket_resmi.size > 0:
                dosya_adi = f'{image_output_dir}/etiket_{i}.jpg'
                
                # 🔥 Türkçe karakter güvenli resim kaydetme yöntemi
                _, img_encoded = cv2.imencode('.jpg', etiket_resmi)
                img_encoded.tofile(dosya_adi)
                
print("\n" + "="*60)
print("✅ İŞLEM TAMAMLANDI! Tüm raflar sırasına göre klasörlendi.")
print(f"📂 Çıktıları incelemek için '{OUTPUT_DIR}' klasörüne göz atabilirsin.")
print("="*60)