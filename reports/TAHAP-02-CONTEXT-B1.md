# PAKET KONTEKS BAB 001

Proyek: gang-yang-hilang-dari-peta
Target naskah: stories/gang-yang-hilang-dari-peta/manuscript/chapter-001.md
Target State Update: stories/gang-yang-hilang-dari-peta/state-updates/chapter-001.md
Gunakan sumber di bawah sebagai sumber kebenaran. Bedakan KANON, WAJIB, FLEKSIBEL, dan BELUM DIPUTUSKAN.
Jangan menyimpulkan fakta yang tidak didukung sumber. Jika ada konflik yang memengaruhi cerita, laporkan dan jangan menebak.
State Update bab setelah target tidak boleh digunakan.
Mode: PENULISAN BARU

## Instruksi AI — AI_INSTRUCTIONS.md

# Instruksi Operasional AI — writenovelAI

Baca dokumen ini sebelum bekerja. Repository adalah sumber kebenaran proyek, bukan sekadar backup. Jangan mengklaim menjalankan program, membaca file, menguji, atau menyimpan perubahan jika tindakan itu tidak benar-benar dilakukan.

## Pembagian tanggung jawab

- **Python:** membaca sumber, menyusun memori berbasis sumber, membangun paket konteks, memeriksa struktur, memverifikasi file, dan mengorkestrasi proses.
- **AI:** memahami cerita, merancang sebab-akibat, mengembangkan karakter, menilai planting-payoff, mengambil keputusan kreatif dalam ruang yang diizinkan, mengaudit, dan menulis prosa.
- **Git:** melacak perubahan. Jangan menimpa perubahan pengguna yang belum diperiksa.

## Sumber kebenaran dan status informasi

Urutan sumber: dokumen kanon/konsep proyek dan decision log yang disetujui, outline aktif, blueprint, naskah aktual, lalu State Update yang bersumber dari naskah. Jika sumber bertentangan, jangan memilih diam-diam. Tunjukkan lokasi konflik dan usulkan perbaikan.

Gunakan label:
- **KANON:** fakta yang sudah diputuskan atau terjadi.
- **WAJIB:** hasil/peristiwa harus ada, cara penyampaian masih terbuka.
- **FLEKSIBEL:** ruang improvisasi yang tidak mengubah fungsi atau fakta.
- **BELUM DIPUTUSKAN:** jangan mengarang jawaban lalu memperlakukannya sebagai fakta.

AI tidak boleh mengubah canon, keputusan, hubungan inti, mekanisme konflik, atau akhir secara diam-diam.

Gunakan dokumen metode di `docs/` saat membangun alur, blueprint, kontinuitas, audit, atau workspace. Saat membuat proyek baru, gunakan template di `templates/` sebagai format awal; jangan menyalin isi cerita dari `examples/` ke novel lain.

## Alur dari premis

Premis adalah input awal yang cukup. AI mengembangkan konsep, karakter, dunia, alur lengkap, jumlah bab sesuai kebutuhan, dan blueprint. Jangan meminta pengguna mengisi formulir panjang jika keputusan kreatif dapat diambil secara wajar. Tandai hanya ketidakpastian yang benar-benar memengaruhi identitas cerita atau logika utama.

Sebelum penulisan, audit outline dan blueprint:
- rantai sebab-akibat dan konsekuensi;
- motivasi dan pilihan karakter;
- character arc dan perubahan hubungan;
- timeline kronologis versus urutan penyajian;
- pengetahuan karakter dan pembaca pada setiap titik;
- planting, perkembangan petunjuk, dan payoff;
- batas kewenangan, prosedur, dan realisme dunia;
- keputusan kanon dan dampak perubahan lintas bab.

Setiap temuan audit harus menyebut lokasi, bukti, tingkat kepastian, dampak, dan perbaikan minimum. Pisahkan kontradiksi pasti, risiko, dan preferensi subjektif. Audit tidak otomatis memberi izin mengedit.

## Gunakan Python sebagai gerbang data

Jalankan dari root repository. Jika beberapa proyek tersedia, selalu tentukan slug.

```bash
python novel.py --story SLUG status
python novel.py --story SLUG memory --before NOMOR_BAB
python novel.py --story SLUG context NOMOR_BAB
python novel.py --story SLUG context NOMOR_BAB --rewrite
python novel.py --story SLUG audit
python novel.py --story SLUG audit --prompt
python novel.py --story SLUG verify NOMOR_BAB
python novel.py --story SLUG agy 1-5,8
```

- `status`: lihat progres file.
- `memory --before N`: susun memori dari dokumen inti dan State Update sebelum bab N. Jangan gunakan memori masa depan.
- `context N`: buat paket konteks lengkap. Baca seluruh file hasil yang dilaporkan Python sebelum menulis.
- `context N --rewrite`: hanya setelah pengguna secara eksplisit meminta rewrite.
- `audit`: jalankan pemeriksaan deterministik.
- `audit --prompt`: buat paket sumber dan instruksi untuk audit AI. Baca dan kerjakan auditnya, jangan menganggap prompt sebagai hasil audit.
- `verify N`: cek keberadaan naskah, blueprint, dan State Update. Ini bukan penilaian kualitas.
- `agy 1-5,8`: jalankan AGY satu bab demi satu bab. Bab yang sudah ada dilewati; batch berhenti jika satu bab gagal. Tambahkan `--rewrite` hanya jika pengguna meminta rewrite.

Untuk menulis langsung sebagai AI:
1. Jalankan `context N`.
2. Baca paket konteks dari awal sampai akhir.
3. Tulis prosa lengkap ke target naskah yang disebutkan.
4. Buat/perbarui State Update berdasarkan kejadian aktual di naskah, bukan rencana blueprint.
5. Jalankan `verify N`.
6. Audit kesesuaian naskah terhadap blueprint dan periksa konsekuensi ke bab berikutnya.
7. Lanjutkan ke bab berikutnya hanya setelah naskah dan State Update tersimpan.

Jika target sudah ada, jangan timpa tanpa persetujuan eksplisit. Batch harus berurutan, tidak paralel. Setelah tiap bab, perbarui State Update sebelum mengambil konteks bab berikutnya.

## State Update dan memori

State Update adalah catatan faktual, bukan prosa ulang atau interpretasi bebas. Catat seperlunya:
- waktu dan lokasi aktual;
- kondisi fisik/emosional yang relevan;
- apa yang diketahui, diduga, dan belum diketahui setiap karakter;
- fakta baru dan sumbernya;
- perubahan hubungan, tujuan, sumber daya, atau konflik;
- benda/dokumen/petunjuk dan statusnya;
- janji, keputusan, konsekuensi, dan pertanyaan terbuka.

Jangan menulis State Update untuk peristiwa yang hanya direncanakan tetapi tidak muncul dalam naskah. Jangan menaikkan dugaan menjadi kanon. Perubahan kanon harus melalui decision log dan menyebut dampak pada bab terkait.

## Prinsip anti-halusinasi

