// Quick script untuk menambah mahasiswa dummy
// Jalankan di Browser Console (F12) saat di halaman Kaprodi Dashboard

async function addDummyStudent(nim, name) {
    try {
        const response = await axios.post('/admin/mahasiswa', {
            nim: nim,
            full_name: name,
            password: 'password123'
        });
        console.log('✅ Berhasil:', response.data);
        return response.data;
    } catch (error) {
        console.error('❌ Gagal:', error.response?.data || error.message);
        return null;
    }
}

// Tambah beberapa mahasiswa sekaligus
async function addMultipleStudents() {
    const students = [
        { nim: 'A11.2025.16500', name: 'Haruna Kojima' },
        { nim: 'A11.2025.16501', name: 'Yuki Kashiwagi' },
        { nim: 'A11.2025.16502', name: 'Mayu Watanabe' },
        { nim: 'A11.2025.16503', name: 'Jurina Matsui' },
        { nim: 'A11.2025.16504', name: 'Sakura Miyawaki' }
    ];
    
    console.log('📝 Menambahkan', students.length, 'mahasiswa...');
    
    for (const student of students) {
        await addDummyStudent(student.nim, student.name);
        await new Promise(resolve => setTimeout(resolve, 500)); // Delay 500ms
    }
    
    console.log('✅ Selesai! Refresh halaman untuk melihat mahasiswa baru.');
    
    // Auto refresh users list
    setTimeout(() => {
        Swal.fire({
            title: 'Berhasil!',
            text: students.length + ' mahasiswa baru telah ditambahkan',
            icon: 'success',
            confirmButtonText: 'Refresh'
        }).then(() => {
            location.reload();
        });
    }, 1000);
}

// Jalankan fungsi ini:
console.log('🎯 Script loaded! Jalankan perintah:');
console.log('   addDummyStudent("A11.2025.16500", "Haruna Kojima")');
console.log('   addMultipleStudents()');
