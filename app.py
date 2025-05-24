import streamlit as st
import yt_dlp
import os
import sys
from datetime import datetime, timedelta
import subprocess
import time
import tempfile

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(page_title="Pengunduh Video YouTube 🎬", layout="centered")

# --- Fungsi Bawaan ---
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def format_size(bytes_size):
    if bytes_size == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"

# --- Variabel Session State (Inisialisasi) ---
if 'video_url_key' not in st.session_state:
    st.session_state.video_url_key = ""
if 'download_progress' not in st.session_state:
    st.session_state.download_progress = 0
if 'download_status_message' not in st.session_state:
    st.session_state.download_status_message = ""
if 'video_file_path' not in st.session_state:
    st.session_state.video_file_path = None
if 'qualities_labels' not in st.session_state:
    st.session_state.qualities_labels = None
if 'qualities_map' not in st.session_state:
    st.session_state.qualities_map = None
if 'video_info' not in st.session_state:
    st.session_state.video_info = None
if 'error_fetching_info' not in st.session_state:
    st.session_state.error_fetching_info = None
if 'ffmpeg_available' not in st.session_state:
    st.session_state.ffmpeg_available = None

# --- Fungsi Reset Aplikasi ---
def reset_application_state():
    """Mereset semua state aplikasi ke kondisi awal."""
    st.session_state.video_url_key = ""
    st.session_state.download_progress = 0
    st.session_state.download_status_message = ""
    st.session_state.video_file_path = None
    st.session_state.qualities_labels = None
    st.session_state.qualities_map = None
    st.session_state.video_info = None
    st.session_state.error_fetching_info = None
    st.toast("Aplikasi telah direset!", icon="🔄")

# --- Fungsi Inti Pengunduh Video ---
def progress_hook(d):
    if d['status'] == 'downloading':
        downloaded = d.get('downloaded_bytes', 0)
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        if total and total > 0:
            percentage = (downloaded / total) * 100
            st.session_state.download_progress = int(percentage)
            speed = d.get('speed')
            speed_str = format_size(speed) + '/s' if speed else 'N/A'
            eta = d.get('eta')
            eta_str = str(timedelta(seconds=int(eta))) if eta is not None else 'N/A'
            st.session_state.download_status_message = (
                f"Unduh ke Server: {percentage:.1f}% | {format_size(downloaded)}/{format_size(total)} | "
                f"Kecepatan: {speed_str} | ETA: {eta_str}"
            )
        else:
            st.session_state.download_status_message = "Mengunduh ke server... (ukuran total tidak tersedia)"
    elif d['status'] == 'finished':
        st.session_state.download_progress = 100
        st.session_state.download_status_message = "Selesai unduh ke server, memproses file..."
        final_filepath = d.get('info_dict', {}).get('_filename') or d.get('filename')
        if final_filepath and os.path.exists(final_filepath):
            st.session_state.video_file_path = final_filepath