- Jangan mengisi celah sumber dengan detail yang terdengar masuk akal tetapi tidak didukung.
- Jangan membuat karakter mengetahui sesuatu sebelum ada jalur informasi.
- Jangan memberi bukti lebih kuat daripada yang benar-benar ditampilkan.
- Jangan membuat payoff tanpa planting yang cukup, atau menganggap setiap detail kecil wajib menjadi misteri.
- Jangan mengubah blueprint agar membenarkan kesalahan naskah.
- Jika ada ketidakpastian lokal yang tidak merusak cerita, pilih opsi paling sederhana dan tandai sebagai fleksibel. Jika menyentuh struktur inti, hentikan bagian yang bergantung padanya dan laporkan.
- Hindari mengulang ringkasan dan memori yang tidak relevan. Gunakan konteks bab yang sudah disiapkan Python.

## Mode kerja

1. **ARCHITECT:** konsep, karakter, dunia, alur makro, dan jumlah bab.
2. **BLUEPRINT:** urutan adegan, tujuan, perubahan, pengetahuan tokoh/pembaca, sebab-akibat, batas fakta.
3. **WRITER:** menulis prosa, tidak memparafrasekan blueprint.
4. **AUDITOR:** melaporkan temuan berbukti tanpa mengedit.
5. **REPAIRER:** memperbaiki masalah dengan perubahan terkecil dan menelusuri dampak.
6. **LIBRARIAN:** menjaga indeks, status, dan struktur file tanpa mengubah cerita.

## Standar prosa

Gunakan paragraf normal, bahasa alami, dialog dengan suara berbeda, detail yang bekerja untuk adegan, dan emosi yang muncul dari tindakan. Hindari kalimat puitis yang dipaksakan, metafora berulang, dialog eksposisi, repetisi informasi, cliffhanger buatan, serta satu kalimat per baris. Blueprint menjaga fungsi dan logika, bukan mengunci setiap kalimat.

## GitHub Actions

Workflow pemeriksaan menjalankan Python compile, unit test, dan audit deterministik. Lolos workflow hanya berarti pemeriksaan teknis tersebut lolos; bukan bukti novel sudah konsisten atau layak terbit.

## Larangan klaim

Jangan menyatakan file tersimpan sebelum operasi Git berhasil. Jangan menyatakan pengujian lolos jika workflow atau test belum benar-benar dijalankan. Jika AI tidak memiliki akses terminal, jangan berpura-pura telah menjalankan Python; gunakan tool repository yang tersedia atau minta pengguna menjalankan perintah secara lokal.

## Panduan blueprint adegan — docs/02-scene-blueprint.md

# Scene Blueprint

## Fungsi
Scene Blueprint adalah jembatan antara kerangka makro dan naskah bab. Ia cukup rinci untuk menjaga logika cerita, tetapi cukup terbuka agar prosa tidak terasa seperti instruksi yang diparafrasekan. Blueprint mengendalikan apa yang terjadi dan mengapa, bukan setiap kalimat.

## Dua sumbu waktu
- Waktu kronologis: kapan peristiwa benar-benar terjadi di dunia cerita.
- Urutan penyajian: kapan pembaca melihat peristiwa tersebut.

Contoh: Bab 1 dibuka pada 18 Oktober, Bab 2–4 mundur ke 15–17 Oktober, lalu Bab 5 kembali ke 18 Oktober. Ini sah selama perpindahan jelas dan informasi tetap masuk akal. Terapkan pembedaan ini pada flashback, in medias res, lompatan waktu, pergantian POV, dan pengungkapan tertunda.

## Format blueprint

### Identitas bab
- Nomor dan judul
- POV
- Waktu kronologis
- Posisi dalam urutan penyajian
- Lokasi
- Jenis bab: pembuka / pengembangan / transisi / karakter / titik balik / pengungkapan / resolusi / lainnya
- Fungsi utama

### Posisi cerita
- Kondisi cerita sebelum bab
- Keinginan tokoh POV
- Konflik, tekanan, atau pertanyaan yang dibawa masuk
- Hubungan dengan bab sebelumnya
- Jembatan menuju bab berikutnya

### Rangkaian adegan
Untuk setiap adegan:
- Lokasi dan waktu
- Tokoh yang hadir
- Tujuan adegan
- Situasi awal
- Urutan tindakan/peristiwa
- Informasi yang tersedia bagi tokoh
- Informasi yang belum diketahui tokoh
- Informasi yang boleh diketahui pembaca
- Informasi yang harus ditahan
- Perubahan setelah adegan
- Detail wajib
- Ruang pengembangan prosa

### Penutup bab
- Keadaan tokoh setelah bab
- Perubahan konflik atau hubungan
- Fakta baru yang menjadi kanon
- Pertanyaan/ketegangan yang dibawa ke depan
- Hal yang tidak boleh disimpulkan pembaca secara keliru

### Batasan penulisan
- Fakta yang tidak boleh diubah
- Peristiwa wajib
- Ruang pengembangan
- Hal yang belum diputuskan dan tidak boleh diada-adakan

## Tingkat rincian
Rinci pada sebab-akibat, alasan karakter bertindak, tujuan adegan, pengetahuan tokoh/pembaca, perubahan keadaan, detail yang menjadi petunjuk, serta urutan waktu.
Jangan terlalu rinci pada setiap gerakan kecil, seluruh ekspresi, setiap kalimat dialog, dekorasi yang tidak relevan, atau penjelasan emosi yang seharusnya muncul melalui tindakan dan dialog.

Blueprint boleh memberi arah dialog jika ada informasi atau batas yang wajib dijaga. Jangan mengunci seluruh dialog kecuali ada alasan khusus seperti kalimat kunci, kebohongan spesifik, atau petunjuk.

## Empat kategori keputusan
1. **Tetap:** fakta kanon yang tidak boleh berubah tanpa revisi terencana.
2. **Wajib terjadi:** peristiwa/hasil yang harus ada, tetapi cara penyampaiannya masih terbuka.
3. **Ruang pengembangan:** dialog sehari-hari, gerak kecil, detail suasana, dan transisi yang tidak mengubah fakta.
4. **Belum diputuskan:** keputusan penting yang belum tersedia. Jangan mengarang jawaban lalu memperlakukannya sebagai kanon.

## Jenis fungsi bab
Satu bab dapat memiliki beberapa fungsi, tetapi tentukan satu fungsi utama:
- Plot: mengubah konflik atau tujuan.
- Karakter: memperlihatkan pola, pilihan, atau perubahan.
- Hubungan: mengubah kedekatan, jarak, kepercayaan, atau ketegangan.
- Transisi: memindahkan tokoh/waktu/keadaan secara bermakna.
- Atmosfer: membangun pengalaman tempat atau situasi yang penting.
- Informasi: memberi atau mengubah pemahaman.
- Titik balik: mengubah arah cerita.
- Konsekuensi/resolusi: memperlihatkan akibat dan penyelesaian.

Bab tenang tidak otomatis tidak berguna. Ia perlu memberi pengalaman atau perubahan yang tidak bisa diperoleh dengan cara sama dari bab lain.

