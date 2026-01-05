import cv2
import time
import requests
import numpy as np
from insightface.app import FaceAnalysis

# ================= KONFIGURASI =================
VIDEO_PATH = "video_siswa.mp4"       # Ganti dengan path video kamu
INTERVAL_DETIK = 5                   # Ambil sampel tiap 5 detik
API_FACE_URL = "https://risetkami-risetkami.hf.space/predict_face"
API_TEXT_URL = "https://risetkami-risetkami.hf.space/predict_text"

# ================= 1. SETUP MODEL DETEKSI =================
print("⏳ Memuat model InsightFace untuk cropping...")
try:
    # Menggunakan model deteksi ringan
    app = FaceAnalysis(name='buffalo_sc', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    print("✅ Model Siap.")
except Exception as e:
    print(f"❌ Error Load Model: {e}")
    exit()

# ================= 2. FUNGSI POST KE API =================
def kirim_wajah_ke_api(waktu_video, face_image):
    """
    Mengirim gambar wajah (numpy array) ke API risetkami
    """
    # 1. Encode gambar crop jadi format JPG (bytes)
    success, img_encoded = cv2.imencode('.jpg', face_image)
    if not success:
        print("   ⚠️ Gagal encode gambar.")
        return

    # 2. Siapkan payload file
    # Format: "file": (nama_file, bytes_data, mime_type)
    files_payload = {
        "file": (f"face_{waktu_video:.1f}.jpg", img_encoded.tobytes(), "image/jpeg")
    }

    print(f"   🚀 [POST] Detik ke-{waktu_video}: Mengirim wajah ke API...")

    try:
        response = requests.post(API_FACE_URL, files=files_payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"      ✅ Response API: {result}")
            # Contoh output nanti: {'emotion': 'happy', 'confidence': 0.98} (tergantung API)
        else:
            print(f"      ❌ API Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"      ❌ Koneksi Gagal: {e}")

# (Opsional) Fungsi Text jika nanti kamu punya hasil Speech-to-Text
def kirim_teks_ke_api(teks):
    payload = {"text": teks}
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(API_TEXT_URL, json=payload, headers=headers)
        print("Text Response:", resp.json())
    except Exception as e:
        print("Text Error:", e)

# ================= 3. MAIN LOOP (VIDEO) =================
cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print(f"❌ Gagal membuka video: {VIDEO_PATH}")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
frame_jump = int(fps * INTERVAL_DETIK) # Hitung jumlah frame yang diloncati
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"📂 Mulai Analisis Video. FPS: {fps}. Interval: {INTERVAL_DETIK} detik.\n")

current_frame_pos = 0

while True:
    # Lompat ke frame tertentu (Seeking)
    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_pos)
    
    ret, frame = cap.read()
    if not ret:
        print("✅ Selesai.")
        break
    
    current_seconds = current_frame_pos / fps
    print(f"▶️ Processing Detik ke-{current_seconds:.1f}...")

    # --- A. DETEKSI & CROP ---
    faces = app.get(frame)
    
    if len(faces) == 0:
        print("   ⚠️ Tidak ada wajah.")
    
    for face in faces:
        bbox = face.bbox.astype(int)
        x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]

        # Validasi koordinat agar tidak error saat crop
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
        
        # Crop Wajah
        face_crop = frame[y1:y2, x1:x2]
        
        # --- B. KIRIM KE API ---
        # Hanya kirim jika hasil crop valid (tidak kosong)
        if face_crop.size > 0:
            kirim_wajah_ke_api(current_seconds, face_crop)
            
            # (Visualisasi Kotak di Layar - Opsional)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Tampilkan preview (Tekan Q untuk stop)
    cv2.imshow("Video Processing", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Update posisi frame selanjutnya
    current_frame_pos += frame_jump
    if current_frame_pos >= total_frames: break

cap.release()
cv2.destroyAllWindows()