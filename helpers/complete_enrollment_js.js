// ============================================================================
// STUDENT CLASS MANAGEMENT FUNCTIONS (New)
// ============================================================================

// Tab switching for enrollment view
function switchEnrollmentTab(tab) {
    const tabStudentClass = document.getElementById('tabStudentClass');
    const tabEnrollment = document.getElementById('tabEnrollment');
    const contentStudentClass = document.getElementById('contentStudentClass');
    const contentEnrollment = document.getElementById('contentEnrollment');
    
    if (tab === 'studentclass') {
        tabStudentClass.classList.remove('border-transparent', 'text-slate-400');
        tabStudentClass.classList.add('border-indigo-600', 'text-indigo-600');
        tabEnrollment.classList.remove('border-indigo-600', 'text-indigo-600');
        tabEnrollment.classList.add('border-transparent', 'text-slate-400');
        contentStudentClass.classList.remove('hidden');
        contentEnrollment.classList.add('hidden');
        loadStudentClasses();
    } else {
        tabEnrollment.classList.remove('border-transparent', 'text-slate-400');
        tabEnrollment.classList.add('border-indigo-600', 'text-indigo-600');
        tabStudentClass.classList.remove('border-indigo-600', 'text-indigo-600');
        tabStudentClass.classList.add('border-transparent', 'text-slate-400');
        contentEnrollment.classList.remove('hidden');
        contentStudentClass.classList.add('hidden');
        loadEnrollments();
    }
}

// Load all student classes
async function loadStudentClasses() {
    try {
        const res = await axios.get('/admin/student-class');
        const tbody = document.getElementById('tableStudentClass');
        
        if (res.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center py-8 text-slate-400">Belum ada kelas mahasiswa</td></tr>';
            return;
        }
        
        tbody.innerHTML = res.data.map(sc => `
            <tr class="hover:bg-slate-50 transition">
                <td class="px-6 py-4 font-semibold text-slate-800">${sc.class_name}</td>
                <td class="px-6 py-4 text-slate-600">-</td>
                <td class="px-6 py-4 text-slate-600 text-sm">${new Date(sc.created_at).toLocaleDateString('id-ID')}</td>
                <td class="px-6 py-4 text-center">
                    <button onclick="deleteStudentClass(${sc.class_id}, '${sc.class_name}')"
                        class="text-red-600 hover:text-red-800 font-semibold text-sm">
                        <i class="fa-solid fa-trash"></i> Hapus
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        console.error(e);
        Swal.fire('Error', 'Gagal memuat data kelas', 'error');
    }
}

// Open modal add student class
function openModalAddStudentClass() {
    document.getElementById('studentClassName').value = '';
    document.getElementById('modalAddStudentClass').classList.remove('hidden');
}

// Close modal add student class
function closeModalAddStudentClass() {
    document.getElementById('modalAddStudentClass').classList.add('hidden');
}

// Create student class
async function createStudentClass(e) {
    e.preventDefault();
    const className = document.getElementById('studentClassName').value;
    
    try {
        const formData = new FormData();
        formData.append('class_name', className);
        
        const res = await axios.post('/admin/student-class', formData);
        Swal.fire({ icon: 'success', title: 'Berhasil!', text: res.data.msg, timer: 1500, showConfirmButton: false });
        closeModalAddStudentClass();
        loadStudentClasses();
    } catch (e) {
        const errorMsg = e.response?.data?.detail || 'Gagal membuat kelas';
        Swal.fire('Error', errorMsg, 'error');
    }
}

// Delete student class
async function deleteStudentClass(classId, className) {
    const result = await Swal.fire({
        title: 'Hapus Kelas?',
        text: `Yakin ingin menghapus kelas "${className}"?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Ya, Hapus',
        cancelButtonText: 'Batal',
        confirmButtonColor: '#ef4444'
    });
    
    if (result.isConfirmed) {
        try {
            await axios.delete(`/admin/student-class/${classId}`);
            Swal.fire({ icon: 'success', title: 'Terhapus', timer: 1000, showConfirmButton: false });
            loadStudentClasses();
        } catch (e) {
            const errorMsg = e.response?.data?.detail || 'Gagal menghapus kelas';
            Swal.fire('Error', errorMsg, 'error');
        }
    }
}

// ============================================================================
// UPDATED ENROLLMENT FUNCTIONS
// ============================================================================

// Open modal add enrollment (UPDATED)
function openModalAddEnrollment() {
    // Populate mahasiswa dropdown
    axios.get('/users/').then(res => {
        const sel = document.getElementById('enrollmentNim');
        sel.innerHTML = '<option value="">Pilih Mahasiswa</option>';
        res.data.forEach(m => {
            sel.innerHTML += `<option value="${m.nim}">${m.nama} (${m.nim})</option>`;
        });
    });
    
    // Populate student class dropdown
    axios.get('/admin/student-class').then(res => {
        const sel = document.getElementById('enrollmentStudentClass');
        sel.innerHTML = '<option value="">Pilih Kelas Mahasiswa</option>';
        res.data.forEach(sc => {
            sel.innerHTML += `<option value="${sc.class_id}">${sc.class_name}</option>`;
        });
    });
    
    document.getElementById('modalAddEnrollment').classList.remove('hidden');
}

