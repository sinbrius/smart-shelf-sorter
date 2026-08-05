import io
import os
import cv2
import json
import asyncio
import httpx
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO

app = FastAPI(title="Kayseri Kütüphane Otomasyonu Hızlı Hibrit Servis")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"], expose_headers=["X-Analysis-Results"]
)

current_dir = os.path.dirname(os.path.abspath(__file__))
yolo_path = os.path.normpath(os.path.join(current_dir, "..", "models", "kitap-beyni.pt"))
yolo_model = YOLO(yolo_path)

CNN_API_URL = "http://127.0.0.1:8002/predict_label"

def parse_call_number(book_data):
    """
    Çift Cutter (Double Cutter) kuralına uygun, kurşun geçirmez LC sıralama anahtarı üretir.
    Girdi örn: {"sinif": "PS", "sayi": "3566", "cutter": ".A822 S86 2008"}
    """
    try:
        import re
        
        # 1. Sınıf kodunu temizle (Örn: PS)
        sinif = str(book_data.get("sinif", "Z")).strip().upper()
        
        # 2. Sınıf numarasını temizle (Örn: 3566)
        try:
            sayi = float(book_data.get("sayi", 9999))
        except:
            sayi = 9999.0
            
        # 3. Cutter kısmını analiz et (Örn: ".A822 S86 2008")
        cutter_str = str(book_data.get("cutter", "Z")).strip().upper()
        
        # İçindeki tüm Harf+Sayı kombinasyonlarını bul (Örn: [('A', '822'), ('S', '86')])
        cutter_matches = re.findall(r"([A-Z])(\d+)", cutter_str)
        
        cutter1_letter = "Z"
        cutter1_num = 9999
        cutter2_letter = "Z"
        cutter2_num = 9999
        
        # Eğer en az bir tane Cutter kodu varsa (Örn: .A822)
        if len(cutter_matches) >= 1:
            cutter1_letter = cutter_matches[0][0]
            cutter1_num = int(cutter_matches[0][1])
            
        # 🎯 İŞTE BURASI HAYAT KURTARIYOR: Eğer ikinci Cutter kodu da varsa (Örn: S86)
        if len(cutter_matches) >= 2:
            cutter2_letter = cutter_matches[1][0]
            cutter2_num = int(cutter_matches[1][1])
            
        # 4. Basım yılını ayıkla (Örn: 2008)
        years = re.findall(r"\d{4}", cutter_str)
        year_val = int(years[-1]) if years else 2000
        
        # Python tuple sıralama önceliği: Sırasıyla hepsini alt alta kıyaslar kanka
        return (sinif, sayi, cutter1_letter, cutter1_num, cutter2_letter, cutter2_num, year_val)
        
    except:
        # Hata durumunda en sona atsın diye güvenli fallback
        return ("Z", 9999.0, "Z", 9999, "Z", 9999, 2000)

# 🚀 HIZ SİHİRBAZI: Gemini API'ye paralel asenkron istek atan yardımcı fonksiyon
# 🚀 PRO MODEL OPTİMİZASYONU: Zaman aşımını esneten ve hataları yutmayan asenkron fonksiyon
async def fetch_gemini_label(client, label_bytes, semaphore):
    # Pro modelin nefes alması için eşzamanlılık kilidini koruyoruz
    async with semaphore:
        for deneme in range(2): # 🔄 Hata durumunda 2 kez otomatik yeniden deneme (Retry mekanizması)
            try:
                files = {"file": ("label.png", label_bytes, "image/png")}
                
                # Google sunucularını ardışık isteklerle boğmamak için küçük bir es
                await asyncio.sleep(0.3) 
                
                # 🎯 KRİTİK: Pro model için timeout süresini 30 saniyeye çıkarıyoruz!
                response = await client.post(CNN_API_URL, files=files, timeout=30.0)
                
                if response.status_code == 200:
                    raw_label = response.json().get("label", "OKUNAMADI")
                    
                    # Gemini Pro'nun üretebileceği olası satır sonlarını ve temizlikleri yapıyoruz
                    raw_label = raw_label.replace("\n", "").strip()
                    
                    if "|" in raw_label:
                        parts = [p.strip() for p in raw_label.split("|")]
                        if len(parts) >= 3:
                            return {
                                "sinif": parts[0],
                                "sayi": parts[1],
                                "cutter": " ".join(parts[2:]),
                                "full_text": raw_label.replace("|", " ")
                            }
                    
                    # Eğer format uymadıysa ama metin geldiyse metni kurtaralım
                    if len(raw_label) > 3 and raw_label != "OKUNAMADI":
                        return {"sinif": "PS", "sayi": "3566", "cutter": "KONTROL", "full_text": raw_label}
                        
                elif response.status_code == 429:
                    # Kota hatası aldıysak biraz bekleyip döngünün ikinci hakkını kullansın
                    await asyncio.sleep(1.0)
                    continue
                    
            except Exception as e:
                print(f"⚠️ Pro Model Bağlantı Denemesi {deneme+1} Hatası: {e}")
                if deneme == 1: # İki deneme de başarısız olursa pes et
                    return {"sinif": "Z", "sayi": "9999", "cutter": "Z", "full_text": "OKUNAMADI"}
                await asyncio.sleep(0.5)
                
        return {"sinif": "Z", "sayi": "9999", "cutter": "Z", "full_text": "OKUNAMADI"}
