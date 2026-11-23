# GitHub sebagai Workspace Penulisan Novel

## Fungsi GitHub

Repository writenovelAI menyimpan dua hal yang berbeda:
1. **Standar bersama:** instruksi AI, metodologi, dan template di root, `docs/`, serta `templates/`.
2. **Proyek novel:** seluruh rancangan, keputusan, naskah, dan audit di `stories/<slug-judul>/`.

Folder `stories/` adalah tempat menulis. Jangan menaruh naskah novel langsung di `docs/` atau `examples/`.

## Struktur satu novel

Gunakan struktur ini sebagai default. Folder yang belum diperlukan boleh dibuat ketika dibutuhkan; jangan membuat puluhan file kosong.

```text
stories/
└── <slug-judul>/
    ├── README.md
    ├── 00-premise.md
    ├── 01-concept.md
    ├── 02-characters.md
    ├── 03-world-and-rules.md
    ├── 04-story-outline.md
    ├── 05-decision-log.md
    ├── blueprint/
    │   ├── README.md
    │   ├── chapter-001.md
    │   └── chapter-002.md
    ├── manuscript/
    │   ├── chapter-001.md
    │   └── chapter-002.md
    ├── continuity/
    │   ├── timeline.md
    │   ├── character-knowledge.md
    │   ├── story-state.md
    │   └── character-behavior.md
    ├── state-updates/
    │   ├── chapter-001.md
    │   └── chapter-002.md
    ├── audits/
    │   ├── design-audit.md
    │   ├── chapter-001.md
    │   └── final-audit.md
    └── research/
        └── README.md
```

## Peran file

- `README.md`: dashboard proyek, status, indeks dokumen, bab yang selesai, dan langkah berikutnya.
- `00-premise.md`: premis asli pengguna; jangan mengganti maksudnya.
- `01-concept.md`: genre, pembaca, pengalaman, konflik, taruhan, dan arah cerita.
- `02-characters.md`: tokoh yang benar-benar diperlukan.
- `03-world-and-rules.md`: latar dan aturan yang memengaruhi peristiwa.
- `04-story-outline.md`: alur keseluruhan dan fungsi bab.
- `05-decision-log.md`: keputusan penting, alasan, tanggal/urutan, dan dampak.
- `blueprint/`: rancangan adegan per bab.
- `manuscript/`: naskah bab final terkini, satu bab per file.
- `continuity/`: catatan lintas bab terkini.
- `state-updates/`: rekam perubahan setelah setiap bab.
- `audits/`: hasil audit rancangan, bab, dan akhir.
- `research/`: sumber dan catatan riset faktual bila cerita memerlukannya.

## Aturan penamaan

- Gunakan slug sederhana untuk folder novel, misalnya `catatan-untuk-orang-sungkan`.
- Nomor bab tiga digit: `chapter-001.md`, `chapter-002.md`.
- Satu bab = satu file. Jangan gabungkan seluruh novel dalam satu file panjang.
- Jangan menggunakan nama file seperti `final-final-baru2.md`.
- Jika perlu menyimpan versi lama, gunakan riwayat Git atau folder `archive/` dengan alasan jelas. Jangan menggandakan naskah aktif tanpa kebutuhan.

## Dashboard README novel

README setiap novel harus memuat:
- Judul kerja dan status proyek.
- Premis singkat.
- Genre/pengalaman membaca.
- Status rancangan (WORKING/REVIEW/ACTIVE/LOCKED).
- Jumlah bab yang direncanakan dan alasan jika masih berubah.
- Status penulisan: bab terakhir ACCEPTED.
- Tautan dokumen inti.
- Keputusan terbuka yang menghambat.
- Langkah kerja berikutnya.

README harus diperbarui ketika status atau struktur proyek berubah.

## Sumber kebenaran dan konflik

- Naskah di `manuscript/` adalah versi prosa aktif.
- Blueprint aktif adalah acuan pelaksanaan, bukan pengganti naskah.
- Decision log mencatat perubahan keputusan.
- State Update dan continuity harus mencerminkan naskah yang benar-benar terjadi.
- Jika file berbeda, jangan memilih diam-diam. Tentukan sumber masalah dan catat konflik.

## Cara kerja dengan GitHub

1. Baca `AI_INSTRUCTIONS.md` dan dokumen relevan.
2. Baca README proyek.
3. Periksa status dan file yang sudah ada sebelum membuat perubahan.
4. Tulis atau perbarui file proyek yang tepat.
5. Perbarui README proyek dan indeks jika diperlukan.
6. Buat commit dengan pesan spesifik.
7. Verifikasi file dan commit tersimpan.

GitHub menjadi sumber kebenaran lintas sesi. Jangan menganggap isi chat sebagai satu-satunya tempat penyimpanan naskah.

## Penggunaan untuk model AI

Jika model tidak memiliki akses langsung ke GitHub, pengguna perlu menyediakan file atau menyalin konteks yang diperlukan. Jangan mengklaim model otomatis membaca repository hanya karena repository bersifat publik. Jika model/agent memiliki konektor GitHub, minta atau gunakan akses repository yang sesuai.

## Batasan

GitHub menyimpan dan melacak dokumen, tetapi tidak otomatis menjalankan AI, membuat audit, atau menjamin kualitas naskah. Kualitas tetap bergantung pada kepatuhan model terhadap instruksi dan pengujian metode.
