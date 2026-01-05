"""
Bulk Face Registration System with User Account Creation
==========================================================
Sistem untuk upload batch foto mahasiswa dalam format ZIP.
Akan otomatis:
1. Create user accounts dengan credentials auto-generated
2. Detect face & generate embeddings
3. Save to database (atomic transaction)

Author: Senior Backend Engineer
Date: 2026-01-03
Version: 2.0 (Enhanced with Auth)
"""

import os
import zipfile
import tempfile
import shutil
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
import cv2
from insightface.app import FaceAnalysis
from pydantic import BaseModel, Field
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================================
# PYDANTIC MODELS
# ==========================================

class BulkRegistrationResult(BaseModel):
    """Model untuk hasil processing satu foto"""
    nim: str
    filename: str
    status: str  # 'success', 'failed'
    error_reason: Optional[str] = None
    faces_detected: int = 0
    user_created: bool = False  # NEW: Track if user account was created
    embedding_saved: bool = False  # NEW: Track if embedding was saved

class BulkRegistrationSummary(BaseModel):
    """Model untuk summary keseluruhan proses"""
    total_processed: int
    success_count: int
    failed_count: int
    users_created: int  # NEW: Total user accounts created
    embeddings_saved: int  # NEW: Total embeddings saved
    results: List[BulkRegistrationResult]
    processing_time_seconds: float

# ==========================================
# PASSWORD GENERATION LOGIC
# ==========================================

def generate_default_password(nim: str) -> str:
    """
    Generate default password from NIM.
    
    Business Rule:
    Password = "mhs" + last 5 digits of NIM
    
    Examples:
        'A11.2025.16442' -> 'mhs16442'
        '123456789' -> 'mhs56789'
        'A11.4109' -> 'mhs04109' (pad with 0 if less than 5 digits)
    
    Args:
        nim: Student ID (NIM)
        
    Returns:
        Plain text password (will be hashed before saving)
    """
    # Extract only digits from NIM
    digits = re.sub(r'\D', '', nim)  # Remove non-digit characters
    
    # Get last 5 digits (or pad with leading zeros if less than 5)
    if len(digits) >= 5:
        last_five = digits[-5:]
    else:
        # Pad with zeros on the left to make it 5 digits
        last_five = digits.zfill(5) if digits else nim[-5:].replace('.', '0')
    
    password = f"mhs{last_five}"
    return password