## Kriteria siap ditulis
Blueprint siap ditulis jika fungsi bab jelas, urutan adegan dan sebab-akibat dapat dipahami, motivasi masuk akal, pengetahuan tokoh/pembaca tidak tertukar, waktu/lokasi cukup jelas, fakta wajib ditandai, ruang pengembangan tersedia, dan tidak ada keputusan struktural penting yang menggantung.
Detail yang belum diputuskan tetapi tidak memengaruhi bab ini boleh tetap terbuka.

## Panduan kontinuitas — docs/03-continuity.md

# Kontinuitas dan State Update

## Tujuan
Menjaga hubungan antarbab tanpa memaksa AI membaca ulang seluruh naskah setiap kali menulis. Catatan harus ringkas, akurat, dan hanya menyimpan informasi yang berguna.

## State Update setelah setiap bab
Catat:
1. Fakta cerita baru yang benar-benar menjadi fakta.
2. Pengetahuan karakter: siapa mengetahui apa, dari sumber mana, dan kapan.
3. Pengetahuan pembaca: informasi yang telah diperlihatkan.
4. Keadaan cerita: lokasi tokoh, benda penting, kondisi hubungan, konflik aktif.
5. Perubahan karakter yang tampak melalui tindakan/pilihan.
6. Pertanyaan terbuka.
7. Anomali atau risiko yang perlu diperiksa.

Jangan menambahkan tafsir sebagai fakta. Bedakan apa yang terjadi, diduga, dan belum diketahui.

## Empat catatan lintas bab

### Timeline
Tanggal/jam, durasi perjalanan/aktivitas, urutan kejadian, flashback, dan jeda waktu yang memengaruhi kondisi tokoh. Jangan menghapus tanggal hanya karena terasa kaku. Jika tanggal dihilangkan dari prosa, orientasi waktu tetap harus jelas dan alami.

### Character Knowledge
Untuk setiap tokoh: apa yang diketahui, kapan, dari siapa/peristiwa apa, tingkat keyakinan, serta apa yang belum diketahui atau disalahpahami.
Pengetahuan tidak boleh berpindah tanpa sumber. Tokoh tidak dapat mengetahui lokasi, isi pikiran, pesan, percakapan, atau peristiwa yang tidak pernah mereka akses, kecuali mekanisme cerita sudah ditetapkan.

### Story State
Lokasi/posisi tokoh, kepemilikan dan lokasi benda penting, status dokumen/pesan/bukti, keadaan konflik, hubungan, pekerjaan, janji, dan komitmen yang belum selesai.

### Character Behavior
Kebiasaan, pemicu, respons, dampak respons, perilaku baru yang dicoba, serta apakah perubahan bertahan, gagal, atau mundur.
Jangan menyamakan satu tindakan dengan perubahan karakter permanen. Perubahan meyakinkan memerlukan pengulangan, tekanan, konsekuensi, dan pilihan berbeda.

## Aturan pengetahuan tokoh
Setiap kali tokoh menyebut atau bereaksi terhadap informasi, tanyakan:
- Dari mana informasi diperoleh?
- Kapan ia mendapatkannya?
- Apakah ia melihat, mendengar, membaca, diberi tahu, atau menyimpulkan?
- Apakah kesimpulannya masuk akal?
- Apakah pembaca sudah mengetahui hal yang sama?

Contoh kesalahan: Mira berkata, “Aku tahu kamu sedang di penginapan,” padahal tidak ada sumber yang memberinya informasi itu.
Perbaikan minimal: ubah dialog menjadi respons yang sesuai pengetahuannya. Tidak perlu mengubah bab sebelumnya jika memang tidak ada sumber informasi.

## Tingkat kepentingan
- Kritis: identitas, kematian, lokasi benda bukti, pengetahuan tokoh, urutan peristiwa.
- Penting: hubungan, tujuan, janji, pekerjaan, konflik berjalan.
- Kontekstual: detail yang mungkin berguna untuk bab terdekat.
- Tidak perlu dilacak: dekorasi atau gerakan kecil tanpa konsekuensi.

## Prinsip pembaruan
Perbarui catatan hanya ketika fakta/keadaan berubah. Jangan mengubah catatan untuk menutupi kesalahan naskah. Jika prosa salah tetapi blueprint benar, perbaiki prosa dan pertahankan catatan. Jika keputusan cerita berubah, perbarui blueprint dan semua catatan terdampak. Simpan sumber informasi agar pengetahuan karakter dapat ditelusuri.

## Standar prosa — docs/05-writing-standard.md

# Standar Penulisan Prosa

## Prinsip
Blueprint yang benar tidak otomatis menghasilkan bab yang enak dibaca. Kualitas rancangan cerita dan kualitas pelaksanaan prosa harus diperiksa terpisah. Prosa harus terasa seperti cerita, bukan instruksi blueprint yang diparafrasekan.

## Narasi
- Gunakan bahasa sesuai karakter, latar, genre, dan pembaca.
- Utamakan kalimat jelas dan alami.
- Variasikan panjang kalimat sesuai ritme.
- Gunakan paragraf normal; jangan memecah setiap kalimat menjadi baris tersendiri tanpa alasan.
- Pilih detail yang membantu pembaca membayangkan situasi atau memahami tindakan.
- Jangan menjelaskan ulang hal yang sudah ditunjukkan.
- Jangan memaksakan metafora, simbol, atau kalimat puitis pada setiap adegan.
- Jangan menutup setiap bab dengan kalimat dramatis jika situasi tidak menuntut.
- Jangan menerangkan makna adegan setelah adegan itu sendiri sudah menyampaikannya.

## Dialog
- Dialog harus terdengar seperti sesuatu yang mungkin diucapkan tokoh tersebut.
- Perbedaan karakter muncul dari pilihan kata, cara menghindar, menjawab, kebiasaan, dan hal yang tidak dikatakan.
- Hindari dialog terlalu rapi untuk percakapan spontan.
- Jangan membuat tokoh menjelaskan konflik yang sudah diketahui lawan bicara hanya demi memberi informasi kepada pembaca.
- Jangan membuat semua tokoh berbicara dengan suara sama.
- Dialog boleh terpotong, canggung, atau salah paham jika sesuai situasi.
- Jangan membuat tokoh menyimpulkan sesuatu yang belum didukung informasi.

## Emosi dan karakter
Tampilkan emosi melalui tindakan, pilihan, respons tubuh, dialog, dan perhatian tokoh. Penjelasan langsung boleh digunakan, tetapi jangan menjadi satu-satunya cara.
Jangan membuat tokoh berubah total karena satu percakapan. Perubahan perlu diuji oleh situasi berbeda dan konsekuensi nyata. Kemunduran dapat menjadi bagian perkembangan. Tokoh pendukung bukan penyelamat instan; mereka punya batas dan kepentingan sendiri.

## Ritme dan adegan
Setiap adegan sebaiknya memiliki setidaknya satu fungsi: mengubah situasi, memperlihatkan karakter, mengembangkan hubungan, memberi informasi, membangun suasana relevan, atau mempersiapkan konsekuensi.
Adegan tenang sah jika memberi pengalaman/kedekatan/pemahaman yang dibutuhkan.
Hindari pengulangan, konflik karena tokoh tidak mau bertanya tanpa alasan, kesalahpahaman yang dipertahankan tidak masuk akal, penyelesaian kebetulan tanpa persiapan, dan peristiwa besar tanpa konsekuensi.

