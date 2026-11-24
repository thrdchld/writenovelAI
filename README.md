# writenovelAI

Kerangka kerja sekaligus workspace GitHub untuk mengembangkan dan menulis novel dengan bantuan AI secara terarah, konsisten, dan tetap nyaman dibaca.

Repository ini memiliki dua fungsi:
- **Knowledge base AI:** instruksi operasional, metode, standar, dan template yang harus dibaca AI sebelum bekerja.
- **Workspace penulisan:** tempat menyimpan premis, rancangan, blueprint, naskah per bab, kontinuitas, keputusan, dan audit setiap novel.

## Mulai dari premis

Pengguna cukup memberikan premis. AI bertanggung jawab mengembangkan konsep, karakter, dunia, alur, jumlah bab, blueprint, penulisan, kontinuitas, dan audit. Detail opsional boleh diberikan pengguna, tetapi bukan prasyarat.

**Instruksi wajib AI:** [AI_INSTRUCTIONS.md](AI_INSTRUCTIONS.md)

## Prinsip utama

1. Cerita lebih dulu, kalimat kemudian.
2. Blueprint mengendalikan logika, bukan setiap kalimat.
3. Tidak ada jumlah bab baku; jumlah mengikuti kebutuhan cerita.
4. Kronologi berbeda dari urutan penyajian.
5. Kontinuitas dicatat secara selektif dan berbasis fakta.
6. Audit harus menunjukkan bukti.
7. Perbaikan sekecil mungkin.
8. Kualitas cerita dan kualitas prosa dinilai terpisah.
9. Targetnya novel yang layak dibaca, bukan kesempurnaan tanpa akhir.

## Metodologi

- [Alur kerja novel](docs/01-workflow.md)
- [Scene Blueprint](docs/02-scene-blueprint.md)
- [Kontinuitas dan State Update](docs/03-continuity.md)
- [Audit dan perbaikan minimal](docs/04-audit-and-repair.md)
- [Standar penulisan prosa](docs/05-writing-standard.md)
- [Kontrak operasional AI dan quality gates](docs/06-ai-operating-contract.md)
- [GitHub sebagai workspace penulisan](docs/07-github-writing-workspace.md)

## Template

- [Dashboard proyek novel](templates/novel-project-readme-template.md)
- [Template Scene Blueprint](templates/scene-blueprint-template.md)
- [Template State Update](templates/state-update-template.md)
- [Template laporan audit](templates/audit-report-template.md)
- [Template decision log](templates/decision-log-template.md)
- [Template paket konteks bab](templates/chapter-context-template.md)

## Struktur proyek novel

Setiap novel disimpan terpisah di `stories/<slug-judul>/`. Folder itu menjadi sumber kebenaran untuk naskah dan seluruh keputusan cerita. Gunakan struktur dan aturan di [panduan workspace](docs/07-github-writing-workspace.md).

## Contoh pengujian metode

- [Salah Kirim: drama keseharian dan perubahan karakter](examples/salah-kirim.md)
- [Arman dan Mira: misteri, in medias res, flashback, dan pengetahuan tokoh](examples/arman-mira.md)

## Cara menggunakan

1. Berikan premis kepada AI yang memiliki akses repository.
2. Pastikan AI membaca `AI_INSTRUCTIONS.md`.
3. AI membuat folder proyek novel dan mengembangkan rancangan.
4. Setelah rancangan siap, AI menulis satu bab per siklus.
5. Setiap perubahan penting, State Update, dan audit disimpan ke GitHub.

GitHub menyimpan dan melacak pekerjaan; GitHub tidak dengan sendirinya menjalankan AI atau menjamin kualitas tulisan. Model yang tidak memiliki akses repository harus diberi file/konteks yang relevan secara manual.

## Status

Repository ini adalah knowledge base dan workspace dokumentasi. Metode sudah memiliki instruksi operasional, tetapi konsistensinya tetap harus dibuktikan melalui uji premis lintas genre, penulisan bab, dan audit/perbaikan.

## Pengelola data dan penulisan bab

Program `novel.py` mendukung dua jalur kerja:

### 1. AI menulis, Python mengambil data

AI dapat menulis bab secara langsung dengan meminta Python menyiapkan paket konteks terlebih dahulu. Jalankan dari direktori utama repository:

```bash
python novel.py --context 5 --story nama-folder-novel
```

Python membuat `stories/<slug>/workbench/context-chapter-005.md`. Paket ini berisi instruksi, standar prosa, README proyek, dokumen inti, blueprint bab, bab sebelumnya, serta catatan kontinuitas yang relevan. State Update dari bab setelah target tidak disertakan.

AI membaca paket tersebut, menulis naskah ke `manuscript/chapter-005.md`, membuat State Update ke `state-updates/chapter-005.md`, lalu meminta Python memeriksa hasil:

```bash
python novel.py --verify 5 --story nama-folder-novel
python novel.py --status --story nama-folder-novel
```

Untuk batch, AI mengulang proses satu bab demi satu bab. Bab selanjutnya baru diproses setelah naskah dan State Update bab sebelumnya tersimpan.

### 2. Python menjalankan AGY

Jika ingin program yang mengendalikan penulisan melalui Antigravity CLI, jalankan:

```bash
python novel.py
```

Menu interaktif menyediakan status bab, penulisan satu bab, penulisan beberapa bab berurutan, penghapusan dengan konfirmasi, dan pemilihan proyek. Dalam jalur ini Python menyiapkan prompt lalu menjalankan AGY satu proses per bab. Batch berhenti jika AGY gagal, limit terdeteksi, atau file naskah tidak berhasil diverifikasi.

### Perintah dan prasyarat

- `python novel.py --status --story SLUG`: melihat status bab.
- `python novel.py --context NOMOR --story SLUG`: menyiapkan paket konteks untuk AI.
- `python novel.py --verify NOMOR --story SLUG`: memeriksa naskah dan State Update.
- `python novel.py`: membuka menu interaktif yang menjalankan AGY.

Python 3 diperlukan untuk semua jalur. Antigravity CLI (`agy`) yang terpasang dan terautentikasi hanya diperlukan untuk jalur menu interaktif. Jika terdapat beberapa proyek, tentukan nama folder dengan `--story`.

**Batas verifikasi:** perintah `--verify` hanya memeriksa bahwa file naskah ada dan tidak kosong serta memberi peringatan jika State Update belum tersedia. Ia tidak menilai kualitas tulisan, kesesuaian blueprint, atau kelulusan audit. AI tetap bertanggung jawab melakukan pemeriksaan isi.
