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
| `INVALID_ARGUMENTS` | `2` | Argumen CLI tidak valid, operasi tidak dikenal, nomor bab `< 1`, atau nilai `--limit` di luar batas (`1..200`). |
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

Contoh keluaran:

```json
{
  "schema_version": 1,
  "ok": true,
  "operation": "status",
  "story": "gang-yang-hilang-dari-peta",
  "data": {
    "story": "gang-yang-hilang-dari-peta",
    "story_path": "stories/gang-yang-hilang-dari-peta",
    "structure": {
      "core_files": {
        "00-premise.md": { "exists": true, "path": "stories/gang-yang-hilang-dari-peta/00-premise.md" }
      },
      "directories": {
        "blueprint": true,
        "manuscript": true,
        "state-updates": true,
        "continuity": false,
        "audits": false
      }
    },
    "chapters": [
      {
        "chapter": 1,
        "in_outline": true,
        "has_blueprint": true,
        "has_manuscript": true,
        "has_state_update": true,
        "manuscript_path": "stories/gang-yang-hilang-dari-peta/manuscript/chapter-001.md",
        "state_update_path": "stories/gang-yang-hilang-dari-peta/state-updates/chapter-001.md"
      }
    ],
    "progress": {
      "total_chapters": 1,
      "manuscripts_written": 1,
      "state_updates_written": 1,
      "blueprints_available": 1,
      "completed_chapters": 1,
      "completion_ratio": 1.0
    }
  },
  "sources": [
    "stories/gang-yang-hilang-dari-peta/00-premise.md"
  ]
}
```

### 3.2 `context` — Paket Konteks Temporal untuk Bab Tertentu

Memuat dokumen inti, blueprint bab target, pemisahan batas pengetahuan karakter/pembaca/penulis, naskah bab sebelumnya (`N-1`), serta hanya State Update dan kontinuitas dengan nomor bab `< N`. State Update bab `>= N` tidak pernah dimasukkan.

```bash
python novel.py --story gang-yang-hilang-dari-peta agent context 2
# Opsional menandai mode rewrite (tetap read-only):
python novel.py --story gang-yang-hilang-dari-peta agent context 2 --rewrite
```

Field utama pada `data`:
- `chapter`, `mode`, `target_manuscript`, `target_state_update`, `has_manuscript`, `has_state_update`, `has_blueprint`
- `temporal_boundary`: menegaskan `excludes_current_and_future_state_updates: true`
- `conflicts`: peringatan konflik sumber dari pemeriksa deterministik
- `core_documents`, `blueprint`, `character_boundaries`, `canon_classification`
- `previous_state_updates`, `continuity_notes`, `previous_manuscript`
- `rendered_context`: paket konteks Markdown lengkap hasil `build_context`

### 3.3 `character` — Profil Karakter & Pemisahan Pengetahuan

```bash
python novel.py --story gang-yang-hilang-dari-peta agent character "Salma"
```

Field utama pada `data`:
- `name`, `header`, `blueprint_appearances`, `raw_profile`
- `character_known`: `public_profile` dan `character_secrets` (informasi publik & rahasia pribadi karakter)
- `author_known`: `author_secrets` (`Rahasia Penulis` / `Author-Only`), `unclassified_profile_notes`, `needs_review`, serta `decision_log_mentions` yang sudah dipilah berdasarkan klasifikasi kerahasiaan.

### 3.4 `timeline` — Kronologi Terekam Sebelum Bab Tertentu

Mengekstrak metadata waktu, lokasi, POV, dan peristiwa secara verbatim dari `state-updates/` dan `continuity/` tanpa mengarang tanggal atau kejadian baru.

```bash
python novel.py --story gang-yang-hilang-dari-peta agent timeline --before 3
```

Jika `--before` tidak diisi, seluruh kronologi terekam akan dikembalikan. Jika sumber tidak mencantumkan waktu, `recorded_time` bernilai `null`.

### 3.5 `search` — Pencarian Terbatas di Folder Cerita

```bash
python novel.py --story gang-yang-hilang-dari-peta agent search "Gang Kenari" --limit 10 --before 3
```

Field utama pada `data`:
- `query`, `before_chapter`, `limit`, `total_matches`, `returned_matches`, `truncated`
- `matches`: daftar `{ "file", "line", "snippet" }` yang seluruhnya berada di dalam folder cerita (file di luar folder cerita dan folder `workbench/` tidak pernah dipindai).

### 3.6 `validate` — Validasi Terstruktur Bab

Memeriksa keberadaan dan keutuhan isi (bukan placeholder) pada manuskrip, State Update, blueprint, serta menggabungkan temuan deterministik (`deterministic_audit`) dan konflik sumber (`detect_source_conflicts`).

```bash
python novel.py --story gang-yang-hilang-dari-peta agent validate 1
```

Field utama pada `data`:
- `chapter`, `valid` (`true`/`false`), `checks` (`manuscript_exists`, `manuscript_meaningful`, `state_update_exists`, `state_update_meaningful`, `blueprint_exists`)
- `findings`: daftar objek `{ "severity", "code", "message", "source" }`
- `conflicts`, `summary` (`total_findings`, `by_severity`)

## 4. Pola Interaksi Bertahap bagi AI Agent

Alih-alih memuat seluruh repository ke dalam satu prompt besar, AI agent disarankan bekerja dalam siklus permintaan terarah:

1. **Cek peta proyek:** Jalankan `agent status` untuk mengetahui bab mana yang sudah ditulis, mana yang siap ditulis, dan dokumen inti apa saja yang tersedia.
2. **Ambil konteks bab target:** Jalankan `agent context N` untuk memperoleh blueprint, batas pengetahuan karakter/pembaca, serta State Update sebelum Bab `N`.
3. **Minta detail tambahan saat berpikir:**
   - Butuh memastikan rahasia tokoh tertentu tanpa membocorkan rahasia penulis? Panggil `agent character "<Nama>"`.
   - Butuh mengecek urutan kejadian sebelum bab target? Panggil `agent timeline --before N`.
   - Butuh melacak penyebutan istilah, benda, atau lokasi tertentu tanpa membaca bab masa depan? Panggil `agent search "<kata>" --before N --limit 15`.
4. **Tulis naskah dan State Update** sesuai aturan cerita.
5. **Validasi hasil:** Jalankan `agent validate N` untuk memastikan manuskrip, State Update, dan blueprint lengkap serta bebas placeholder sebelum melanjutkan ke Bab `N+1`.
