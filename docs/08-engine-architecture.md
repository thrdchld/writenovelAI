# Novel Engine v2 — arsitektur operasional

## Sasaran

Menjaga satu sumber kebenaran cerita dan mengurangi pengulangan konteks. Mesin tidak mengganti penilaian sastra AI dengan aturan kaku.

## Komponen yang dipakai

1. `novel.py`: satu pintu masuk CLI.
2. `novel_engine/project.py`: resolver proyek, parser nomor bab/blueprint gabungan, memori bersumber, dan paket konteks.
3. `novel_engine/audit.py`: pemeriksaan struktur dan paket audit naratif untuk AI.
4. `novel_engine/agy.py`: adapter opsional untuk penulisan AGY berurutan.
5. `novel_engine/cli.py`: antarmuka perintah lokal.
6. `novel_engine/github_bot.py`: bot issue untuk status, audit outline, dan penulisan bab/batch melalui API model yang kompatibel dengan OpenAI Chat Completions.
7. `tests/test_engine.py`: uji parsing blueprint gabungan, temuan blueprint hilang, batas memori temporal, dan nomor bab.
8. `.github/workflows/python-check.yml`: compile, unit test, dan audit struktur pada push/PR.
9. `.github/workflows/novel-bot.yml`: menerima perintah issue dari pemilik repository, menjalankan bot, dan menyimpan hasil melalui commit.

Tidak ada database atau indeks memori duplikat. Memori dibangun dari dokumen sumber setiap kali diminta. Tidak ada cache basi yang dapat berubah menjadi sumber fakta baru.

## Sumber memori

- Dokumen inti proyek: premis, konsep, karakter, dunia/aturan, outline, decision log.
- State Update dan catatan continuity yang terjadi sebelum bab target.
- Naskah bab sebelumnya sebagai konteks prosa lokal.
- Blueprint bab target.

State Update masa depan dikecualikan dari konteks bab yang lebih awal. Perintah `memory`, `context`, dan `audit` tidak mengubah dokumen sumber.

## Validasi deterministik versus audit AI

Python memeriksa fakta struktural yang dapat dibuktikan dari file: nomor bab, blueprint hilang/terlepas, celah bab, dan pasangan naskah-State Update. Audit AI menilai hubungan semantik: motivasi, logika sebab-akibat, perkembangan karakter, pengetahuan tokoh, dan fungsi petunjuk. Temuan AI harus memiliki bukti dan membedakan kontradiksi dari risiko atau preferensi.

## Siklus penulisan

`status → audit → audit --prompt → perbaikan outline/blueprint → context N → penulisan → State Update → verify N → audit → bab berikutnya`

Setiap perubahan struktural harus dicatat di decision log dan dampaknya pada bab lain ditelusuri. Usulan AI belum menjadi kanon sampai disetujui.

## GitHub chatbot

Komentar issue dari pemilik repository dapat menjalankan:
- `@novelbot status SLUG`
- `@novelbot audit SLUG`
- `@novelbot write SLUG 5`
- `@novelbot write SLUG 1-5`

Bot memakai secret `NOVEL_AI_API_KEY` dan variable `NOVEL_AI_MODEL`, dengan `NOVEL_AI_BASE_URL` opsional. Provider harus kompatibel dengan OpenAI Chat Completions. Bot hanya menulis ke bab yang belum memiliki naskah maupun State Update, menyimpan setiap bab batch secara berurutan, dan berhenti jika satu bab gagal. Bot tidak memproses komentar pull request.

## Batasan yang diketahui

- Audit deterministik tidak memahami makna naratif; ia tidak dapat membuktikan motivasi meyakinkan atau payoff memuaskan.
- Perintah `verify` memeriksa kelengkapan berkas, bukan kualitas.
- Tidak ada jaminan bebas halusinasi. Sumber yang tidak lengkap tetap dapat menghasilkan konteks tidak lengkap.
- GitHub Actions CI menguji mesin tanpa memanggil AI. Bot issue memanggil AI hanya setelah provider secret/variable diatur.
- Penulisan bot adalah draft, bukan bab yang otomatis diterima. Audit naratif dan persetujuan perubahan canon tetap diperlukan.
