import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'dart:typed_data';
import 'dart:ui';
import '../services/api_services.dart';
import '../../main.dart'; // main.dart içindeki 'kameralar' listesine ulaşmak için

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? _controller;
  bool _isCameraInitialized = false;
  bool _isProcessing = false; // Fotoğraf çekildikten sonra işleme sürecini göstermek için

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  // 📷 Kamerayı Çalıştıran Sihirli Fonksiyon
  void _initializeCamera() async {
    if (cameras.isEmpty) {
      print("Cihazda kullanılabilir kamera bulunamadı!");
      return;
    }

    // Listeden 0. kamerayı yani arka kamerayı seçiyoruz
    _controller = CameraController(
      cameras[0],
      ResolutionPreset.high, // Yüksek çözünürlük jüride jilet gibi gösterir
      enableAudio: false,    // Raf taratacağımız için sese gerek yok
    );

    try {
      await _controller!.initialize();
      if (mounted) {
        setState(() {
          _isCameraInitialized = true;
        });
      }
    } catch (e) {
      print("Kamera başlatılamadı: $e");
    }
  }

  @override
  void dispose() {
    // 🧹 Bellek sızıntısı (Memory Leak) olmasın diye çıkarken kamerayı kapatıyoruz
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black, // Kamera arkası karanlık olsun ki odaklanalım
      appBar: AppBar(
        title: const Text('Raf Tarama Modülü', style: TextStyle(color: Colors.white, fontSize: 16)),
        centerTitle: true,
        backgroundColor: const Color(0xff122E26), // Senin o asil koyu yeşilin
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Stack(
        children: [
          // 1. CANLI KAMERA ÖNİZLEME ALANI
          if (_isCameraInitialized && _controller != null)
            Center(
              child: CameraPreview(_controller!),
            )
          else
            const Center(
              child: CircularProgressIndicator(color: Color(0xff122E26)), // Kamera açılana kadar yükleme dönsün
            ),

          // Yapay zeka işlenirken araya giren şık Loading katmanı kanka:
          if (_isProcessing)
            Container(
              color: Colors.black54, // Yarı saydam siyah arka plan
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: const [
                    CircularProgressIndicator(color: Colors.greenAccent),
                    SizedBox(height: 15),
                    Text(
                      "Yapay Zeka ve OCR Analizi Yapılıyor...",
                      style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                    )
                  ],
                ),
              ),
            ),

          // 2.  YAPAY ZEKA ODAKLAMA ÇERÇEVESİ
          if (!_isProcessing)
            Center(
              child: Container(
                width: MediaQuery.of(context).size.width * 0.8,
                height: 200,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.greenAccent, width: 2.5), // Yeşil tarama çerçevesi
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Align(
                  alignment: Alignment.topCenter,
                  child: Padding(
                    padding: EdgeInsets.only(top: 8.0),
                    child: Text(
                      'KİTAP SIRTINI BU ALANA HIZALAYIN',
                      style: TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold, backgroundColor: Colors.black54),
                    ),
                  ),
                ),
              ),
            ),

          // 3. EN ALTTAKİ FOTOĞRAF ÇEKME / TARAMA DÜĞMESİ
          if (!_isProcessing)
            Positioned(
              bottom: 40,
              left: 0,
              right: 0,
              child: Center(
                child: FloatingActionButton(
                  backgroundColor: const Color(0xff122E26),
                  onPressed: () async {
                    if (_controller != null && _controller!.value.isInitialized) {
                      try {
                        // 📸 Fotoğrafı çekiyoruz kanka!
                        XFile photo = await _controller!.takePicture();
                        print("Fotoğraf çekildi.");
                        
                        setState(() {
                          _isProcessing = true; // İşleme sürecini başlatıyoruz
                        });

                        // 🎯 SAF BAYT DÖNÜŞÜMÜ: Çekilen fotoğrafın baytlarını söküyoruz kanka!
                        Uint8List photoBytes = await photo.readAsBytes();

                        // API servisini yeni bayt mimarimizle çağırıyoruz:
                        ApiService apiService = ApiService();
                        Uint8List? processedImageBytes = await apiService.analizliResmiGetir(null, photoBytes);

                        setState(() {
                          _isProcessing = false; // İşleme tamamlandı
                        });

                        if (processedImageBytes != null) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Raf tarama başarılı! İşlenmiş resim gösteriliyor.'),
                              backgroundColor: Colors.green,
                              behavior: SnackBarBehavior.floating,
                            ),
                          );
                          
                          // 🎯 ANA EKRANA SÜPER UYUM: Artık ana ekrana dosya nesnesi yerine
                          // doğrudan hafızadaki saf bayt dizisini fırlatıyoruz kanka!
                          Navigator.pop(context, processedImageBytes);
                        } else {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Raf tarama sırasında bir hata oluştu. Lütfen tekrar deneyin.'),
                              backgroundColor: Colors.red,
                              behavior: SnackBarBehavior.floating,
                            ),
                          );
                          setState(() {
                            _isCameraInitialized = true; // Hata durumunda kamerayı geri aç kanka
                          });
                        }
                        
                      } catch (e) {
                        print("Fotoğraf çekilirken hata oluştu: $e");
                        setState(() {
                          _isProcessing = false;
                          _isCameraInitialized = true;
                        });
                      }
                    }
                  },
                  child: const Icon(Icons.blur_circular_rounded, size: 36, color: Colors.white),
                ),
              ),
            ),
        ],
      ),
    );
  }
}