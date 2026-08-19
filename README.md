# 📚 Kayseri Kütüphane Otomasyonu: Akıllı Raf Sıralama ve Doğrulama Sistemi

Bu proje; kütüphane raflarındaki kitap sırtı etiketlerini bilgisayarlı görü ve büyük dil modelleri (Multimodal LLM) kullanarak tespit eden, Library of Congress (LC) standartlarına göre dizilim doğruluğunu denetleyen ve kullanıcıya adım adım düzeltme görseli sunan hibrit bir karar destek sistemidir.

---

## 🎬 Canlı Demo

<div align="center">
  <img src="assets/demo2.gif" alt="Kütüphane Raf Analiz Demosu" width="750"/>
</div>

---

## 🚀 Proje Mimarisi ve Çalışma Mantığı

1. **Nesne Tespiti (YOLOv8):** Görüntüdeki kitap etiketlerini `kitap-beyni.pt` modeli ile optimize edilmiş güven eşiğinde (`conf=0.21` - `0.22`) sınır kutularına (Bounding Box) ayırır.
2. **Görüntü Ön İşleme (OpenCV):** Karakter kaybını önlemek için dinamik %5 padding uygular ve dikey etiketleri doğal okuma yönü için 90° saat yönünde döndürür.
3. **Semantik Karakter Tanıma (Gemini Pro / OCR):** Asenkron paralel kuyruk (`httpx` + `asyncio.Semaphore`) ve yeniden deneme mekanizması ile etiket kodlarını yüksek doğrulukla metne dönüştürür.
4. **LC Sıralama Motoru:** Çift Cutter (Double Cutter) kuralı ve basım yılı hiyerarşisini matematiksel tuple karşılaştırmasıyla çözer.
5. **Çift Adımlı Simülasyon Motoru:** Tek görsel taramasında ardışık iki düzeltme adımını hesaplar ve yönlendirme oklarını dikey birleştirilmiş görsel (`cv2.vconcat`) olarak kullanıcıya sunar.

---

## 🛠️ Kurulum ve Gereksinimler

### Gereksinimler
* Python 3.10+
* Flutter SDK (Mobil/Web arayüzü için)

### Python Bağımlılıkları
```bash
pip install -r backend/requirements.txt
