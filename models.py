from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from pgvector.sqlalchemy import Vector

# ==========================================
# 1. TABEL USER (Induk Data Akun)
# ==========================================
class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    username = Column(String, unique=True, index=True) # NIM atau NPP (Primary Identity)
    password = Column(String)
    full_name = Column(String) # Nama Lengkap disimpan di sini
    role = Column(String)      # 'mahasiswa', 'dosen', 'kaprodi'
    is_active = Column(Boolean, default=True)

# ==========================================
# 2. TABEL MAHASISWA (Data Biometrik)
# ==========================================
class Mahasiswa(Base):
    __tablename__ = "mahasiswa"
    nim = Column(String, primary_key=True, index=True) # NIM sebagai Primary Key Business
    
    # Relasi ke Users (One to One)
    user_id = Column(Integer, ForeignKey("users.user_id")) 
    
    # Vector Wajah (512 dimensi untuk InsightFace)
    embedding_data = Column(Vector(512))

    # Relasi agar bisa memanggil mhs.user.full_name
    user = relationship("Users", backref="data_mahasiswa")

# ==========================================
# 3. TABEL KELAS (Mata Kuliah)
# ==========================================
class Kelas(Base):
    __tablename__ = "kelas"
    kelas_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama_matkul = Column(String, index=True)
    kode_ruang = Column(String)

# ==========================================
# 4. TABEL STUDENT CLASS (Kelas Mahasiswa: A11.4109, dll)
# ==========================================
class StudentClass(Base):
    __tablename__ = "student_class"
    class_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_name = Column(String, unique=True, nullable=False, index=True)  # A11.4109, A11.4110
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    enrollments = relationship("KelasEnrollment", back_populates="student_class")
    jadwal_list = relationship("Jadwal", back_populates="student_class")

# ==========================================
# 5. TABEL KELAS ENROLLMENT (Pendaftaran Mahasiswa ke Kelas)
# ==========================================
class KelasEnrollment(Base):
    """
    Enrollment mahasiswa ke student class (kelas mahasiswa).
    Relasi: Mahasiswa -> StudentClass
    
    Catatan: kelas_id dihapus karena tidak digunakan.
    Sistem menggunakan student_class_id untuk filtering enrollment.
    """
    __tablename__ = "kelas_enrollment"
    enrollment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    nim = Column(String, ForeignKey("mahasiswa.nim"), nullable=False)
    student_class_id = Column(Integer, ForeignKey("student_class.class_id"), nullable=False)
    
    # Metadata
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    mahasiswa = relationship("Mahasiswa", backref="enrollments")
    student_class = relationship("StudentClass", back_populates="enrollments")

# ==========================================
# 6. TABEL JADWAL (Sesi Kuliah)
# ==========================================
class Jadwal(Base):
    __tablename__ = "jadwal"
    jadwal_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    dosen_username = Column(String, ForeignKey("users.username"))
    kelas_id = Column(Integer, ForeignKey("kelas.kelas_id"))
    student_class_id = Column(Integer, ForeignKey("student_class.class_id"), nullable=False)  # NEW: Kelas Mahasiswa
    
    hari = Column(String)       # Senin, Selasa, dst
    jam_mulai = Column(String)  # Format HH:MM
    jam_selesai = Column(String)# Format HH:MM

    # Relationships
    dosen = relationship("Users", backref="jadwal_ajar")
    kelas = relationship("Kelas", backref="jadwal_kuliah")
    student_class = relationship("StudentClass", back_populates="jadwal_list")

# ==========================================
# 7. TABEL VIDEO TASKS (Riwayat Upload)
# ==========================================
class VideoTask(Base):
    __tablename__ = "video_tasks"
    task_db_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(String, unique=True, index=True) # UUID Task
    
    dosen_username = Column(String, ForeignKey("users.username"))
    
    # [NEW] Mengikat video ke jadwal spesifik
    # Agar riwayat video jelas ini untuk mata kuliah apa
    jadwal_id = Column(Integer, ForeignKey("jadwal.jadwal_id"), nullable=True)
    
    filename = Column(String)
    status = Column(String, default="processing") # processing, completed, failed
    is_closed = Column(Boolean, default=False)  # Menandai apakah kelas sudah ditutup dosen
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relasi untuk mengambil info matkul dari task
    jadwal = relationship("Jadwal")

# ==========================================
# 8. TABEL LOG ABSENSI (Transaksi)
# ==========================================
class LogAbsensi(Base):
    __tablename__ = "log_absensi"
    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Relasi Asal Data
    task_id = Column(String, ForeignKey("video_tasks.task_id"), nullable=True) 
    nim = Column(String, ForeignKey("mahasiswa.nim"))
    
    # [NEW] KUNCI SINKRONISASI STRICT
    # Mengikat absensi ke jadwal spesifik.
    # Mahasiswa bisa Hadir di Matkul A (Jadwal ID 1), tapi Alpha di Matkul B (Jadwal ID 2) pada hari yang sama.
    jadwal_id = Column(Integer, ForeignKey("jadwal.jadwal_id"), nullable=True) 
    
    waktu_absen = Column(DateTime(timezone=True), server_default=func.now())
    metode = Column(String) # 'AI_VIDEO' atau 'MANUAL_DOSEN'
    
    # Data Analisis AI
    jumlah_muncul = Column(Integer, nullable=True)
    emosi_dominan = Column(String, nullable=True)
    bukti_foto = Column(String, nullable=True) # Path ke file crop wajah
    
    # Fitur Sengketa/Lapor
    is_disputed = Column(Boolean, default=False)
    keterangan_report = Column(String, nullable=True)
    
    # Relasi
    jadwal = relationship("Jadwal")