import os
import random
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

if not os.path.exists("egitim_verisi_raf"):
    os.makedirs("egitim_verisi_raf")


# =====================================================================
# 1. SENİN YAZDIĞIN GÖRÜNTÜ İŞLEME (PREPROCESSING) FONKSİYONLARI
# =====================================================================
def isik_ve_golge_ekle(image):
    """Resmin üzerine gerçekçi kütüphane gölgesi ve lamba parlaması ekler."""
    img_array = np.array(image, dtype=np.float32)
    rows, cols, ch = img_array.shape  # Raf renkli olduğu için 3 kanal (RGB)

    # --- RASTGELE GÖLGELENDİRME (Linear Gradient Shadow) ---
    if random.random() > 0.3:
        golge_katsayisi = random.uniform(0.4, 0.7)
        x = np.linspace(0, 1, cols)
        y = np.linspace(0, 1, rows)
        X, Y = np.meshgrid(x, y)
        yon = random.choice([X, 1 - X, Y, 1 - Y, (X + Y) / 2, (2 - X - Y) / 2])

        # 3 kanala da uygulamak için maskeyi genişletiyoruz
        maske = 1.0 - (1.0 - golge_katsayisi) * yon
        maske = np.expand_dims(maske, axis=2)
        img_array = img_array * maske

    # --- RASTGELE IŞIK YANSIMASI (Gaussian Spotlight) ---
    if random.random() > 0.3:
        merkez_x = random.randint(0, cols)
        merkez_y = random.randint(0, rows)
        yaricap = random.randint(150, 300)  # Tüm raf büyük olduğu için yarıçapı büyüttük

        y, x = np.ogrid[:rows, :cols]
        mesafe_kare = (x - merkez_x) ** 2 + (y - merkez_y) ** 2
        isik_maskesi = np.exp(-mesafe_kare / (2 * (yaricap**2)))
        isik_maskesi = np.expand_dims(isik_maskesi, axis=2)

        isik_gucu = random.randint(30, 70)
        img_array = img_array + (isik_maskesi * isik_gucu)

    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    return Image.fromarray(img_array)


def perspektif_ekle_belirgin(image):
    """Tüm rafa kamera eğikliği / perspektif bozulması ekler."""
    img_array = np.array(image)
    rows, cols, ch = img_array.shape

    kayma = random.randint(30, 50)
    pts1 = np.float32([[0, 0], [cols, 0], [0, rows], [cols, rows]])

    if random.random() > 0.5:
        pts2 = np.float32(
            [[kayma, 0], [cols - kayma, 0], [0, rows], [cols, rows]]
        )
    else:
        pts2 = np.float32(
            [[0, kayma], [cols, 0], [0, rows - kayma], [cols, rows]]
        )

    M = cv2.getPerspectiveTransform(pts1, pts2)
    # borderValue=(220,220,220) kütüphane duvarı rengi arkada sırıtmasın diye
    img_array = cv2.warpPerspective(
        img_array, M, (cols, rows), borderValue=(220, 220, 220)
    )

    return Image.fromarray(img_array)


def gurultu_ekle(image):
    """Hafif kamera bulanıklığı ve mikro dönme ekler."""
    img_array = np.array(image)

    if random.random() > 0.2:
        k_size = random.choice([3, 5])
        img_array = cv2.GaussianBlur(img_array, (k_size, k_size), 0)

    image = Image.fromarray(img_array)
    if random.random() > 0.5:
        aci = random.uniform(-1.5, 1.5)
        image = image.rotate(aci, expand=False, fillcolor=(220, 220, 220))

    return image