// Create enrollment (UPDATED)
async function createEnrollment(e) {
    e.preventDefault();
    const nim = document.getElementById('enrollmentNim').value;
    const studentClassId = document.getElementById('enrollmentStudentClass').value;
    
    try {
        const res = await axios.post('/admin/enrollment', {
            nim: nim,
            student_class_id: parseInt(studentClassId)
        });
        Swal.fire({ icon: 'success', title: 'Berhasil!', text: res.data.msg, timer: 1500, showConfirmButton: false });
        closeModalAddEnrollment();
        loadEnrollments();
    } catch (e) {
        const errorMsg = e.response?.data?.detail || 'Gagal menambahkan enrollment';
        Swal.fire('Error', errorMsg, 'error');
    }
}

// Open bulk enrollment modal (UPDATED)
function openModalBulkEnrollment() {
    // Populate student class dropdown for both manual and Excel
    axios.get('/admin/student-class').then(res => {
        const sel = document.getElementById('bulkEnrollmentStudentClass');
        sel.innerHTML = '<option value="">Pilih Kelas Mahasiswa</option>';
        res.data.forEach(sc => {
            sel.innerHTML += `<option value="${sc.class_id}">${sc.class_name}</option>`;
        });
    });
    
    document.getElementById('bulkEnrollmentNims').value = '';
    document.getElementById('bulkEnrollmentFile').value = '';
    document.getElementById('excelFileLabel').innerText = 'Klik untuk upload file Excel';
    switchBulkTab('manual');
    document.getElementById('modalBulkEnrollment').classList.remove('hidden');
}

// Bulk enroll manual (UPDATED)
async function bulkEnrollManual(e) {
    e.preventDefault();
    const studentClassId = document.getElementById('bulkEnrollmentStudentClass').value;
    const nimsText = document.getElementById('bulkEnrollmentNims').value;
    const nimList = nimsText.split('\n').map(n => n.trim()).filter(n => n);
    
    if (!studentClassId) {
        return Swal.fire('Error', 'Pilih kelas mahasiswa terlebih dahulu', 'warning');
    }
    
    try {
        const res = await axios.post('/admin/enrollment/bulk', {
            student_class_id: parseInt(studentClassId),
            nim_list: nimList
        });
        Swal.fire({ icon: 'success', title: 'Selesai!', html: `<p>${res.data.msg}</p>`, confirmButtonColor: '#14b8a6' });
        closeModalBulkEnrollment();
        loadEnrollments();
    } catch (e) {
        const errorMsg = e.response?.data?.detail || 'Gagal bulk enrollment';
        Swal.fire('Error', errorMsg, 'error');
    }
}

// Bulk enroll Excel (UPDATED)
async function bulkEnrollExcel(e) {
    e.preventDefault();
    const studentClassId = document.getElementById('bulkEnrollmentStudentClass').value;
    const fileInput = document.getElementById('bulkEnrollmentFile');
    const file = fileInput.files[0];
    
    if (!studentClassId) {
        return Swal.fire('Error', 'Pilih kelas mahasiswa terlebih dahulu', 'warning');
    }
    
    if (!file) {
        return Swal.fire('Error', 'Pilih file Excel terlebih dahulu', 'warning');
    }
    
    try {
        const formData = new FormData();
        formData.append('student_class_id', studentClassId);
        formData.append('file', file);
        
        Swal.fire({
            title: 'Memproses...',
            text: 'Membaca file Excel dan mendaftarkan mahasiswa',
            allowOutsideClick: false,
            didOpen: () => { Swal.showLoading(); }
        });
        
        const res = await axios.post('/admin/enrollment/bulk-excel', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        Swal.fire({ 
            icon: 'success', 
            title: 'Selesai!', 
            html: `<p class="text-sm">${res.data.msg}</p><p class="text-xs text-slate-500 mt-2">Berhasil: ${res.data.success} | Gagal: ${res.data.failed}</p>`,
            confirmButtonColor: '#14b8a6'
        });
        
        closeModalBulkEnrollment();
        loadEnrollments();
    } catch (e) {
        const errorMsg = e.response?.data?.detail || 'Gagal upload file Excel';
        Swal.fire('Error', errorMsg, 'error');
    }
}

// Load enrollments (UPDATED)
async function loadEnrollments() {
    try {
        const res = await axios.get('/admin/enrollment');
        const tbody = document.getElementById('tableEnrollments');
        
        // Update stats
        document.getElementById('countEnrollments').innerText = res.data.length;
        
        if (res.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-8 text-slate-400">Belum ada enrollment</td></tr>';
            return;
        }
        
        tbody.innerHTML = res.data.map(enr => `
            <tr class="hover:bg-slate-50 transition">
                <td class="px-6 py-4 font-mono text-sm text-slate-800">${enr.nim}</td>
                <td class="px-6 py-4 text-slate-800">${enr.nama}</td>
                <td class="px-6 py-4 font-semibold text-indigo-600">${enr.class_name}</td>
                <td class="px-6 py-4 text-slate-600 text-sm">${new Date(enr.enrolled_at).toLocaleDateString('id-ID')}</td>
                <td class="px-6 py-4 text-center">
                    <button onclick="deleteEnrollment(${enr.enrollment_id})"
                        class="text-red-600 hover:text-red-800 font-semibold text-sm">
                        <i class="fa-solid fa-trash"></i> Hapus
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        console.error(e);
        Swal.fire('Error', 'Gagal memuat data enrollment', 'error');
    }
}

// Initialize when enrollment view is opened
function initEnrollmentView() {
    switchEnrollmentTab('studentclass');
}
