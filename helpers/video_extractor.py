import cv2
import requests
import numpy as np
import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from insightface.app import FaceAnalysis
from collections import defaultdict

# ================= KONFIGURASI =================
API_URL = "https://risetkami-risetkami.hf.space/predict_face"
CONFIDENCE_THRESHOLD = 0.25
INTERVAL_DETIK = 5

# Folder Penyimpanan
TEMP_FOLDER = "temp_videos"       # Untuk video mentah upload user
CROPPED_FOLDER = "hasil_crop"     # Untuk menyimpan hasil crop wajah

# Buat folder jika belum ada
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(CROPPED_FOLDER, exist_ok=True)

# ================= GLOBAL STATE =================
tasks_db = {}

# ================= SETUP MODEL AI =================
print("⏳ Memuat model InsightFace...")
try:
    face_app = FaceAnalysis(name='buffalo_sc', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    face_app.prepare(ctx_id=0, det_size=(640, 640))
    print("✅ Model Siap.")
except Exception as e:
    print(f"❌ Gagal memuat model: {e}")
    face_app = None

app = FastAPI(title="Video Emotion Analysis API")

# ================= FUNGSI PROSES BACKGROUND =================
def process_video_background(task_id: str, file_path: str):
    """Proses video: Crop wajah -> Simpan ke Folder -> Kirim ke API"""
    
    print(f"🚀 [Task {task_id}] Mulai memproses video...")
    tasks_db[task_id]["status"] = "processing"

    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            raise Exception("Gagal membuka file video")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_jump = int(fps * INTERVAL_DETIK)
        
        # Variabel Statistik
        total_probabilitas = defaultdict(float)
        count_prediksi = defaultdict(int)
        jumlah_sampel_wajah = 0
        list_file_tersimpan = [] # Untuk tracking file yang disimpan
        
        current_frame_pos = 0
        
        while True:
            # Update Progress (0-99%)
            progress = min(int((current_frame_pos / total_frames) * 100), 99)
            tasks_db[task_id]["progress"] = progress
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_pos)
            ret, frame = cap.read()
            if not ret: break

            detik_ke = current_frame_pos / fps

            # 1. Deteksi Wajah
            faces = face_app.get(frame)
            
            # Pakai enumerate agar dapat index jika ada 2 wajah dalam 1 frame
            for idx, face in enumerate(faces):
                bbox = face.bbox.astype(int)
                x1, y1 = max(0, bbox[0]), max(0, bbox[1])
                x2, y2 = min(frame.shape[1], bbox[2]), min(frame.shape[0], bbox[3])
                face_crop = frame[y1:y2, x1:x2]

                if face_crop.size == 0: continue

                # ==========================================
                # A. SIMPAN GAMBAR KE FOLDER LOKAL (BARU)
                # ==========================================
                # Format: {task_id}_sec_{detik}_face_{index}.jpg
                nama_file = f"{task_id}_sec_{int(detik_ke)}_face_{idx}.jpg"
                path_simpan = os.path.join(CROPPED_FOLDER, nama_file)
                
                cv2.imwrite(path_simpan, face_crop)
                list_file_tersimpan.append(nama_file)
                # ==========================================

                # B. KIRIM KE API EKSTERNAL
                success, img_encoded = cv2.imencode('.jpg', face_crop)
                if success:
                    files = {"file": (nama_file, img_encoded.tobytes(), "image/jpeg")}
                    try:
                        response = requests.post(API_URL, files=files, timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success"):
                                jumlah_sampel_wajah += 1
                                
                                pred = data['predicted']
                                conf = data['confidence']
                                probs = data['probabilities']

                                # Threshold Logic
                                final_label = "normal" if conf < CONFIDENCE_THRESHOLD else pred
                                count_prediksi[final_label] += 1

                                for k, v in probs.items():
                                    total_probabilitas[k] += v
                                    
                    except Exception as err:
                        print(f"⚠️ Error request API: {err}")

            # Lompat Frame
            current_frame_pos += frame_jump
            if current_frame_pos >= total_frames: break

        cap.release()
        
        # 4. Hitung Hasil Akhir
        final_result = {
            "total_sampel": jumlah_sampel_wajah,
            "total_file_disimpan": len(list_file_tersimpan),
            "folder_penyimpanan": CROPPED_FOLDER,
            "frekuensi_emosi": {},
            "rata_rata_level": {}
        }

        if jumlah_sampel_wajah > 0:
            for emosi, jumlah in count_prediksi.items():
                final_result["frekuensi_emosi"][emosi] = {
                    "count": jumlah,
                    "percentage": round((jumlah / jumlah_sampel_wajah) * 100, 2)
                }
            
            for emosi, total in total_probabilitas.items():
                final_result["rata_rata_level"][emosi] = round(total / jumlah_sampel_wajah, 4)

        # Update DB selesai
        tasks_db[task_id]["status"] = "completed"
        tasks_db[task_id]["progress"] = 100
        tasks_db[task_id]["result"] = final_result
        
        # Hapus file video mentah (untuk hemat storage)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        print(f"✅ [Task {task_id}] Selesai. {len(list_file_tersimpan)} gambar tersimpan.")

    except Exception as e:
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"❌ [Task {task_id}] Error: {e}")

# ================= ENDPOINTS =================

@app.post("/analyze_video/")
async def analyze_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not face_app:
        raise HTTPException(status_code=500, detail="Model AI belum siap.")
    
    task_id = str(uuid.uuid4())
    
    # Simpan Video Upload
    file_path = os.path.join(TEMP_FOLDER, f"{task_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    tasks_db[task_id] = {
        "status": "queued",
        "progress": 0,
        "result": None,
        "error": None
    }
    
    background_tasks.add_task(process_video_background, task_id, file_path)
    
    return {
        "message": "Processing started",
        "task_id": task_id,
        "check_status_url": f"/status/{task_id}"
    }

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task ID tidak ditemukan")
    return tasks_db[task_id]