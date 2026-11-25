# TAHAP-05S-VALIDATION.md

**Tanggal:** 2026-11-25  
**Basis Commit:** `ef857acd6dbfea982a740597ffefb8003de759e0`  
**Repository:** `thrdchld/writenovelAI`

---

## 1. Perubahan Kode

### `novel_engine/agy.py`
1. **Menyatukan standar validasi file existing dan file baru:**
   - Pada `run_one()`, pemeriksaan file existing (`if not rewrite and target.exists():`) sebelumnya hanya memakai `if read(target) and read(state):`.
   - Kini pemeriksaan tersebut menggunakan `_is_meaningful_content(read(target)) and _is_meaningful_content(read(state))` — standar yang sama persis dengan validasi file baru setelah AGY selesai.
   - Jika salah satu file kosong, hanya heading/komentar HTML, hanya placeholder, atau hanya satu file yang tersedia, `run_one()` mengembalikan `"incomplete"` tanpa memanggil AGY dan tanpa menimpa file.
   - Karena `run_batch()` berhenti bila `result not in ("success", "skipped")`, status `"incomplete"` pada file existing otomatis menghentikan batch (mengembalikan kode keluar `1`).
2. **Memperkuat deteksi placeholder (`_is_placeholder_line` & `_is_meaningful_content`):**
   - Menangani penanda placeholder langsung (`TODO`, `TBD`, `placeholder`, `belum ditulis`, `isi di sini`, `n/a`, `...`, `-`, `kosong`, termasuk variasi tanda kurung `[]`/`()` dan awalan list/quote) serta pola berawalan prefix seperti `TODO: tulis bab` atau `TBD: ...`.
   - Tetap menolak file yang hanya berisi heading markdown tanpa isi atau komentar HTML tanpa isi.
   - Memastikan prosa wajar yang mengandung kata `TODO` dalam kalimat biasa (misalnya *"catatan kecil bertuliskan TODO dari rapat kemarin"*) **tetap diterima** sebagai konten valid (`True`) karena tidak cocok dengan penanda/prefix baris placeholder.

### `tests/test_agy.py`
Menambahkan 6 pengujian regresi baru (total 14 tes di `tests/test_agy.py`):
- `test_placeholder_detection_cases` (menguji `TODO`, `TODO: tulis bab`, `TBD`, `Belum ditulis`, `Isi di sini`, heading tanpa isi, komentar HTML tanpa isi, serta prosa valid dengan kata `TODO`)
- `test_existing_both_placeholder_incomplete_and_no_agy`
- `test_existing_valid_manuscript_placeholder_state_incomplete`
- `test_existing_placeholder_manuscript_valid_state_incomplete`
- `test_existing_manuscript_without_state_incomplete`
- `test_batch_stops_on_incomplete_existing_files`

---

## 2. Contoh Kasus Sebelum vs. Sesudah Perbaikan

| Kondisi File Existing (`rewrite=False`) | Sebelum Perbaikan | Sesudah Perbaikan |
|---|---|---|
| Naskah `# Bab 1\n\nTODO: tulis bab`, State `# State\n\nBelum ditulis` | Dianggap ada (`skipped`), `run_batch()` lanjut ke bab berikutnya | Mengembalikan `incomplete`, AGY tidak dipanggil, `run_batch()` berhenti (`rc=1`) |
| Naskah valid, State hanya `TBD` | Dianggap ada (`skipped`), lolos validasi | Mengembalikan `incomplete`, AGY tidak dipanggil, `run_batch()` berhenti |
| Naskah hanya `<!-- kosong -->`, State valid | Dianggap ada (`skipped`), lolos validasi | Mengembalikan `incomplete`, AGY tidak dipanggil, `run_batch()` berhenti |
| Naskah `# Bab 1\n\n...TODO dalam kalimat biasa...`, State valid | `skipped` | Tetap `skipped` (tidak salah ditolak) |

---

## 3. Hasil Pengujian & Kompilasi

- **`python -m py_compile novel_engine/*.py tests/*.py novel.py`**: lulus (exit code `0`).
- **`python -m unittest discover tests`**: **75/75 tes lulus** (`Ran 75 tests in 1.416s — OK`).
  - `tests/test_agy.py`: 14 tes (8 lama + 6 baru) — semua lulus.
  - `tests/test_character_context.py`: 15 tes — semua lulus.
  - `tests/test_engine.py`: 46 tes — semua lulus.

---

## 4. Konfirmasi Integritas Cerita Utama

Pemeriksaan `git status --short` menunjukkan hanya `novel_engine/agy.py` dan `tests/test_agy.py` yang dimodifikasi (ditambah laporan ini). Tidak ada perubahan pada `stories/gang-yang-hilang-dari-peta/`, `stories/arman-mira/`, blueprint, canon, outline, atau naskah yang sudah ada.
