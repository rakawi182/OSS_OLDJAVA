# Changelog

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id-ID/1.1.0/).

## [R2026_11] — 2026-11-06
### Diubah
- Tab **Database Damais** dan **Analisis Sistem Zodiak** digabung menjadi satu tab **Damais & Zodiak**. Tautan lama ke tab Zodiak tetap membuka tab gabungan.
- Data sāyana / nirayana tidak lagi tetap (hardcode). Kolom Sistem (jam acuan dan ±24 jam), grafik distribusi, tabel per abad Śaka, dan kesimpulan kini dihitung dari run **A2** (nakṣatra), dengan fungsi yang sama dengan panel A2 di tab Audit Damais. Kesimpulan berisi angka hasil run beserta pembanding kebetulan (chance), bukan teks tetap.
- Kolom Status, KA, dan Skor di tab Damais & Zodiak kini dari run **reverse** (audit B), tidak lagi dari data validasi tetap. Skor kini dihitung langsung dan dapat berbeda sedikit dari angka tetap sebelumnya.
- Run A2 dan reverse berbagi hasil antara tab Damais & Zodiak dan tab Audit Damais: hasil yang sudah ada langsung ditampilkan tanpa hitung ulang. Tombol **Recompute** (Audit) dan **Hitung ulang** (Damais & Zodiak) memaksa hitung ulang. Hasil tersimpan selama berkas terbuka; setelah dimuat ulang, run perlu diulang.
- Ukuran berkas sekitar 7,9 MB. Nama berkas berubah menjadi `OSS_OLDJAVA_R2026_11.html`; `APP_FILE` di `sw.js` dan `index.html` disesuaikan, dan nama cache service worker menjadi `oss-oldjava-v2` agar salinan lama dibersihkan.

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
