import streamlit as st
import json
import os
import hashlib
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Setup Konfigurasi Halaman
st.set_page_config(
    page_title="GALERI KENANGAN PRODI TEKNOLOGI 21",
    page_icon="🎓",
    layout="wide"
)

# --- MASUKKAN ID FOLDER GOOGLE DRIVE KAMU DI SINI ---
# Bersihkan dari parameter URL seperti ?hl=ID
DRIVE_FOLDER_ID = "1E-4Mmx_YARr7Gqv00zuoLY2T13yPXSoH"

# Folder Penyimpanan File Lokal & JSON
UPLOAD_DIR = "uploads"
AUDIO_DIR = "audio"
DATA_FILE = "intelligence_data.json"
USER_FILE = "users_db.json"
CREDENTIALS_FILE = "credentials.json"

# Master Password Global untuk Registrasi
REGISTRATION_MASTER_KEY = "teknologi@2024"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# --- FUNGSI GOOGLE DRIVE API ---
def get_drive_service():
    """Inisialisasi koneksi ke Google Drive Service Account dengan penanganan error"""
    try:
        # 1. Cek file lokal credentials.json
        if os.path.exists(CREDENTIALS_FILE):
            creds = service_account.Credentials.from_service_account_file(
                CREDENTIALS_FILE,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            return build('drive', 'v3', credentials=creds)
        
        # 2. Cek Streamlit Secrets (Cloud)
        elif "gcp_service_account" in st.secrets:
            creds = service_account.Credentials.from_service_account_info(
                dict(st.secrets["gcp_service_account"]),
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            return build('drive', 'v3', credentials=creds)
        else:
            st.error("⚠️ Kredensial Google Drive tidak ditemukan! Harap sediakan 'credentials.json' atau atur '[gcp_service_account]' di Streamlit Secrets.")
            return None
    except Exception as e:
        st.error(f"❌ Gagal Inisialisasi Google Drive API: {e}")
        return None

def upload_to_google_drive(file_path, file_name, folder_id):
    """Mengunggah file ke folder Google Drive"""
    # Otomatis bersihkan parameter URL seperti ?hl=ID dari ID folder
    if folder_id and "?" in folder_id:
        folder_id = folder_id.split("?")[0]
        
    # Ambil dari Secrets jika ID folder di kode belum valid
    if (not folder_id or folder_id == "MASUKKAN_ID_FOLDER_DRIVE_KAMU_DI_SINI") and "DRIVE_FOLDER_ID" in st.secrets:
        folder_id = st.secrets["DRIVE_FOLDER_ID"]

    if not folder_id or folder_id == "MASUKKAN_ID_FOLDER_DRIVE_KAMU_DI_SINI":
        st.error("⚠️ ID Folder Google Drive belum diisi atau tidak valid!")
        return None

    service = get_drive_service()
    if service:
        try:
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            media = MediaFileUpload(file_path, resumable=True)
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            return file.get('id')
        except Exception as e:
            st.error(f"❌ Gagal upload ke Google Drive: {e}")
            return None
    return None

# --- HELPER DATABASE LOCAL ---
def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {} if "users" in filepath else []

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_uploaded_audio_files():
    if os.path.exists(AUDIO_DIR):
        files = [f for f in os.listdir(AUDIO_DIR) if f.lower().endswith(('.mp3', '.wav'))]
        return files
    return []

# --- INIT SESSION STATE ---
if "users" not in st.session_state:
    st.session_state.users = load_json(USER_FILE)

if "memories" not in st.session_state:
    st.session_state.memories = load_json(DATA_FILE)

uploaded_songs = get_uploaded_audio_files()

if "active_audio" not in st.session_state:
    if uploaded_songs:
        st.session_state.active_audio = os.path.join(AUDIO_DIR, uploaded_songs[0])
    else:
        st.session_state.active_audio = None

if "logged_user" not in st.session_state:
    st.session_state.logged_user = None

# --- STYLING CSS MODERN GLASSMORPHISM & SEMBUNYIKAN HEADER GITHUB ---
st.markdown("""
    <style>
    /* Sembunyikan Header Bawaan Streamlit (Termasuk Ikon GitHub) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Background Utama */
    .stApp {
        background: radial-gradient(circle at 20% 20%, #1e1b4b 0%, #0f172a 40%, #020617 100%) !important;
        background-attachment: fixed !important;
        color: #f8fafc !important;
    }
    
    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    /* Typography */
    h1 {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    
    h2, h3 { color: #38bdf8 !important; }

    .names-badge {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 20px;
        color: #cbd5e1 !important;
        backdrop-filter: blur(8px);
    }

    /* Form Container */
    [data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        backdrop-filter: blur(12px) !important;
    }

    /* Inputs */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="textarea"] > div,
    input, textarea {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
    }

    /* Buttons */
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #0284c7 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* Card Foto */
    .memory-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }

    .badge-uploader {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: CONTROL CENTER & AUDIO PLAYER ---
st.sidebar.markdown("## 📡 CONTROL CENTER")

if st.session_state.logged_user:
    st.sidebar.markdown(f"**Status:** `<{st.session_state.logged_user}>` 🟢")
    if st.sidebar.button("🔴 Logout / Disconnect"):
        st.session_state.logged_user = None
        st.rerun()
else:
    st.sidebar.markdown("**Status:** `OFFLINE` 🔴")

st.sidebar.markdown("---")

# Pemutar Musik
st.sidebar.markdown("### 🎵 Musik Latar")
current_audio = st.session_state.active_audio

if current_audio and os.path.exists(current_audio):
    st.sidebar.audio(current_audio, autoplay=True)
else:
    st.sidebar.info("💡 Belum ada lagu terunggah. Silakan upload file lagu MP3/WAV di bawah.")

# Pengaturan Musik
st.sidebar.markdown("#### ⚙️ Ganti / Tambah Musik")
audio_source_type = st.sidebar.radio("Sumber Audio:", ["Upload File MP3", "Pilih Playlist"])

if audio_source_type == "Upload File MP3":
    uploaded_audio = st.sidebar.file_uploader("Upload File Lagu (.mp3, .wav):", type=["mp3", "wav"])
    if uploaded_audio is not None:
        if st.sidebar.button("Simpan & Putar Lagu"):
            audio_path = os.path.join(AUDIO_DIR, uploaded_audio.name)
            with open(audio_path, "wb") as f:
                f.write(uploaded_audio.getbuffer())
            
            # Backup Lagu ke Google Drive
            upload_to_google_drive(audio_path, uploaded_audio.name, DRIVE_FOLDER_ID)
            
            st.session_state.active_audio = audio_path
            st.sidebar.success(f"Lagu '{uploaded_audio.name}' Berhasil Diputar & Disimpan!")
            st.rerun()

elif audio_source_type == "Pilih Playlist":
    available_songs = get_uploaded_audio_files()
    if available_songs:
        selected_song = st.sidebar.selectbox("Pilih Lagu (Terupload):", available_songs)
        if st.sidebar.button("Putar Lagu Terpilih"):
            st.session_state.active_audio = os.path.join(AUDIO_DIR, selected_song)
            st.sidebar.success(f"Memutar: {selected_song}")
            st.rerun()
    else:
        st.sidebar.warning("⚠️ Belum ada file lagu di folder 'audio'. Upload lagu terlebih dahulu!")

# --- HEADER UTAMA ---
st.title("🎓 GALERI KENANGAN PRODI TEKNOLOGI 21")

st.markdown("""
<div class="names-badge">
✨ <b>ANGGOTA TEKNOLOGI 21:</b><br>
ALKAHFI • ARINTO • ALZAKI • DAMAR • DEDI • GAVRI • MARIO • MADAN • MUKTI • MAHESA • MAHDI • 
NIKO • RAJA • SANDI • SALMAN • WIRA • YANTO • MUSTOFA • VELANTIKA • NAJMA • TAMI • AMARA
</div>
""", unsafe_allow_html=True)

# --- AUTHENTICATION (LOGIN & REGISTER) ---
if not st.session_state.logged_user:
    st.warning("🔒 SISTEM TERPROTEKSI: Anda harus login terlebih dahulu untuk mengakses galeri dan mengunggah foto.")
    
    tab_login, tab_register = st.tabs(["🔒 LOGIN AKUN", "📝 REGISTRASI BARU"])
    
    with tab_login:
        with st.form("login_form"):
            st.markdown("### Masuk ke Akun Anda")
            username = st.text_input("Username / Nama Anggota:")
            password = st.text_input("Kata Sandi:", type="password")
            btn_login = st.form_submit_button("Masuk Ke Galeri")
            
            if btn_login:
                hashed = hash_password(password)
                if username in st.session_state.users and st.session_state.users[username] == hashed:
                    st.session_state.logged_user = username
                    st.success(f"Selamat Datang Kembali, {username}!")
                    st.rerun()
                else:
                    st.error("Username atau Kata Sandi Salah!")
                    
    with tab_register:
        with st.form("register_form"):
            st.markdown("### Buat Akun Anggota Baru")
            reg_username = st.text_input("Buat Username:")
            reg_password = st.text_input("Buat Kata Sandi Akun:", type="password")
            global_key = st.text_input("Password Otorisasi Registrasi Global:", type="password")
            btn_register = st.form_submit_button("Daftarkan Akun")
            
            if btn_register:
                if reg_username and reg_password and global_key:
                    if global_key != REGISTRATION_MASTER_KEY:
                        st.error("Password Otorisasi Global Registrasi Salah!")
                    elif reg_username in st.session_state.users:
                        st.error("Username Sudah Terdaftar!")
                    else:
                        st.session_state.users[reg_username] = hash_password(reg_password)
                        save_json(USER_FILE, st.session_state.users)
                        st.success("Akun Berhasil Didaftarkan! Silakan Login pada Tab Login.")
                else:
                    st.error("Harap Isi Semua Bidang Registration!")

else:
    # --- GALERI & UNGGAH FOTO ---
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Arsip Foto", f"{len(st.session_state.memories)} Foto")
    col_m2.metric("Anggota Terdaftar", f"{len(st.session_state.users)} Akun")
    col_m3.metric("Status Cloud Drive", "Terhubung ☁️")

    st.markdown("---")

    with st.expander("📂 UNGGAH FOTO KENANGAN BARU", expanded=True):
        with st.form("upload_archive_form", clear_on_submit=True):
            st.markdown(f"**Pengunggah:** `{st.session_state.logged_user}`")
            caption = st.text_area("Deskripsi / Catatan Cerita Kenangan:")
            uploaded_img = st.file_uploader("Pilih File Foto Kenangan:", type=["jpg", "jpeg", "png"])
            
            submit_archive = st.form_submit_button("💾 Simpan Kenangan")
            
            if submit_archive:
                if uploaded_img and caption:
                    img_path = os.path.join(UPLOAD_DIR, uploaded_img.name)
                    with open(img_path, "wb") as f:
                        f.write(uploaded_img.getbuffer())
                    
                    # 🚀 AUTO-UPLOAD KE GOOGLE DRIVE
                    drive_id = upload_to_google_drive(img_path, uploaded_img.name, DRIVE_FOLDER_ID)
                    
                    new_memory = {
                        "agent": st.session_state.logged_user,
                        "caption": caption,
                        "image_path": img_path,
                        "drive_id": drive_id,
                        "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M")
                    }
                    
                    st.session_state.memories.append(new_memory)
                    save_json(DATA_FILE, st.session_state.memories)
                    
                    if drive_id:
                        st.success("Foto Berhasil Disimpan di Lokal & Google Drive!")
                    else:
                        st.warning("Foto Berhasil Disimpan di Lokal, Namun Gagal Terunggah ke Google Drive. Cek Pesan Error di Atas!")
                    st.rerun()
                else:
                    st.error("Deskripsi dan File Foto Wajib Diisi!")

    # --- GALERI FOTO ---
    st.markdown("### 📸 ARSIP FOTO KENANGAN")

    memories = st.session_state.memories

    if not memories:
        st.info("Belum ada kenangan yang diunggah. Jadilah yang pertama!")
    else:
        cols = st.columns(3)
        for index, item in enumerate(reversed(memories)):
            col = cols[index % 3]
            with col:
                st.markdown('<div class="memory-card">', unsafe_allow_html=True)
                if os.path.exists(item["image_path"]):
                    st.image(item["image_path"], use_container_width=True)
                else:
                    st.warning("⚠️ File Foto Tidak Ditemukan")
                
                st.markdown(f"<p style='margin-top:10px; font-weight:600;'>{item['caption']}</p>", unsafe_allow_html=True)
                st.markdown(f"<span class='badge-uploader'>👤 {item['agent']}</span>", unsafe_allow_html=True)
                st.caption(f"🕒 {item['timestamp']}")
                st.markdown('</div>', unsafe_allow_html=True)