# Instruksi AI untuk writenovelAI

Dokumen ini adalah pintu masuk operasional. Baca sebelum mengerjakan novel di repository ini. Jika instruksi di sini bertentangan dengan dokumen metodologi, ikuti prinsip yang lebih ketat dan laporkan konflik; jangan diam-diam memilih aturan yang mengubah cerita.

## Peran repository

Repository ini memiliki dua fungsi:
1. **Knowledge base:** standar, metode, template, dan instruksi kerja AI.
2. **Workspace penulisan:** tempat menyimpan seluruh dokumen dan naskah setiap novel agar keputusan serta progres dapat dilacak.

Jangan mencampur naskah satu novel dengan novel lain. Setiap novel memiliki folder proyek sendiri di `stories/<slug-judul>/`.

## Titik mulai: pengguna hanya memberi premis

Anggap premis sebagai input awal yang cukup untuk memulai. Jangan meminta pengguna menyiapkan outline, jumlah bab, biodata tokoh, atau blueprint terlebih dahulu.

Dari premis, kerjakan secara bertahap:
1. Tafsirkan daya tarik inti premis dan hal yang belum ditentukan.
2. Kembangkan konsep cerita, genre/subgenre yang cocok, pembaca sasaran, pengalaman membaca, konflik, taruhan, dan batas realitas.
3. Bangun karakter dan dunia seperlunya, bukan biodata panjang yang tidak berfungsi.
4. Rancang alur lengkap dari awal sampai akhir dan tentukan jumlah bab berdasarkan kebutuhan cerita.
5. Buat blueprint bab dan audit rancangan keseluruhan.
6. Tulis hanya setelah rancangan yang diperlukan siap.
7. Tulis satu bab per giliran kerja, lalu lakukan State Update dan audit.

Jangan menganggap setiap keputusan harus ditanyakan kepada pengguna. Ambil keputusan kreatif yang wajar secara mandiri. Namun, tandai keputusan besar yang belum memiliki dasar atau yang akan mengubah identitas, mekanisme utama, hubungan inti, penyebab konflik, atau akhir cerita.

## Kategori status informasi

Gunakan empat label ini secara konsisten:
- **KANON:** fakta yang sudah diputuskan atau telah terjadi dalam naskah dan tidak boleh diubah diam-diam.
- **WAJIB:** hasil/peristiwa yang harus ada, tetapi cara penyampaiannya masih terbuka.
- **FLEKSIBEL:** ruang pengembangan yang tidak mengubah fakta, sebab-akibat, atau fungsi cerita.
- **BELUM DIPUTUSKAN:** pertanyaan penting yang belum memiliki jawaban. Jangan mengarang jawaban lalu memperlakukannya sebagai kanon.

Bedakan fakta dari dugaan, interpretasi, dan kemungkinan.

## Mode kerja

Pilih mode sesuai tahap; jangan mencampur semua pekerjaan dalam satu keluaran.

### 1. ARCHITECT
Membangun konsep, karakter, dunia, alur makro, jumlah bab, dan rancangan akhir dari premis. Menghasilkan dokumen perencanaan. Tidak menulis naskah penuh.

### 2. BLUEPRINT
Menyusun blueprint bab berdasarkan rancangan aktif. Menjaga kronologi dan urutan penyajian sebagai dua hal berbeda. Memeriksa pengetahuan tokoh dan pembaca. Tidak menambah fakta struktural tanpa mencatat keputusan.

### 3. WRITER
Menulis satu bab berdasarkan blueprint dan paket konteks bab. Prosa harus terasa sebagai cerita, bukan parafrasa blueprint. Tidak mengubah kanon, urutan peristiwa wajib, atau pengungkapan utama secara diam-diam.

### 4. AUDITOR
Memeriksa rancangan, naskah, atau kontinuitas. Setiap temuan harus memiliki lokasi dan bukti. Pisahkan kesalahan pasti, risiko, dan preferensi subjektif. Jangan mengedit ketika hanya diminta audit.

### 5. REPAIRER
Memperbaiki temuan audit dengan perubahan terkecil yang cukup. Pertahankan bagian yang sudah benar. Telusuri dampak terhadap dokumen/bab lain dan perbarui hanya yang terdampak.

### 6. LIBRARIAN
Menjaga struktur folder, indeks, status dokumen, decision log, dan tautan antarfile. Tidak mengubah isi cerita tanpa alasan.

## Protokol sebelum menulis bab

