# LAPORAN AUDIT MENYELURUH REPOSITORY writenovelAI (TAHAP 1)

- **Tanggal Audit:** 24 November 2026
- **Auditor:** AGY (Google DeepMind Antigravity CLI)
- **Target Repository:** `thrdchld/writenovelAI`
- **Branch Aktif:** `main`
- **Commit Basis:** `2e73c7a` (*Fix instruction document line breaks*)
- **Status Audit:** Selesai (Non-destruktif: tidak ada kode atau file cerita yang diubah/dihapus)

---

## 1. Kondisi Aktual Repository dan Git

Pemeriksaan status Git dan remote origin menunjukkan kondisi bersih dan sinkron:
- **Branch:** `main`
- **Remote Origin:** `https://github.com/thrdchld/writenovelAI`
- **Working Tree:** Bersih (*clean*), tidak ada perubahan tertunda (*uncommitted*) atau file tak terlacak (*untracked*).
- **Status Sinkronisasi:** Identik dengan `origin/main` (`git fetch origin main --dry-run` menunjukkan 0 commit masuk dan 0 commit keluar).

---

## 2. Hasil Pengujian Aktual

Seluruh pengujian teknis yang tersedia diuji langsung di lingkungan runtime Android / Termux dengan Python 3.14.6:

### A. Kompilasi Python (`py_compile`)
```bash
python3 -m py_compile novel.py novel_engine/*.py tests/*.py
```
- **Hasil:** Sukses tanpa peringatan maupun syntax error (Exit code: `0`).

### B. Unit Test Inti (`tests/test_engine.py`)
```bash
python3 -m unittest discover -s tests -v
```
- **Hasil:** 6 pengujian berhasil dijalankan (Exit code: `0`):
```text
test_audit_detects_duplicate_outline_number (test_engine.EngineTests.test_audit_detects_duplicate_outline_number) ... ok
test_audit_detects_missing_blueprint (test_engine.EngineTests.test_audit_detects_missing_blueprint) ... ok
test_chapter_numbers (test_engine.EngineTests.test_chapter_numbers) ... ok
test_combined_blueprint_split (test_engine.EngineTests.test_combined_blueprint_split) ... ok
test_context_does_not_include_future_state (test_engine.EngineTests.test_context_does_not_include_future_state) ... ok
test_context_refuses_to_overwrite_orphan_state (test_engine.EngineTests.test_context_refuses_to_overwrite_orphan_state) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.063s
OK
```

### C. Pengujian CLI pada Proyek `gang-yang-hilang-dari-peta`
```bash
python3 novel.py --story gang-yang-hilang-dari-peta status
```
- **Hasil:** Terdeteksi 30 bab (Bab 001 – 030). Progres naskah 0/30. Status seluruhnya `BELUM DITULIS | STATE KOSONG | BLUEPRINT`. (Exit code: `0`).

```bash
python3 novel.py --story gang-yang-hilang-dari-peta audit
```
- **Hasil:** "Tidak ada masalah struktural sederhana yang terdeteksi." (Exit code: `0`).

### D. Pengujian CLI pada Proyek `arman-mira`
```bash
python3 novel.py --story arman-mira audit
```
- **Hasil:** Terdeteksi 5 temuan struktural kategori `HIGH`:
```text
[HIGH] BLUEPRINT_MISSING: Bab 1: ada di outline tetapi blueprint tidak ditemukan.
[HIGH] BLUEPRINT_MISSING: Bab 6: ada di outline tetapi blueprint tidak ditemukan.
[HIGH] BLUEPRINT_MISSING: Bab 7: ada di outline tetapi blueprint tidak ditemukan.
[HIGH] BLUEPRINT_MISSING: Bab 8: ada di outline tetapi blueprint tidak ditemukan.
[HIGH] BLUEPRINT_MISSING: Bab 9: ada di outline tetapi blueprint tidak ditemukan.
```
- **Catatan:** Exit code tetap `0` karena audit mengembalikan status gagal (`1`) hanya jika ada temuan berkategori `CRITICAL`.

### E. Pengujian Posisi Argumen CLI
```bash
python3 novel.py status --story gang-yang-hilang-dari-peta
```
- **Hasil:** Gagal dengan `novel.py: error: unrecognized arguments: --story gang-yang-hilang-dari-peta` (Exit code: `2`). Argumen `--story` wajib diletakkan sebelum subperintah.

---

## 3. Struktur dan Fungsi File Utama

