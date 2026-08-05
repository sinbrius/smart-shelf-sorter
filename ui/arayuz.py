import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from tensorflow.keras.models import load_model # 🚀 CNN modelini yüklemek için ekledik

# ==============================================================================
# 1. AYARLAR VE CNN MODELİNİN YÜKLENMESİ
# ==============================================================================
MODEL_PATH = "models/kutuphane_cnn_model_2.h5"
IMG_SIZE = (28, 28) # 🎯 Kesişen CNN boyutu (28x28)

CHAR_LIST = "0123456789ABCÇDEFGHIİJKLMNOÖPRSŞTUÜVYZ"
num_to_char = {idx: char for idx, char in enumerate(CHAR_LIST)}

if not os.path.exists(MODEL_PATH):
    print(f"❌ HATA: '{MODEL_PATH}' bulunamadı! Önce cnn_model.py kodunu çalıştırıp modeli eğitmelisin .")
    exit()

# 🧠 Keras ile derin öğrenme modelimizi güvenle yüklüyoruz
cnn_model = load_model(MODEL_PATH)

# ==============================================================================
# 2. GELİŞMİŞ CNN OCR TAHMİN FONKSİYONU
# ==============================================================================
def ocr_tahmin_et(image_path):
    img_array = np.fromfile(image_path, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
    if img is None: 
        return "Resim Okunamadı!"
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    clahe_img = clahe.apply(img)
    
    # 🌟 GÖLGE AVCISI: Sabit threshold yerine gölgeleri kıran adaptif filtreye geçtik
    thresh = cv2.adaptiveThreshold(
        clahe_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_chars = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > 2 and h > 6: # Esnek harf limitleri
            detected_chars.append((x, y, w, h))
            
    detected_chars = sorted(detected_chars, key=lambda b: (b[1] // 20, b[0]))
    predicted_string = ""
    
    # Her bir harf kutusunu CNN modeline besleme döngüsü
    for (x, y, w, h) in detected_chars:
        char_crop = thresh[y:y+h, x:x+w]
        char_resize = cv2.resize(char_crop, IMG_SIZE)
        
        # Giriş verisini CNN formatına normalize etme: (1, 28, 28, 1)
        char_input = char_resize / 255.0
        char_input = np.expand_dims(char_input, axis=0)
        char_input = np.expand_dims(char_input, axis=-1)
        
        # Model tahmini
        predictions = cnn_model.predict(char_input, verbose=0)
        pred_idx = np.argmax(predictions)
        predicted_string += num_to_char[pred_idx]
        
   
    
            
    return predicted_string

# ==============================================================================
# 3. TKINTER ARAYÜZÜ (Görsel Tasarım)
# ==============================================================================
root = tk.Tk()
root.title("🤖 Library Book Arrangement System - CNN OCR 🤖")
root.geometry("500x570")
root.configure(bg="#2c3e50")

def resim_sec():
    dosya_yolu = filedialog.askopenfilename(filetypes=[("Resim Dosyaları", "*.png *.jpg *.jpeg")])
    if not dosya_yolu: 
        return
    
    # Seçilen resmi Tkinter penceresine sığacak şekilde ölçekle
    img = Image.open(dosya_yolu)
    img.thumbnail((200, 250))
    img_tk = ImageTk.PhotoImage(img)
    lbl_img.config(image=img_tk)
    lbl_img.image = img_tk
    
    # Arka planda derin öğrenme modelini koştur
    okunan_kod = ocr_tahmin_et(dosya_yolu)
    
    # Arayüz etiketlerini güncelle
    lbl_dosya.config(text=f"Dosya: {os.path.basename(dosya_yolu)}")
    lbl_sonuc.config(text=okunan_kod)

# UI Bileşenleri
lbl_baslik = tk.Label(root, text="KÜTÜPHANE KİTAP DÜZENLEME SİSTEMİ", font=("Arial", 14, "bold"), fg="#ecf0f1", bg="#2c3e50")
lbl_baslik.pack(pady=20)

btn_sec = tk.Button(root, text="📁 Kitap Barkod Resmi Seç", command=resim_sec, font=("Arial", 11, "bold"), bg="#2ecc71", fg="white", padx=10, pady=5, relief="raised", cursor="hand2")
btn_sec.pack(pady=10)

lbl_img = tk.Label(root, bg="#2c3e50")
lbl_img.pack(pady=10)

lbl_dosya = tk.Label(root, text="Lütfen bir resim seçin...", font=("Arial", 9, "italic"), fg="#bdc3c7", bg="#2c3e50")
lbl_dosya.pack(pady=5)

lbl_sonuc_baslik = tk.Label(root, text="🤖 Yapay Zekanın Okuduğu Kod:", font=("Arial", 12, "bold"), fg="#f1c40f", bg="#2c3e50")
lbl_sonuc_baslik.pack(pady=10)

lbl_sonuc = tk.Label(root, text="---", font=("Courier", 18, "bold"), fg="#e74c3c", bg="#ecf0f1", width=22, relief="sunken", bd=3)
lbl_sonuc.pack(pady=10)

root.mainloop()