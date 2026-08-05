import io
import os
import numpy as np
import cv2
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types

app = FastAPI(title="Gemini API Tabanlı Kusursuz OCR Servisi")

# 🔑 Google AI Studio'dan aldığın API Key'i buraya yapıştır kanka
# (Sunumda patlamamak için key'i tırnak içine doğrudan yazabilirsin)
API_KEY = "AIzaSyB993gYR3BOBjH3-LqbkafGI_T2Dxrq1vY"
client = genai.Client(api_key=API_KEY)

@app.post("/predict_label")
async def predict_label(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        
        # 🎯 Sıfır Önişleme: Resmi sadece Gemini'ın anlayacağı formata (bytes) çeviriyoruz
        image_parts = [
            types.Part.from_bytes(
                data=file_bytes,
                mime_type="image/png"
            )
        ]
        
        # 🧠 Gemini'a ne yapacağını insan gibi anlatıyoruz
        prompt = (
            "Resimdeki kütüphane etiketini yukarıdan aşağıya doğru dikkatlice oku.\n"
            "Bu etiket Library of Congress (LC) kütüphane sınıflandırma sistemine aittir "
            "ve ÇİFT CUTTER (Double Cutter) barındırmaktadır.\n\n"
            
            "Metni tam olarak şu 3 ana parçaya ayır ve aralarına SADECE dikey çizgi (|) koy:\n"
            "SINIF_KODU | HARF_SONRASI_SAYI | CUTTER_VE_YIL_ALANI\n\n"
            
            "Kurallar:\n"
            "1. Birinci parça sadece ana harf sınıfı olmalı (Örn: PS).\n"
            "2. İkinci parça sadece harften sonra gelen ana kitaplık numarası olmalı (Örn: 3566).\n"
            "3. Üçüncü parça ise etiketteki birinci cutter, ikinci cutter ve en alttaki basım yılının tamamını "
            "aralarında sadece birer boşluk bırakarak içermeli (Örn: .A822 S86 2008).\n\n"
            
            "Örnek Çıktı Formatı:\n"
            "PS | 3566 | .A822 S86 2008\n\n"
            
            "CRITICAL: Asla markdown (```), ek açıklama, giriş-gelişme metni veya nokta ekleme. "
            "Sadece ve sadece yukarıdaki gibi tek bir satır string döndür."
        )
        
        # Hız için en hızlı ve ucuz model olan gemini-2.5-flash kullanıyoruz
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image_parts[0], prompt]
        )
        
        # Gelen cevaptaki boşlukları temizle
        predicted_string = response.text.strip().replace(" ", "").replace("\n", "").upper()
        
        final_label = predicted_string if predicted_string != "" else "OKUNAMADI"
        return {"success": True, "label": final_label}
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})