| Berkas / Modul | Fungsi Aktual Berdasarkan Kode | Status & Temuan |
|---|---|---|
| `novel.py` | Pintu masuk CLI tunggal; memanggil `novel_engine.cli.main()`. | Berfungsi normal. |
| `novel_engine/project.py` | Mengelola konstanta path, pembacaan berkas aman, resolusi proyek, pembacaan blueprint, outline, penyusunan memori, dan pembuatan paket konteks bab. | Berfungsi, namun terdapat risiko pada filter memori folder `continuity/` dan ukuran konteks yang sangat besar. |
| `novel_engine/audit.py` | Pemeriksaan deterministik struktur bab (duplikasi nomor outline, celah bab, ketiadaan blueprint, inkonsistensi naskah vs State Update) serta generator prompt audit naratif AI. | Berfungsi normal; sesuai dengan rancangan. |
| `novel_engine/agy.py` | Adapter untuk memanggil CLI `agy` secara batch/sekuensial. | Belum teruji unit test; memiliki kelemahan kritis pada perizinan subproses AGY. |
| `novel_engine/cli.py` | Pengurai argumen `argparse` dan antarmuka menu interaktif terminal. | Berfungsi; memiliki batasan kaku pada urutan argumen dan penanganan *orphan state*. |
| `novel_engine/github_bot.py` | Handler webhook issue comment GitHub untuk status, audit outline, dan penulisan bab via endpoint OpenAI-compatible. | Berfungsi secara sintaksis, namun belum memiliki unit test dan rentan terhadap JSON parse error. |
| `docs/*.md` (8 berkas) | Metodologi kerja penulisan, kontrak operasional AI, standar prosa, kontinuitas, audit, ruang kerja GitHub, dan arsitektur engine. | Lengkap dan rapi. Menjadi acuan prinsip kerja sistem. |
| `templates/*.md` (6 berkas) | Template markdown untuk audit, blueprint, konteks, decision log, readme, dan state update. | Dokumen statis; tidak terikat langsung pada pemanggilan kode Python. |
| `stories/gang-yang-hilang-dari-peta/` | Proyek novel utama 30 bab (berisi premis, konsep, karakter, dunia, outline, decision log, dan blueprint). | Memiliki inkonsistensi dan tumpang tindih blueprint antara file Bab 7–14 dan Bab 7–30. |
| `stories/arman-mira/` | Proyek novel uji/sampel parsial (Bab 2–5). | Tidak lengkap (hilang dokumen 01, 02, 03, serta Bab 1 dan 6–9); menimbulkan duplikasi dengan `examples/arman-mira.md`. |
| `.github/workflows/python-check.yml` | Workflow GitHub Actions CI untuk kompilasi Python, unit test, dan audit seluruh cerita. | Berfungsi baik di CI; tidak membutuhkan secret eksternal. |
| `.github/workflows/novel-bot.yml` | Workflow GitHub Actions untuk menjalankan bot komentar issue. | Memerlukan secrets `NOVEL_AI_API_KEY` dan variables `NOVEL_AI_MODEL`. |

---

## 4. Analisis Alur Kerja dan Potensi Masalah

### A. Alur Pengambilan Konteks Cerita (`build_context`)
1. **Perlindungan Data Masa Depan:**
   - State Update masa depan (`state-updates/chapter-XXX.md`) terbukti berhasil dicegah masuk ke bab sebelum targetnya lewat logika `n < before_chapter`.
2. **Risiko Kebocoran Informasi via `continuity/`:**
   - Di `novel_engine/project.py:103`, pemindaian memeriksa `before_chapter is None or n is None or n < before_chapter`.
   - File catatan umum seperti `continuity/timeline.md` atau `continuity/character-knowledge.md` (sebagaimana diinstruksikan dalam `docs/03-continuity.md`) tidak memiliki nomor bab (`n is None`).
   - Akibatnya, `n is None` selalu bernilai `True`. Jika file-file ini dibuat, seluruh catatan timeline sampai akhir cerita akan bocor masuk ke dalam konteks Bab 1.
3. **Pembengkakan Ukuran Konteks (*Context Bloat*):**
   - Paket konteks Bab 1 yang dihasilkan `build_context` berukuran **52.699 karakter (772 baris / ~11.000–13.000 token)**.
   - Konteks ini menggabungkan `AI_INSTRUCTIONS.md`, 4 panduan metodologi `docs/`, `00-premise`, `01-concept`, `02-characters`, `03-world-and-rules`, `04-story-outline`, `05-decision-log`, dan blueprint bab target.
   - Karena `04-story-outline.md` menyertakan tabel 30 bab lengkap dan 10 butir penyelesaian misteri (*cause-effect chain*), AI penulis menerima seluruh spoiler cerita saat menulis bab pembuka.