def hash_password(plain_password: str) -> str:
    """
    Hash password using bcrypt.
    
    Args:
        plain_password: Plain text password
        
    Returns:
        Hashed password suitable for database storage
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

# ==========================================
# FACE PROCESSING CLASS
# ==========================================

class BulkFaceProcessor:
    """
    Core class untuk processing batch face registration with user account creation.
    
    Enhanced Responsibilities:
    1. Extract ZIP file
    2. Detect faces in images
    3. Generate face embeddings
    4. Validate face count (must be exactly 1)
    5. Generate user credentials (username + hashed password)
    6. Create User account in database (ATOMIC)
    7. Create Mahasiswa record with embedding (ATOMIC)
    8. Cleanup temporary files
    
    IMPORTANT: User account creation and face embedding are ATOMIC.
    If AI validation fails, NO user account is created.
    """
    
    def __init__(self, db_session):
        """
        Initialize face processor with database session.
        
        Args:
            db_session: AsyncSession untuk database operations
        """
        self.db_session = db_session
        
        # Initialize InsightFace model (buffalo_l)
        print("🔄 Loading InsightFace model (buffalo_l)...")
        self.face_app = FaceAnalysis(
            name='buffalo_l',
            providers=['CPUExecutionProvider']  # Use GPU if available
        )
        self.face_app.prepare(ctx_id=0, det_size=(640, 640))
        print("✅ InsightFace model loaded successfully")
        
        # Supported image formats
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    def extract_nim_from_filename(self, filename: str) -> str:
        """
        Extract NIM from filename.
        
        Examples:
            'A11.2025.16442.jpg' -> 'A11.2025.16442'
            '123456789.png' -> '123456789'
            'student_A11.2025.16442_photo.jpg' -> 'A11.2025.16442'
        
        Args:
            filename: nama file foto
            
        Returns:
            NIM (Student ID)
        """
        # Remove extension
        name_without_ext = Path(filename).stem
        
        # Strategy 1: Check if contains pattern like A11.YYYY.XXXXX
        if 'A11.' in name_without_ext.upper():
            parts = name_without_ext.split('_')
            for part in parts:
                if 'A11.' in part.upper():
                    return part.upper()
        
        # Strategy 2: Just use the filename without extension
        return name_without_ext
    
    def detect_and_extract_face(self, image_path: str) -> Dict:
        """
        Detect face in image and extract embedding.
        
        Args:
            image_path: path ke file gambar
            
        Returns:
            Dict dengan keys: 
                - faces_detected: jumlah wajah terdeteksi
                - embedding: numpy array embedding (jika 1 wajah)
                - error: pesan error (jika ada)
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return {
                    'faces_detected': 0,
                    'embedding': None,
                    'error': 'Failed to read image file'
                }
            
            # Convert BGR to RGB (InsightFace uses RGB)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            faces = self.face_app.get(img_rgb)
            num_faces = len(faces)
            
            # Validation
            if num_faces == 0:
                return {
                    'faces_detected': 0,
                    'embedding': None,
                    'error': 'No face detected in image'
                }
            
            elif num_faces > 1:
                return {
                    'faces_detected': num_faces,
                    'embedding': None,
                    'error': f'Multiple faces detected ({num_faces} faces). Please use photo with single face only'
                }
            
            else:  # Exactly 1 face - SUCCESS
                face = faces[0]
                embedding = face.normed_embedding  # 512-dimensional vector
                
                return {
                    'faces_detected': 1,
                    'embedding': embedding,
                    'error': None
                }
        
        except Exception as e:
            return {
                'faces_detected': 0,
                'embedding': None,
                'error': f'Processing error: {str(e)}'
            }
    
    async def save_to_database(self, nim: str, embedding: np.ndarray) -> Tuple[bool, str]:
        """
        Save or update mahasiswa record with face embedding AND create user account.
        
        **ATOMIC TRANSACTION:**
        Both User and Mahasiswa records must be created/updated together.
        If one fails, the entire transaction is rolled back.
        
        **Password Generation:**
        - Default password = "mhs" + last 5 digits of NIM
        - Example: NIM 'A11.2025.16442' → Password 'mhs16442'
        - Password is hashed with bcrypt before saving
        
        Args:
            nim: Student ID
            embedding: Face embedding vector (512-dim)
            
        Returns:
            Tuple[bool, str]: (success, operation_type)
            - success: True if saved successfully
            - operation_type: 'created', 'updated', or 'failed'
        """
        try:
            from models import Mahasiswa, Users
            from sqlalchemy import select
            
            # Convert numpy array to list for pgvector
            embedding_list = embedding.tolist()
            
            # Generate password
            plain_password = generate_default_password(nim)
            hashed_password = hash_password(plain_password)
            
            # Check if mahasiswa already exists
            stmt = select(Mahasiswa).where(Mahasiswa.nim == nim)
            result = await self.db_session.execute(stmt)
            mahasiswa = result.scalar_one_or_none()
            
            if mahasiswa:
                # UPDATE EXISTING RECORD
                # Update embedding only (user already exists)
                mahasiswa.embedding_data = embedding_list
                await self.db_session.commit()
                print(f"  ✏️  Updated embedding for NIM: {nim}")
                return True, 'updated'
            
            else:
                # CREATE NEW RECORD (ATOMIC TRANSACTION)
                # Step 1: Check if user exists
                stmt_user = select(Users).where(Users.username == nim)
                result_user = await self.db_session.execute(stmt_user)
                user = result_user.scalar_one_or_none()
                
                if not user:
                    # Step 2: Create user account
                    user = Users(
                        username=nim,
                        password=hashed_password,  # Hashed password
                        full_name=f"Mahasiswa {nim}",
                        role="mahasiswa",
                        is_active=True
                    )
                    self.db_session.add(user)
                    await self.db_session.flush()  # Get user_id without committing
                    print(f"  👤 Created user account: {nim} (password: mhs*****)")
                
                # Step 3: Create mahasiswa record with embedding
                new_mahasiswa = Mahasiswa(
                    nim=nim,
                    user_id=user.user_id,
                    embedding_data=embedding_list
                )
                self.db_session.add(new_mahasiswa)
                
                # Step 4: COMMIT TRANSACTION (Atomic - both or none)
                await self.db_session.commit()
                print(f"  ➕ Created mahasiswa record with face embedding")
                print(f"  🔐 Credentials: {nim} / {plain_password}")
                
                return True, 'created'
            
        except Exception as e:
            # ROLLBACK on any error
            await self.db_session.rollback()
            print(f"  ❌ Database error for NIM {nim}: {str(e)}")
            return False, 'failed'
    
    async def process_zip_file(
        self, 
        zip_path: str,
        temp_dir: Optional[str] = None
    ) -> BulkRegistrationSummary:
        """
        Main processing function untuk ZIP file with ATOMIC user creation.
        
        **Enhanced Workflow:**
        1. Extract ZIP ke temporary directory
        2. Iterate semua image files
        3. Extract NIM dari filename
        4. Detect face dan generate embedding
        5. **VALIDATE: Must be exactly 1 face**
        6. **IF VALID: Create user account + Save embedding (ATOMIC)**
        7. **IF INVALID: Skip user creation entirely**
        8. Cleanup temporary files
        9. Return comprehensive summary
        
        **Critical Rule:**
        User account is ONLY created if face validation passes.
        This prevents orphan user accounts without face data.
        
        Args:
            zip_path: Path ke ZIP file
            temp_dir: Optional custom temp directory
            
        Returns:
            BulkRegistrationSummary dengan detail hasil
        """
        import time
        start_time = time.time()
        
        results: List[BulkRegistrationResult] = []
        success_count = 0
        users_created = 0
        embeddings_saved = 0
        
        # Create temporary directory
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp(prefix='bulk_face_reg_')
        
        print(f"📦 Extracting ZIP file to: {temp_dir}")
        
        try:
            # Extract ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            print(f"✅ ZIP extracted successfully")
            
            # Get all image files
            image_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if Path(file).suffix.lower() in self.supported_formats:
                        image_files.append(os.path.join(root, file))
            
            total_files = len(image_files)
            print(f"📸 Found {total_files} image files")
            print("=" * 60)
            
            # Process each image
            for idx, image_path in enumerate(image_files, 1):
                filename = os.path.basename(image_path)
                print(f"[{idx}/{total_files}] Processing: {filename}")
                
                # Extract NIM from filename
                nim = self.extract_nim_from_filename(filename)
                print(f"  📝 Extracted NIM: {nim}")
                
                # Generate password (for display only - will be hashed before saving)
                plain_password = generate_default_password(nim)
                print(f"  🔑 Generated password: {plain_password}")
                
                # Detect face and extract embedding
                detection_result = self.detect_and_extract_face(image_path)
                faces_detected = detection_result['faces_detected']
                embedding = detection_result['embedding']
                error = detection_result['error']
                
                # Validation and database save
                if error:
                    # FAILED - AI validation failed, DO NOT create user
                    results.append(BulkRegistrationResult(
                        nim=nim,
                        filename=filename,
                        status='failed',
                        error_reason=error,
                        faces_detected=faces_detected,
                        user_created=False,
                        embedding_saved=False
                    ))
                    print(f"  ❌ FAILED: {error}")
                    print(f"  ⚠️  User account NOT created (AI validation failed)")
                
                else:
                    # SUCCESS - AI validation passed, CREATE user + Save embedding (ATOMIC)
                    db_success, operation_type = await self.save_to_database(nim, embedding)
                    
                    if db_success:
                        success_count += 1
                        user_was_created = operation_type == 'created'
                        
                        if user_was_created:
                            users_created += 1
                        
                        embeddings_saved += 1
                        
                        results.append(BulkRegistrationResult(
                            nim=nim,
                            filename=filename,
                            status='success',
                            error_reason=None,
                            faces_detected=1,
                            user_created=user_was_created,
                            embedding_saved=True
                        ))
                        print(f"  ✅ SUCCESS: {'Created' if user_was_created else 'Updated'}")
                    else:
                        results.append(BulkRegistrationResult(
                            nim=nim,
                            filename=filename,
                            status='failed',
                            error_reason='Database transaction failed (rolled back)',
                            faces_detected=1,
                            user_created=False,
                            embedding_saved=False
                        ))
                        print(f"  ❌ FAILED: Database error (transaction rolled back)")
                
                print()  # Empty line for readability
        
        finally:
            # Cleanup: Delete temporary directory
            try:
                shutil.rmtree(temp_dir)
                print(f"🧹 Cleaned up temporary directory")
            except Exception as e:
                print(f"⚠️  Warning: Failed to cleanup temp dir: {e}")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create summary
        summary = BulkRegistrationSummary(
            total_processed=len(results),
            success_count=success_count,
            failed_count=len(results) - success_count,
            users_created=users_created,
            embeddings_saved=embeddings_saved,
            results=results,
            processing_time_seconds=round(processing_time, 2)
        )
        
        print("=" * 60)
        print("📊 PROCESSING SUMMARY")
        print("=" * 60)
        print(f"✅ Success: {summary.success_count}/{summary.total_processed}")
        print(f"❌ Failed: {summary.failed_count}/{summary.total_processed}")
        print(f"👤 Users Created: {summary.users_created}")
        print(f"🎭 Embeddings Saved: {summary.embeddings_saved}")
        print(f"⏱️  Time: {summary.processing_time_seconds}s")
        print("=" * 60)
        
        return summary


# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def validate_zip_file(file_size: int, max_size_mb: int = 500) -> tuple[bool, str]:
    """
    Validate uploaded ZIP file.
    
    Args:
        file_size: Size in bytes
        max_size_mb: Maximum allowed size in MB
        
    Returns:
        (is_valid, error_message)
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        return False, f"File too large. Maximum size is {max_size_mb}MB"
    
    if file_size == 0:
        return False, "Empty file"
    
    return True, ""


def is_valid_zip_file(file_path: str) -> tuple[bool, str]:
    """
    Check if file is valid ZIP.
    
    Args:
        file_path: Path to file
        
    Returns:
        (is_valid, error_message)
    """
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Test ZIP integrity
            bad_file = zip_ref.testzip()
            if bad_file:
                return False, f"Corrupted file in ZIP: {bad_file}"
        return True, ""
    except zipfile.BadZipFile:
        return False, "Not a valid ZIP file"
    except Exception as e:
        return False, f"ZIP validation error: {str(e)}"