# =====================================================================
# 2. SENTETİK RAF VE ETİKET ÜRETİM MOTORU
# =====================================================================
def sentetik_raf_uretim(miktar):
    # Gerçekçi kütüphane havuzları
    harf_havuzu = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    populer_ana_kodlar = ["PS", "PR", "PE", "PA", "PN"]
    authors = ["MARK TWAIN", "ADAM BLAKE", "AMBROSE BIERCE", "BURNETT", "TWAIN"]
    titles = [
        "HUCKLEBERRY FINN",
        "ONLAR",
        "SEYTANIN SOZLUGU",
        "THE SECRET GARDEN",
        "TOM SAWYER",
    ]

    try:
        font_kitap = ImageFont.truetype("arial.ttf", 16)
        font_etiket = ImageFont.truetype("arial.ttf", 14)
    except:
        font_kitap = font_etiket = ImageFont.load_default()

    for m in range(miktar):
        # 1000x1000 boyutunda boş bir kütüphane rafı tabanı (RGB)
        raf_img = Image.new("RGB", (1000, 1000), color=(210, 210, 210))
        draw = ImageDraw.Draw(raf_img)

        current_x = 30
        taban_y = 850  # Kitapların basacağı alt hizası

        while current_x < 930:
            book_width = random.randint(50, 85)
            book_height = random.randint(600, 780)

            if current_x + book_width > 970:
                break

            # Rastgele kitap rengi (Görseldeki palet)
            book_color = random.choice(
                [
                    (25, 28, 36),  # Siyah
                    (135, 25, 35),  # Koyu Kırmızı
                    (40, 85, 135),  # Mavi
                    (245, 240, 215),  # Krem
                    (220, 130, 50),  # Turuncu
                    (55, 105, 85),  # Yeşil
                ]
            )

            # Kitap sırtı koordinatları
            x1, y1 = current_x, taban_y - book_height
            x2, y2 = current_x + book_width, taban_y

            # Kitap gövdesini çiz
            draw.rectangle(
                [x1, y1, x2, y2], fill=book_color, outline=(45, 45, 45)
            )

            # --- Kitap Üzerine Dikey Başlık Yazma ---
            yazi_rengi = (
                (245, 245, 245) if sum(book_color) < 400 else (40, 40, 40)
            )
            kitap_metni = f"{random.choice(authors)}  {random.choice(titles)}"

            # Yazıyı dikey yapmak için geçici yüzey kullanıyoruz
            yazi_tuvali = Image.new(
                "RGBA", (book_height - 180, book_width), (0, 0, 0, 0)
            )
            yazi_draw = ImageDraw.Draw(yazi_tuvali)
            yazi_draw.text((15, 5), kitap_metni, fill=yazi_rengi, font=font_kitap)
            dondurulmus_yazi = yazi_tuvali.rotate(270, expand=True)
            raf_img.paste(dondurulmus_yazi, (x1 + 5, y1 + 40), dondurulmus_yazi)

            # --- Kitap Üzerine Gerçekçi Kütüphane Etiketi Ekleme ---
            label_w = book_width - 12
            label_h = random.randint(85, 105)
            lx1 = x1 + 6
            ly1 = y2 - label_h - 30  # Görseldeki gibi biraz yukarıda durması için
            lx2 = lx1 + label_w
            ly2 = y2 - 30

            # Beyaz etiket bloğu
            draw.rectangle(
                [lx1, ly1, lx2, ly2],
                fill=(255, 255, 255),
                outline=(190, 190, 190),
            )

            # Görseldeki formata %100 uyumlu etiket metni üretimi
            ana_kod = random.choice(populer_ana_kodlar)
            sayi_1 = str(random.randint(1000, 2500))
            cutter = (
                "." + random.choice(harf_havuzu) + str(random.randint(30, 99))
            )
            cutter2 = (
                random.choice(harf_havuzu) + str(random.randint(20, 99))
                if random.random() > 0.5
                else ""
            )
            yil = str(random.randint(1950, 2026))

            satirlar = [ana_kod, sayi_1, cutter]
            if cutter2:
                satirlar.append(cutter2)
            satirlar.append(yil)

            # Etiket metin satırlarını dikey basma
            satir_yuksekligi = 15
            for idx, satir in enumerate(satirlar):
                text_y = ly1 + 4 + (idx * satir_yuksekligi)
                if text_y + satir_yuksekligi < ly2:
                    draw.text(
                        (lx1 + 4, text_y), satir, fill=(0, 0, 0), font=font_etiket
                    )

            current_x += book_width + 2

        # Alt kısma fiziksel ahşap/metal raf çizgisi ekleme
        draw.rectangle([0, taban_y, 1000, taban_y + 20], fill=(160, 160, 160))

        # =====================================================================
        # 3. İŞLEM SIRALAMASI (SENİN KURALINA GÖRE TÜM RAFA UYGULANIYOR)
        # =====================================================================
        raf_img = gurultu_ekle(raf_img)  # 1. Yazıları ve rafı hafifçe esnet/bulandır
        raf_img = isik_ve_golge_ekle(raf_img)  # 2. Üzerine oda ışığı ve gölgesi düşür
        raf_img = perspektif_ekle_belirgin(
            raf_img
        )  # 3. En son kamerayı yamult (Perspektif)

        # Sonucu kaydet
        raf_img.save(f"egitim_verisi_raf/sentetik_raf_{m}.png")


print("🚀 Preprocessing adımlarına bağlı kalarak Komple Raf üretimi başladı...")
sentetik_raf_uretim(10)  # Kaç adet tam raf istiyorsan burayı değiştirebilirsin
print("✅ İşlem tamam! 'egitim_verisi_raf' klasörünü kontrol et kanka.")