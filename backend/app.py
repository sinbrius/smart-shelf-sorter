import io
import os
import cv2
import json
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from ultralytics import YOLO
from PIL import Image
import tensorflow as tf

app = FastAPI(title="Kayseri Kütüphane Akıllı Kontrol ve Görselleştirme API")

# 📌 CORS Ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Analysis-Results"] # Bizim o custom header raporunu Flutter okuyabilsin kanka!
)

# 📂 Konumlandırmalar
current_dir = os.path.dirname(os.path.abspath(__file__))
yolo_path = os.path.join(current_dir, "..", "models", "kitap-beyni.pt")
cnn_path = os.path.join(current_dir, "..", "models", "kutuphane_cnn_model.h5")

yolo_model = YOLO(yolo_path)
cnn_model = tf.keras.models.load_model(cnn_path)

# 📝 Sınıf isimleri (Doğru alfabetik hiyerarşi)
CNN_CLASSES = ["Kitap_A", "Kitap_B", "Kitap_C", "Kitap_D"]

@app.post("/predict_and_draw")
async def predict_and_draw(image: UploadFile = File(...)):
    try:
        # 1. Resmi oku ve OpenCV formatına çevir
        image_bytes = await image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        original_pil = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))

        # 2. YOLOv8 ile Kitap Tespiti
        yolo_results = yolo_model.predict(source=original_pil, conf=0.25)
        
        raw_books = []

        # 3. Nesne Segmentasyonu ve CNN Sınıflandırma
        for result in yolo_results:
            for box in result.boxes:
                xyxy = box.xyxy[0].tolist()
                x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                
                # Kırp ve Normalize Et
                cropped = original_pil.crop((x1, y1, x2, y2))
                cropped_gray = cropped.convert('L') # CNN genelde gri tonlama ister
                img_resized = cropped_gray.resize((28, 28))
                img_flat = np.array(img_resized, dtype=np.float32) / 255.0
                img_array=img_flat.reshape(1, 28, 28, 1) # CNN giriş formatı


                cnn_predictions = cnn_model.predict(img_array)
                predicted_idx = np.argmax(cnn_predictions[0])
                book_name = CNN_CLASSES[predicted_idx]

                raw_books.append({
                    "name": book_name,
                    "bbox": [x1, y1, x2, y2],
                    "center_x": (x1 + x2) / 2
                })

        if not raw_books:
            return JSONResponse(status_code=400, content={"success": False, "error": "Rafta hiç kitap tespit edilemedi kanka!"})

        # 🔥 4. MEKANSAL ANOMALİ VE SIRALAMA VALIDASYONU
        # Kitapları X ekseninde soldan sağa diziyoruz
        sorted_by_shelf = sorted(raw_books, key=lambda x: x["center_x"])
        correct_sorted_names = sorted([b["name"] for b in sorted_by_shelf])

        final_results = []
        
        for i, book in enumerate(sorted_by_shelf):
            correct_name_here = correct_sorted_names[i]
            x1, y1, x2, y2 = book["bbox"]

            if i<len(correct_sorted_names) :
                correct_name_here = correct_sorted_names[i]
            else:
                correct_name_here = "Bilinmeyen Kitap"
            
            if book["name"] != correct_name_here:
                # ❌ ANOMALİ DETEKTÖRÜ: Kitap yanlış dizilmiş -> Kırmızı Emniyet Çerçevesi
                cv2.rectangle(img_cv2, (x1, y1), (x2, y2), (0, 0, 255), 3) # BGR Kırmızı
                cv2.putText(img_cv2, f"YANLIS: {book['name']}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                # 💡 HEDEF LOKASYON SİMÜLASYONU: Bu kitabın asıl gitmesi gereken indeks aranıyor
                # StopIteration hatasını engellemek için default=None verdik kanka:
                target_index = next((idx for idx, b in enumerate(sorted_by_shelf) if correct_sorted_names[idx] == book["name"]), None)
                
                if target_index is not None:
                    tx1, ty1, tx2, ty2 = sorted_by_shelf[target_index]["bbox"]
                    
                    # Üst üste bindiğinde çirkin durmasın diye yeşil çizgiyi biraz daha ince (thickness=1) yapıyoruz
                    cv2.rectangle(img_cv2, (tx1, ty1), (tx2, ty2), (0, 255, 0), 1) # BGR Yeşil
                    # Yazıyı da alta basıyoruz ki kırmızı etiketle çakışmasın:
                    cv2.putText(img_cv2, f"-> {book['name']} BURAYA", (tx1, ty2 + 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

                is_valid = False
            else:
                # ✅ İDEAL DURUM: Kitap doğru konumda
                is_valid = True

            final_results.append({
                "book_name": book["name"],
                "is_placement_correct": is_valid,
                "should_be_here": correct_name_here
            })

        # 🖼️ 5. İMGE ÇIKTISI VE HTTP RESPONSE SEVKİYATI
        output_image_path = os.path.join(current_dir, "processed_shelf.jpg")
        cv2.imwrite(output_image_path, img_cv2)

        headers = {"X-Analysis-Results": json.dumps({"success": True, "books": final_results})}
        return FileResponse(output_image_path, media_type="image/jpeg", headers=headers)

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})