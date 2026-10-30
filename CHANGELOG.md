# Changelog

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id-ID/1.1.0/).

## [R2026_10, revisi] — 2026-10-30
### Ditambahkan
- Tab **Unit Waktu**: sub-tab **Saka**, kalender lunisolar Saka rata-rata (Caitra-initial, amānta) dari Kali Ahargaṇa. Tiga mode masukan (tanggal, KA, tanggal Saka), tujuh aturan (Kali, Varāhamihira dua aturan, Khaṇḍakhādyaka, Karaṇaprakāśa, Karaṇakutūhala, Grahalāghava), empat set parameter, dan koreksi interkalasi k.
- 19 uji mandiri Saka di sub-tab **Audit** (epok KA, contoh Bag 2003, contoh Uma & Rao 2018).
- `CITATIONS.md`: bagian satuan waktu dan kalender Saka India (Hayashi 2017; Bag 2003; Uma & Rao 2018).

### Diubah
- Ukuran berkas sekitar 7,7 MB. Nama berkas tetap, sehingga `sw.js` dan `index.html` tidak berubah.

## [R2026_10] — 2026-10-28
### Ditambahkan
- **PWA**: dapat dipasang di layar utama dan berjalan offline (`manifest.webmanifest`, `sw.js`, `index.html`), beserta logo dan set ikon baru.
- Lapisan **EOP IERS**: DUT1 (UT1 − UTC) dan gerak kutub (xp, yp) diterapkan pada vektor pengamat dan alt/az; DUT1 manual opsional.
- Kartu **Orientasi Bumi (EOP)** di halaman Referensi: cakupan data C04, Bulletin A rapid, dan Bulletin A prediksi (MJD dan tanggal), serta keterangan pembaruan terakhir.
- Tab **Tanggal**: ΔT ditampilkan sebagai TT − UT1. Di dalam rentang tabel EOP juga tampil TT − UTC, UT1 − UTC, dan sumber UT1; di luar rentang tampil ΔT model.
- `update_eop.py`: skrip (Python 3 / Pydroid 3) untuk memperbarui blok data EOP di dalam berkas HTML dari berkas IERS EOP 20 C04 dan Bulletin A, tanpa membangun ulang aplikasi.

### Diubah
- Data EOP diperbarui: C04 sampai MJD 61309 (2026-09-26); Bulletin A No. 043 (22 Oktober 2026) rapid sampai MJD 61335, prediksi sampai MJD 61700.
