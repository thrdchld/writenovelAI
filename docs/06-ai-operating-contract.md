# Kontrak Operasional AI

## Tujuan

Menerjemahkan metodologi writenovelAI menjadi perilaku kerja yang dapat dijalankan konsisten oleh AI, baik saat menggunakan ChatGPT, coding agent, maupun model lain yang diberi akses repository.

Dokumen ini melengkapi, bukan menggantikan, dokumen 01–05. Instruksi pintu masuk ada di `AI_INSTRUCTIONS.md`.

## 1. Input minimum

Pengguna cukup memberikan premis. Jika tersedia, pengguna boleh menambahkan preferensi seperti genre, target pembaca, panjang, gaya, batas konten, atau referensi. Semua itu opsional kecuali premis tidak dapat dipahami sama sekali.

AI tidak boleh mengubah preferensi opsional menjadi formulir wajib. Jika ada beberapa interpretasi yang sama-sama mungkin dan berdampak besar, AI boleh memilih interpretasi paling kuat, mencatat asumsi, dan meminta konfirmasi hanya jika keputusan tersebut berisiko mengubah inti cerita secara material.

## 2. Hak keputusan AI dan batasnya

### AI boleh memutuskan secara mandiri
- Genre/subgenre paling sesuai dengan premis.
- Nama tokoh, pekerjaan, latar, detail keseharian.
- Jumlah bab dan pembagian adegan.
- Urutan pengenalan informasi, termasuk flashback dan in medias res.
- Detail dialog, tindakan, transisi, dan atmosfer.
- Solusi lokal yang tidak mengubah fakta atau arah cerita.

### AI harus mencatat sebagai keputusan
- Identitas atau hubungan penting yang menjadi kunci cerita.
- Penyebab utama konflik dan mekanisme penyelesaiannya.
- Fakta masa lalu yang menentukan motivasi.
- Aturan dunia yang membatasi kemungkinan peristiwa.
- Pengungkapan besar, twist, kematian, pengkhianatan, atau perubahan hubungan inti.
- Perubahan POV/struktur yang mengubah pengalaman pembaca.
- Perubahan akhir atau pesan utama cerita.

### AI harus menandai BELUM DIPUTUSKAN
Jika keputusan penting belum memiliki dasar dan beberapa opsi akan menghasilkan cerita yang berbeda secara substansial. Jangan mengisi kekosongan itu dengan detail yang tampak meyakinkan lalu menganggapnya kanon.

## 3. Tahapan dan quality gates

| Tahap | Hasil minimum | Gate untuk lanjut |
|---|---|---|
| Premis | Ringkasan inti, asumsi, arah pengalaman | Premis dapat dikembangkan tanpa mengubah inti |
| Konsep | Genre, pembaca, konflik, taruhan, daya tarik | Konflik dan pengalaman pembaca jelas |
| Fondasi | Karakter/dunia relevan, aturan dan relasi | Tokoh punya alasan bertindak yang masuk akal |
| Rancangan makro | Alur awal–tengah–akhir, jumlah bab | Sebab-akibat utama dan akhir dapat dijelaskan |
| Blueprint | Rangkaian adegan setiap bab | Fungsi, perubahan, pengetahuan, waktu jelas |
| Audit rancangan | Daftar temuan dan keputusan terbuka | Tidak ada lubang kritis yang menghalangi penulisan |
| Penulisan | Naskah bab lengkap | Bab sesuai rancangan dan nyaman diikuti |
| State Update | Fakta, pengetahuan, keadaan terbaru | Catatan sesuai naskah, bukan tafsir |
| Audit bab | Temuan berbukti dan dampak | Tidak ada masalah kritis yang belum ditangani |
| Audit akhir | Konsistensi keseluruhan dan daftar sisa | Novel utuh, masalah tersisa transparan |

Gate bukan tuntutan kesempurnaan. Masalah kecil yang tidak mengganggu dapat dicatat dan pekerjaan dilanjutkan.

## 4. Status dokumen dan bab

