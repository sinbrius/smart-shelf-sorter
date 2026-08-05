import 'dart:math'; // 🎲 Rastgele 4 haneli e-mail kodu üretmek için şart kanka
import 'package:flutter/material.dart';
import '../services/auth_service.dart'; // Şifreyi kalıcı olarak diske yazmak için
import 'login.dart'; // Şifre sıfırlama sonrası login ekranına atmak için

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  // 🎮 Kutuları ve adımları yöneten kumandalarımız
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _codeController = TextEditingController();
  final TextEditingController _newPasswordController = TextEditingController();

  int _currentStep = 1; // 1: Email girme, 2: Emaile giden kodu doğrulama, 3: Yeni şifre set etme
  String _generatedEmailCode = ""; // Arka planda uydurulan asenkron token

  // 🎲 E-mail İçin 4 Haneli Rastgele Token Üreten Fonksiyon
  void _generateEmailOTP() {
    final random = Random();
    _generatedEmailCode = (1000 + random.nextInt(9000)).toString(); // 1000 - 9999 arası
    print("🎯 JÜRİ KOPYASI - E-maile Giden Token: $_generatedEmailCode");
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xffF1ECE1), // Yumuşak krem zemin
      appBar: AppBar(
        title: const Text('Şifre Yenileme', style: TextStyle(color: Colors.white, fontSize: 18)),
        centerTitle: true,
        backgroundColor: const Color(0xff122E26), // İmza koyu yeşilin
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 35.0, vertical: 40.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 📌 ADIM 1: E-MAIL ADRESİNİ SORGULAMA EKRANI
              if (_currentStep == 1) ...[
                const Text('E-mail ile Doğrulama', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xff122E26))),
                const SizedBox(height: 10),
                const Text('Sistemde kayıtlı kurum e-mail adresinizi giriniz. Size şifre sıfırlama kodu ileteceğiz.', style: TextStyle(color: Colors.black54)),
                const SizedBox(height: 30),
                TextField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(
                    hintText: 'example@kayseri.edu.tr',
                    prefixIcon: Icon(Icons.email_rounded, color: Color(0xff122E26)),
                    enabledBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.black26)),
                    focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: Color(0xff122E26))),
                  ),
                ),
                const SizedBox(height: 40),
                _buildButton(
                  text: 'DOĞRULAMA KODU GÖNDER',
                  onPressed: () {
                    String inputEmail = _emailController.text.trim();
                    if (inputEmail.isEmpty) {
                      _showSnack('Lütfen e-mail adresinizi boş bırakmayın!', Colors.orange);
                    } else {
                      _generateEmailOTP(); // Kodu ürettik
                      setState(() => _currentStep = 2); // Kod sorgulama ekranına geç kanka
                      
                      // 📩 E-mail bildirim simülasyonunu ekrana basıyoruz kanka!
                      _showSnack('📧 $inputEmail adresine doğrulama kodu gönderildi: $_generatedEmailCode', const Color(0xff122E26));
                    }
                  },
                ),
              ],

              // 📌 ADIM 2: E-MAILE GELEN KODU DOĞRULAMA EKRANI
              if (_currentStep == 2) ...[
                const Text('E-mail Kodu Doğrulama', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xff122E26))),
                const SizedBox(height: 10),
                Text('${_emailController.text} kutunuza gelen 4 haneli geçici kodu giriniz.', style: const TextStyle(color: Colors.black54)),
                const SizedBox(height: 30),
                TextField(
                  controller: _codeController,
                  keyboardType: TextInputType.number,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, letterSpacing: 12),
                  decoration: const InputDecoration(
                    hintText: 'XXXX',
                    hintStyle: TextStyle(color: Colors.black26, letterSpacing: 0),
                    focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: Color(0xff122E26))),
                  ),
                ),
                const SizedBox(height: 40),
                _buildButton(
                  text: 'KODU ONAYLA',
                  onPressed: () {
                    if (_codeController.text.trim() == _generatedEmailCode) {
                      setState(() => _currentStep = 3); // Kod doğruysa yeni şifre adımına uçur kanka
                      _showSnack('E-mail kodu doğrulandı! Yeni şifrenizi tanımlayabilirsiniz.', Colors.green);
                    } else {
                      _showSnack('Girdiğiniz e-mail kodu hatalı veya eksik!', Colors.redAccent);
                    }
                  },
                ),
              ],

              // 📌 ADIM 3: YENİ ŞİFREYİ SİSTEME YAZMA EKRANI
              if (_currentStep == 3) ...[
                const Text('Yeni Şifre Tanımlama', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xff122E26))),
                const SizedBox(height: 10),
                const Text('Lütfen hesabınız için yeni ve güvenli bir şifre giriniz.', style: TextStyle(color: Colors.black54)),
                const SizedBox(height: 30),
                TextField(
                  controller: _newPasswordController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Yeni Şifre',
                    labelStyle: TextStyle(color: Color(0xff122E26)),
                    focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: Color(0xff122E26))),
                  ),
                ),
                const SizedBox(height: 40),
                _buildButton(
                  text: 'ŞİFREYİ GÜNCELLE VE GİRİŞ YAP',
                  onPressed: () async {
                    String yeniSifre = _newPasswordController.text.trim();
                    if (yeniSifre.length < 4) {
                      _showSnack('Şifre en az 4 karakterden oluşmalıdır ', Colors.orange);
                    } else {
                      // 🎯 SİHİRLİ DOKUNUŞ: Kalıcı hafızayı tetikliyoruz
                      // Kullanıcının başta girdiği e-maili ve yeni şifresini yerel diske kazıyoruz!
                      await AuthService.verileriKaydet(_emailController.text.trim(), yeniSifre);
                      
                      _showSnack('Şifreniz başarıyla güncellendi kanka! Yeni şifrenizle giriş yapabilirsiniz.', Colors.green);
                      
                      if (mounted) {
                        Navigator.of(context).pushAndRemoveUntil(
                          MaterialPageRoute(builder: (context) => LoginScreen()), // Senin login sınıfının adı (const'sız olmasına dikkat kanka)
                          (Route<dynamic> route) => false, // Bu 'false' ifadesi geçmişteki tüm sayfaları hafızadan siler!
                        );
                      }
                    }
                  },
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  // 🛠️ Ortak Şık Buton Yapısı
  Widget _buildButton({required String text, required VoidCallback onPressed}) {
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xff122E26),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
        child: Text(text, style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.bold)),
      ),
    );
  }

  // 🛠️ Ortak SnackBar Uyarı Fırlatıcı
  void _showSnack(String mesaj, Color renk) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(mesaj), backgroundColor: renk, behavior: SnackBarBehavior.floating),
    );
  }
}