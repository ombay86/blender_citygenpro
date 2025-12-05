# blender_citygenpro
Generate Modular City with Auto-Roads in Blender

Cara Instalasi (Beda dengan Script Biasa)
1. Buka Notepad atau Text Editor di komputer Anda.
2. Copy-Paste kode di bawah ini.
3. Simpan file dengan nama: city_gen_pro.py (Pastikan ekstensi filenya .py, bukan .txt).
4. Di Blender, buka Edit > Preferences > Add-ons.
5. Klik Install..., cari file city_gen_pro.py tadi, lalu centang kotak putihnya untuk mengaktifkan.
6. Tutup Preferences. Tekan N di keyboard (di 3D Viewport), cari tab baru bernama "City Gen".

Cara Menggunakan Plugin Ini
Setelah plugin aktif, lihat di N-Panel (tekan N di viewport), tab "City Gen":
1. Settings:
    Size X / Size Y: Ukuran kota (jumlah grid).
    Block Size: PENTING! Isi sesuai lebar jalan Anda (misalnya 4 meter atau 10 meter).
2. Pattern:
    Road Interval: Seberapa sering jalan muncul? (Angka 3 = Jalan setiap 3 blok).
    Building Density: Seberapa padat gedungnya?
    Seed: Ubah angka ini untuk mendapatkan variasi kota yang berbeda dengan setting yang sama.
3. Assets:
    Road Collection: Isi nama collection jalan Anda (Default: My_Roads). Pastikan isinya (Road_Straight, Road_Corner, dll) sudah disetup sesuai diskusi kita sebelumnya.
    Bldg Collection: Isi nama collection gedung Anda (Default: My_Buildings).
4. Tombol Generate:
    Klik Generate City.
    Boom! Kota muncul. Tidak suka hasilnya? Ubah Seed, klik Generate lagi (otomatis menghapus yang lama).