Sebelum menulis, baca:
1. `AI_INSTRUCTIONS.md` dan dokumen metode yang relevan.
2. `stories/<slug>/README.md` untuk status dan indeks proyek.
3. Rancangan makro/outline yang berstatus aktif.
4. Blueprint bab yang akan ditulis.
5. State Update bab sebelumnya.
6. Catatan kontinuitas yang relevan: timeline, character knowledge, story state, character behavior.
7. Keputusan kanon dan pertanyaan terbuka yang berpengaruh pada bab tersebut.

Jangan menganggap ringkasan percakapan sebagai sumber kanon jika dokumen proyek menyatakan hal berbeda. Jika ada konflik, hentikan bagian yang bergantung pada konflik itu, tunjukkan bukti, lalu usulkan penyelesaian.

## Protokol penulisan

- Satu bab per file dan satu bab per siklus kerja.
- Tulis prosa lengkap, bukan ringkasan atau kerangka.
- Gunakan paragraf normal.
- Jangan memecah setiap kalimat menjadi baris sendiri.
- Jangan memaksakan kalimat puitis, metafora, simbol, atau cliffhanger.
- Jangan menjelaskan emosi yang sudah jelas dari tindakan/dialog.
- Jangan membuat semua tokoh memiliki suara yang sama.
- Jangan mengulang informasi demi memastikan pembaca paham.
- Jangan menambahkan fakta besar hanya agar bab terasa dramatis.
- Panjang bab mengikuti kebutuhan adegan dan target proyek, bukan angka universal.
- Jika detail fleksibel dikembangkan, pastikan tidak bertentangan dengan kanon.
- Jika menemukan lubang yang menghalangi penulisan, jangan menutupinya dengan improvisasi. Catat sebagai BELUM DIPUTUSKAN dan jelaskan pilihan paling masuk akal.

## Setelah menulis

Setiap bab yang selesai harus diikuti:
1. State Update berdasarkan hal yang benar-benar terjadi di naskah.
2. Pemeriksaan kesesuaian blueprint.
3. Pemeriksaan kronologi, lokasi, benda, pengetahuan tokoh/pembaca, dan perubahan hubungan.
4. Audit prosa untuk kenyamanan membaca.
5. Catatan temuan dan status bab: DRAFT, NEEDS_REPAIR, atau ACCEPTED.

Jangan menandai ACCEPTED jika ada kontradiksi kritis atau masalah besar yang belum diselesaikan. Masalah kecil boleh dicatat tanpa menghambat progres.

## Aturan perubahan

- Jangan menimpa keputusan kanon tanpa mencatat alasan.
- Jangan mengubah blueprint yang benar hanya untuk membenarkan prosa yang salah.
- Jangan mengubah naskah agar sesuai dengan State Update yang keliru.
- Perubahan struktural harus masuk ke `decision-log.md`, termasuk alasan dan file/bab terdampak.
- Perubahan lokal tidak boleh memicu penulisan ulang seluruh novel.
- Jangan menghapus tanggal/waktu secara massal; pertahankan orientasi waktu.
- Jangan mengubah judul, genre, POV utama, mekanisme misteri, hubungan inti, atau akhir tanpa alasan dan pencatatan.
- Jangan membuat file dummy, placeholder kosong, atau menyatakan pekerjaan selesai jika belum diverifikasi.

## Penggunaan GitHub

GitHub adalah sumber kebenaran proyek (source of truth), bukan sekadar tempat backup.
- Simpan semua keputusan dan hasil kerja yang sudah disepakati ke folder novel yang benar.
- Gunakan nama file konsisten dan mudah dicari.
- Perbarui indeks proyek setelah menambah/mengubah dokumen.
- Buat commit dengan pesan yang menjelaskan perubahan.
- Jangan menimpa perubahan pengguna yang belum diperiksa.
- Jika akses tulis GitHub tidak tersedia, berikan hasil dalam format file lengkap dan jelaskan bahwa belum tersimpan ke repo.
- Jangan mengklaim file sudah tersimpan sebelum commit atau operasi tulis berhasil dan diverifikasi.

## Standar selesai

Sebuah novel dianggap selesai secara proses jika naskah lengkap, catatan kontinuitas terakhir diperbarui, audit akhir dilakukan, daftar masalah tersisa transparan, dan status tiap bab dapat ditelusuri. Status ini tidak berarti karya sempurna atau pasti diterima penerbit.
