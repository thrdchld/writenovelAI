# Antarmuka Python Agent (JSON CLI)

Dokumen ini menjelaskan kontrak dan cara penggunaan antarmuka Python standar (`novel_engine.agent`) agar AI agent apa pun (ChatGPT, Gemini, Claude, atau coding agent dengan akses terminal dan Python) dapat meminta data cerita, konteks temporal, pencarian sumber, dan validasi bab secara berulang dan deterministik tanpa bergantung pada AGY.

## 1. Cara Menjalankan

Antarmuka dapat dipanggil melalui `novel.py` maupun langsung sebagai modul Python:

```bash
python novel.py --story SLUG agent <operasi> [argumen...]
# atau
python -m novel_engine.agent --story SLUG <operasi> [argumen...]
```

Parameter `--story SLUG` dapat diletakkan sebelum maupun sesudah nama operasi. Jika hanya ada satu proyek di folder `stories/`, `--story` bersifat opsional.

## 2. Kontrak Keluaran JSON

Seluruh operasi antarmuka agent mengikuti aturan ketat:
- **`stdout`** hanya berisi satu objek JSON valid (UTF-8).
- **`stderr`** digunakan khusus untuk pesan diagnostik bila terjadi kesalahan tak terduga.
- **Exit code `0`** untuk eksekusi sukses (`"ok": true`), **`2`** untuk argumen tidak valid (`INVALID_ARGUMENTS`), dan **`1`** untuk kegagalan operasional lainnya (`"ok": false`).
- **Read-only & aman:** Tidak ada operasi yang menimpa manuskrip, tidak ada eksekusi shell arbitrer, dan semua akses berkas dibatasi di dalam folder cerita yang dipilih.

### Envelope Sukses (`schema_version: 1`)

```json
{
  "schema_version": 1,
  "ok": true,
  "operation": "context",
  "story": "gang-yang-hilang-dari-peta",
  "data": {},
  "sources": [
    "stories/gang-yang-hilang-dari-peta/00-premise.md"
  ]
}
```

### Envelope Gagal (`schema_version: 1`)

```json
{
  "schema_version": 1,
  "ok": false,
  "operation": "context",
  "error": {
    "code": "CHAPTER_NOT_FOUND",
    "message": "Bab 99 tidak ditemukan dalam outline/blueprint cerita 'gang-yang-hilang-dari-peta'."
  }
}
```

### Daftar Kode Error

| Kode Error | Exit Code | Arti |
| --- | --- | --- |
| `INVALID_ARGUMENTS` | `2` | Argumen CLI tidak valid, operasi tidak dikenal, nomor bab `< 1`, `--scope` tidak valid, atau nilai `--limit` di luar batas (`1..200`). |
| `STORY_NOT_FOUND` | `1` | Folder cerita tidak ditemukan di `stories/`. |
| `STORY_AMBIGUOUS` | `1` | Terdapat lebih dari satu proyek di `stories/` dan `--story` belum ditentukan. |
| `PATH_OUT_OF_BOUNDS` | `1` | Slug cerita mencoba keluar dari direktori `stories/` (misalnya `../`). |
| `CHAPTER_NOT_FOUND` | `1` | Nomor bab tidak terdaftar di outline, blueprint, manuskrip, maupun State Update cerita. |
| `CHARACTER_NOT_FOUND` | `1` | Karakter tidak ditemukan di `02-characters.md`. |
| `CHARACTER_AMBIGUOUS` | `1` | Nama parsial cocok dengan lebih dari satu karakter; gunakan nama lengkap. |
| `INTERNAL_ERROR` | `1` | Kesalahan runtime tak terduga (detail dicatat ke `stderr`). |

## 3. Daftar Operasi dan Contoh

### 3.1 `status` — Status Proyek & Progres Bab

```bash
python novel.py --story gang-yang-hilang-dari-peta agent status
```

Mengembalikan struktur berkas inti, direktori cerita, daftar bab beserta kelengkapan (`in_outline`, `has_blueprint`, `has_manuscript`, `has_state_update`), dan ringkasan `progress`.

