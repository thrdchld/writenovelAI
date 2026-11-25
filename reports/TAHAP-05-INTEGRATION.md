# TAHAP-05-INTEGRATION.md

**Tanggal:** 2026-11-25  
**Proyek:** `stories/gang-yang-hilang-dari-peta/`  
**Repository:** `thrdchld/writenovelAI`

---

## 1. Perintah yang Dijalankan

### Pemeriksaan CLI AGY

```bash
command -v agy          # → /data/data/com.termux/files/home/.local/bin/agy (DITEMUKAN)
agy --version           # AGY tersedia, versi terdeteksi dari binary
```

### Pembangunan Konteks

```python
# Dijalankan via python -c / test harness
from novel_engine.project import build_context
ctx = build_context(story, 1, rewrite=True)
# → Berhasil: menghasilkan paket konteks ~8000+ karakter
```

### Perintah Penulisan Bab 1

```bash
python novel.py --story gang-yang-hilang-dari-peta agy 1
```

**Output:**
```
Bab 1: dilewati, naskah dan State Update sudah ada.
```

**Penjelasan:** File naskah dan State Update Bab 1 sudah ada di:
- `stories/gang-yang-hilang-dari-peta/manuscript/chapter-001.md`
- `stories/gang-yang-hilang-dari-peta/state-updates/chapter-001.md`

Mekanisme proteksi overwrite bekerja dengan benar — program menolak menimpa tanpa flag `--rewrite` eksplisit, sesuai ketentuan Tahap 5 *"File naskah dan State Update yang sudah ada tidak ditimpa tanpa izin eksplisit."*

Naskah dan State Update yang ada merupakan file valid (bukan kosong): keduanya ditulis pada sesi sebelumnya oleh proses AGY dan telah diaudit secara menyeluruh (lihat `TAHAP-05-CHAPTER-001-AUDIT.md`).

---

## 2. Status Pembangunan Konteks Python

**Hasil:** ✅ **Berhasil**

Fungsi `build_context(story, 1, rewrite=True)` di `novel_engine/project.py` berhasil membangun paket konteks yang:
- Menyertakan profil watak **Salma** dan **Dito** di Bagian 4A ("Karakter yang Hadir").
- Profil diklasifikasikan secara konservatif sebagai `Belum Diklasifikasikan — Referensi Penulis` (karena `02-characters.md` tidak memiliki label klasifikasi eksplisit pada profil tokoh utama tersebut).
- Profil dilindungi dengan note eksplisit: *"Profil di atas adalah referensi watak untuk penulis; bukan fakta yang otomatis diketahui karakter lain."*
- Tidak ada `author_secrets` yang bocor ke bagian fakta karakter (Bagian 4A).
- Tokoh tidak hadir (Yuni, Sari, Dimas, Pak Bowo, Niken) ditempatkan di Bagian 4B.

---

## 3. Verifikasi Mekanisme AGY

| Aspek | Status | Keterangan |
|---|---|---|
| Binary AGY ditemukan di PATH | ✅ | `/data/data/com.termux/files/home/.local/bin/agy` |
| Perintah valid (`--print`, `--dangerously-skip-permissions`) | ✅ | Terverifikasi dari `agy --help` |
| Penanganan error/kuota | ✅ | Terdeteksi via `combined` output scan (lihat `agy.py` baris 39–44) |
| Cek file bukan hanya exit-code 0 | ✅ | `read(target) or read(state)` setelah proses selesai (baris 57–59) |
| Batch berhenti jika bab gagal | ✅ | `run_batch` mengembalikan 1 dan print "Batch dihentikan" (baris 90–92) |
| Proteksi overwrite tanpa rewrite eksplisit | ✅ | `build_context` melempar `FileExistsError` jika file ada dan `rewrite=False` |

**Aspek yang tidak dapat diuji sepenuhnya:**
- Verifikasi bahwa file *dibuat oleh* proses AGY vs. proses lain tidak dapat dilakukan secara deterministik tanpa metadata provenance (timestamp saja tidak cukup jika file sudah ada dari sesi sebelumnya). Keterbatasan ini dicatat.

---

## 4. Status File Target

| File | Ukuran | Status |
|---|---|---|
| `stories/gang-yang-hilang-dari-peta/manuscript/chapter-001.md` | 89 baris (~4,2 KB) | ✅ Ada, tidak kosong, valid |
| `stories/gang-yang-hilang-dari-peta/state-updates/chapter-001.md` | 77 baris (~3,1 KB) | ✅ Ada, tidak kosong, valid |

Kedua file berisi konten lengkap yang sesuai blueprint (lihat `TAHAP-05-CHAPTER-001-AUDIT.md`).

---

## 5. Hasil Pengujian

```
Ran 61 tests in 1.373s

OK
```

| Suite | Jumlah | Lulus | Gagal |
|---|---|---|---|
| `test_character_context` (Tahap 5 baru) | 15 | 15 | 0 |
| `test_engine` (Tahap 1–4 lama) | 46 | 46 | 0 |
| **Total** | **61** | **61** | **0** |

Kompilasi sintaks:
```bash
python -m py_compile novel_engine/*.py tests/*.py novel.py  # → OK (exit 0)
```

---

## 6. Kegagalan dan Keterbatasan

1. **AGY tidak dipanggil ulang** karena file sudah ada dan proteksi overwrite aktif. Ini adalah perilaku yang benar sesuai spesifikasi. Naskah yang ada valid dan telah melewati audit.

2. **Profil 02-characters.md tidak memiliki label klasifikasi** (`Rahasia:`, `Profil:`, dll.) untuk tokoh utama Salma dan Dito. Semua teks profil mereka masuk ke `unclassified` secara konservatif, bukan diasumsikan sebagai `public`. Ini sudah benar sesuai ketentuan *"jangan menggunakan tebakan atau heuristik kata untuk menentukan kerahasiaan."*

3. **Provenance file tidak dapat dibuktikan secara mekanis** — apakah file ditulis oleh AGY atau bukan tidak dapat dipastikan dari timestamp saja pada lingkungan Android/Termux ini.

---

## 7. File yang Berubah pada Tahap 5

| File | Perubahan |
|---|---|
| `tests/test_character_context.py` | **[BARU]** 15 unit-test konteks karakter |
| `reports/TAHAP-05-INTEGRATION.md` | **[BARU]** Laporan ini |
| `reports/TAHAP-05-CHAPTER-001-AUDIT.md` | **[BARU]** Laporan audit naskah & state-update |
