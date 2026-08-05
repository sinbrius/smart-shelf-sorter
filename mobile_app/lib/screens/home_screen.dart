import 'dart:io';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'dart:typed_data';
import 'package:file_picker/file_picker.dart' as fp; // Çakışmayı önleyen asil takma adımız
import '../services/api_services.dart'; 
import 'account.dart';
import 'camera_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Uint8List? _imageBytes;          // Galeriden seçilen ham resmin önizlemesi için kanka
  Uint8List? _analizliResimBytes;  // Sunucudan dönen kırmızı/yeşil kutulu işlenmiş resmin baytları
  bool _isUploading = false;       // Yükleniyor animasyonu kontrolü

  // 📂 GALERİDEN/DOSYADAN SEÇİM YAPIP ANALİZE GÖNDEREN ESAS FONKSİYON
  Future<void> _galeridenResimSec() async {
    try {
      fp.FilePickerResult? result = await fp.FilePicker.pickFiles(
        type: fp.FileType.image,
        withData: true, // Baytları RAM'e çek kanka (Web için zorunlu)
      );

      if (result != null && result.files.first.bytes != null) {
        Uint8List imageBytes = result.files.first.bytes!;

        // 🧠 Sunucu yanıtı gelmeden hemen önce ham resmi ekrana yansıtıyoruz:
        setState(() {
          _imageBytes = imageBytes;
          _analizliResimBytes = null; // Eski analizi tamamen temizle
          _isUploading = true;        // Yükleniyor animasyonunu aç
        });

        print("Dosya başarıyla seçildi. Sunucuya postalanıyor...");

        // 🚀 API servisini çağırıyoruz
        ApiService apiService = ApiService();
        
        // backend mikroservisimize resmi byte olarak fırlatıyoruz
        Uint8List? islenmisResim = await apiService.analizliResmiGetir(null, imageBytes);

        // 🎯 DART NULL-SAFETY KONTROLÜ: Gelen verinin null olup olmadığını garantiye alıyoruz
        setState(() {
          if (islenmisResim != null) {
            // Eğer dosya boş değilse, web dostu senkron bayt dönüşümü yapıyoruz:
            _analizliResimBytes = islenmisResim;
          } else {
            _analizliResimBytes = null;
          }
          _isUploading = false; // Yükleniyor çarkını kapat kanka
        });

        if (islenmisResim != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Yapay zeka analizi başarıyla tamamlandı! 🚀'), 
              backgroundColor: Colors.green,
              behavior: SnackBarBehavior.floating,
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Sunucu bağlantısı kurulamadı veya boş veri döndü kanka!'), 
              backgroundColor: Colors.orangeAccent,
              behavior: SnackBarBehavior.floating,
            ),
          );
        }
      }
    } catch (e) {
      print("Dosya seçim veya API hatası kanka: $e");
      setState(() {
        _isUploading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        centerTitle: true,
        title: const Icon(Icons.menu_book_rounded, color: Colors.white),
        backgroundColor: const Color(0xff122E26),
        actions: [
          IconButton(
            icon: const Icon(Icons.person, color: Colors.white),
            onPressed: () {
              Navigator.push(context, MaterialPageRoute(builder: (context) => const AccountScreen()));
            },
          ),
        ],
      ),
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/books.jpg'),
            fit: BoxFit.cover,
          ),
        ),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Container(
            color: Colors.white.withAlpha(128),
            child: SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 30.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    const SizedBox(height: 60),
                    const Text(
                      'Hoş geldiniz!',
                      style: TextStyle(fontSize: 18, color: Colors.black87, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 20),
                    const Text(
                      'Bu, Kayseri Kütüphane Sıralama uygulamasının ana sayfasıdır. Raf sıralamasını kontrol edebilirsiniz.',
                      style: TextStyle(fontSize: 14, color: Colors.black54),
                    ),
                    const SizedBox(height: 40),
                    
                    // 🎯 BUZLU CAM VE KAMERALI AKILLI KUTU
                    ClipRRect(
                      borderRadius: BorderRadius.circular(24),
                      child: BackdropFilter(
                        filter: ImageFilter.blur(sigmaX: 10.0, sigmaY: 10.0),
                        child: Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(24.0),
                          decoration: BoxDecoration(
                            color: Colors.white.withAlpha(40),
                            borderRadius: BorderRadius.circular(24),
                            border: Border.all(color: Colors.white.withAlpha(60), width: 1.5),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: const [
                                  Icon(Icons.auto_awesome_motion_rounded, color: Colors.white, size: 24),
                                  SizedBox(width: 10),
                                  Text(
                                    'Akıllı Raf Tarayıcı',
                                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 20),

                              // 🔄 1. LOADING DURUMU KONTROLÜ (Yapay zeka çalışırken ham resmi gösterir kanka)
                              if (_isUploading && _analizliResimBytes == null && _imageBytes != null) ...[
                                Center(
                                  child: Column(
                                    children: [
                                      ClipRRect(
                                        borderRadius: BorderRadius.circular(16),
                                        child: Image.memory(
                                          _imageBytes!, 
                                          height: 280, 
                                          width: double.infinity, 
                                          fit: BoxFit.contain
                                        ),
                                      ),
                                      const SizedBox(height: 15),
                                      const CircularProgressIndicator(color: Color(0xff122E26)),
                                      const SizedBox(height: 10),
                                      const Text(
                                        "Yapay zeka katmanı işleniyor kanka...", 
                                        style: TextStyle(color: Colors.white70, fontSize: 12)
                                      ),
                                    ],
                                  ),
                                )
                              ]
                              // 🔄 2. SAF BELLEK DOSTU RESİM GÖSTERİM ALANI (Web'de asla patlamaz)
                              else if (_analizliResimBytes != null || _imageBytes != null) ...[
                                Center(
                                  child: ClipRRect(
                                    borderRadius: BorderRadius.circular(16),
                                    child: _analizliResimBytes != null
                                        ? Image.memory(
                                            _analizliResimBytes!, // Sunucudan dönen kırmızılı analiz resmi kanka
                                            height: 280, 
                                            width: double.infinity, 
                                            fit: BoxFit.contain
                                          )
                                        : Image.memory(
                                            _imageBytes!, // İlk başta seçilen ham resim önizlemesi
                                            height: 280, 
                                            width: double.infinity, 
                                            fit: BoxFit.contain
                                          ),
                                  ),
                                ),
                                const SizedBox(height: 15),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                                  children: [
                                    TextButton.icon(
                                      onPressed: () => _kameraSayfasinaGit(context),
                                      icon: const Icon(Icons.camera_alt, color: Colors.white),
                                      label: const Text('Yeniden Çek', style: TextStyle(color: Colors.white)),
                                    ),
                                    TextButton.icon(
                                      onPressed: _galeridenResimSec,
                                      icon: const Icon(Icons.photo_library, color: Colors.white),
                                      label: const Text('Farklı Seç', style: TextStyle(color: Colors.white)),
                                    ),
                                  ],
                                ),
                              ] 
                              // 🔄 3. BAŞLANGIÇTAKİ SEÇİM BUTONLARIMIZ
                              else ...[
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                                  children: [
                                    _buildAksiyonButonu(
                                      icon: Icons.camera_alt_rounded,
                                      label: 'Kamera İle Tara',
                                      onTap: () => _kameraSayfasinaGit(context),
                                    ),
                                    _buildAksiyonButonu(
                                      icon: Icons.folder_open_rounded,
                                      label: 'Dosyadan Seç',
                                      onTap: _galeridenResimSec,
                                    ),
                                  ],
                                ),
                              ],
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildAksiyonButonu({required IconData icon, required String label, required VoidCallback onTap}) {
    return Column(
      children: [
        InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(50),
          child: Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: const Color(0xff122E26),
              boxShadow: [BoxShadow(color: Colors.black.withAlpha(40), blurRadius: 10, offset: const Offset(0, 4))],
            ),
            child: Icon(icon, color: Colors.white, size: 28),
          ),
        ),
        const SizedBox(height: 8),
        Text(label, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w500)),
      ],
    );
  }

  void _kameraSayfasinaGit(BuildContext context) async {
    final File? donenResimDosyasi = await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const CameraScreen()),
    );
    if (donenResimDosyasi != null) {
      setState(() {
        // 🎯 Kameradan dönen dosyayı da anlık olarak web uyumlu baytlara çeviriyoruz:
        _analizliResimBytes = donenResimDosyasi.readAsBytesSync();
        _imageBytes = null; // Kamera modu seçildiyse galeri önizlemesini temizle
      });
    }
  }
}