# Tahap 8 — Python Core Tidak Bergantung pada AGY

**Status:** selesai  
**Merge commit:** `982b3378c86dfda5bd83b239496fd10b52808258`  
**Validasi:** GitHub Actions PR check #64 — Success

## Perubahan

1. Menambahkan `novel_engine/chapter_selection.py` sebagai modul netral untuk parsing nomor bab.
2. `agy.py` menggunakan utilitas bersama tersebut; adapter tetap dapat menjalankan batch seperti sebelumnya.
3. `github_bot.py` tidak lagi mengimpor parser dari `agy.py`.
4. `cli.py` hanya memuat modul AGY ketika pengguna benar-benar memilih perintah `agy`. Import dan penggunaan perintah inti tidak membutuhkan AGY.
5. Menambahkan `tests/test_chapter_selection.py` untuk format nomor/rentang, input tidak valid, bab yang tidak tersedia, dan bukti bahwa modul CLI inti dapat diimpor ketika import AGY diblokir.

## Hasil CI

Workflow Novel Engine checks untuk commit branch terakhir sebelum merge:
- Compile Python: success
- Unit tests: success
- Audit every story: success

Run: https://github.com/thrdchld/writenovelAI/actions/runs/45576451492

CI tersebut memeriksa source yang sama dengan yang kemudian digabungkan ke main. Tidak ada klaim bahwa workflow menjalankan AI atau AGY.

## Batas tahap ini

- AGY masih tersedia sebagai adapter opsional.
- Bot API masih menggunakan satu permintaan model dan belum memiliki tool-calling loop.
- Belum ada kontrak JSON universal untuk semua operasi Python.
- Belum ada implementasi tool-calling berulang untuk GitHub Actions.

## Tahap berikutnya

Membuat antarmuka Python yang stabil untuk agen: status, konteks, pencarian sumber, timeline, profil karakter, validasi, dan penyimpanan draft terbatas. Antarmuka harus dapat dipanggil baik dari agen interaktif yang punya terminal maupun dari adapter API di GitHub Actions.