## Pola prosa AI yang perlu diperiksa
- Terlalu sering menjelaskan perasaan setelah dialog/tindakan.
- Mengulang gagasan dengan beberapa kalimat.
- Menggunakan gestur sama berulang kali untuk semua tokoh.
- Berlebihan memakai jeda, tatapan, helaan napas, atau senyum tipis.
- Menyisipkan simbolisme terlalu jelas lalu menjelaskannya.
- Membuat setiap paragraf terdengar seperti kutipan.
- Menutup adegan dengan refleksi abstrak yang tidak muncul alami.
- Menyusun dialog seperti sesi terapi/wawancara.
- Menggunakan tanggal/jam secara kaku ketika orientasi waktu bisa lebih alami.

Ini tanda untuk diperiksa, bukan larangan mutlak. Masalah muncul jika berulang, tidak sesuai konteks, atau membuat tulisan terasa dibuat-buat.

## Pemeriksaan kenyamanan membaca
- Apakah pembaca bisa mengikuti siapa melakukan apa?
- Apakah dialog terasa wajar jika dibaca keras?
- Apakah narasi menjelaskan hal yang sudah terlihat?
- Apakah perpindahan paragraf/adegan mulus?
- Apakah ritme sesuai jenis adegan?
- Apakah kalimat indah cocok dengan tokoh dan situasi?
- Apakah pembaca diberi ruang menyimpulkan sendiri?

Bab bisa lolos audit kontinuitas tetapi tetap perlu penyuntingan prosa. Prosa indah tidak dapat menutupi logika cerita yang rusak.

## Kontrak kerja — docs/06-ai-operating-contract.md

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

## README proyek — stories/gang-yang-hilang-dari-peta/README.md

# Gang yang Hilang dari Peta

- **Slug:** gang-yang-hilang-dari-peta
- **Status proyek:** UJI BLUEPRINT
- **Status rancangan:** DRAF UNTUK DINILAI
- **Status penulisan:** Belum dimulai
- **Jumlah bab:** 30
- **Terakhir diperbarui:** 2026-11-23

## Premis
Salma, teknisi pemetaan berusia 29 tahun, kembali ke Gang Kenari untuk memverifikasi peta kawasan yang akan digunakan dalam proyek pelebaran saluran drainase. Peta resmi menunjukkan gang itu berakhir di sebuah tembok, padahal tiga keluarga masih tinggal di baliknya. Ketika ia mencari asal-usul kesalahan tersebut, ia menemukan bahwa ayahnya, Hadi, yang dulu menjadi sekretaris lingkungan, pernah menandatangani perubahan peta yang menghapus keberadaan rumah-rumah itu.

## Arah cerita
- **Genre:** Misteri sosial, drama keluarga, realisme kontemporer.
- **Pengalaman membaca:** Misteri yang bertumpu pada dokumen, ingatan warga, dan keputusan manusia; bukan konspirasi besar atau kejutan supernatural.
- **Konflik utama:** Salma harus menentukan apakah akan melaporkan keberadaan tiga rumah yang tidak tercatat, meskipun bukti itu juga membuka kesalahan ayahnya dan dapat menghambat proyek.
- **Taruhan:** Jika peta disahkan apa adanya, akses tiga rumah berisiko tertutup dan keberadaan penghuninya tidak masuk proses peninjauan dampak. Jika Salma mengajukan temuan, proyek perlu ditinjau ulang dan warga tetap belum otomatis memperoleh hak atas tanah.
- **POV:** Orang ketiga terbatas, dominan Salma.
- **Target:** Novel sekitar 30 bab; panjang naskah belum ditetapkan.

## Status pekerjaan

| Tahap | Status | Catatan |
|---|---|---|
| Premis dan konsep | DRAF | Dibuat mandiri untuk pengujian blueprint |
| Karakter dan dunia | DRAF | Perlu dinilai bersama outline |
| Outline | DRAF LENGKAP | 30 bab |
| Blueprint | DRAF LENGKAP | 30 file, dua adegan utama per bab |
| Audit rancangan | BELUM DILAKUKAN | Sengaja belum mengaudit sendiri sampai dinilai |
| Penulisan | Belum dimulai | Menunggu penilaian blueprint |

## Dokumen inti
- [Premis](00-premise.md)
- [Konsep](01-concept.md)
- [Karakter](02-characters.md)
- [Dunia dan aturan](03-world-and-rules.md)
- [Outline 30 bab](04-story-outline.md)
- [Decision log](05-decision-log.md)
- [Indeks blueprint](blueprint/README.md)

## Catatan pengujian
Dokumen ini sengaja dibuat sebagai rancangan yang bisa diuji, bukan diklaim sudah sempurna atau lolos audit. Penilaian utama: apakah sebab-akibat jelas, motivasi tokoh masuk akal, bukti ditemukan secara wajar, konflik berkembang, dan blueprint memberi cukup arah tanpa mendikte prosa.

## MEMORI CERITA BERDASARKAN SUMBER

## SOURCE: stories/gang-yang-hilang-dari-peta/00-premise.md

# Premis — Gang yang Hilang dari Peta

Salma (29), teknisi pemetaan kontrak, mendapat tugas memverifikasi batas bangunan dan akses jalan di Gang Kenari sebelum proyek pelebaran saluran drainase dimulai. Peta kerja menunjukkan gang berakhir di tembok kosong. Namun, saat survei, Salma menemukan tiga keluarga masih tinggal di balik tembok itu.

Masalah menjadi pribadi ketika ia menemukan tanda tangan ayahnya, Hadi, pada perubahan peta tahun 2011 yang menghapus tiga rumah tersebut dari catatan lingkungan. Hadi sudah meninggal. Ibunya, Yuni, menolak membicarakan kejadian itu.

Salma harus menentukan apa yang sebenarnya terjadi pada 2011, mengumpulkan bukti yang dapat diperiksa, dan memutuskan apa yang harus ia laporkan sebelum peta final disahkan. Mengungkap keberadaan rumah-rumah itu tidak otomatis menyelesaikan status tanah mereka, tetapi membiarkan peta salah akan membuat mereka semakin sulit terlihat.

## Pertanyaan dramatik
Mengapa Hadi menghapus tiga rumah dari catatan, dan apa yang akan dilakukan Salma ketika kebenaran itu ternyata tidak membuat ayahnya sepenuhnya benar atau sepenuhnya jahat?

## Batas cerita
- Tidak ada tokoh yang memiliki akses ajaib ke dokumen atau pikiran orang lain.
- Dokumen lama dapat rusak, tidak lengkap, atau saling bertentangan.
- Ingatan warga bukan bukti sempurna.
- Temuan pemetaan bukan putusan kepemilikan tanah.
- Proyek tidak dihentikan secara ajaib; hasil realistisnya adalah peninjauan ulang jalur akses dan dampak sosial.
- Konflik diselesaikan melalui verifikasi, keterbukaan, dan keputusan yang memiliki biaya, bukan pengakuan dramatis satu orang.

