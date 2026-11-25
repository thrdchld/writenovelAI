# Arsitektur Agent-Agnostic dan Eksekusi GitHub

**Status:** rancangan target, belum seluruhnya diimplementasikan  
**Keputusan:** AGY bukan komponen inti dan tidak boleh menjadi ketergantungan mesin penulisan.

## 1. Prinsip dasar

Sistem harus memisahkan tiga tanggung jawab:

1. **Python Context Engine** membaca sumber cerita, membangun konteks temporal, menyediakan data saat diminta, memvalidasi hasil, dan mengelola operasi file.
2. **AI Agent** memahami cerita, mengambil keputusan kreatif, melakukan audit, dan menulis prosa. Agen dapat berupa ChatGPT, Gemini, Claude, atau sistem lain yang memiliki akses ke repository dan kemampuan menjalankan tool.
3. **Execution Host** menyediakan tempat menjalankan Python dan menghubungkan agen dengan repository. Host dapat berupa GitHub Actions, ChatGPT Work/agent dengan konektor GitHub dan terminal, Gemini dengan integrasi repository, atau lingkungan coding agent lain.

AGY hanyalah salah satu adapter opsional. Tidak ada format data, aturan cerita, atau alur inti yang boleh bergantung pada executable AGY.

## 2. Dua mode penggunaan yang berbeda

### A. Agen interaktif yang mengoperasikan repository

Contoh: ChatGPT atau Gemini yang sedang digunakan pengguna, dengan konektor GitHub dan kemampuan menjalankan perintah Python melalui lingkungan kerja yang tersedia.

Alur:
1. Agen membaca instruksi repository dan status branch.
2. Agen menjalankan Python untuk meminta konteks bab tertentu.
3. Agen membaca hasil yang disiapkan Python.
4. Jika ada pertanyaan data tambahan, agen menjalankan perintah Python lagi dengan parameter yang sesuai.
5. Agen menulis naskah dan State Update ke file yang dituju.
6. Agen menjalankan validasi Python.
7. Agen memeriksa diff, memperbaiki masalah, lalu membuat commit atau pull request.

Dalam mode ini, agen web dan Python tidak harus berjalan di GitHub Actions. Yang penting, agen memiliki akses nyata ke repository dan execution tool. Konektor GitHub saja dapat mengubah file, tetapi tidak otomatis berarti agen dapat menjalankan Python. Kemampuan edit repository dan kemampuan menjalankan program adalah dua izin/tool terpisah.

### B. Otomatisasi headless melalui GitHub Actions

Alur:
1. Issue, dispatch, atau pemicu lain memulai workflow.
2. Python mengambil sumber dan menyiapkan konteks.
3. Workflow memanggil provider AI melalui API.
4. Jika provider mendukung tool/function calling, AI dapat meminta fungsi Python yang diizinkan secara berulang.
5. Python menjalankan fungsi tersebut dan mengembalikan hasilnya ke AI.
6. AI menghasilkan naskah dan State Update.
7. Python memvalidasi hasil, lalu membuat commit atau pull request.

Mode ini membutuhkan API key, biaya API, batas penggunaan, dan implementasi tool-calling. Sesi ChatGPT/Gemini web milik pengguna tidak otomatis tersedia sebagai API di GitHub Actions. Menggunakan API provider berarti menggunakan jalur produk dan autentikasi API tersendiri.

## 3. Bentuk interaksi AI dan Python

Targetnya bukan satu prompt besar yang memaksa AI menulis sekaligus. AI harus bisa melakukan siklus:

`AI → minta data → Python → hasil → AI → minta data lanjutan → Python → hasil → AI menulis`

Tool Python yang kelak disediakan harus sempit dan aman, misalnya:
- `get_story_status(story)`
- `get_chapter_context(story, chapter, mode)`
- `get_character_profile(story, character)`
- `get_timeline(story, before_chapter)`
- `search_story_sources(story, query, temporal_limit)`
- `validate_chapter(story, chapter)`
- `save_draft(story, chapter, manuscript, state_update)`

Nama di atas adalah kontrak rancangan, bukan klaim bahwa fungsi-fungsi tersebut sudah tersedia.

Python harus tetap menjadi sumber data yang dapat ditelusuri. AI tidak boleh membaca seluruh repository tanpa batas lalu mencampur fakta masa depan dengan pengetahuan tokoh. Setiap hasil tool perlu menyebutkan sumber file, batas waktu, dan kategori informasi bila relevan.

## 4. Kontrak hasil penulisan

Untuk setiap bab, hasil minimum:
- Naskah lengkap.
- State Update yang hanya memuat hal yang benar-benar terjadi atau dinyatakan dalam naskah.
- Referensi sumber konteks yang digunakan.
- Status validasi.
- Daftar keputusan baru yang perlu dicatat, bukan langsung dimasukkan sebagai kanon.

State Update harus membedakan observasi langsung, keterangan lisan, dugaan, dan fakta yang belum diverifikasi. Informasi dari profil karakter tidak boleh otomatis ditulis sebagai peristiwa bab.

