import 'package:flutter/material.dart';
import 'dart:ui'; 
import 'home_screen.dart'; // Ana sayfayı giriş sayfasına bağlıyoruz
import '../services/auth_service.dart';
import 'forgot_password.dart'; // Şifremi unuttum ekranını giriş sayfasına bağlıyoruz


class LoginScreen extends StatelessWidget {
   LoginScreen({super.key});
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        // 1. Arka plandaki yumuşak geçişli renk efekti (Gradient)
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/books.jpg'), // Arka plan görseli
            fit: BoxFit.cover,
          ),
        ),
    child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5), // Arka planı hafifçe bulanıklaştırarak metni öne çıkarıyoruz
      child: Container(
        color: Colors.white.withAlpha(128), // Görselin üzerine hafif beyaz
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 30.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,

              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                const SizedBox(height: 60),

                // 2. Logo Alanı (Şimdilik ikon ve yazı ile yapıyoruz)
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: const Color(0xff122E26), width: 3),
                  ),
                  child: const Icon(
                    Icons.menu_book_rounded, // Kitap ikonu
                    size: 60,
                    color: Color(0xff122E26),
                  ),
                ),
                const SizedBox(height: 15),
                const Text(
                  'Kayseri Kütüphane',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                    color: Color(0xff122E26),
                  ),
                ),
                const Text(
                  'Kütüphane uygulamasına hoş geldiniz! Lütfen giriş yapınız.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.black54,
                  ),
                ),

                const SizedBox(height: 60),

                // 3. E-mail Giriş Kutusu
                const Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'E-mail Adresi',
                    
                    style: TextStyle(color: Colors.black54, fontSize: 14),
                  ),
                ),
                 TextField(
                  autofillHints: [AutofillHints.email], // Klavyenin e-mail önerisi sunmasını sağlar
                  controller: _emailController,
                  decoration: InputDecoration(
                    hintText: 'example@gmail.com',
                    hintStyle: TextStyle(color: Colors.black38),
                    enabledBorder: UnderlineInputBorder(
                      borderSide: BorderSide(color: Colors.black26),
                    ),
                    focusedBorder: UnderlineInputBorder(
                      borderSide: BorderSide(color: Color(0xff122E26)),
                    ),
                  ),
                ),
                const SizedBox(height: 25),

                // 4. Şifre Giriş Kutusu
                const Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'Şifre',
                    style: TextStyle(color: Colors.black54, fontSize: 14),
                  ),
                ),
                 TextField(
                  obscureText: true, // Yazılan şifreyi gizli yapar (●●●●)
                  controller: _passwordController,
                  decoration: InputDecoration(
                    hintText: '••••••••••••',
                    hintStyle: TextStyle(color: Colors.black38),
                    enabledBorder: UnderlineInputBorder(
                      borderSide: BorderSide(color: Colors.black),
                    ),
                    focusedBorder: UnderlineInputBorder(
                      borderSide: BorderSide(color: Color(0xff122E26)),
                    ),
                  ),
                ),
                
                // 5. Şifremi Unuttum Yazısı
                Align(
                  alignment: Alignment.centerLeft,
                  child: TextButton(
                    onPressed: () {Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(builder: (context) => const ForgotPasswordScreen()),
                    );
                    },
                    child: const Text(
                      'Şifreni mi unuttun?',
                      style: TextStyle(color: Colors.black87, fontSize: 13),
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                // 6. Giriş Butonu (LOGIN)
                SizedBox(
                  width: double.infinity,
                  height: 55,
                  child: ElevatedButton(
                    onPressed: () {
    // 🔍 1. Kutuların içindeki yazıları alıp sağındaki solundaki gereksiz boşlukları (trim) temizliyoruz
                      String email = _emailController.text.trim();
                      String password = _passwordController.text.trim();

                      // ⛔ 2. KONTROL: Eğer e-mail VEYA şifre alanlarından biri bomboşsa geçişi engelle!
                      if (email.isEmpty || password.isEmpty) {
                        // 🚨 Ekranda uyarı mesajı (SnackBar) fırlatıyoruz
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Lütfen E-mail ve Şifre alanlarını boş bırakmayınız!'),
                            backgroundColor: Colors.redAccent,
                            behavior: SnackBarBehavior.floating, // Mesaj ekranda şık bir şekilde süzülsün
                          ),
                        );
                      } 
                      else if(email == AuthService.email && password == AuthService.password) {
                        // 🚀 TEST BAŞARILI: Eğer e-mail "kayseri" VE şifre "kütüphane" ise geçiş yapabiliriz (Bu sadece test amaçlı, gerçek uygulamada böyle sert kodlanmaz tabii ki)
                        Navigator.pushReplacement(
                          context,
                          MaterialPageRoute(builder: (context) => const HomeScreen()),
                        );
                      }
                      // ✅ 3. ONAY: İki kutu da doluysa artık ana sayfaya geçebiliriz kanka
                      else {
                        // 🚨 Ekranda uyarı mesajı (SnackBar) fırlatıyoruz
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('E-mail veya Şifre yanlış! Lütfen tekrar deneyiniz.'),
                            backgroundColor: Colors.redAccent,
                            behavior: SnackBarBehavior.floating, // Mesaj ekranda şık bir şekilde süzülsün
                          ),
                        );
                      }
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xff0D241F), // Koyu buton rengi
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30), // Oval kenarlar
                      ),
                    ),
                    child: const Text(
                      'GİRİŞ YAP',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, letterSpacing: 1),
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                // 7. Kayıt Ol Yazısı
                
              ],
            ),
          ),
        ),
      ),
    ),),);
  }
}