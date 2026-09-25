import streamlit as st
import json
import os
import hashlib
from datetime import datetime

# Setup Konfigurasi Halaman
st.set_page_config(
    page_title="GALERI KENANGAN PRODI TEKNOLOGI 21",
    page_icon="🎓",
    layout="wide"
)

# Folder Penyimpanan File
UPLOAD_DIR = "uploads"
AUDIO_DIR = "audio"
DATA_FILE = "intelligence_data.json"
USER_FILE = "users_db.json"

# Master Password Global untuk Registrasi
REGISTRATION_MASTER_KEY = "teknologi@2024"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Fungsi untuk Memindai File Lagu dari Folder audio/
def get_uploaded_audio_files():
    if os.path.exists(AUDIO_DIR):
        files = [f for f in os.listdir(AUDIO_DIR) if f.lower().endswith(('.mp3', '.wav'))]
        return files
    return []

# Helper untuk Hashing Password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fungsi Load & Save Data
def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {} if "users" in filepath else []

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

# Inisialisasi Database dalam Session State
if "users" not in st.session_state:
    st.session_state.users = load_json(USER_FILE)

if "memories" not in st.session_state:
    st.session_state.memories = load_json(DATA_FILE)

# Mendapatkan daftar lagu lokal yang telah terunggah
uploaded_songs = get_uploaded_audio_files()

if "active_audio" not in st.session_state:
    if uploaded_songs:
        st.session_state.active_audio = os.path.join(AUDIO_DIR, uploaded_songs[0])
    else:
        st.session_state.active_audio = None

if "logged_user" not in st.session_state:
    st.session_state.logged_user = None

# --- STYLING CSS MODERN GLASSMORPHISM & NEON GRADIENT ---
st.markdown("""
    <style>
    /* 1. Background Utama - Deep Cyber Nebula Gradient */
    .stApp {
        background: radial-gradient(circle at 20% 20%, #1e1b4b 0%, #0f172a 40%, #020617 100%) !important;
        background-attachment: fixed !important;
        color: #f8fafc !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    }
    
    /* 2. Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    /* 3. Typography & Judul */
    h1 {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        margin-bottom: 0px !important;
    }
    
    h2, h3 {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }

    .names-badge {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px 18px;
        margin-top: 10px;
        margin-bottom: 25px;
        font-size: 0.9rem;
        color: #cbd5e1 !important;
        backdrop-filter: blur(8px);
        line-height: 1.6;
    }

    /* 4. Form Container Glassmorphism */
    [data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border-radius: 16px !important;
        padding: 28px !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(12px) !important;
    }

    /* 5. Inputs (Text, Password, Textarea) Rapi & Elegan */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="textarea"] > div,
    input, textarea {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
    }
    input:focus, textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.3) !important;
    }

    /* 6. Buttons Styling */
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #0284c7 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3) !important;
    }
    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    }

    /* 7. Tabs (Login / Register) */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border-bottom: 2px solid transparent !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    button[aria-selected="true"] {
        border-bottom: 2px solid #38bdf8 !important;
    }
    button[aria-selected="true"] p {
        color: #38bdf8 !important;
    }

    /* 8. Warning & Info Notification Box */
    div[data-testid="stNotification"] {
        background: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid rgba(245, 158, 11, 0.4) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(8px) !important;
    }
    div[data-testid="stNotification"] * {
        color: #fbbf24 !important;
    }

    /* 9. Card Foto Kenangan (Glassmorphism + Hover Effect) */
    .memory-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
    }
    .memory-card:hover {
        transform: translateY(-5px);
        border-color: rgba(56, 189, 248, 0.5);
        box-shadow: 0 15px 30px rgba(56, 189, 248, 0.2);
    }

    .badge-uploader {
        display: inline-block;
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 8px;
    }

    /* File Uploader Container Fix */
    [data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px dashed rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 10px !important;
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
elif current_audio and current_audio.startswith("http"):
    st.sidebar.audio(current_audio, autoplay=True)
else:
    st.sidebar.info("💡 Belum ada lagu terunggah. Silakan upload file lagu MP3/WAV di bawah.")

# Pengaturan Musik
st.sidebar.markdown("#### ⚙️ Ganti / Tambah Musik")
audio_source_type = st.sidebar.radio("Sumber Audio:", ["Upload File MP3", "Pilih Playlist", "URL Link MP3"])

if audio_source_type == "Upload File MP3":
    uploaded_audio = st.sidebar.file_uploader("Upload File Lagu (.mp3, .wav):", type=["mp3", "wav"])
    if uploaded_audio is not None:
        if st.sidebar.button("Simpan & Putar Lagu"):
            audio_path = os.path.join(AUDIO_DIR, uploaded_audio.name)
            with open(audio_path, "wb") as f:
                f.write(uploaded_audio.getbuffer())
            st.session_state.active_audio = audio_path
            st.sidebar.success(f"Lagu '{uploaded_audio.name}' Berhasil Diputar!")
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

else:
    new_url = st.sidebar.text_input("Masukkan URL Link Audio MP3:")
    if st.sidebar.button("Set Audio Link"):
        if new_url:
            st.session_state.active_audio = new_url
            st.sidebar.success("Frekuensi Audio Diperbarui!")
            st.rerun()

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
    # --- JIKA SUDAH LOGIN: TAMPILKAN METRIK, FORM UNGGAH & GALERI FOTO ---
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Arsip Foto", f"{len(st.session_state.memories)} Foto")
    col_m2.metric("Anggota Terdaftar", f"{len(st.session_state.users)} Akun")
    col_m3.metric("Status Server", "Online 🟢")

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
                    
                    new_memory = {
                        "agent": st.session_state.logged_user,
                        "caption": caption,
                        "image_path": img_path,
                        "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M")
                    }
                    
                    st.session_state.memories.append(new_memory)
                    save_json(DATA_FILE, st.session_state.memories)
                    st.success("Foto Berhasil Disimpan Ke Galeri!")
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
                
                st.markdown(f"<p style='margin-top:10px; font-weight:600; color:#f8fafc;'>{item['caption']}</p>", unsafe_allow_html=True)
                st.markdown(f"<span class='badge-uploader'>👤 {item['agent']}</span>", unsafe_allow_html=True)
                st.caption(f"🕒 {item['timestamp']}")
                st.markdown('</div>', unsafe_allow_html=True)