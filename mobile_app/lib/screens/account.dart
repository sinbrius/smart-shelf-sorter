import "package:flutter/material.dart";
import "../services/auth_service.dart";
import "login.dart"; // Giriş ekranına geri dönebilmesi için onu bağladık

class AccountScreen extends StatefulWidget {
  const AccountScreen({super.key});

  @override
  State<AccountScreen> createState() => _AccountScreenState();
}

class _AccountScreenState extends State<AccountScreen> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  @override
  void initState() {
    super.initState();
    // Burada gerçek uygulamada kullanıcı bilgilerini çekip controller'lara atarız
    _emailController.text = AuthService.email;
    _passwordController.text = AuthService.password;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
         title: const Icon(Icons.menu_book_rounded, color: Colors.white),
        centerTitle: true,
        backgroundColor: const Color(0xff122E26),
      ),
      body: SizedBox(
        width: double.infinity,
        height: double.infinity,
        child: Container(
          color: Colors.white.withAlpha(128),
          child: SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 30.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const SizedBox(height: 40),
                  Text(
                    'Hesap Bilgileri',
                    style: TextStyle(fontSize: 18, color: Colors.black87),
                  ),
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Padding(
                      padding: EdgeInsets.only(top: 20.0, bottom: 10.0),
                      child: Text(
                        'Email Adresi:',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                  TextField(
                    controller: _emailController,
                    decoration: InputDecoration(
                      hintText: 'example@gmail.com',
                      hintStyle: TextStyle(color: Colors.black54),
                      enabledBorder: UnderlineInputBorder(
                        borderSide: BorderSide(color: Colors.black),
                      ),
                  ),
              ),
              // 4. Şifre Giriş Kutusu
                const Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'Şifre',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ),
                 TextField(
                  controller: _passwordController,
                  obscureText: true, // Yazılan şifreyi gizli yapar (●●●●)
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

                const SizedBox(height: 30),
                SizedBox(width: double.infinity,
                height: 40,
                child: ElevatedButton(
                  onPressed: () async {
                    String newEmail = _emailController.text.trim();
                    String newPassword = _passwordController.text.trim();
                    // Buraya hesap bilgilerini güncelleme işlemi eklenebilir
                    if(newEmail.isEmpty || newPassword.isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('E-mail ve Şifre boş bırakılamaz!'),
                          backgroundColor: Colors.redAccent,
                          behavior: SnackBarBehavior.floating,
                        ),
                      );
                    } else {
                      await AuthService.verileriKaydet(newEmail, newPassword);
                      setState(() {}); // Değişiklikleri ekrana yansıtmak için setState çağırıyoruz
                    }
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Hesap bilgileri güncellendi!'),
                        backgroundColor: Colors.green,
                        behavior: SnackBarBehavior.floating,
                      
                      ),
                    );
                    Navigator.of(context).pushAndRemoveUntil(
                    MaterialPageRoute(builder: (context) => LoginScreen()), // Senin login sınıfının adı (const'sız olmasına dikkat kanka)
                    (Route<dynamic> route) => false, // Bu 'false' ifadesi geçmişteki tüm sayfaları hafızadan siler!
            );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xff122E26),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text('Hesap Bilgilerini Güncelle',
                    style: TextStyle(color: Colors.white),
                  ),
                    
                ),
                            
              ),
            ],
              ),
            ),
          ),
        ),
      
      ),
    );
  }
}