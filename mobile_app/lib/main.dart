import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart'; // kIsWeb kontrolü için gerekli
import 'dart:io'; // Platform kontrolü için gerekli
import 'package:camera/camera.dart'; // Kamerayı kullanabilmek için gerekli kütüphane
import 'screens/splash.dart'; // Splash ekranını ana dosyaya bağladık
import 'services/auth_service.dart'; // AuthService'i ana dosyaya bağlayarak uygulama genelinde erişilebilir hale getiriyoruz
import 'package:window_manager/window_manager.dart'; // Masaüstü uygulaması için pencere yönetimi kütüphanesi


List<CameraDescription> cameras = []; // Kameraları global bir değişkende tutarak istediğimiz yerden erişebiliriz
void main() async {
  
  WidgetsFlutterBinding.ensureInitialized();

  if(!kIsWeb && (Platform.isWindows || Platform.isLinux || Platform.isMacOS)) {
    await windowManager.ensureInitialized();
    WindowOptions windowOptions = const WindowOptions(
      size: Size(400, 700),
      minimumSize: Size(400, 700),
      maximumSize: Size(400, 700),
      center: true,
      title: "Raf Analiz Uygulaması",
    );
    windowManager.waitUntilReadyToShow(windowOptions, () async {
      await windowManager.show();
      await windowManager.focus();
    });
  }

  await AuthService.yukleVerileri();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false, // Sağ üstteki kırmızı şeridi kaldırır
      home: const SplashScreen(),
    );
  }
}