## SOURCE: stories/gang-yang-hilang-dari-peta/01-concept.md

# Konsep Cerita — Gang yang Hilang dari Peta

## Premis pengembangan
Misteri berpusat pada ketidaksesuaian antara peta resmi dan keadaan lapangan. Setiap sumber informasi memberi potongan berbeda: peta digital, sketsa ukur, buku administrasi, kuitansi, foto, dan kesaksian. Tidak satu pun langsung menyelesaikan persoalan.

## Struktur
Cerita dibuka pada 17 Agustus 2026, ketika Salma menolak menandatangani peta final yang menyatakan area di balik tembok sebagai lahan kosong. Setelah itu cerita mundur ke 4 Agustus, saat ia pertama kali menerima tugas. Bab 2–18 bergerak maju sampai kembali ke hari rapat tersebut. Bab 19–30 melanjutkan akibat keputusan Salma.

Pembuka bukan adegan yang harus diulang utuh. Bab 19 melanjutkan dari sesudah penolakan di rapat.

## Mekanisme misteri
Pada 2011, setelah banjir dan pekerjaan darurat untuk membuka jalur air, tiga rumah di halaman belakang Gang Kenari tidak dimasukkan ke peta pembaruan. Hadi, sekretaris lingkungan saat itu, menandatangani lembar perubahan yang menyebut area tersebut sebagai bangunan penyimpanan sementara. Ia bermaksud menunda penggusuran saat warga belum punya tempat pindah, dengan janji bahwa data akan diperbaiki setelah keadaan stabil. Perbaikan itu tidak pernah dilakukan.

Keputusan Hadi bukan satu-satunya penyebab masalah: proses pendataan pemerintah tidak ditindaklanjuti, warga tidak memiliki dokumen tanah yang kuat, dan Hadi memilih diam ketika status sementara berubah menjadi catatan permanen. Ia juga tidak menerima uang suap. Motifnya campuran: perlindungan jangka pendek, ketakutan pada konflik, dan rasa malu setelah gagal menepati janji.

## Pusat konflik masa kini
Proyek drainase memakai peta yang menganggap gang berakhir di tembok. Rencana teknis akan menutup jalur sempit menuju tiga rumah. Salma tidak berwenang menetapkan hak tanah atau membatalkan proyek. Ia dapat mencatat ketidaksesuaian lapangan, mengajukan verifikasi tambahan, dan meminta rancangan akses ditinjau sebelum dokumen final.

## Perkembangan karakter
- Salma: dari menganggap data teknis netral menjadi memahami bahwa keputusan pencatatan punya akibat; ia belajar membedakan kesetiaan pada ayah dan tanggung jawab pada fakta.
- Yuni: dari menghindari masa lalu menjadi mengakui bahwa diamnya ikut mempertahankan kesalahan.
- Bu Sari: dari curiga Salma hanya datang untuk mengukur lalu pergi menjadi bersedia menyerahkan bukti, tetapi tetap menuntut hasil konkret.
- Dimas: dari menolak kerja sama menjadi membantu verifikasi setelah melihat Salma tidak menjanjikan hal yang tak bisa ia penuhi.
- Dito: rekan kerja yang menguji klaim dengan bukti dan prosedur; bukan penyelamat atau penghalang.
- Pak Bowo: ketua RT yang ingin proyek berjalan dan takut warga diberi harapan palsu; bukan antagonis jahat.

## Akhir yang dituju
Peta final ditahan untuk verifikasi tambahan. Tim proyek mengubah detail akses dan meminta pemeriksaan dampak pada tiga rumah. Status kepemilikan belum selesai. Salma menyerahkan salinan catatan ayahnya kepada warga dan kantor terkait, tanpa menghapus bagian yang menunjukkan kesalahan Hadi. Perubahan nyata tetapi terbatas.

## SOURCE: stories/gang-yang-hilang-dari-peta/02-characters.md

# Karakter

## Salma — 29
Teknisi pemetaan kontrak di perusahaan konsultan infrastruktur. Teliti, cenderung percaya bahwa data yang rapi berarti data yang benar. Ia kembali ke Gang Kenari karena tugas lapangan, bukan karena ingin menyelidiki ayahnya. Ayahnya, Hadi, meninggal pada 2022. Salma mengingat Hadi sebagai orang yang tertib dan disegani, tetapi hubungan mereka tidak terlalu terbuka. Kelemahan: ketika fakta mengganggu gambaran yang ia pegang, ia menunda mengambil kesimpulan.

## Yuni — 56
Ibu Salma. Tinggal di rumah lama keluarga, beberapa gang dari lokasi survei. Mengetahui Hadi pernah berjanji memperbaiki catatan tiga rumah setelah pekerjaan darurat 2011. Ia tidak mengetahui semua detail administrasi. Ia memilih diam karena menganggap persoalan sudah berlalu dan takut Salma merusak nama ayahnya. Perubahannya bukan pengakuan total, melainkan kesediaan memberi informasi yang ia tahu dan mengakui batas pengetahuannya.

## Sari — 54
Penghuni salah satu rumah di halaman belakang. Menjalankan jasa jahit rumahan. Menyimpan kuitansi listrik, foto keluarga, dan surat-surat yang menunjukkan mereka telah tinggal di sana, tetapi tidak memiliki sertifikat tanah. Ia tidak selalu ramah kepada Salma karena sudah beberapa kali didata tanpa hasil.

## Dimas — 27
Anak Sari, kurir barang. Praktis dan curiga pada pendataan resmi. Ia pernah diminta mengosongkan area untuk pekerjaan saluran, tetapi tidak mendapat penjelasan tertulis. Ia mengetahui jalur keluar-masuk dan perubahan fisik gang, bukan sejarah administrasi lengkap.

## Dito — 32
Rekan Salma di tim survei. Bertanggung jawab pada pengukuran lapangan dan dokumentasi teknis. Berorientasi prosedur, tetapi tidak kaku. Ia mengingatkan Salma bahwa kesaksian dan foto harus dicatat sumber serta tanggalnya.

## Pak Bowo — 61
Ketua RT saat ini. Ingin proyek drainase selesai karena banjir berulang mengganggu warga. Ia tahu tiga keluarga tinggal di belakang, tetapi mengira status mereka sedang diurus. Ia pernah menerima salinan peta 2011, namun tidak memahami dampaknya.

## Niken — 63
Mantan staf administrasi kelurahan yang pensiun. Pernah membantu mengarsipkan dokumen pembaruan wilayah pada 2011. Ia dapat menjelaskan alur administrasi dan mengenali format dokumen, tetapi tidak mengetahui semua keputusan di baliknya.

## SOURCE: stories/gang-yang-hilang-dari-peta/03-world-and-rules.md

# Dunia dan Aturan Cerita

## Tempat
Gang Kenari berada di kawasan padat Kota Tanjung Sagara, kota pesisir fiktif. Gang utama berujung pada tembok penahan lama. Di baliknya ada halaman bersama dan tiga rumah kecil yang dapat dicapai melalui lorong samping selebar kurang lebih 1,2 meter. Peta kerja proyek tidak menggambarkan lorong tersebut sebagai akses publik.

