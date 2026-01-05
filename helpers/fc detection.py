import os
import sys
import csv 
import cv2
import time
import math
import numpy as np
import onnxruntime as ort
from insightface.app import FaceAnalysis

# --- 1. SETUP GPU (WAJIB) ---
# Memastikan CUDA Path dikenal oleh sistem
try:
    cuda_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin"
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(cuda_path)
    os.environ['PATH'] = cuda_path + ';' + os.environ['PATH']
except Exception as e:
    print(f"Warning: Gagal setup CUDA path: {e}")


# --- 2. KONFIGURASI ---
FOLDER_FOTO = "a114109"              # Folder foto wajah (format nama file = NIM)
FILE_CSV = "database_mahasiswa.csv"  # File database nama
MOVEMENT_THRESHOLD = 30              # Toleransi gerakan (pixel)
RESET_THRESHOLD = 150                # Jarak reset ID jika pindah posisi
SIMILARITY_THRESHOLD = 0.5           # Batas kemiripan
AGE_CORRECTION = 10                  # Koreksi Umur: Kurangi X tahun (misal: 10)

# --- 3. LOAD MODEL AI ---
print("⏳ Sedang memuat model InsightFace (buffalo_sc) ke GPU...")
try:
    app = FaceAnalysis(name='buffalo_sc', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    print("✅ Model AI berhasil dimuat.")
except Exception as e:
    print(f"❌ ERROR: Gagal memuat model InsightFace. Pastikan InsightFace dan ONNX runtime sudah terinstal dengan dukungan CUDA. Detail: {e}")
    sys.exit()

# --- 4. LOAD DATA DATABASE (NIM & NAMA) ---
known_faces = {} # {'NIM': embedding}
database_nama = {} # {'NIM': 'Nama Lengkap'}

# A. Baca CSV Nama
def load_database_nama():
    print(f"📂 Membaca data nama dari '{FILE_CSV}'...")
    if not os.path.exists(FILE_CSV):
        print("⚠️ WARNING: File CSV tidak ditemukan! Jalankan script convert data dulu.")
        return

    try:
        with open(FILE_CSV, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                nim = row['NIM'].strip()
                nama = row['NAMA'].strip()
                database_nama[nim] = nama
                count += 1
            print(f" ✅ Berhasil memuat {count} nama mahasiswa.")
    except Exception as e:
        print(f" ❌ Gagal baca CSV: {e}")

# B. Baca Foto Wajah (Embedding)
def load_data_wajah(folder_path):
    print(f"📂 Membaca foto wajah dari folder '{folder_path}'...")
    if not os.path.exists(folder_path):
        print(f"❌ ERROR: Folder '{folder_path}' tidak ditemukan!")
        return

    count = 0
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            nim = os.path.splitext(filename)[0]
            path = os.path.join(folder_path, filename)
            
            img = cv2.imread(path)
            if img is None: continue
            
            faces = app.get(img)
            if len(faces) > 0:
                embedding = faces[0].embedding
                norm_embedding = embedding / np.linalg.norm(embedding)
                known_faces[nim] = norm_embedding
                count += 1
            else:
                print(f" ⚠️ Skip: Wajah tidak terdeteksi di {filename}")
    
    print(f"Total Wajah Terlatih: {count}")

# Jalankan Loading Data
load_database_nama()
load_data_wajah(FOLDER_FOTO)

# --- 5. FUNGSI PENGENALAN ---
def cek_identitas(target_embedding):
    max_score = 0
    identity = "Unknown"
    
    target_norm = target_embedding / np.linalg.norm(target_embedding)
    
    for nim, db_emb in known_faces.items():
        score = np.dot(target_norm, db_emb)
        if score > max_score:
            max_score = score
            identity = nim
            
    if max_score < SIMILARITY_THRESHOLD:
        return "Unknown", max_score
    return identity, max_score

# --- 6. MAIN LOOP ---
print("✅ Sistem Siap! Kamera aktif... (Tekan 'q' keluar)")
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

trackers = {} # { ID: {'start_time': t, 'last_body': (x,y), 'nim': str, 'status': str} }
next_id = 0

while True:
    ret, frame = cap.read()
    if not ret: break
    
    start_loop = time.time()
    faces = app.get(frame)
    current_frame_data = {}
    
    for face in faces:
        bbox = face.bbox.astype(int)
        
        # # --- Ekstraksi & Koreksi Umur & Gender ---
        # raw_age = int(face.age) 
        # # Koreksi Umur: Kurangi AGE_CORRECTION tahun, tapi pastikan minimal 1 tahun
        # age = max(1, raw_age - AGE_CORRECTION) 
        
        gender_code = face.gender # 0=Female, 1=Male
        gender = "Pria" if gender_code == 1 else "Wanita"
        
        # Titik Badan (Body Center, untuk Tracking)
        face_cx = (bbox[0] + bbox[2]) // 2
        face_cy = (bbox[1] + bbox[3]) // 2
        face_h = bbox[3] - bbox[1]
        body_cx = face_cx
        body_cy = int(bbox[3] + (face_h * 0.8)) 
        current_body = (body_cx, body_cy)
        
        # --- TRACKING ---
        matched_id = None
        min_dist = 99999
        
        for trk_id, data in trackers.items():
            prev_body = data['last_body']
            dist = math.hypot(body_cx - prev_body[0], body_cy - prev_body[1])
            if dist < min_dist:
                min_dist = dist
                matched_id = trk_id
        
        # --- RECOGNITION ---
        detected_nim, score = cek_identitas(face.embedding)
        
        # --- LOGIKA STATUS & ASSIGN ID ---
        if matched_id is not None and min_dist < RESET_THRESHOLD:
            prev_data = trackers[matched_id]
            
            if min_dist < MOVEMENT_THRESHOLD:
                start_time = prev_data['start_time']
                status = "DIAM"
            else:
                start_time = time.time()
                status = "GERAK"
            
            final_nim = detected_nim if detected_nim != "Unknown" else prev_data['nim']
            
            current_frame_data[matched_id] = {
                'start_time': start_time,
                'last_body': current_body,
                'nim': final_nim,
                'status': status
            }
            duration = time.time() - start_time
            assigned_id = matched_id
        else:
            current_frame_data[next_id] = {
                'start_time': time.time(),
                'last_body': current_body,
                'nim': detected_nim,
                'status': "BARU"
            }
            duration = 0
            status = "BARU"
            assigned_id = next_id
            next_id += 1

        # --- VISUALISASI ---
        
        nim_final = current_frame_data[assigned_id]['nim']
        
        nama_lengkap = database_nama.get(nim_final, nim_final) 
        
        color = (0, 255, 0) if nim_final != "Unknown" else (150, 150, 150)
        
        # Kotak & Titik
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        cv2.circle(frame, current_body, 5, (0, 0, 255), -1)
        
        # Tampilkan Nama (Header)
        cv2.putText(frame, nama_lengkap, (bbox[0], bbox[1]-30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Tampilkan NIM (Sub-header)
        if nim_final != "Unknown" and nim_final != nama_lengkap:
             cv2.putText(frame, f"({nim_final})", (bbox[0], bbox[1]-8), 
                             cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)


        # Status Waktu (Baris Kedua Info Bawah)
        if status == "DIAM":
            time_color = (0, 0, 255) if duration > 10 else (0, 255, 255)
            status_text = f"DIAM: {duration:.1f}s"
        else:
            time_color = (0, 200, 255)
            status_text = "AKTIF"
        
        cv2.putText(frame, status_text, (bbox[0], bbox[3]+45), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, time_color, 2)

    # Update tracker list untuk frame berikutnya
    trackers = current_frame_data
    
    # Hitung dan Tampilkan FPS
    fps = 1.0 / (time.time() - start_loop)
    cv2.putText(frame, f"GPU FPS: {fps:.1f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Presensi Pintar - Nama Asli', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()