### 3.2 `context` — Paket Konteks Temporal untuk Bab Tertentu

Memuat dokumen inti, blueprint bab target, pemisahan batas pengetahuan karakter/pembaca/penulis, naskah bab sebelumnya (`N-1`), serta hanya State Update dan kontinuitas bernomor dengan nomor bab `< N`. State Update bab `>= N` tidak pernah dimasukkan.

```bash
python novel.py --story gang-yang-hilang-dari-peta agent context 2
# Opsional menandai mode rewrite (tetap read-only):
python novel.py --story gang-yang-hilang-dari-peta agent context 2 --rewrite
```

**Penanganan berkas `continuity/` tanpa nomor bab:**
- Berkas kontinuitas bernomor bab (`chapter-NNN.md`, `NNN < N`) ditandai `temporal_status: "verified_before_chapter"`, `temporal_boundary_verified: true`, dan `safe_as_prior_fact: true`.
- Berkas kontinuitas **tanpa nomor bab** tetap disertakan agar sumber tidak hilang, tetapi ditandai secara eksplisit dengan `temporal_status: "unverified_temporal"`, `temporal_boundary_verified: false`, `safe_as_prior_fact: false`, serta `warning` dan `agent_guidance`. AI tidak boleh memperlakukannya secara otomatis sebagai fakta yang sudah diketahui pada bab sebelumnya.
- Ringkasan statusnya tersedia di `data.temporal_boundary.has_unverified_continuity` dan `data.temporal_boundary.unverified_continuity_sources`.

### 3.3 `character` — Profil Karakter & Pemisahan Pengetahuan

```bash
python novel.py --story gang-yang-hilang-dari-peta agent character "Salma"
```

Field utama pada `data`:
- `name`, `header`, `blueprint_appearances`, `raw_profile`
- `character_known`: `public_profile` dan `character_secrets` (informasi publik & rahasia pribadi karakter)
- `author_known`: `author_secrets` (`Rahasia Penulis` / `Author-Only`), `unclassified_profile_notes`, `needs_review`, serta `decision_log_mentions` yang dipilah berdasarkan klasifikasi kerahasiaan.

### 3.4 `timeline` — Kronologi Terekam Sebelum Bab Tertentu

Mengekstrak metadata waktu, lokasi, POV, dan peristiwa secara verbatim dari `state-updates/` dan `continuity/` tanpa mengarang tanggal atau kejadian baru.

```bash
python novel.py --story gang-yang-hilang-dari-peta agent timeline --before 3
```

Jika `--before` tidak diisi, seluruh kronologi terekam akan dikembalikan. Jika sumber tidak mencantumkan waktu, `recorded_time` bernilai `null`. Berkas `continuity/` tanpa nomor bab tetap disertakan dengan status `temporal_status: "unverified_temporal"` dan `safe_as_prior_fact: false` (beserta ringkasan di `data.temporal_boundary`).

### 3.5 `search` — Pencarian Terbatas & Terklasifikasi Temporal

```bash
# Pencarian kronologis ketat sebelum Bab 3 (default --scope chronological saat --before dipakai):
python novel.py --story gang-yang-hilang-dari-peta agent search "Gang Kenari" --before 3 --limit 10

# Pencarian dokumen global (outline, decision log, profil karakter, continuity umum):
python novel.py --story gang-yang-hilang-dari-peta agent search "brankas" --scope global --limit 10

# Pencarian gabungan (dokumen bab < N + dokumen global dengan peringatan risiko masa depan):
python novel.py --story gang-yang-hilang-dari-peta agent search "Gang Kenari" --before 3 --scope all
```