## Proyek drainase
Pemerintah kota menyiapkan pelebaran saluran dan perbaikan dinding penahan setelah banjir berulang. Perusahaan konsultan tempat Salma bekerja mengumpulkan data lapangan untuk gambar teknis dan dokumen dampak. Tim Salma bukan penentu hak tanah, bukan pelaksana penggusuran, dan tidak bisa menjanjikan kompensasi.

Jika ada bangunan atau akses yang tidak tercatat, Salma dapat memasukkannya sebagai ketidaksesuaian untuk diverifikasi. Hal itu dapat menunda pengesahan gambar di segmen terkait dan memicu peninjauan desain. Tidak otomatis membatalkan seluruh proyek.

## Riwayat 2011
Banjir besar merusak sebagian saluran. Pekerjaan darurat membuka akses alat berat melalui Gang Kenari. Tiga rumah di halaman belakang dikosongkan sementara, lalu ditempati kembali. Dalam pembaruan peta, area rumah dicatat sebagai bangunan penyimpanan sementara. Hadi menandatangani lembar administrasi tersebut. Tidak ada bukti suap atau perintah rahasia.

## Aturan bukti
- Foto hanya membuktikan apa yang terlihat dan sejauh mana tanggal/lokasinya dapat diverifikasi.
- Kuitansi listrik atau pembayaran menunjukkan pemakaian/aktivitas, bukan kepemilikan tanah.
- Kesaksian menguatkan kronologi tetapi dapat berbeda.
- Buku lapangan dan peta lama perlu diperiksa asal-usul serta konteksnya.
- Salma harus mencatat temuan dan sumber, bukan mengubah peta diam-diam.

## Batas teknis
Tidak ada akses ke basis data rahasia atau sistem yang dapat mengungkap semuanya dalam satu klik. Salma menggunakan perangkat survei, peta kerja, arsip yang dapat diminta secara wajar, dan wawancara lapangan.

## SOURCE: stories/gang-yang-hilang-dari-peta/04-story-outline.md

# Outline Aktif — Gang yang Hilang dari Peta

**Status:** DRAF UNTUK DINILAI  
**Jumlah:** 30 bab  
**Genre:** Misteri sosial, drama keluarga, realisme kontemporer  
**Rentang waktu:** 4–30 Agustus 2026  
**Struktur:** Pembuka in medias res pada 17 Agustus; bab 2–17 mundur ke awal penugasan; bab 18 kembali ke rapat pembuka tanpa mengulang adegan; bab 19–30 bergerak maju.