def download_video_streamlit(url, preferred_quality_str,
                             progress_bar, status_text_element, download_link_placeholder_arg):
    st.session_state.video_file_path = None
    st.session_state.download_progress = 0
    st.session_state.download_status_message = "Memulai..."
    try:
        with tempfile.TemporaryDirectory(prefix="yt_dlp_temp_") as tmpdir:
            ffmpeg_available = st.session_state.ffmpeg_available
            ydl_opts_info = {'quiet': True, 'noplaylist': True, 'skip_download': True, 'forcejson': True}
            info = None
            with st.spinner("Mengambil informasi video awal... ⏳"):
                try:
                    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                        info = ydl.extract_info(url, download=False)
                except yt_dlp.utils.DownloadError as e:
                    status_text_element.error(f"Gagal mengambil informasi video: {e}")
                    st.warning("Pastikan URL valid dan video dapat diakses (publik, tidak ada batasan usia/wilayah).")
                    return
                except Exception as e:
                    status_text_element.error(f"Terjadi kesalahan tak terduga saat mengambil info video: {str(e)}")
                    return
            if not info:
                status_text_element.error("Tidak dapat mengambil informasi video. Silakan coba URL lain.")
                return

            st.subheader("Detail Video (Akan Diunduh ke Server Sementara):")
            video_title = info.get('title', 'Tidak Diketahui')
            st.write(f"**Judul:** {video_title}")
            duration_s = info.get('duration')
            st.write(f"**Durasi:** {str(timedelta(seconds=int(duration_s))) if duration_s else 'Tidak diketahui'}")

            safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_- .,()')
            clean_title_list = [c if c in safe_chars else '_' for c in video_title]
            MAX_FILENAME_LEN = 100
            clean_title = "".join(clean_title_list)[:MAX_FILENAME_LEN].strip() or "video_unduhan"
            height = int(preferred_quality_str.replace('p', ''))

            if ffmpeg_available:
                format_selection = (
                    f'bestvideo[height<={height}][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/bestvideo[height<={height}][ext=mp4]+bestaudio/'
                    f'bestvideo[height<={height}][vcodec^=avc1]+bestaudio/bestvideo[height<={height}]+bestaudio/'
                    f'best[height<={height}][ext=mp4]/best[height<={height}]/best'
                )
            else:
                format_selection = (
                    f'best[height<={height}][ext=mp4][vcodec^=avc1][acodec!=none]/'
                    f'best[height<={height}][ext=mp4][acodec!=none]/'
                    f'best[height<={height}][acodec!=none][ext=mp4]'
                )
            filename_template_on_server = os.path.join(tmpdir, f"{clean_title}.%(ext)s")
            ydl_opts_download = {
                'progress_hooks': [progress_hook], 'outtmpl': filename_template_on_server,
                'verbose': False, 'noplaylist': True, 'format': format_selection,
                'merge_output_format': 'mp4',
            }

            status_text_element.info(f"Memulai proses untuk '{video_title}' ({preferred_quality_str}). Video akan diunduh sementara ke server.")
            progress_bar.progress(0)
            status_text_element.text("Mengunduh ke server... 0%")
            download_actually_started = False
            with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                try:
                    ydl.download([url])
                    download_actually_started = True
                except yt_dlp.utils.DownloadError as e:
                    status_text_element.error(f"Gagal mengunduh video ke server: {str(e)}")
                    if "Unsupported URL" in str(e): st.warning("URL mungkin tidak didukung.")
                    elif "Video unavailable" in str(e): st.warning("Video tidak tersedia (mungkin dihapus atau privat).")
                    elif "age-restricted" in str(e).lower(): st.warning("Video ini memiliki batasan usia.")
                    return
                except Exception as e:
                    status_text_element.error(f"Terjadi kesalahan tak terduga saat mengunduh ke server: {str(e)}")
                    return

            max_wait_after_download = 7
            start_wait_time = time.time()
            while st.session_state.download_progress < 100 and \
                  (time.time() - start_wait_time) < max_wait_after_download and \
                  download_actually_started:
                progress_bar.progress(st.session_state.download_progress)
                status_text_element.text(st.session_state.download_status_message)
                time.sleep(0.2)
                if "ETA" not in st.session_state.download_status_message and \
                   "memproses file..." in st.session_state.download_status_message.lower() and \
                   st.session_state.download_progress > 90:
                    time.sleep(0.5)
                elif "ETA" not in st.session_state.download_status_message and st.session_state.download_progress > 0:
                    break
            progress_bar.progress(st.session_state.download_progress)
            status_text_element.text(st.session_state.download_status_message)

            final_video_server_path = st.session_state.video_file_path
            if not final_video_server_path or not os.path.isfile(final_video_server_path):
                potential_filename_mp4 = f"{clean_title}.mp4"
                potential_path = os.path.join(tmpdir, potential_filename_mp4)
                if os.path.isfile(potential_path):
                    final_video_server_path = potential_path
                    st.session_state.video_file_path = final_video_server_path
                    st.info(f"Menggunakan path fallback: {potential_filename_mp4}")
                else:
                    found_files = [f for f in os.listdir(tmpdir) if f.startswith(clean_title) and os.path.isfile(os.path.join(tmpdir, f))]
                    if found_files:
                        final_video_server_path = os.path.join(tmpdir, found_files[0])
                        st.session_state.video_file_path = final_video_server_path
                        st.warning(f"Menggunakan file pertama yang ditemukan di server: {found_files[0]}")
                    else:
                        status_text_element.error(f"File video tidak ditemukan di direktori temporer server ('{tmpdir}') setelah proses unduh.")
                        return
            if not os.path.isfile(final_video_server_path):
                status_text_element.error(f"Path file video di server ('{final_video_server_path}') tidak valid atau bukan file.")
                return

            client_download_filename = f"{clean_title}.mp4"
            if st.session_state.download_progress == 100:
                status_text_element.success(f"Video '{client_download_filename}' siap diunduh dari server!")
                try:
                    with open(final_video_server_path, "rb") as file_to_download_data:
                        download_link_placeholder_arg.download_button(
                            label=f"📥 Unduh '{client_download_filename}' ke Komputer Anda",
                            data=file_to_download_data, file_name=client_download_filename,
                            mime="video/mp4"
                        )
                    st.info(f"File sementara di server ('{os.path.basename(final_video_server_path)}' dalam '{tmpdir}') akan otomatis dihapus.")
                except FileNotFoundError:
                    status_text_element.error(f"File temporer tidak ditemukan di server untuk diunduh: {final_video_server_path}")
                except Exception as e_btn:
                    status_text_element.error(f"Tidak bisa membuat tombol unduh: {e_btn}")
            elif download_actually_started:
                status_text_element.warning("Proses unduhan ke server selesai, tetapi progres tidak mencapai 100%.")
    except Exception as e_outer:
        status_text_element.error(f"Terjadi kesalahan pada aplikasi: {str(e_outer)}")
        st.markdown("""**Tips Pemecahan Masalah Tambahan:**
        1. Pastikan `yt-dlp` dan `ffmpeg` (jika digunakan) adalah versi terbaru.
        2. Coba URL video dari sumber atau channel yang berbeda.
        3. Periksa log terminal tempat Anda menjalankan `streamlit run app.py`.""")

