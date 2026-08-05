import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  // 💾 RAM'deki geçici değişkenlerimiz (Varsayılan ilk değerler)
  static String email = 'kayseri';
  static String password = 'kütüphane';

  // 1. ⚙️ UYGULAMA İLK AÇILDIĞINDA: Telefona kaydedilmiş eski şifre var mı diye bakan fonksiyon
  static Future<void> yukleVerileri() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    // Eğer telefonda daha önce kaydedilmiş bir mail varsa onu al, yoksa varsayılanı kullan
    email = prefs.getString('kayitli_email') ?? 'kayseri';
    password = prefs.getString('kayitli_sifre') ?? 'kütüphane';
  }

  // 2. 💾 VERİLERİ DEĞİŞTİRDİĞİMİZDE: Hem RAM'i hem de telefonun diskini güncelleyen fonksiyon
  static Future<void> verileriKaydet(String yeniEmail, String yeniSifre) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    
    // RAM'i güncelliyoruz kanka
    email = yeniEmail;
    password = yeniSifre;

    // Telefonun kalıcı diskine kazıyoruz 🎯
    await prefs.setString('kayitli_email', yeniEmail);
    await prefs.setString('kayitli_sifre', yeniSifre);
  }
}