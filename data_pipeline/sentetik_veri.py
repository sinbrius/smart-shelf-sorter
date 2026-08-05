import os
import random
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

if not os.path.exists('egitim_verisi_2'):
    os.makedirs('egitim_verisi_2')

def isik_ve_golge_ekle(image):
    """
    Resmin üzerine gerçekçi kütüphane gölgesi ve lamba parlaması ekler.
    """
    img_array = np.array(image, dtype=np.float32)
    rows, cols = img_array.shape

    # --- 1. RASTGELE GÖLGELENDİRME (Linear Gradient Shadow) ---
    if random.random() > 0.3:  # %70 ihtimalle gölge ekle
        # Gölgenin yoğunluğunu rastgele seç (0.4 - 0.7 arası karartma)
        golge_katsayisi = random.uniform(0.4, 0.7)
        
        # Rastgele eğimde bir gradyan matrisi üretme
        x = np.linspace(0, 1, cols)
        y = np.linspace(0, 1, rows)
        X, Y = np.meshgrid(x, y)
        
        # Gölgenin yönünü rastgele değiştir (sağdan sola, yukarıdan aşağıya vb.)
        yon = random.choice([X, 1-X, Y, 1-Y, (X+Y)/2, (2-X-Y)/2])
        
        # Maskeyi uygula: Karartılacak yerleri kademeli olarak düşür
        maske = 1.0 - (1.0 - golge_katsayisi) * yon
        img_array = img_array * maske

    # --- 2. RASTGELE IŞIK YANSIMASI (Gaussian Spotlight / Flash) ---
    if random.random() > 0.3:  # %70 ihtimalle parlayan flaş ışığı ekle
        # Işığın merkezini rastgele seç (etiketin herhangi bir yeri)
        merkez_x = random.randint(0, cols)
        merkez_y = random.randint(0, rows)
        
        # Parlama çapı (yansıma genişliği)
        yaricap = random.randint(60, 120)
        
        # Mesafe matrisi hesapla
        y, x = np.ogrid[:rows, :cols]
        mesafe_kare = (x - merkez_x)**2 + (y - merkez_y)**2
        
        # Işığın merkezden dışarıya doğru sönümlenmesi (Radyal Gradyan)
        isik_maskesi = np.exp(-mesafe_kare / (2 * (yaricap ** 2)))
        
        # Parlama gücü (0-100 arası pikselleri beyaza yaklaştır)
        isik_gucu = random.randint(40, 90)
        img_array = img_array + (isik_maskesi * isik_gucu)

    # Değerleri 0-255 arasına sabitle ve veri tipini geri dönüştür
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    return Image.fromarray(img_array)

def perspektif_ekle_belirgin(image):
    img_array = np.array(image)
    rows, cols = img_array.shape
    
    kayma = random.randint(25, 35) 
    pts1 = np.float32([[0, 0], [cols, 0], [0, rows], [cols, rows]])
    
    if random.random() > 0.5:
        pts2 = np.float32([[kayma, 0], [cols-kayma, 0], [0, rows], [cols, rows]])
    else:
        pts2 = np.float32([[0, kayma], [cols, 0], [0, rows-kayma], [cols, rows]])
        
    M = cv2.getPerspectiveTransform(pts1, pts2)
    img_array = cv2.warpPerspective(img_array, M, (cols, rows), borderValue=255)
    
    return Image.fromarray(img_array)

def gurultu_ekle(image):
    img_array = np.array(image)
    
    if random.random() > 0.2:
        k_size = random.choice([3, 5])
        img_array = cv2.GaussianBlur(img_array, (k_size, k_size), 0)
    
    image = Image.fromarray(img_array)
    if random.random() > 0.5:
        aci = random.uniform(-3, 3)
        image = image.rotate(aci, expand=False, fillcolor=255)
        
    return image

def etiket_uretim(miktar):
    for i in range(miktar):
        ana_kod = "".join(random.choices("ABCÇDEFGHIİJKLMNOÖPRSŞTUÜVYZ", k=2))
        sayi_1 = random.randint(0, 10000)
        cutter = "." + random.choice("ABCÇDEFGHIİJKLMNOÖPRSŞTUÜVYZ") + str(random.randint(10, 99))
        cutter2 = ""
        if random.random() > 0.5:
            cutter2 = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + str(random.randint(10, 99))
        
        yil = str(random.randint(1950, 2026))

        satirlar = [ana_kod, str(sayi_1), cutter]
        if cutter2: satirlar.append(cutter2)
        satirlar.append(yil)
        
        tam_metin = "\n".join(satirlar)

        img = Image.new('L', (150, 250), color=255)
        d = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            font = ImageFont.load_default()

        d.multiline_text((20, 20), tam_metin, fill=0, font=font, spacing=5)

        label = tam_metin.replace("\n", "_").replace(".", "")
        
        # 🔥 İŞLEM SIRALAMASI ÇOK KRİTİK 🔥
        img = gurultu_ekle(img)             # 1. Yazıyı hafifçe esnet ve bulandır
        img = isik_ve_golge_ekle(img)       # 2. Üzerine oda ışığı ve gölgesi düşür
        img = perspektif_ekle_belirgin(img) # 3. En son kamerayı yamult (Perspektif)
        
        img.save(f'egitim_verisi_2/{label}_{i}.png')

print("🚀 Işık ve gölge efektli akıllı üretim başladı...")
# Jüriden önce bilgisayarı çok yormamak için ilk etapta 1000 veya 5000 adet basabilirsin kanka
etiket_uretim(5000) 
print("✅ İşlem tamam. 'egitim_verisi_2' klasörünü kontrol et!")