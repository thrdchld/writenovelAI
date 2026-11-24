# writenovelAI

Sistem kerja penulisan novel berbantuan AI. Python mengelola sumber cerita, memori, konteks, pemeriksaan struktural, dan eksekusi. AI menangani pemahaman naratif, keputusan kreatif, audit interpretatif, dan penulisan prosa.

## Mulai

Python 3.11+ direkomendasikan. Tidak ada dependensi pihak ketiga untuk mesin inti. Jalankan `python novel.py` untuk membuka menu interaktif, atau gunakan perintah langsung di bawah.

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
| `agy 1-5,8` | Menjalankan AGY secara berurutan; bab yang sudah ada dilewati |
| `agy 5 --rewrite` | Menjalankan AGY untuk rewrite yang diminta secara eksplisit |

## Referensi kerja

**Metodologi**
- [Alur kerja novel](docs/01-workflow.md)
- [Scene Blueprint](docs/02-scene-blueprint.md)
- [Kontinuitas](docs/03-continuity.md)
- [Audit dan perbaikan](docs/04-audit-and-repair.md)
- [Standar prosa](docs/05-writing-standard.md)
- [Kontrak operasional AI](docs/06-ai-operating-contract.md)
- [GitHub sebagai workspace](docs/07-github-writing-workspace.md)
- [Arsitektur Novel Engine v2](docs/08-engine-architecture.md)

**Template**
- [Template proyek novel](templates/novel-project-readme-template.md)
- [Template blueprint bab](templates/scene-blueprint-template.md)
- [Template State Update](templates/state-update-template.md)
- [Template audit](templates/audit-report-template.md)
- [Template decision log](templates/decision-log-template.md)
- [Template paket konteks](templates/chapter-context-template.md)

**Contoh metode**
- [Salah Kirim](examples/salah-kirim.md)
- [Arman dan Mira](examples/arman-mira.md)

Contoh adalah referensi cara menerapkan metode, bukan fakta atau canon untuk novel lain.

## Prinsip memori

Tidak ada ringkasan AI yang otomatis dianggap kanon. Sumber kebenaran adalah dokumen proyek, decision log, blueprint, naskah, dan State Update. Python menyusun ulang memori dari sumber-sumber itu sesuai kebutuhan bab. AI tidak boleh mengubah canon atau decision log tanpa usulan dan persetujuan.

Status KANON, WAJIB, FLEKSIBEL, dan BELUM DIPUTUSKAN harus dibedakan. Fakta, dugaan, interpretasi, dan kemungkinan tidak boleh dicampur.

## Pemeriksaan dan batasnya

Python memeriksa hal yang dapat ditentukan dari struktur file: nomor bab, blueprint yang hilang/terlepas, celah nomor, dan sinkronisasi naskah-State Update. AI memeriksa hal yang memerlukan pemahaman cerita: motivasi, kewajaran sebab-akibat, perkembangan karakter, pengetahuan tokoh, serta fungsi planting-payoff.

Tidak ada pemeriksaan otomatis yang menjamin cerita bebas kesalahan. Temuan AI harus menyertakan bukti dan lokasi; perubahan struktural harus dicatat di decision log. Pemeriksaan Python yang lolos bukan berarti kualitas cerita sudah lolos.

## GitHub Actions

Workflow `.github/workflows/python-check.yml` menjalankan compile, unit test, dan audit struktur pada push, pull request, serta pemicu manual. Workflow ini tidak memanggil model AI dan tidak membutuhkan API key.

## GitHub Issue chatbot

Workflow `.github/workflows/novel-bot.yml` menerima perintah dari komentar issue oleh pemilik repository:

```text
@novelbot status gang-yang-hilang-dari-peta
@novelbot audit gang-yang-hilang-dari-peta
@novelbot write gang-yang-hilang-dari-peta 1
@novelbot write gang-yang-hilang-dari-peta 1-5
```

Agar aktif, atur Repository Secret `NOVEL_AI_API_KEY` serta Repository Variables `NOVEL_AI_MODEL` dan opsional `NOVEL_AI_BASE_URL` (default `https://api.openai.com/v1`). Endpoint harus kompatibel dengan OpenAI Chat Completions. Bot menolak komentar selain dari pemilik repository, tidak memproses pull request, dan tidak menimpa naskah/State Update yang sudah ada. Penulisan bot disimpan dalam commit dan tetap harus diaudit.

## Struktur kode

- `novel.py`: satu pintu masuk CLI.
- `novel_engine/project.py`: penemuan proyek, pembacaan sumber, memori, dan paket konteks.
- `novel_engine/audit.py`: pemeriksaan deterministik dan paket instruksi audit AI.
- `novel_engine/cli.py`: antarmuka perintah dan menu interaktif.\n- `novel_engine/agy.py`: adapter AGY berurutan.\n- `novel_engine/github_bot.py`: bot GitHub Issue untuk AI API.
- `tests/`: uji fungsi inti.
- `docs/`: metodologi dan kontrak kerja manusia/AI.

File di `workbench/` adalah artefak sementara yang dibuat ulang dari sumber; jangan jadikan sumber kebenaran atau commit ke repository. Naskah, outline, blueprint, State Update, audit, dan decision log tetap berada di folder proyek.

## Proyek contoh

- `stories/gang-yang-hilang-dari-peta/`
- `stories/arman-mira/`

AI wajib membaca [AI_INSTRUCTIONS.md](AI_INSTRUCTIONS.md) sebelum mengubah proyek.
