# Tahap Arsitektur Agent-Agnostic — Audit Awal dan Koreksi

**Branch:** `architecture/agent-agnostic-workflow`  
**Basis:** `73d9d4bbebbdb55ab71ad941cb7619fb7f9e5048`  
**Status:** dokumentasi arsitektur dan koreksi fakta selesai; implementasi mesin belum dimulai.

## Keputusan

AGY bukan pusat sistem. Python Context Engine harus dapat digunakan oleh berbagai AI Agent dan execution host. ChatGPT/Gemini web yang memiliki akses repository serta tool eksekusi dapat menjalankan alur secara interaktif. GitHub Actions dapat menjalankan alur headless melalui API provider. Keduanya berbeda dan tidak boleh disamakan.

## Temuan kode yang mendasari keputusan

1. `novel_engine/project.py` sudah menjadi fondasi netral: membaca sumber proyek, membangun memori temporal, dan menyusun konteks bab.
2. `novel_engine/cli.py` sudah menyediakan antarmuka perintah yang dapat dipanggil agen yang punya akses terminal.
3. `novel_engine/agy.py` mengikat eksekusi ke executable lokal `agy`; modul ini harus diperlakukan sebagai adapter opsional.
4. `novel_engine/github_bot.py` memanggil model satu kali untuk menghasilkan JSON naskah dan State Update. Belum ada loop tool-calling yang memungkinkan model meminta Python mengambil data tambahan.
5. `github_bot.py` mengimpor parser rentang bab dari `agy.py`, sehingga utilitas generik masih bergantung pada adapter AGY.
6. Bot API melakukan commit/push langsung. Untuk pengembangan selanjutnya, branch dan pull request lebih aman.
7. Workflow CI terpisah dari AI dan tidak membutuhkan API key. Pemisahan ini harus dipertahankan.

## Koreksi State Update Bab 3

State Update sebelumnya menyatakan Dimas tinggal bersama ibunya di salah satu rumah belakang tembok. Naskah hanya menyatakan ibu Dimas dan keluarga lain tinggal di sana; tempat tinggal Dimas sendiri tidak ditetapkan secara eksplisit. Klaim tersebut dihapus. Keterangan lisan Dimas kini dibedakan dari fakta yang telah diverifikasi tim survei. Status pekerjaan kurir tidak lagi dimasukkan sebagai fakta baru bab karena berasal dari profil, bukan penegasan peristiwa di naskah.

## File yang diubah

- `stories/gang-yang-hilang-dari-peta/state-updates/chapter-003.md`: koreksi overclaim faktual.
- `docs/09-agent-agnostic-architecture.md`: arsitektur target, perbedaan agen interaktif dan Actions API, kontrak interaksi Python, kesenjangan, tahapan implementasi.
- `README.md`: menjelaskan bahwa AGY opsional dan menautkan arsitektur baru.

Tidak ada naskah, outline, blueprint, profil karakter, engine code, atau workflow yang diubah.

## Tahap implementasi berikutnya

1. Ekstrak parser nomor bab ke modul netral dan pastikan core dapat diuji tanpa AGY.
2. Tambahkan antarmuka Python ber-output JSON untuk status, konteks, pencarian sumber, dan validasi.
3. Tambahkan operasi simpan draft yang dibatasi ke folder cerita dan mencegah overwrite tanpa izin.
4. Baru setelah fondasi tersebut stabil, implementasikan tool-calling berulang untuk GitHub Actions API.
5. Uji agen interaktif (ChatGPT/Gemini dengan akses repository dan Python) terpisah dari jalur API Actions.

## Batas verifikasi

Perubahan dilakukan melalui GitHub API pada branch terpisah. Tidak ada Python runtime di GitHub yang dieksekusi oleh proses edit ini, sehingga unit test dan workflow belum diklaim lolos. CI harus berjalan pada branch/PR untuk memverifikasi kode pada tahap berikutnya.