### B. Alur Audit Outline dan Kontinuitas
1. **Audit Deterministik Python:**
   - Sangat cepat dan andal dalam memeriksa inkonsistensi file fisik, celah nomor bab, dan kelengkapan berpasangan antara naskah dan State Update.
2. **Audit Naratif AI:**
   - Melalui `novel.py audit --prompt`, sistem menyusun paket prompt lengkap ke `workbench/outline-audit-prompt.md`. AI dapat mengevaluasi kewajaran sebab-akibat, motivasi, dan perkembangan karakter tanpa mengubah dokumen kanon.

### C. Alur Penulisan Satu Bab dan Multi-Bab
1. **Penulisan Manual / Semi-Otomatis (Rekomendasi Utama):**
   - Menjalankan `python novel.py --story gang-yang-hilang-dari-peta context 1`, membaca paket konteks, menuliskan naskah ke `manuscript/chapter-001.md`, menuliskan State Update ke `state-updates/chapter-001.md`, lalu memverifikasinya dengan `verify 1`. Alur ini aman dan terkendali.
2. **Penulisan Batch Otomatis via AGY (`novel.py agy 1-5`):**
   - Memiliki kelemahan kritis: `agy.py` mengeksekusi binary `agy` dalam subproses non-interaktif tanpa parameter persetujuan izin (`--dangerously-skip-permissions`).
   - Selain itu, `agy.py` tidak mengambil teks prosa dari output JSON respons terminal, melainkan mengharapkan AGY menulis file langsung ke disk. Jika subproses tidak memiliki izin eksekusi tool penulisan berkas, bab akan selalu gagal dengan status `incomplete`.
3. **Penulisan via GitHub Issue Bot (`github_bot.py`):**
   - Jika `verify(story, number)` gagal (misalnya karena blueprint hilang atau format tidak sesuai), kode langsung mengeksekusi `target.unlink()` dan `state.unlink()`. Naskah prosa hasil generasi AI dihapus permanen tanpa backup draft.
   - Batch penulisan melakukan `git commit` dan `git push` setelah setiap satu bab. Jika push gagal di bab ketiga, status repo di remote berada dalam kondisi parsial.

---

## 5. Klasifikasi Masalah yang Ditemukan

### Kritis (Critical)
1. **Konflik Data Blueprint pada `gang-yang-hilang-dari-peta`:**
   - File `stories/gang-yang-hilang-dari-peta/blueprint/chapter-007.md` sampai `chapter-014.md` bertentangan isi dan formatnya dengan entri Bab 7–14 di dalam `chapter-007-to-030.md`.
   - Kode di `novel_engine/project.py` memprioritaskan file individual dan membuang entri Bab 7–14 dari file gabungan. Sementara itu, `blueprint/README.md` dan outline hanya menautkan anchor ke file gabungan.
2. **Kelemahan Eksekusi Subproses pada `novel_engine/agy.py`:**
   - Pemanggilan `agy -p` tanpa `--dangerously-skip-permissions` berisiko macet pada pengecekan tool permission. Kode tidak memiliki mekanisme fallback untuk menulis file jika teks hanya dikembalikan pada JSON stdout.

### Tinggi (High)
1. **Kebocoran Memori Temporal pada Folder `continuity/`:**
   - Logika `n is None` pada `novel_engine/project.py:103` menyebabkan catatan kontinuitas global tanpa nomor bab dimasukkan ke semua bab tanpa filter waktu.
2. **Beban Konteks Masif (52+ KB per Bab):**
   - Menyertakan seluruh dokumen instruksi dan outline makro 30 bab lengkap berpotensi memicu halusinasi dan kebocoran pengetahuan tokoh (*character knowledge leakage*).
3. **Ketiadaan Validasi JSON Mode pada `github_bot.py`:**
   - Panggilan API tidak menggunakan `response_format: {"type": "json_object"}` dan tidak membatasi `max_tokens`, rentan memicu kegagalan parsing JSON pada naskah panjang.

### Sedang (Medium)
1. **Jebakan Orphan State pada Menu Interaktif CLI:**
   - Menu CLI opsi 4 hanya menanyakan rewrite jika naskah ada. Jika hanya State Update yang ada (*orphan state*), CLI langsung gagal melempar `FileExistsError` tanpa opsi konfirmasi.
