import 'dart:async'; // 🎯 Zamanlayıcı (Timer) için en üste eklemeyi unutma kanka
import 'package:flutter/material.dart';
import 'login.dart'; // Giriş ekranına geçiş yapabilmesi için onu bağladık


class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    // ⏳ 2 saniye sonra otomatik olarak LoginScreen'e geçiş yap diyoruz
    Timer(const Duration(seconds: 2), () {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) =>  LoginScreen()),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Giriş ekranınla bütünlük sağlasın diye aynı yeşil-krem geçişini kullanıyoruz
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
         image: DecorationImage(
            image: AssetImage('assets/images/books.jpg'), // Arka plan görseli
            fit: BoxFit.cover,
          ),
        ),
      child: Container(
        color: Colors.white.withAlpha(128), // Görselin üzerine hafif beyaz bir katman ekleyerek yazının okunabilirliğini artırıyoruz
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // 🪆 Matruşka İç İçe Geçiş: Daire çerçeve içi ikon
              Container(
                padding: const EdgeInsets.all(25),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: const Color(0xff122E26).withAlpha(128),
                  border: Border.all(color: const Color(0xff122E26), width: 3),
                ),
                child: const Icon(
                  Icons.menu_book_rounded, // Kitap ikonun
                  size: 80, // Açılış ekranı olduğu için biraz daha büyük yaptık
                  color: Color(0xff122E26),
                ),
              ),
              const SizedBox(height: 25),
              const Text(
                'KAYSERİ KÜTÜPHANE',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 36,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 4, // Harf arası boşluğu açarak premium hava kattık
                  color: Color(0xff122E26),
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'Yükleniyor...',
                style: TextStyle(
                  fontSize: 14,
                  fontStyle: FontStyle.italic,
                  color: Colors.black45,
                ),
              ),
              const SizedBox(height: 40),
              // Modern, dairesel yüklenme çarkı (Progress Indicator)
              const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  color: Color(0xff122E26),
                  strokeWidth: 2.5,
                ),
              ),
            ],
          ),
        ),
      ),
    ),);
  }
}