@app.post("/predict_and_draw")
async def predict_and_draw(image: UploadFile = File(...)):
    try:
        image_bytes = await image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        yolo_results = yolo_model.predict(source=img_cv2, conf=0.21)
        img_h, img_w = img_cv2.shape[:2]
        
        tasks = []
        box_coords = []

        # 1. Döngü: Sadece kutuları belirle ve resimleri hazırla
        for result in yolo_results:
            for box in result.boxes:
                xyxy = box.xyxy[0].tolist()
                x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                
                h_box, w_box = y2 - y1, x2 - x1
                pad_w, pad_h = int(w_box * 0.05), int(h_box * 0.05)
                x1_pad, y1_pad = max(0, x1 - pad_w), max(0, y1 - pad_h)
                x2_pad, y2_pad = min(img_w, x2 + pad_w), min(img_h, y2 + pad_h)

                cropped_cv2 = img_cv2[y1_pad:y2_pad, x1_pad:x2_pad]
                if cropped_cv2.size == 0:
                    continue

                rotated_label = cv2.rotate(cropped_cv2, cv2.ROTATE_90_CLOCKWISE)
                _, encoded_label = cv2.imencode('.png', rotated_label)
                
                box_coords.append([x1, y1, x2, y2])
                tasks.append(encoded_label.tobytes())

        # 🎯 PARALEL TETİKLEME: Pro model kararlılığı için semaför devrede
        raw_books = []
        semaphore = asyncio.Semaphore(2)  
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=20)
        async with httpx.AsyncClient(limits=limits) as client:
            responses = await asyncio.gather(*(fetch_gemini_label(client, label, semaphore) for label in tasks))
            
        for coords, parsed_data in zip(box_coords, responses):
            raw_books.append({
                "parsed": parsed_data,
                "name": parsed_data["full_text"],
                "bbox": coords,
                "center_x": (coords[0] + coords[2]) / 2
            })

        if not raw_books:
            return JSONResponse(status_code=400, content={"success": False, "error": "Kitap bulunamadı!"})

        # X koordinatına göre (soldan sağa) gerçek raf dizilimini alıyoruz
        sorted_by_shelf = sorted(raw_books, key=lambda x: x["center_x"])
        # Çift Cutter destekli ideal kütüphane sıralamamız
        correct_sorted_books = sorted(sorted_by_shelf, key=lambda b: parse_call_number(b["parsed"]))

        # ─── 🛠️ ADIM 1: İLK HATAYI TESPİT ET VE ÜST RESME ÇİZ ───
        img_top = img_cv2.copy()
        first_error_drawn = False
        first_error_index_shelf = None
        first_error_ideal_name = None

        # Doğru olan kitapları arka planda ince yeşil yapalım
        for book, ideal in zip(sorted_by_shelf, correct_sorted_books):
            x1, y1, x2, y2 = book["bbox"]
            cv2.rectangle(img_top, (x1, y1), (x2, y2), (0, 255, 0), 1)

        for i, (book, ideal) in enumerate(zip(sorted_by_shelf, correct_sorted_books)):
            if book["name"] != ideal["name"] and book["name"] != "OKUNAMADI":
                x1, y1, x2, y2 = book["bbox"]
                
                # İlk hatayı kalın kırmızı kutuya al ve oku çiz
                cv2.rectangle(img_top, (x1, y1), (x2, y2), (0, 0, 255), 3)
                
                target_shelf_index = next((idx for idx, b in enumerate(sorted_by_shelf) if b["name"] == ideal["name"]), None)
                if target_shelf_index is not None:
                    tx1, ty1, tx2, ty2 = sorted_by_shelf[target_shelf_index]["bbox"]
                    cv2.rectangle(img_top, (tx1, ty1), (tx2, ty2), (0, 255, 0), 2)
                    
                    start_point = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                    end_point = (int((tx1 + tx2) / 2), int((ty1 + ty2) / 2))
                    cv2.arrowedLine(img_top, start_point, end_point, (0, 255, 0), 4, tipLength=0.1)
                    cv2.putText(img_top, "ADIM 1: KITABI BURAYA KOY!", (tx1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # 🎯 İleride simülasyon yapmak için bu ilk hatanın verilerini kaydediyoruz
                first_error_drawn = True
                first_error_index_shelf = i
                first_error_ideal_name = ideal["name"]
                break

        # Eğer rafta hiç hata yoksa, üst resme doğrudan temiz raporu basıp geçelim
        if not first_error_drawn:
            cv2.putText(img_top, "RAF TAMAMEN DUZGUN!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)

        # ─── 🛠️ ADIM 2: SİMÜLASYON MOTORU VE ALT RESME ÇİZ ───
        img_bottom = img_cv2.copy()
        
        # Her ihtiyaca karşı doğruları ince yeşil çiz
        for book in sorted_by_shelf:
            x1, y1, x2, y2 = book["bbox"]
            cv2.rectangle(img_bottom, (x1, y1), (x2, y2), (0, 255, 0), 1)

        if first_error_drawn:
            # 🔄 SİHİRLİ ADIM: Sanal bir raf oluşturup Adım 1'deki kitabın yerine oturduğunu hayal ediyoruz!
            simulated_shelf = list(sorted_by_shelf)
            
            # Adım 1'deki hatalı kitabın ismini olması gereken ideal isimle güncelleyerek simüle ediyoruz
            simulated_shelf[first_error_index_shelf] = {
                **simulated_shelf[first_error_index_shelf],
                "name": first_error_ideal_name
            }
            
            second_error_drawn = False
            # Sanal raf üzerinden İKİNCİ HATAYI aramaya başlıyoruz kanka
            for j, (book, ideal) in enumerate(zip(simulated_shelf, correct_sorted_books)):
                if book["name"] != ideal["name"] and book["name"] != "OKUNAMADI":
                    x1, y1, x2, y2 = book["bbox"]
                    
                    # İkinci hatayı kalın kırmızı yap
                    cv2.rectangle(img_bottom, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    
                    target_shelf_index = next((idx for idx, b in enumerate(simulated_shelf) if b["name"] == ideal["name"]), None)
                    if target_shelf_index is not None:
                        tx1, ty1, tx2, ty2 = simulated_shelf[target_shelf_index]["bbox"]
                        cv2.rectangle(img_bottom, (tx1, ty1), (tx2, ty2), (0, 255, 0), 2)
                        
                        start_point = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                        end_point = (int((tx1 + tx2) / 2), int((ty1 + ty2) / 2))
                        cv2.arrowedLine(img_bottom, start_point, end_point, (0, 255, 0), 4, tipLength=0.1)
                        cv2.putText(img_bottom, "ADIM 2: SONRA BU KITABI KOY!", (tx1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    second_error_drawn = True
                    break
            
            if not second_error_drawn:
                cv2.putText(img_bottom, "ADIM 1'DEN SONRA RAF TAMAMEN DUZELIYOR!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(img_bottom, "IKINCI BIR ADIMA GEREK YOK.", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # ─── 🎯 NİHAİ DİKEY BİRLEŞTİRME ───
        combined_image = cv2.vconcat([img_top, img_bottom])

        success, encoded_image = cv2.imencode('.jpg', combined_image)
        image_stream = io.BytesIO(encoded_image.tobytes())

        final_results = [{"book_name": b["name"], "is_placement_correct": (b["name"] == ideal["name"])} for b, ideal in zip(sorted_by_shelf, correct_sorted_books)]
        headers = {"X-Analysis-Results": json.dumps({"success": True, "books": final_results})}
        return StreamingResponse(image_stream, media_type="image/jpeg", headers=headers)

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})