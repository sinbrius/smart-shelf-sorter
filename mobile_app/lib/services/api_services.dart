import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

class ApiService {
  // 🎯 Mikroservis mimarimizin ana giriş kapısı: YOLO Servisi (Port: 8001)
  static const String _baseUrl = 'http://127.0.0.1:8001';

  Future<Uint8List?> analizliResmiGetir(dynamic _, Uint8List imageBytes) async {
    try {
      print("🚀 YOLO API'sine istek atılıyor: $_baseUrl/predict_and_draw");

      var request = http.MultipartRequest('POST', Uri.parse('$_baseUrl/predict_and_draw'));
      
      // 🎯 WEB DOSTU MULTIPART: Dosya yolu yerine doğrudan RAM'deki baytları fırlatıyoruz kanka!
      request.files.add(
        http.MultipartFile.fromBytes(
          'image',
          imageBytes,
          filename: 'sentetik_raf.png',
        ),
      );

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        print("✅ Sunucudan 200 OK geldi. İşlenmiş resim baytları alınıyor...");
        
        // 🪵 Tarayıcıda yerel dosya sistemine (File) ASLA dokunmuyoruz.
        // Doğrudan sunucudan gelen ham resim baytlarını (bodyBytes) arayüze fırlatıyoruz kanka!
        return response.bodyBytes;
      } else {
        print("❌ Sunucu hatası döndü kanka! Kod: ${response.statusCode}");
        print("Hata içeriği: ${response.body}");
        return null;
      }
    } catch (e) {
      print("🚨 API Servis Katmanında Hata Çıktı Kanka: $e");
      return null;
    }
  }
}