Batch selalu berurutan:
1. Siapkan konteks bab N.
2. Tulis dan simpan bab N.
3. Buat State Update N.
4. Validasi keduanya.
5. Baru siapkan konteks bab N+1.

Jika satu bab gagal, batch berhenti. Bab yang sudah valid tidak dihapus.

## 5. Audit kondisi repository saat rancangan ini dibuat

Implementasi yang sudah ada:
- `project.py` membangun memori berbasis sumber dan konteks bab.
- `cli.py` menyediakan perintah status, memory, context, audit, dan verify.
- `agy.py` menjalankan AGY lokal secara berurutan. Ini adapter khusus, bukan mesin inti.
- `github_bot.py` menjalankan status, audit outline, dan write melalui GitHub Issue + API model kompatibel OpenAI Chat Completions.
- `novel-bot.yml` menjalankan bot di GitHub Actions.
- `python-check.yml` menjalankan compile, unit test, dan audit deterministik.

Kesenjangan yang teridentifikasi:
1. `github_bot.py` menggunakan satu permintaan model untuk menghasilkan JSON naskah + State Update. Belum ada siklus tool-calling agar model dapat meminta Python mengambil data tambahan saat proses menulis.
2. Jalur bot mengimpor `parse_numbers` dari `agy.py`. Utilitas umum tidak boleh bergantung pada adapter AGY.
3. Validasi hasil bot saat ini terutama memeriksa kelengkapan file/blueprint melalui `verify`. Itu belum menjamin isi bermakna, akurasi State Update, atau tidak ada placeholder.
4. Bot langsung melakukan commit dan push. Untuk perubahan yang lebih berisiko, pull request dan pemeriksaan diff lebih aman.
5. ChatGPT/Gemini web yang bekerja interaktif melalui konektor bukan hal yang sama dengan bot API di Actions. Keduanya perlu didukung sebagai execution host yang berbeda.
6. GitHub Actions CI saat ini menguji Python tanpa menjalankan model AI. Itu baik dan harus dipertahankan agar tes inti tidak memerlukan API key.

## 6. Rencana implementasi bertahap

### Tahap A — Fondasi bebas AGY
- Pindahkan utilitas umum seperti parsing rentang bab ke modul netral.
- Pastikan modul inti dapat diimpor tanpa AGY terpasang.
- Pertahankan adapter AGY hanya sebagai opsi.
- Tambahkan tes yang membuktikan Python Context Engine bekerja tanpa executable AGY.

### Tahap B — Antarmuka Python untuk agen
- Tetapkan perintah/format keluaran yang stabil dan mudah dibaca agen.
- Sediakan output JSON untuk status, konteks, pencarian sumber, dan validasi, tanpa menghilangkan format Markdown untuk pembacaan manusia.
- Tambahkan operasi simpan draft yang membatasi path ke folder proyek dan menolak overwrite tanpa izin eksplisit.
- Sertakan daftar file sumber dan batas temporal di hasil konteks.

### Tahap C — Protokol agen interaktif
- Dokumentasikan instruksi universal bagi ChatGPT, Gemini, Claude, dan coding agent.
- Agen harus mampu menjalankan Python, membaca hasil, menulis file, menjalankan tes, dan memeriksa diff.
- Sediakan mode audit, write, repair, dan batch dengan aturan yang sama.
- Jangan menganggap konektor GitHub otomatis menyediakan terminal/Python.

### Tahap D — API tool-calling di GitHub Actions
- Ubah bot API dari satu-shot generation menjadi loop tool-calling dengan allowlist fungsi Python.
- Batasi jumlah putaran, ukuran konteks, timeout, dan operasi file.
- Validasi setiap hasil tool dan setiap output AI.
- Simpan hasil sebagai branch/PR terlebih dahulu, bukan langsung mengubah main.
- Uji dengan provider yang benar-benar mendukung format tool calling; jangan menganggap semua endpoint kompatibel hanya karena mendukung Chat Completions.

### Tahap E — Pengujian lintas agen
- Uji satu skenario yang sama melalui agen interaktif dan API Actions.
- Bandingkan akurasi konteks, State Update, kontinuitas batch, kualitas naskah, dan jejak perubahan.
- Baru tetapkan jalur default setelah ada bukti.

## 7. Keputusan yang tidak boleh dilanggar

- Tidak ada ketergantungan wajib pada AGY.
- Tidak ada API key yang disimpan di repository.
- CI deterministik tetap dapat berjalan tanpa AI provider.
- Agen tidak boleh menimpa naskah yang sudah ada tanpa instruksi rewrite eksplisit.
- AI tidak boleh mengubah canon atau decision log diam-diam.
- Python tidak mengambil keputusan sastra; Python menyediakan data dan menjaga batas operasional.
- Semua perubahan harus dapat diaudit melalui diff dan riwayat Git.

## 8. Definisi selesai

Arsitektur dianggap berhasil jika agen yang berbeda dapat menggunakan Python yang sama untuk mengambil konteks, meminta data lanjutan, menulis satu atau banyak bab secara berurutan, memvalidasi hasil, dan menyimpan perubahan tanpa mengubah aturan cerita atau bergantung pada executable agen tertentu.
