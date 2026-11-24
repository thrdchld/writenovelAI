# LAPORAN TAHAP 3E — PENGUJIAN KLASIFIKASI RAHASIA DAN PENGETAHUAN LINTAS CERITA

**Tanggal:** 24 November 2026  
**Repository:** `thrdchld/writenovelAI`  
**Test Suite:** `tests/test_engine.py` (`test_3e_01`, `test_3e_02`, `test_3e_03`)  
**Hasil Uji:** 42 Passed, 0 Failed, 0 Skipped  

---

## 1. Pengujian Klasifikasi Decision Log (`test_3e_01`)

### A. Contoh Masukan Dokumen (`05-decision-log.md`)

```markdown
# Decision Log Uji 3E

## D-010 — Rahasia Penulis Murni
- **Status:** KANON
- **Klasifikasi:** Rahasia Penulis
- **Keputusan:** Motif penggelapan melibatkan konspirasi tingkat tinggi pejabat kementerian.

## D-020 — Rahasia Milik Karakter
- **Status:** KANON
- **Klasifikasi:** Rahasia Karakter
- **Pemilik Rahasia:** Maya Indah
- **Keputusan:** Maya diam-diam menyimpan salinan kunci brankas arsip lama.

## D-030 — Rahasia Berstatus Tag Bracket [RAHASIA]
- **Status:** KANON
- **Keputusan:** Arya pernah diberhentikan dari kepolisian karena pelanggaran etik.

## D-040 — Informasi Publik Dinyatakan Terbuka
- **Status:** KANON
- **Klasifikasi:** Publik
- **Keputusan:** Jadwal audit tahunan diumumkan di papan pengumuman kantor.

## D-050 — Keputusan Kanon Tanpa Klasifikasi
- **Status:** KANON
- **Keputusan:** Firma konsultan didirikan pada tahun 2005 oleh tiga sekawan.

## D-060 — Klasifikasi Kosong
- **Status:** KANON
- **Klasifikasi:**
- **Keputusan:** Pengarsipan digital diperbarui setiap bulan.

## D-070 — Klasifikasi Bertentangan [RAHASIA PENULIS]
- **Status:** KANON
- **Klasifikasi:** Publik
- **Keputusan:** Bukti fisik disembunyikan di bawah lantai ruang arsip.
```

### B. Hasil Klasifikasi Nyata pada Bagian 5 Konteks

```markdown
### Rahasia yang HANYA DIKETAHUI PENULIS (Author-Only Secrets):
- D-010 — Rahasia Penulis Murni: Motif penggelapan melibatkan konspirasi tingkat tinggi pejabat kementerian.
> [!WARNING] RAHASIA PENULIS: Poin-poin di atas adalah rahasia mutlak penulis untuk menjaga payoff masa depan...

### Rahasia Karakter dalam Dokumen Keputusan (Bukan Rahasia Penulis):
- D-020 — Rahasia Milik Karakter: Maya diam-diam menyimpan salinan kunci brankas arsip lama. *(Rahasia karakter; tidak otomatis menjadi rahasia penulis atau diketahui karakter lain)*
- D-030 — Rahasia Berstatus Tag Bracket [RAHASIA]: Arya pernah diberhentikan dari kepolisian karena pelanggaran etik. *(Rahasia karakter; tidak otomatis menjadi rahasia penulis atau diketahui karakter lain)*

### Keputusan Kanon Perlu Pemeriksaan (Klasifikasi Kosong atau Bertentangan):
- D-060 — Klasifikasi Kosong: Pengarsipan digital diperbarui setiap bulan. *(Klasifikasi tidak jelas atau bertentangan; tandai untuk pemeriksaan)*
- D-070 — Klasifikasi Bertentangan [RAHASIA PENULIS]: Bukti fisik disembunyikan di bawah lantai ruang arsip. *(Klasifikasi tidak jelas atau bertentangan; tandai untuk pemeriksaan)*

### Keputusan Kanon Tanpa Klasifikasi Kerahasiaan (Status Terbuka / Belum Ditentukan):
- D-050 — Keputusan Kanon Tanpa Klasifikasi: Firma konsultan didirikan pada tahun 2005 oleh tiga sekawan. *(Klasifikasi kerahasiaan belum ditentukan eksplisit)*
> [!NOTE] KEPUTUSAN KANON BELUM DIKLASIFIKASIKAN: Keputusan di atas adalah fakta kanon dunia cerita, namun dokumen sumber belum menentukan klasifikasi kerahasiaan eksplisit...

### Keputusan Kanon Publik (Informasi Terbuka):
- D-040 — Informasi Publik Dinyatakan Terbuka: Jadwal audit tahunan diumumkan di papan pengumuman kantor.
```

---

## 2. Pengujian Klasifikasi Profil Karakter Non-Hadir (`test_3e_02`)

### A. Contoh Masukan Dokumen (`02-characters.md`)

```markdown
## Saksi Kunci — 40
Profil: Ia bekerja sebagai arsiparis.
Rahasia: Ia memindahkan dokumen sebelum audit.
Rahasia Penulis: Ia mengetahui hasil akhir sejak awal.
Ia menyembunyikan berkas audit di loteng.
Ia gemar merawat kebun mawar di akhir pekan.
- **Catatan Ambigu:** Keterangannya mengenai tanggal rapat saling bertentangan.
```

