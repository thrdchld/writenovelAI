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

## Pengelola bab interaktif

Untuk melihat status penulisan, menyiapkan konteks bab, atau menghapus naskah bab, jalankan dari folder utama repository:

```bash
python novel.py
```

Menu:
1. Lihat status semua bab.
2. Siapkan penulisan atau revisi bab yang dipilih.
3. Hapus naskah bab yang dipilih (memerlukan konfirmasi).
4. Ganti proyek novel.
0. Keluar.

Saat memilih penulisan, program menggabungkan instruksi, dokumen inti novel, blueprint bab, dan naskah bab sebelumnya (jika tersedia) ke file `stories/<slug>/workbench/write-chapter-NNN.md`. Setelah itu minta Antigravity membaca file tersebut dan menulis ke folder `manuscript/`.

**Batasan yang perlu diketahui:** program Python ini tidak menghasilkan prosa dan tidak menjalankan model AI. Fungsinya mengelola status dan menyiapkan konteks. Status SELESAI hanya berarti file naskah bab ada dan tidak kosong, bukan berarti bab sudah lolos audit atau layak terbit. Penghapusan hanya menghapus file naskah bab, bukan blueprint.

