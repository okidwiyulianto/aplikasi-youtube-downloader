# 🎬 Pengunduh Video YouTube Super Kece dengan Streamlit! 🚀

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Terbaru-ff69b4?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-Terbaru-brightgreen?style=for-the-badge)](https://github.com/yt-dlp/yt-dlp)

👋 Selamat datang di **Pengunduh Video YouTube Super Kece**! Aplikasi web sederhana namun powerful yang dibangun dengan Python dan Streamlit untuk mengunduh video favoritmu dari YouTube dengan mudah dan cepat. Ucapkan selamat tinggal pada proses unduh yang ribet! 😉

<p align="center">
  <em>[Screenshot](.assets/sc-aplikasi-youtube-downloader.png)</em>
</p>

## 🌟 Fitur Unggulan

Aplikasi ini hadir dengan berbagai fitur keren untuk memudahkan hidup Anda:

* 📥 **Unduh Video YouTube**: Cukup tempel URL video YouTube dan biarkan aplikasi melakukan sisanya.
* 🎞️ **Pilih Kualitas Video**: Dapatkan daftar kualitas video yang tersedia (misalnya 720p, 1080p) dan pilih sesuai keinginanmu.
* ⚙️ **Output MP4 (Video & Audio)**: Video akan diunduh lengkap dengan audio dalam format MP4 yang universal.
* ⏳ **Progres Unduhan Real-time**: Pantau proses unduhan ke server dengan progress bar dan detail status (ukuran, kecepatan, ETA).
* 🛠️ **Deteksi FFmpeg Otomatis**: Aplikasi akan mendeteksi keberadaan FFmpeg di sistem Anda. FFmpeg disarankan untuk kualitas terbaik dan penggabungan format video/audio resolusi tinggi.
* 🧹 **Penyimpanan Server Temporer & Otomatis Bersih**: Video diproses sementara di server dan file temporer akan dihapus secara otomatis. Aman dan hemat ruang!
* 🔄 **Tombol Reset Cerdas**: Ingin memulai dari awal? Tombol reset akan membersihkan semua input dan hasil sebelumnya dengan sekali klik.
* 🎨 **Antarmuka Pengguna Intuitif**: Dibangun dengan Streamlit, memberikan pengalaman pengguna yang bersih dan mudah digunakan.

## 🛠️ Teknologi yang Digunakan

Proyek ini dibangun menggunakan teknologi-teknologi hebat berikut:

* **Python**: Bahasa pemrograman utama yang serbaguna.
* **Streamlit**: Framework Python open-source untuk membuat aplikasi web data sains dan machine learning dengan cepat.
* **yt-dlp**: Fork dari youtube-dl yang sangat powerful dan selalu update untuk mengunduh video dari berbagai sumber, termasuk YouTube.
* **FFmpeg** (Opsional, tapi Sangat Direkomendasikan): Untuk kemampuan pemrosesan video dan audio terbaik, terutama untuk menggabungkan stream video dan audio berkualitas tinggi.

## 🚀 Instalasi & Setup Lokal

Ingin menjalankan aplikasi ini di komputermu? Ikuti langkah-langkah mudah berikut:

1.  **Prasyarat:**
    * Pastikan **Python 3.7** atau versi lebih baru sudah terinstal.
    * Pastikan **pip** (package installer for Python) juga sudah terinstal dan terupdate.
    * (Sangat Direkomendasikan) **FFmpeg**:
        * Unduh dan instal FFmpeg dari [situs resminya](https://ffmpeg.org/download.html).
        * Pastikan FFmpeg ditambahkan ke PATH sistem Anda agar bisa diakses dari mana saja oleh aplikasi.

2.  **Clone Repositori:**
    ```bash
    git clone https://github.com/okidwiyulianto/aplikasi-youtube-downloader.git
    cd aplikasi-youtube-downloader
    ```

3.  **Buat dan Aktifkan Virtual Environment (Sangat Direkomendasikan):**
    ```bash
    python -m venv venv
    # Untuk Windows:
    venv\Scripts\activate
    # Untuk macOS/Linux:
    source venv/bin/activate
    ```

4.  **Install Dependencies:**
    Buat file `requirements.txt` di root direktori proyek Anda dengan isi berikut:
    ```txt
    streamlit
    yt-dlp
    ```
    Kemudian jalankan perintah berikut di terminal Anda (pastikan virtual environment sudah aktif):
    ```bash
    pip install -r requirements.txt
    ```

## 🏃 Menjalankan Aplikasi

Setelah semua dependensi terinstal, jalankan aplikasi dengan perintah berikut di terminal dari direktori root proyek:

```bash
streamlit run app.py
```