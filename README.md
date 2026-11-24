# writenovelAI

Sistem kerja penulisan novel berbantuan AI. Python mengelola sumber cerita, memori, konteks, pemeriksaan struktural, dan eksekusi. AI menangani pemahaman naratif, keputusan kreatif, audit interpretatif, dan penulisan prosa.

## Mulai

Python 3.11+ direkomendasikan. Tidak ada dependensi pihak ketiga untuk mesin inti.

```bash
python novel.py --story gang-yang-hilang-dari-peta status
python novel.py --story gang-yang-hilang-dari-peta memory
python novel.py --story gang-yang-hilang-dari-peta context 5
python novel.py --story gang-yang-hilang-dari-peta audit
python novel.py --story gang-yang-hilang-dari-peta audit --prompt
python novel.py --story gang-yang-hilang-dari-peta verify 5
```

Urutan argumen: `python novel.py --story SLUG PERINTAH`. Jika hanya ada satu proyek, `--story` boleh dihilangkan.

## Alur kerja

1. Berikan premis. AI membangun konsep, karakter, dunia, outline, dan blueprint.
2. Jalankan `audit` untuk pemeriksaan deterministik.
3. Jalankan `audit --prompt` untuk membuat paket audit yang dibaca AI. Audit AI memeriksa sebab-akibat, motivasi, character arc, timeline, knowledge state, planting-payoff, dan keputusan.
4. Setelah outline/blueprint disepakati, jalankan `context NOMOR`. Python menyusun sumber yang relevan tanpa memasukkan State Update dari masa depan.
5. AI membaca paket konteks, menulis naskah, dan membuat State Update faktual.
6. Jalankan `verify NOMOR` dan `audit` lagi. Perbarui memori hanya berdasarkan naskah yang benar-benar ditulis dan keputusan yang disetujui.

## Perintah

| Perintah | Fungsi |
|---|---|
| `status` | Status outline, blueprint, naskah, dan State Update |
| `memory` | Memori berbasis sumber; `--before N` membatasi hingga sebelum bab N |
| `context N` | Membuat paket konteks bab untuk AI |
| `context N --rewrite` | Mengizinkan paket rewrite; hanya gunakan setelah persetujuan pengguna |
| `audit` | Pemeriksaan struktur deterministik |
| `audit --prompt` | Selain cek deterministik, membuat paket audit untuk AI di workbench |
| `verify N` | Memastikan naskah, blueprint, dan State Update tersedia |

## Prinsip memori

Tidak ada ringkasan AI yang otomatis dianggap kanon. Sumber kebenaran adalah dokumen proyek, decision log, blueprint, naskah, dan State Update. Python menyusun ulang memori dari sumber-sumber itu sesuai kebutuhan bab. AI tidak boleh mengubah canon atau decision log tanpa usulan dan persetujuan.

Status KANON, WAJIB, FLEKSIBEL, dan BELUM DIPUTUSKAN harus dibedakan. Fakta, dugaan, interpretasi, dan kemungkinan tidak boleh dicampur.

## Pemeriksaan dan batasnya

Python memeriksa hal yang dapat ditentukan dari struktur file: nomor bab, blueprint yang hilang/terlepas, celah nomor, dan sinkronisasi naskah-State Update. AI memeriksa hal yang memerlukan pemahaman cerita: motivasi, kewajaran sebab-akibat, perkembangan karakter, pengetahuan tokoh, serta fungsi planting-payoff.

Tidak ada pemeriksaan otomatis yang menjamin cerita bebas kesalahan. Temuan AI harus menyertakan bukti dan lokasi; perubahan struktural harus dicatat di decision log. Pemeriksaan Python yang lolos bukan berarti kualitas cerita sudah lolos.

## GitHub Actions

Workflow `.github/workflows/python-check.yml` menjalankan compile, unit test, dan audit struktur pada push, pull request, serta pemicu manual. Workflow ini tidak memanggil model AI dan tidak membutuhkan API key.

## Struktur kode

- `novel.py`: satu pintu masuk CLI.
- `novel_engine/project.py`: penemuan proyek, pembacaan sumber, memori, dan paket konteks.
- `novel_engine/audit.py`: pemeriksaan deterministik dan paket instruksi audit AI.
- `novel_engine/cli.py`: antarmuka perintah.
- `tests/`: uji fungsi inti.
- `docs/`: metodologi dan kontrak kerja manusia/AI.

File di `workbench/` adalah artefak sementara yang dibuat ulang dari sumber; jangan jadikan sumber kebenaran atau commit ke repository. Naskah, outline, blueprint, State Update, audit, dan decision log tetap berada di folder proyek.

## Proyek contoh

- `stories/gang-yang-hilang-dari-peta/`
- `stories/arman-mira/`

AI wajib membaca [AI_INSTRUCTIONS.md](AI_INSTRUCTIONS.md) sebelum mengubah proyek.