# --- Antarmuka Streamlit Utama ---
st.title("Pengunduh Video YouTube 🎞️")
st.markdown("""
Selamat datang gaes! 
1. Tempel URL video YouTube kemudian tekan Enter. 
2. Pilih kualitas. 
3. Lalu klik tombol unduh.
4. Video akan **diproses dan diunduh sementara di server** kami. 
5. Setelah siap, Anda akan melihat tombol untuk **mengunduh file MP4 tersebut ke komputer Anda**. 
6. Dialog "Simpan Sebagai..." akan muncul dari browser Anda.
**File sementara di server akan dihapus secara otomatis.**
""")

# --- Input URL dan Tombol Reset ---
video_url = st.text_input(
    "🔗 Masukkan URL Video YouTube:",
    placeholder="Contoh: https://www.youtube.com/watch?v=...",
    key="video_url_key", # Terhubung dengan st.session_state.video_url_key
    # label_visibility="collapsed" # Bisa diaktifkan jika label dirasa redundan
)

st.button(
    "🔄 Reset Aplikasi",
    on_click=reset_application_state,
    key="reset_app_btn",
    help="Hapus URL, hasil, dan kembalikan aplikasi ke kondisi awal."
)

# --- Pemeriksaan FFmpeg ---
if st.session_state.ffmpeg_available is None:
    with st.spinner("Memeriksa instalasi FFmpeg..."):
        st.session_state.ffmpeg_available = check_ffmpeg()

if not st.session_state.ffmpeg_available:
    st.warning("""**Perhatian:** FFmpeg tidak ditemukan. Kemampuan mengunduh dan menggabungkan kualitas video/audio terbaik mungkin terbatas. 
    Aplikasi akan mencoba mengunduh format MP4 pra-gabung terbaik yang tersedia. 
    Instal FFmpeg dan pastikan ada di PATH sistem Anda untuk fungsionalitas penuh.""")
else:
    st.info("**FFmpeg terdeteksi!** Opsi kualitas video penuh dan penggabungan audio ke MP4 didukung. ✅", icon="🛠️")

# --- Placeholder untuk UI Dinamis ---
progress_bar_placeholder = st.empty()
status_message_placeholder = st.empty()
download_link_placeholder = st.empty()