2. **Penghapusan File Tanpa Cadangan di `github_bot.py`:**
   - Kegagalan fungsi `verify` langsung menghapus file naskah dan State Update yang baru dibuat.
3. **Tingkat Kelulusan Audit CI Terlalu Longgar:**
   - Audit CI hanya gagal jika ada `CRITICAL`. Ketiadaan blueprint (`HIGH`) pada proyek `arman-mira` tetap menghasilkan status hijau.

### Rendah (Low)
1. **Urutan Argumen CLI `--story`:**
   - Parser mengharuskan `--story` sebelum subperintah.
2. **Duplikasi Proyek Uji `arman-mira`:**
   - Keberadaan folder `stories/arman-mira/` yang tidak lengkap mengganggu kenyamanan CLI (mengharuskan pemilihan manual) dan memicu peringatan audit terus-menerus.

---

## 6. Daftar File yang Berpotensi Tidak Terpakai atau Tumpang Tindih

1. `stories/gang-yang-hilang-dari-peta/blueprint/chapter-007.md` s.d. `chapter-014.md`
   - *Alasan:* Tumpang tindih dengan `chapter-007-to-030.md`. Menimbulkan ambiguitas sumber kebenaran (*single source of truth*).
2. `stories/arman-mira/`
   - *Alasan:* Duplikasi konsep dari `examples/arman-mira.md`. Merupakan proyek parsial yang belum lengkap (hanya Bab 2–5, tanpa dokumen konsep, karakter, dan aturan dunia).
3. `templates/*.md`
   - *Alasan:* Hanya dokumen referensi statis; belum diintegrasikan ke dalam automasi atau generator proyek baru.

---

## 7. Rekomendasi Urutan Perbaikan

1. **Harmonisasi Blueprint `gang-yang-hilang-dari-peta` (Prioritas Utama):**
   - Satukan pilihan: gunakan file individual penuh untuk 30 bab, atau pertahankan pembagian Bab 1–6 terpisah dan Bab 7–30 di file gabungan. Hapus file yang duplikat agar tidak ada kontradiksi.
2. **Penyempurnaan Modul `novel_engine/agy.py`:**
   - Tambahkan flag perizinan pada eksekusi AGY atau buat mekanisme penulisan berkas langsung dari hasil respons JSON.
   - Buat unit test komprehensif menggunakan mock subprocess untuk menguji `agy.py`.
3. **Perbaikan Logika Filter Memori Temporal:**
   - Sesuaikan `build_memory` di `novel_engine/project.py` agar berkas di `continuity/` hanya diikutsertakan jika memang dirancang aman dari spoiler masa depan.
4. **Optimasi Beban Konteks Bab:**
   - Batasi penyertaan outline masa depan pada paket konteks bab tertentu, atau pisahkan antara ringkasan makro dengan rincian bab masa depan.
5. **Relokasi atau Penyelesaian `stories/arman-mira`:**
   - Pindahkan folder sampel `arman-mira` ke luar direktori kerja utama (misal ke `tests/fixtures/`) agar perintah CLI dapat langsung mendeteksi `gang-yang-hilang-dari-peta` secara otomatis tanpa perlu argumen `--story`.

---

## 8. Kesimpulan Kesiapan

### Apakah repository siap masuk tahap pengujian penulisan bab pertama?

**STATUS: SIAP UNTUK PENULISAN MANUAL/SEMI-OTOMATIS, BELUM SIAP UNTUK OTOMASI PENUH AGY/BOT.**

- **Jalur Penulisan Terpandu (AI Kerja Langsung):** **SIAP.**
  Dokumen premis, konsep, karakter, aturan dunia, outline, dan blueprint Bab 1 (`chapter-001.md`) untuk novel `gang-yang-hilang-dari-peta` dalam kondisi lengkap, solid, dan lulus uji deterministik. Penulisan Bab 1 dapat segera dilakukan dengan memanfaatkan paket dari `python novel.py --story gang-yang-hilang-dari-peta context 1`.
- **Jalur Automasi Runner (`novel.py agy 1` / GitHub Issue Bot):** **BELUM SIAP.**
  Perlu perbaikan konfigurasi eksekusi perizinan tool pada `agy.py` dan perapian inkonsistensi blueprint Bab 7–14 sebelum sistem automasi batch dapat dijalankan dengan aman.