Aturan `scope` dan batas temporal:
- `--scope chronological` (default otomatis jika `--before N` dipakai): hanya memindai dokumen bernomor bab (`manuscript/`, `state-updates/`, `blueprint/`, `continuity/` bernomor) dengan batas eksklusif `max_chapter < N`. Dokumen global dan berkas tanpa nomor bab dikecualikan dan dicatat di `excluded_unbounded_files`. `all_results_temporally_bounded` bernilai `true`.
- `--scope global`: memindai dokumen global/tanpa nomor bab (`global_outline`, `global_decision_log`, `global_character_profile`, `global_core`, `unnumbered_continuity`, `unnumbered_document`). Setiap hasil ditandai `temporal_status: "unverified_temporal"` dan `may_contain_future_info: true`, serta `all_results_temporally_bounded: false` dengan `temporal_warning`.
- `--scope all` (default saat `--before` tidak dipakai): memindai keduanya; jika `--before N` turut diberikan, dokumen bernomor dibatasi `< N` sementara dokumen global/tanpa nomor bab tetap ditandai `may_contain_future_info: true` dan `temporal_guarantee: "partial_contains_unbounded_documents"`.

### 3.6 `validate` — Validasi Terstruktur Bab & Klasifikasi Konflik Sumber

Memeriksa keberadaan dan keutuhan isi (bukan placeholder) pada manuskrip, State Update, blueprint, serta menggabungkan temuan deterministik (`deterministic_audit`) dan klasifikasi konflik sumber (`detect_source_conflicts`).

```bash
python novel.py --story gang-yang-hilang-dari-peta agent validate 2
```

Aturan klasifikasi konflik deterministik:
- **Pemblokir (`blocking: true`, membuat `valid: false` dan `validation_status: "invalid"`):**
  - `MANUSCRIPT_MISSING`, `MANUSCRIPT_PLACEHOLDER`, `STATE_UPDATE_MISSING`, `STATE_UPDATE_PLACEHOLDER`
  - `BLUEPRINT_MISSING`, `ORPHAN_STATE_CONFLICT`, `PREVIOUS_STATE_UPDATE_MISSING` (rantai kontinuitas kanon bab sebelumnya terputus)
  - Temuan audit `CRITICAL` / `HIGH` (`OUTLINE_MISSING`, `DUPLICATE_OUTLINE_NUMBER`)
- **Peringatan non-pemblokir (`blocking: false`, dapat tetap `valid: true` dengan `validation_status: "valid_with_warnings"`):**
  - `PREVIOUS_MANUSCRIPT_MISSING` (naskah bab sebelumnya belum ada, tetapi State Update bab sebelumnya dan berkas bab target lengkap)
  - Temuan audit `MEDIUM` / `LOW` (`ORPHAN_BLUEPRINT`, `CHAPTER_GAP`)

Field utama pada `data`:
- `chapter`, `valid` (`true`/`false`), `validation_status` (`"valid"` | `"valid_with_warnings"` | `"invalid"`), `status_reason` (penjelasan alasan status)
- `checks`, `blocking_findings`, `warning_findings`, `findings`, `conflicts`, `classified_conflicts`, `summary`

## 4. Pola Interaksi Bertahap bagi AI Agent

1. **Cek peta proyek:** Jalankan `agent status` untuk mengetahui bab mana yang sudah ditulis dan dokumen inti apa saja yang tersedia.
2. **Ambil konteks bab target:** Jalankan `agent context N` untuk memperoleh blueprint, batas pengetahuan karakter/pembaca, serta State Update sebelum Bab `N`. Periksa `temporal_boundary.has_unverified_continuity` bila ada berkas kontinuitas tanpa nomor bab.
3. **Minta detail tambahan saat berpikir:**
   - Profil dan batas rahasia tokoh: `agent character "<Nama>"`.
   - Urutan kejadian terekam sebelum Bab `N`: `agent timeline --before N`.
   - Pencarian fakta kronologis aman: `agent search "<kata>" --before N` (otomatis `--scope chronological`).
   - Pencarian dokumen global (outline/decision log/karakter) bila memang diperlukan sebagai penulis: `agent search "<kata>" --scope global`.
4. **Tulis naskah dan State Update** sesuai aturan cerita.
5. **Validasi hasil:** Jalankan `agent validate N` dan periksa `valid`, `validation_status`, `status_reason`, serta `blocking_findings` sebelum melanjutkan ke Bab `N+1`.
