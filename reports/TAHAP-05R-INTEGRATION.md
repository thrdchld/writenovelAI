# TAHAP-05R-INTEGRATION.md

**Tanggal:** 2026-11-25  
**Basis Commit:** `a73dd7d6902e893df77265c229af280cfb1604bd`  
**Repository:** `thrdchld/writenovelAI`

---

## 1. Perbaikan Keamanan Eksekusi AGY (`novel_engine/agy.py`)

### Perubahan yang Dilakukan
1. **Penghapusan `--dangerously-skip-permissions`:** Flag tersebut dihapus dari `novel_engine/agy.py`.
2. **Mekanisme Izin Aman (`--mode accept-edits`):** Berdasarkan `agy --help` pada lingkungan aktif (`--mode Set the agent execution mode for this session (accept-edits, auto, plan)`), runner menggunakan `--mode accept-edits` sehingga hanya persetujuan pengeditan/penulisan file di workspace yang diotomatisasi tanpa melewati seluruh izin (misalnya eksekusi perintah terminal sembarangan).
3. **Pembatasan Workspace (`cwd`):** `cwd` dipersempit dari `story.parents[1]` (seluruh root repository) menjadi `story.resolve()` (hanya direktori cerita target). Jalur target pada prompt menggunakan path relatif terhadap direktori cerita (`manuscript/chapter-001.md` dan `state-updates/chapter-001.md`).

### Perintah AGY yang Benar-Benar Dijalankan
```text
/data/data/com.termux/files/home/.local/bin/agy -p <prompt> --mode accept-edits --output-format json
```
dengan `cwd=<story_root>` (hanya folder proyek cerita target).

---

## 2. Perbaikan Validasi Hasil (`run_one` & `run_batch`)

1. **Validasi JSON Ketat:** Respons `stdout` dari `agy --output-format json` wajib berupa objek JSON valid (`dict`) dengan `status == "SUCCESS"` (case-insensitive). JSON rusak, tipe bukan `dict`, atau status selain `"SUCCESS"` kini mengembalikan `"error"` (tidak lagi diabaikan oleh `except: pass`).
2. **Penolakan Aksi & Kuota:** `denied_actions`, exit code bukan 0, maupun kata kunci kuota/rate limit (`quota`, `429`, `rate limit`, `resource_exhausted`, dll.) tetap mengembalikan `"error"`.
3. **Deteksi File Kosong / Placeholder (`_is_meaningful_content`):** File yang kosong, hanya berisi heading markdown, komentar HTML, garis pemisah, atau penanda placeholder (`TODO`, `TBD`, `placeholder`, `[placeholder]`, `belum ditulis`, `isi di sini`, `n/a`, `...`, `-`, `kosong`, `(kosong)`) ditolak dan mengembalikan `"incomplete"`.
4. **Verifikasi Perubahan saat `rewrite=True`:** Memeriksa `st_mtime_ns` dan `st_size` untuk file naskah (`target`) maupun State Update (`state`). Jika salah satu tidak berubah saat rewrite, mengembalikan `"incomplete"`.
5. **Proteksi Overwrite & Penghentian Batch:** File yang sudah ada tidak ditimpa tanpa `rewrite=True`; `run_batch()` langsung berhenti dan mengembalikan kode keluar `1` saat ada bab yang gagal (`result not in ("success", "skipped")`).

---

## 3. Bukti Pengujian Nyata End-to-End (Proyek Sementara Terisolasi)

Pengujian dilakukan menggunakan runner resmi (`novel_engine.agy.run_batch`) pada direktori sementara `tempfile.TemporaryDirectory(prefix="novel_e2e_v2_")` yang berisi proyek uji `uji-terisolasi` (`00-premise.md`, `02-characters.md`, `04-story-outline.md`, `blueprint/chapter-001.md`). Seluruh file proyek uji otomatis terhapus setelah `TemporaryDirectory` ditutup.

