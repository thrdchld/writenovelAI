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