# --- Logika Utama Aplikasi (setelah input URL) ---
if st.session_state.video_url_key:
    if st.button("🔍 Pilih Kualitas", key="get_quality_button_main"):
        progress_bar_placeholder.empty()
        status_message_placeholder.empty()
        download_link_placeholder.empty()
        st.session_state.qualities_labels = None
        st.session_state.qualities_map = None
        st.session_state.video_info = None
        st.session_state.error_fetching_info = None

        with st.spinner("Mengambil informasi kualitas video... Harap tunggu. 🕵️‍♂️"):
            try:
                ydl_opts_info_qual = {'quiet': True, 'noplaylist': True, 'skip_download': True}
                with yt_dlp.YoutubeDL(ydl_opts_info_qual) as ydl:
                    info_dict_qual = ydl.extract_info(st.session_state.video_url_key, download=False)
                st.session_state.video_info = info_dict_qual
                formats_list = info_dict_qual.get('formats', [])
                quality_set_unique = set()
                temp_qualities_list_details = []

                for f_format_detail in formats_list:
                    height_val = f_format_detail.get('height')
                    ext_val = f_format_detail.get('ext')
                    vcodec_val = f_format_detail.get('vcodec', 'none')
                    acodec_val = f_format_detail.get('acodec', 'none')
                    
                    if height_val and vcodec_val != 'none':
                        if not st.session_state.ffmpeg_available and (acodec_val == 'none' or ext_val != 'mp4'):
                            if not (ext_val == 'mp4' and acodec_val != 'none'):
                                continue
                        label_str = f"{height_val}p"
                        quality_key_str = f"{height_val}p"
                        if quality_key_str not in quality_set_unique:
                            temp_qualities_list_details.append({'height': height_val, 'label': label_str})
                            quality_set_unique.add(quality_key_str)
                
                if not temp_qualities_list_details:
                    st.warning("Tidak ada kualitas video yang cocok ditemukan (target MP4). Video mungkin tidak tersedia, privat, atau formatnya tidak didukung.")
                    st.session_state.error_fetching_info = True
                else:
                    sorted_qualities_details = sorted(temp_qualities_list_details, key=lambda x: x['height'], reverse=True)
                    st.session_state.qualities_labels = [q['label'] for q in sorted_qualities_details]
                    st.session_state.qualities_map = {q['label']: str(q['height']) + 'p' for q in sorted_qualities_details}
                    
                    st.subheader("Pratinjau Video:")
                    video_title_prev = st.session_state.video_info.get('title', 'Tidak Diketahui')
                    st.write(f"**Judul:** {video_title_prev}")
                    duration_prev_s = st.session_state.video_info.get('duration')
                    if duration_prev_s: st.write(f"**Durasi:** {str(timedelta(seconds=int(duration_prev_s)))}")
                    thumbnail_url = st.session_state.video_info.get('thumbnail')
                    if thumbnail_url: st.image(thumbnail_url, caption=video_title_prev, width=320)

            except yt_dlp.utils.DownloadError as e_info_fetch:
                st.error(f"Gagal mengambil informasi video: {str(e_info_fetch)}")
                st.warning("Pastikan URL valid, video publik, dan tidak ada batasan geografis/usia.")
                st.session_state.error_fetching_info = True
            except Exception as e_info_general_fetch:
                st.error(f"Terjadi kesalahan tak terduga saat mengambil info kualitas: {str(e_info_general_fetch)}")
                st.session_state.error_fetching_info = True

    if st.session_state.get('qualities_labels') and not st.session_state.get('error_fetching_info'):
        st.subheader("Pilih Kualitas Video (Output Akan Selalu MP4):")
        default_quality_idx_val = 0
        preferred_defaults_q_list = ["1080p", "720p"]
        for pref_q_item in preferred_defaults_q_list:
            if pref_q_item in st.session_state.qualities_labels:
                default_quality_idx_val = st.session_state.qualities_labels.index(pref_q_item)
                break
        
        selected_quality_label_str = st.selectbox(
            "Pilih kualitas yang diinginkan:", options=st.session_state.qualities_labels,
            index=default_quality_idx_val, key="quality_select_box_key"
        )
        preferred_quality_actual_val_str = st.session_state.qualities_map.get(selected_quality_label_str, "best")
        video_title_for_button = st.session_state.video_info.get('title', 'Video')
        max_title_len_button = 30
        if len(video_title_for_button) > max_title_len_button:
            video_title_for_button = video_title_for_button[:max_title_len_button] + "..."

        if st.button(f"🚀 Unduh", key="download_video_key_final"):
            if st.session_state.video_url_key and preferred_quality_actual_val_str:
                progress_bar_placeholder.empty()
                status_message_placeholder.empty()
                download_link_placeholder.empty()
                current_progress_bar_ui_el = progress_bar_placeholder.progress(0)
                current_status_text_ui_el = status_message_placeholder.empty() 
                current_download_link_ui_el = download_link_placeholder.empty()
                download_video_streamlit(
                    st.session_state.video_url_key,
                    preferred_quality_actual_val_str,
                    current_progress_bar_ui_el,
                    current_status_text_ui_el,
                    current_download_link_ui_el
                )
            else:
                st.warning("URL video atau pilihan kualitas tidak valid. Harap masukkan URL dan dapatkan kualitas lagi.")
    elif st.session_state.get('error_fetching_info') and st.session_state.video_url_key :
        st.info("Tidak dapat melanjutkan karena gagal mengambil info video. Silakan perbaiki URL atau coba video lain, lalu klik 'Dapatkan Pilihan Kualitas Video' lagi.")

st.markdown("---")
st.markdown("Dibuat dengan ❤️ oleh Mas Oki.")