| Bab | Judul | Waktu | POV | Fungsi |
|---:|---|---|---|---|
| 1 | [Garis Merah di Atas Peta](blueprint/chapter-001.md) | 17 Agustus 14.00 | Salma | Pembuka in medias res: Salma menolak mengesahkan peta yang menyebut area di balik tembok sebagai lahan kosong. |
| 2 | [Tugas yang Kelihatannya Sederhana](blueprint/chapter-002.md) | 4 Agustus 09.00 | Salma | Salma menerima tugas verifikasi peta proyek drainase dan kembali ke kawasan tempat ayahnya pernah menjadi sekretaris lingkungan. |
| 3 | [Tembok yang Terlalu Rapi](blueprint/chapter-003.md) | 5 Agustus 08.00 | Salma | Survei menemukan lorong aktif yang tidak tercantum pada peta; Dimas mengakui ada rumah di baliknya tetapi curiga pada pendataan. |
| 4 | [Tiga Rumah di Belakang](blueprint/chapter-004.md) | 6 Agustus 15.00 | Salma | Salma melihat tiga rumah di halaman belakang dan mendengar pengalaman warga yang pernah didata tanpa tindak lanjut. |
| 5 | [Peta Tidak Mengukur Penghuni](blueprint/chapter-005.md) | 7 Agustus 09.00 | Salma | Laporan anomali diterima, tetapi tim meminta bukti tambahan dan mengingatkan Salma agar tidak mengubah peta sendiri. |
| 6 | [Kuitansi yang Disimpan](blueprint/chapter-006.md) | 8 Agustus 10.00 | Salma | Sari memperlihatkan kuitansi dan surat lama yang menunjukkan aktivitas hunian, tetapi tidak membuktikan kepemilikan. |
| 7 | [Foto Sebelum Tembok](blueprint/chapter-007-to-030.md#bab-07) | 9 Agustus 14.00 | Salma | Foto kerja bakti menunjukkan bangunan telah ada; Yuni mengenali Hadi di foto dan menghindari pertanyaan tentang perannya. |
| 8 | [Orang yang Mengingat Banjir](blueprint/chapter-007-to-030.md#bab-08) | 10 Agustus 08.00 | Salma | Kesaksian Pak Bowo dan Bu Rukmini berbeda dalam detail waktu, sehingga Salma mencari arsip tertulis. |
| 9 | [Berkas yang Tidak Lengkap](blueprint/chapter-007-to-030.md#bab-09) | 11 Agustus 09.00 | Salma | Indeks arsip 2011 ditemukan; nama Hadi tercatat sebagai pengantar lingkungan. |
| 10 | [Tanda Tangan Ayah](blueprint/chapter-007-to-030.md#bab-10) | 12 Agustus 13.00 | Salma | Lampiran menunjukkan Hadi menandatangani perubahan yang mencatat tiga rumah sebagai bangunan penyimpanan sementara. |
| 11 | [Istilah Sementara](blueprint/chapter-007-to-030.md#bab-11) | 13 Agustus 09.00 | Salma | Staf arsip menjelaskan keterbatasan formulir lama; Salma menghubungi Niken, mantan staf kelurahan. |
| 12 | [Catatan di Pinggir Buku](blueprint/chapter-007-to-030.md#bab-12) | 14 Agustus 10.00 | Salma | Buku agenda Niken mencatat Hadi pernah meminta penundaan pengosongan, tetapi tidak mencatat tindak lanjut. |
| 13 | [Rumah yang Tidak Pernah Kosong](blueprint/chapter-007-to-030.md#bab-13) | 15 Agustus 08.00 | Salma | Salma menyusun kronologi hunian dari ingatan Sari dan Dimas serta bukti fisik yang masih ada. |
| 14 | [Garis yang Berbeda](blueprint/chapter-007-to-030.md#bab-14) | 16 Agustus 09.00 | Salma | Pengukuran menunjukkan rancangan dinding penahan akan mengganggu akses lorong menuju tiga rumah. |
| 15 | [Bukan Sekadar Salah Gambar](blueprint/chapter-007-to-030.md#bab-15) | 16 Agustus 16.00 | Salma | Yuni mengakui Hadi pernah menyebut janji enam bulan, tetapi ia tidak tahu apakah janji itu pernah ditindaklanjuti. |
| 16 | [Orang yang Menandatangani](blueprint/chapter-007-to-030.md#bab-16) | 17 Agustus 08.00 | Salma | Salma memastikan Hadi adalah pengantar permintaan, bukan satu-satunya pejabat penetap perubahan peta. |
| 17 | [Sebelum Tanda Tangan](blueprint/chapter-007-to-030.md#bab-17) | 17 Agustus 11.00 | Salma | Salma dan Dito menyusun lampiran yang memisahkan fakta ukur, kesaksian, dan dugaan. |
| 18 | [Rapat yang Tertunda](blueprint/chapter-007-to-030.md#bab-18) | 17 Agustus 13.45 | Salma | Rapat yang telah dibuka di bab 1 berlangsung; pengesahan segmen ditahan untuk verifikasi. |
| 19 | [Yang Bisa Dibuktikan](blueprint/chapter-007-to-030.md#bab-19) | 18 Agustus 08.00 | Salma | Tim menetapkan pemeriksaan tambahan dan mengukur ulang akses bersama Dimas. |
| 20 | [Tidak Ada Janji Hari Ini](blueprint/chapter-007-to-030.md#bab-20) | 19 Agustus 16.00 | Salma | Sari menuntut kepastian; Salma menjelaskan status review tanpa menjanjikan hasil yang belum ada. |
| 21 | [Buku Ayah](blueprint/chapter-007-to-030.md#bab-21) | 20 Agustus 09.00 | Salma | Catatan pribadi Hadi menunjukkan niat memberi waktu enam bulan, sekaligus tidak adanya tindak lanjut yang tercatat. |
| 22 | [Halaman yang Hilang](blueprint/chapter-007-to-030.md#bab-22) | 21 Agustus 10.00 | Salma | Halaman buku yang terlepas dan arsip yang tidak lengkap tidak memberi jawaban pasti; Salma menolak mengarang kesimpulan. |
| 23 | [Bukti yang Tidak Sempurna](blueprint/chapter-007-to-030.md#bab-23) | 22 Agustus 08.00 | Salma | Salma menyusun laporan jujur tentang hunian dan akses, dengan catatan Hadi sebagai konteks terbatas. |
| 24 | [Gambar yang Harus Diubah](blueprint/chapter-007-to-030.md#bab-24) | 23 Agustus 09.00 | Salma | Tim desain menguji dua opsi akses; keduanya memiliki biaya dan persyaratan. |
| 25 | [Jalan Masuk](blueprint/chapter-007-to-030.md#bab-25) | 24 Agustus 08.00 | Salma | Warga berbeda pendapat tentang akses dan drainase, tetapi sepakat meminta penjelasan teknis. |
| 26 | [Apa yang Ditinggalkan Ayah](blueprint/chapter-007-to-030.md#bab-26) | 24 Agustus 16.00 | Salma | Yuni mengakui ia ikut memilih diam; Salma menerima bahwa ayahnya bertanggung jawab tanpa menyederhanakannya sebagai penjahat. |
| 27 | [Saluran dan Halaman](blueprint/chapter-007-to-030.md#bab-27) | 25 Agustus 09.00 | Salma | Insinyur menjelaskan opsi mempertahankan lorong dengan perubahan terbatas dan risiko yang masih harus dihitung. |
| 28 | [Nama yang Dicatat Kembali](blueprint/chapter-007-to-030.md#bab-28) | 26 Agustus 13.00 | Salma | Tiga rumah dan akses masuk daftar verifikasi lanjutan, tanpa dianggap sebagai pengakuan kepemilikan. |
| 29 | [Bukan Akhir Urusan](blueprint/chapter-007-to-030.md#bab-29) | 27 Agustus 10.00 | Salma | Sari menerima dokumen temuan dan meminta jadwal tindak lanjut tertulis; status tanah tetap belum selesai. |
| 30 | [Ujung Gang yang Baru](blueprint/chapter-007-to-030.md#bab-30) | 30 Agustus 07.00 | Salma | Salma memperbarui peta dengan status yang akurat dan menerima bahwa pencatatan benar adalah awal, bukan penyelesaian seluruh masalah. |

## Rangkaian sebab-akibat
1. Tim proyek menggunakan peta lama untuk merancang pelebaran saluran.
2. Survei Salma menemukan tiga rumah dan lorong yang tidak tergambar.
3. Bukti warga menunjukkan aktivitas hunian, tetapi tidak otomatis membuktikan kepemilikan.
4. Arsip 2011 menghubungkan perubahan peta dengan tanda tangan Hadi.
5. Kesaksian Niken dan catatan Hadi menunjukkan bahwa pencatatan sementara dimaksudkan menunda pengosongan setelah banjir.
6. Tidak ada bukti koreksi pernah diselesaikan. Hadi bertanggung jawab atas keputusan dan diamnya, tetapi bukan satu-satunya pejabat dalam proses.
7. Pengukuran ulang membuktikan rancangan dapat menutup akses.
8. Salma menolak mengesahkan peta kosong dan menyusun laporan dengan membedakan fakta, kesaksian, dan dugaan.
9. Tim menahan pengesahan segmen, meninjau akses, dan memasukkan tiga rumah ke daftar verifikasi.
10. Status kepemilikan belum selesai. Akhir memberi perubahan nyata tetapi terbatas.

## Pertanyaan audit sebelum penulisan
- Apakah orientasi waktu pada pembuka dan kilas balik cukup jelas?
- Apakah bab 18 mengulang terlalu banyak adegan bab 1?
- Apakah kewenangan Salma dan prosedur proyek realistis?
- Apakah bukti cukup untuk mencatat hunian dan akses, tetapi tidak dilebihkan menjadi bukti hak tanah?
- Apakah motif Hadi didukung lebih dari satu sumber tanpa menjadikannya tokoh yang sepenuhnya benar atau jahat?
- Apakah 30 bab benar-benar diperlukan, atau ada bab yang dapat digabung tanpa kehilangan fungsi?
- Apakah kepentingan warga dan kebutuhan drainase sama-sama mendapat bobot?
- Apakah akhir terasa selesai secara emosional meskipun proses administratif berlanjut?

## Batas interpretasi
Tidak ada pembatalan proyek total, sertifikat instan, suap, konspirasi besar, atau satu penjahat yang menanggung semua kesalahan. Peta yang diperbaiki adalah langkah awal, bukan penyelesaian seluruh persoalan warga.

## SOURCE: stories/gang-yang-hilang-dari-peta/05-decision-log.md

# Decision Log

## D-001 — Motif perubahan peta 2011
- **Tanggal:** 23 November 2026
- **Status:** KANON UNTUK RANCANGAN UJI
- **Keputusan:** Hadi menandatangani pencatatan tiga rumah sebagai bangunan penyimpanan sementara setelah banjir 2011. Ia bermaksud menunda pengosongan saat warga belum punya tempat pindah, dengan harapan data diperbaiki kemudian. Ia tidak menerima suap. Ia tetap bertanggung jawab karena tidak memastikan koreksi dilakukan dan kemudian memilih diam.
- **Alasan:** Memberi motif manusiawi tanpa membebaskan Hadi dari konsekuensi. Menghindari antagonis konspiratif yang terlalu mudah.
- **Dampak:** Bukti harus menunjukkan niat sementara dan kelalaian lanjutan; jangan membuat dokumen tunggal menjadi pengakuan sempurna.

## D-002 — Hasil proyek pada akhir cerita
- **Status:** KANON UNTUK RANCANGAN UJI
- **Keputusan:** Peta final segmen tersebut ditahan untuk verifikasi tambahan. Desain akses ditinjau ulang. Status kepemilikan tiga rumah belum selesai.
- **Alasan:** Hasil sebanding dengan kewenangan Salma dan bukti yang tersedia.
- **Dampak:** Jangan menutup cerita dengan sertifikat instan, kompensasi ajaib, atau proyek dibatalkan total.

## D-003 — Hubungan keluarga
- **Status:** KANON UNTUK RANCANGAN UJI
- **Keputusan:** Yuni mengetahui sebagian keputusan Hadi dan janji untuk memperbaiki catatan, tetapi tidak mengetahui seluruh proses administrasi. Ia bukan dalang dan tidak menyimpan dokumen lengkap.
- **Dampak:** Informasi Yuni harus disampaikan sebagai ingatan terbatas, bukan penjelasan serba tahu.

## Belum diputuskan
Tidak ada keputusan struktural utama yang sengaja dibiarkan kosong. Detail teknis kecil seperti nama perusahaan konsultan, nomor dokumen, dan nama jalan lain boleh ditetapkan saat penulisan selama tidak mengubah mekanisme cerita.

## BLUEPRINT BAB 1

# Blueprint Bab 1 — Garis Merah di Atas Peta

## Identitas
- **POV:** Salma
- **Waktu kronologis:** 17 Agustus 2026, 14.00–14.35
- **Urutan penyajian:** Pembuka masa depan relatif; bab berikutnya mundur ke 4 Agustus.
- **Lokasi:** Ruang rapat kantor konsultan
- **Jenis bab:** Pembuka in medias res
- **Fungsi utama:** Memperlihatkan Salma menolak mengesahkan peta yang menganggap halaman belakang Gang Kenari kosong.

## Posisi cerita
- **Kondisi sebelum bab:** Salma sudah melakukan survei awal; pembaca belum mengetahui bagaimana ia menemukan ketidaksesuaian.
- **Tujuan tokoh POV:** Menghindari pengesahan data yang ia tahu tidak sesuai lapangan.
- **Konflik/tekanan/pertanyaan:** Memperlihatkan Salma menolak mengesahkan peta yang menganggap halaman belakang Gang Kenari kosong.
- **Hubungan dengan bab sebelumnya:** Pembuka mendahului rangkaian sebab yang akan dijelaskan melalui kilas balik.
- **Jembatan menuju bab berikutnya:** Bab 2 mundur ke 4 Agustus, saat tugas diberikan.

## Adegan 1 — Peta final
- **Lokasi dan waktu:** 17 Agustus, 14.00
- **Tokoh hadir:** Salma, Dito, koordinator proyek
- **Tujuan adegan:** Menempatkan keputusan Salma di bawah tekanan tenggat.
- **Situasi awal:** Peta segmen Gang Kenari ditampilkan sebagai lahan kosong di balik tembok.
- **Urutan kejadian:** Koordinator meminta tanda tangan verifikasi; Salma menyatakan ada tiga bangunan dan satu akses yang belum masuk; Dito meminta bukti lapangan dilampirkan; rapat ditunda untuk klarifikasi terbatas.
- **Yang diketahui tokoh:** Salma tahu hasil surveinya; Dito tahu catatan lapangan; koordinator hanya tahu peta kerja awal.
- **Yang diketahui pembaca:** Pembaca tahu ada perbedaan peta dan kondisi nyata, tetapi belum tahu asalnya.
- **Informasi yang ditahan:** Alasan Salma yakin ada rumah dan keterlibatan ayahnya ditahan.
- **Perubahan setelah adegan:** Salma menolak menandatangani dokumen yang belum benar.
- **Detail wajib:** Peta, catatan survei, tenggat pengesahan.
- **Ruang pengembangan prosa:** Dialog rapat dan detail teknis boleh disederhanakan; jangan membuat Salma punya kewenangan membatalkan proyek.

## Adegan 2 — Nama di kolom pemeriksa
- **Lokasi dan waktu:** 17 Agustus, 14.20–14.35
- **Tokoh hadir:** Salma, Dito
- **Tujuan adegan:** Menanam hubungan personal dengan masalah administrasi.
- **Situasi awal:** Koordinator keluar; Dito melihat Salma terpaku pada lampiran lama.
- **Urutan kejadian:** Salma mengenali nama Hadi pada kolom pengesahan dokumen 2011; ia tidak menjelaskan semuanya kepada Dito; ia meminta salinan arsip dan berkata ingin memeriksa dari awal.
- **Yang diketahui tokoh:** Salma tahu Hadi ayahnya; Dito baru tahu nama itu punya hubungan pribadi.
- **Yang diketahui pembaca:** Pembaca mengetahui ayah Salma terlibat, belum tahu apa perannya.
- **Informasi yang ditahan:** Isi dan motif perubahan 2011.
- **Perubahan setelah adegan:** Salma memutuskan menelusuri dokumen, bukan menandatangani atau menuduh.
- **Detail wajib:** Lampiran 2011 dengan tanda tangan Hadi.
- **Ruang pengembangan prosa:** Jangan ungkap motif ayah pada pembuka.

## Penutup bab
- **Keadaan tokoh setelah bab:** Salma memiliki satu informasi, keputusan, atau konsekuensi baru yang mengubah langkah berikutnya.
- **Perubahan konflik/hubungan:** Memperlihatkan Salma menolak mengesahkan peta yang menganggap halaman belakang Gang Kenari kosong.
- **Fakta baru yang menjadi kanon:** Mengikuti detail wajib dan perubahan adegan di atas; dugaan tidak boleh dinaikkan menjadi fakta.
- **Pertanyaan/ketegangan yang dibawa ke depan:** Bab 2 mundur ke 4 Agustus, saat tugas diberikan.
- **Hal yang tidak boleh disimpulkan pembaca:** Temuan pemetaan tidak sama dengan kepemilikan tanah; kesaksian dan dokumen memiliki batas pembuktian.

## Batasan
- **Tetap:** Premis, mekanisme perubahan peta 2011, kewenangan Salma, dan hasil akhir parsial sesuai dokumen proyek.
- **Wajib:** Peristiwa dan perubahan yang dijabarkan pada dua adegan.
- **Ruang pengembangan:** Dialog, gerak kecil, detail tempat, transisi, dan respons spontan yang tidak mengubah fakta.
- **Belum diputuskan:** Detail teknis kecil boleh dikembangkan; jangan menambahkan suap, pembunuhan, konspirasi, atau bukti ajaib.

## Kesiapan
- [x] Fungsi bab ditetapkan
- [x] Dua adegan utama dan perubahan ditetapkan
- [x] Batas pengetahuan tokoh/pembaca dicatat
- [x] Kronologi dan urutan penyajian dicatat
- [ ] Audit silang dengan seluruh bab
- [ ] Audit kelayakan teknis dan prosedural
