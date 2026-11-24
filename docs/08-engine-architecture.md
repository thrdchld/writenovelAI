# Novel Engine v2 — arsitektur operasional

## Sasaran

Menjaga satu sumber kebenaran cerita dan mengurangi pengulangan konteks. Mesin tidak mencoba mengganti penilaian sastra AI dengan aturan kaku.

## Komponen yang benar-benar dipakai

1. `novel.py`: entry point CLI agar penggunaan tetap sederhana.
2. `novel_engine/project.py`: resolver proyek, pembaca file, parser nomor bab/blueprint gabungan, pembangun memori bersumber, dan paket konteks.
3. `novel_engine/audit.py`: pemeriksaan deterministik atas outline/blueprint/naskah/State Update dan penyusun paket audit AI.
4. `novel_engine/cli.py`: perintah yang dipakai pengguna dan AI.
5. `tests/test_engine.py`: tes untuk parsing blueprint gabungan, audit blueprint hilang, pencegahan kebocoran State Update masa depan, dan nomor bab.
6. `.github/workflows/python-check.yml`: menjalankan compile, tes, dan audit struktur pada push/PR.\n7. `.github/workflows/novel-bot.yml` dan `novel_engine/github_bot.py`: chatbot issue berbasis provider OpenAI-compatible untuk status, audit, dan penulisan bab.

Tidak ada database atau indeks memori duplikat. Memori dibangun dari dokumen sumber setiap kali diminta. Dengan demikian, cache yang basi tidak bisa menjadi sumber fakta baru.

## Sumber memori

- Dokumen inti proyek: premis, konsep, karakter, dunia/aturan, outline, decision log.
- State Update dan catatan continuity yang sudah terjadi sebelum bab target.
- Naskah bab sebelumnya sebagai konteks prosa lokal.
- Blueprint bab target.

State Update masa depan dikecualikan dari konteks bab yang lebih awal. Naskah dan dokumen sumber tidak diubah oleh perintah `memory`, `context`, atau `audit`.

## Validasi deterministik versus audit AI

Python mengecek fakta struktural yang dapat dibuktikan dari file. Audit AI menilai hubungan semantik: motivasi, logika sebab-akibat, perkembangan karakter, pengetahuan tokoh, dan fungsi petunjuk. AI wajib menyertakan bukti sumber dan membedakan kontradiksi dari risiko atau selera.

## Siklus penulisan

`status → audit → audit --prompt → perbaikan outline/blueprint → context N → penulisan → State Update → verify N → audit naskah → bab berikutnya`

Setiap perubahan struktural harus dicatat di decision log dan dampak lintas bab ditelusuri. Perubahan yang disarankan AI belum menjadi kanon sampai disetujui.

## GitHub chatbot\n\nBot menerima komentar issue dari pemilik repository dengan perintah status, audit, dan write. Ia menggunakan secret API provider dan variable model/base URL. Penulisan hanya boleh ke bab yang belum memiliki naskah maupun State Update; hasil disimpan dalam commit. Bot tidak memproses komentar pull request. Workflow tidak akan bisa menulis dengan AI sampai secret dan variable provider diatur.\n\n## Batasan yang diketahui

- Audit deterministik saat ini tidak memahami makna naratif; ia tidak bisa membuktikan sebuah motivasi meyakinkan atau payoff memuaskan.
- Perintah `verify` memeriksa kelengkapan berkas, bukan kualitas.
- Tidak ada jaminan bebas halusinasi. Sumber yang tidak lengkap tetap dapat menghasilkan konteks tidak lengkap.
- GitHub Actions saat ini menjalankan pemeriksaan lokal repository. Panggilan model AI dan bot komentar memerlukan integrasi provider dan secret terpisah; workflow CI tidak mengirim naskah ke layanan AI.