### B. Hasil Klasifikasi Nyata pada Bagian 4.B Konteks

```markdown
#### Saksi Kunci — 40 (Tidak Hadir di Bab Ini)
- **Profil Umum & Hubungan (Referensi Kanon):** Ia bekerja sebagai arsiparis.
- **Rahasia Pribadi (Eksplisit dari Sumber):**
  - Ia memindahkan dokumen sebelum audit.
- **Rahasia Khusus Penulis (Author-Only dari Profil):**
  - Ia mengetahui hasil akhir sejak awal.
- **Informasi Ambigu / Belum Diklasifikasikan (Perlu Pemeriksaan):**
  - Keterangannya mengenai tanggal rapat saling bertentangan. *(Perlu pemeriksaan: klasifikasi bertentangan/ambigu)*
  - Ia menyembunyikan berkas audit di loteng. *(Belum diklasifikasikan)*
  - Ia gemar merawat kebun mawar di akhir pekan. *(Belum diklasifikasikan)*
- **Batas Isolasi Karakter:**
  > [!NOTE] BATAS AKSES INFORMASI SAKSI KUNCI:
  > Hubungan umum dan peran publik Saksi Kunci dapat diketahui oleh tokoh hadir sesuai relasi mereka.
  > [!CAUTION] ISOLASI RAHASIA: Rahasia pribadi eksplisit SAKSI KUNCI di atas DILARANG dibocorkan ke dalam pikiran, dialog, atau persepsi karakter yang hadir pada bab ini!
  > [!WARNING] RAHASIA PENULIS: Informasi khusus penulis pada SAKSI KUNCI di atas DILARANG diketahui karakter atau pembaca!
  > [!NOTE] INFORMASI PERLU PEMERIKSAAN: Untuk catatan ambigu/belum diklasifikasikan di atas, sumber tidak mencatat siapa saja yang mengetahuinya; jangan mengasumsikan seluruh karakter hadir otomatis tahu atau otomatis tidak tahu, melainkan batasi sesuai bukti nyata dalam blueprint bab ini.
```

**Temuan & Verifikasi Uji:**
1. Penanda `Profil:` berhasil dipetakan ke *Profil Umum & Hubungan*.
2. Penanda `Rahasia:` berhasil dipetakan ke *Rahasia Pribadi*.
3. Penanda `Rahasia Penulis:` berhasil dipetakan ke *Rahasia Khusus Penulis (Author-Only dari Profil)* dan mendapat peringatan `[!WARNING] RAHASIA PENULIS`.
4. Kalimat naratif tanpa penanda ("Ia menyembunyikan berkas audit di loteng." dan "Ia gemar merawat kebun mawar di akhir pekan.") **tidak dibuang** dan **tidak ditebak** sebagai profil umum maupun rahasia, melainkan masuk ke *Informasi Ambigu / Belum Diklasifikasikan (Belum diklasifikasikan)*.
5. Catatan bertanda ambigu dipetakan ke *Informasi Ambigu (Perlu pemeriksaan)*.

---

## 3. Pengujian Pemisahan Akses dari Kepemilikan Rahasia (`test_3e_03`)

### A. Skenario
- Sebuah keputusan kanon memuat rahasia karakter yang hadir di Bab 1 (`Maya Indah`):
  `- **Klasifikasi:** Rahasia Karakter`
  `- **Pemilik Rahasia:** Maya Indah`
  `- **Keputusan:** Maya membeli tanah yayasan atas nama adiknya.`
- Karakter lain yang hadir dalam bab yang sama: `Arya Pratama` (POV) dan `Kepala Cabang`.
- Blueprint menetapkan:
  `- **Yang diketahui tokoh:** Arya tahu selisih laporan kas; Maya tahu kode sandi berkas; kepala cabang hanya tahu jadwal audit.`
  `- **Informasi yang ditahan:** Alasan Arya mencurigai keterlibatan direktur ditahan dari pembaca.`

### B. Hasil Verifikasi Assertions
1. **Bukan Rahasia Penulis:** Rahasia Maya tidak masuk ke daftar *Rahasia yang HANYA DIKETAHUI PENULIS (Author-Only Secrets)*.
2. **Isolasi Antar-Karakter Hadir:** Rahasia Maya (`membeli tanah yayasan`) tidak dimasukkan ke dalam pengetahuan Arya Pratama maupun Kepala Cabang.
3. **Pemisahan Batas Pembaca vs Pengetahuan POV:** Penahanan informasi dari pembaca (`Alasan Arya mencurigai keterlibatan direktur ditahan dari pembaca`) tetap tercatat dalam Bagian 5 Batas Informasi Pembaca, namun fakta yang sah diketahui Arya (`Arya tahu selisih laporan kas`) tetap hadir dalam pengetahuan tokoh Arya di Bagian 4.A.
4. **Hubungan Umum Tidak Diisolasi:** Hubungan keluarga/sosial non-hadir (`Paman Maya`) tetap tersedia pada profil umum referensi kanon tanpa diisolasi sebagai rahasia.