### Hasil Eksekusi Nyata AGY (`task-276`)
- **Status awal:** `BEFORE_EXISTS: False False` (kedua file target belum ada).
- **Output runner:**
  ```text
  Bab 1: naskah dan State Update ditemukan.
  RUN_BATCH_RC: 0
  AFTER_EXISTS: True True
  ```
- **File yang benar-benar dibuat oleh AGY:**
  - `manuscript/chapter-001.md`: **2.668 byte**, **17 baris** — diawali `# Bab 1 — Surat Pagi`, berisi prosa naratif adegan Rina di ruang arsip kota menemukan amplop cokelat tanpa pengirim.
  - `state-updates/chapter-001.md`: **1.576 byte**, **19 baris** — diawali `# State Update — Bab 1 (Surat Pagi)`, mencatat peristiwa faktual bahwa amplop tidak dibuka dan dicatat di buku agenda.
- **Integritas Cerita Utama:** Tidak ada file di `stories/gang-yang-hilang-dari-peta/` atau `stories/arman-mira/` yang dibuat atau diubah selama pengujian.

### Observasi Penanganan Kegagalan Jaringan Nyata (`task-257`)
Pada percobaan pertama sebelumnya (`task-257`), AGY sempat menulis kedua file sementara namun kemudian mengalami galat DNS jaringan (`dial tcp: lookup daily-cloudcode-pa.googleapis.com: no such host`). Runner mendeteksi kegagalan proses AGY tersebut, menghentikan batch (`Batch dihentikan pada Bab 1; bab berikutnya tidak dijalankan.`), dan mengembalikan `RUN_BATCH_RC: 1` — membuktikan kegagalan proses tidak dianggap sukses hanya karena file sempat tertulis.

---

## 4. Klasifikasi Jenis Pengujian

| Kategori | Apa yang Diuji | Metode | Hasil |
|---|---|---|---|
| **Pengujian Nyata (Live E2E)** | `run_batch` memanggil `agy --mode accept-edits --output-format json` pada proyek sementara terisolasi | Eksekusi nyata `agy` CLI | ✅ Lulus (`RUN_BATCH_RC: 0`, 2 file baru 2.668 B & 1.576 B) |
| **Pengujian Nyata (Live Flag Check)** | Verifikasi `--mode accept-edits` pada `agy` CLI di direktori sementara | Eksekusi nyata `agy` CLI | ✅ Lulus (`status: SUCCESS`, `hello.txt` tertulis) |
| **Pengujian Simulasi (Mock Unit Tests)** | `tests/test_agy.py` (8 tes): invalid JSON, `status: ERROR`, `denied_actions`, placeholder `TODO`, proteksi overwrite, rewrite tidak berubah, penghentian batch, tidak ada `--dangerously-skip-permissions` | `unittest.mock.patch` pada `subprocess.run` & `shutil.which` | ✅ 8/8 Lulus |
| **Pengujian Regresi Lama** | `tests/test_engine.py` (46 tes) & `tests/test_character_context.py` (15 tes) | `python -m unittest discover tests` | ✅ 61/61 Lulus |
| **Pemeriksaan Kode & Sintaks** | `python -m py_compile novel_engine/*.py tests/*.py novel.py` | Kompilasi bytecode Python | ✅ Exit code 0 |

**Total Unit Tests:** **69/69 Lulus** (`Ran 69 tests ... OK`).

---

## 5. Keterbatasan yang Belum Terselesaikan

1. **Akses Tulis dalam `cwd`:** Dengan `--mode accept-edits`, AGY dapat membuat/mengedit file di dalam `cwd` (`story_root`). Pembatasan ini mengandalkan `cwd` dan instruksi prompt karena `agy --help` tidak menyediakan flag pembatasan path tulis per-subdirektori secara terpisah.
2. **Kebergantungan Jaringan & Akun AGY:** Eksekusi nyata bergantung pada koneksi ke layanan AGY (`daily-cloudcode-pa.googleapis.com`) dan kuota akun yang aktif.