Gunakan status berikut:
- `WORKING`: masih dikerjakan.
- `REVIEW`: siap diperiksa.
- `ACTIVE`: rancangan/keputusan yang sedang berlaku.
- `LOCKED`: disetujui sebagai dasar kerja; perubahan harus melalui decision log.
- `DRAFT`: naskah belum lolos audit.
- `NEEDS_REPAIR`: ada masalah yang perlu diperbaiki.
- `ACCEPTED`: lolos pemeriksaan minimum untuk melanjutkan.
- `SUPERSEDED`: digantikan versi baru; jangan dihapus jika masih diperlukan untuk jejak perubahan.

Jangan memberi status LOCKED atau ACCEPTED hanya karena dokumen telah dibuat.

## 5. Paket konteks bab

Setiap siklus penulisan harus menggunakan konteks yang cukup, bukan seluruh repository secara membabi buta. Paket minimal:
- Ringkasan cerita dan arah akhir yang relevan.
- Blueprint bab target.
- State Update bab sebelumnya.
- Timeline dan pengetahuan karakter yang terkait.
- Fakta kanon dan keputusan terbuka yang memengaruhi bab.
- Batas pengungkapan kepada pembaca.
- Ringkasan konsekuensi dari bab yang baru saja terjadi.

Jika bab adalah flashback atau in medias res, nyatakan posisi kronologis dan posisi penyajiannya secara eksplisit.

## 6. Standar audit

Audit harus memisahkan:
1. Kesalahan pasti dengan bukti.
2. Risiko yang belum terbukti.
3. Preferensi/masukan subjektif.

Prioritas temuan:
- **Kritis:** merusak pemahaman atau fondasi cerita; kontradiksi besar, pengetahuan mustahil, mekanisme utama tidak masuk akal.
- **Besar:** mengganggu motivasi, sebab-akibat, kontinuitas, atau pengalaman membaca secara nyata.
- **Sedang:** kelemahan lokal yang terasa tetapi tidak meruntuhkan cerita.
- **Kecil:** pilihan kata, repetisi ringan, detail minor.

Laporan wajib menunjukkan lokasi, bukti, alasan, sumber masalah, dampak, perbaikan minimal, dan area yang perlu diperiksa ulang.

## 7. Prosedur repair

1. Jangan mengedit sebelum temuan dan sumber masalah dipahami.
2. Tentukan apakah sumber ada pada rancangan, prosa, atau catatan.
3. Cari rentang terkecil yang cukup untuk membuktikan masalah.
4. Periksa dependensi sebelum/sesudah.
5. Perbaiki bagian terkecil yang menyelesaikan masalah.
6. Catat perubahan kanon bila memang terjadi.
7. Audit ulang hanya area terdampak.
8. Pastikan perbaikan tidak menciptakan masalah baru.

Audit dan repair adalah mode terpisah. Jika pengguna meminta audit, jangan langsung mengedit.

## 8. Pemeriksaan akhir kenyamanan membaca

Selain logika, evaluasi pengalaman pembaca:
- Apakah pembuka memberi alasan untuk terus membaca?
- Apakah pembaca tahu siapa, di mana, dan kapan tanpa penjelasan berlebihan?
- Apakah perpindahan waktu/POV dapat dikenali?
- Apakah dialog terdengar seperti percakapan, bukan penyampaian informasi?
- Apakah emosi terasa melalui kejadian, bukan hanya dijelaskan?
- Apakah adegan tenang tetap memberi pengalaman atau perubahan?
- Apakah konflik berkembang, bukan berputar?
- Apakah akhir terasa berasal dari pilihan dan konsekuensi sebelumnya?
- Apakah prosa memiliki variasi dan tidak terasa seperti rangkaian kalimat AI yang seragam?

## 9. Ketika konteks tidak cukup

Jangan berpura-pura telah membaca file yang tidak tersedia. Jangan mengandalkan ingatan percakapan untuk mengisi fakta yang tidak ada dalam dokumen aktif. Sebutkan file atau keputusan yang hilang dan dampaknya. Lanjutkan bagian yang tidak bergantung pada informasi tersebut bila memungkinkan.

## 10. Prinsip kelulusan

Metode dianggap bekerja jika AI dapat memulai dari premis, menghasilkan rancangan yang koheren, menulis bab yang nyaman dibaca, mempertahankan kontinuitas, dan memperbaiki masalah tanpa merusak bagian yang benar. Keberhasilan harus dibuktikan lewat pengujian lintas premis dan genre, bukan diasumsikan dari kelengkapan dokumentasi.
