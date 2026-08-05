import os
import shutil
import cv2

# ==============================================================================
# KLASÖR AYARLARI
# ==============================================================================
YOLO_ANAKLASOR = r"C:\Users\Feyzanur\OneDrive\Desktop\projeler\OCR\kirpilmis_etiketler"
KNN_EGITIM_KLASOR = r"C:\Users\Feyzanur\OneDrive\Desktop\projeler\derinogrenme\egitim_verisi"

os.makedirs(KNN_EGITIM_KLASOR, exist_ok=True)

print("="*60)
print("⌨️ HIZLI VE BEDAVA MANUEL ETİKETLEME MOTORU BAŞLATILDI... ⌨️")
print("⚡ Kurallar: Kodu yazıp Enter'a bas. Geçmek için boş Enter yap. Çıkış için 'q' yaz.")
print("="*60)

sayac = 0

# Tüm alt klasörlerdeki resimleri buluyoruz
for root, dirs, files in os.walk(YOLO_ANAKLASOR):
    for dosya in files:
        if dosya.lower().endswith(('.png', '.jpg', '.jpeg')):
            tam_resim_yolu = os.path.join(root, dosya)
            
            # Resmi OpenCV ile oku ve ekranda göster
            img = cv2.imread(tam_resim_yolu)
            if img is None:
                continue
                
            # Resmi rahat görebilmek için pencereyi boyutlandırılabilir yapıyoruz
            cv2.namedWindow("Kitap Etiketi", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Kitap Etiketi", 300, 500)
            cv2.imshow("Kitap Etiketi", img)
            cv2.waitKey(1) # Pencerenin yenilenmesi için minik bir tetik
            
            # Terminalden kullanıcı girdisi al
            print(f"\n🖼️  Sıradaki Resim: {dosya[:20]}...")
            user_input = input("✍️  Etiket Kodunu Yaz (Örn: PR_6051_D3352_1988): ").strip().upper()
            
            # Eğer kullanıcı çıkmak isterse
            if user_input.lower() == 'q':
                print("👋 Etiketleme işlemi kullanıcı tarafından sonlandırıldı.")
                cv2.destroyAllWindows()
                exit()
                
            # Eğer boş basılırsa o resmi pas geç
            if not user_input:
                print("⏭️  Resim etiketlenmeden atlandı.")
                continue
                
            # Uzantıyı kap
            uzanti = os.path.splitext(dosya)[1].lower()
            
            # kNN şablonuna göre yeni dosya adını belirle
            yeni_dosya_adi = f"{user_input}_g{sayac}{uzanti}"
            yeni_yol = os.path.join(KNN_EGITIM_KLASOR, yeni_dosya_adi)
            
            # Dosyayı kopyala
            shutil.copy(tam_resim_yolu, yeni_yol)
            print(f"✅ Kaydedildi -> {yeni_dosya_adi}")
            
            sayac += 1

cv2.destroyAllWindows()
print("\n"+"="*60)
print(f"🎉 ETİKETLEME BİTTİ! Toplam {sayac} adet gerçek dünya verisi kNN havuzuna eklendi.")
print("="*60)