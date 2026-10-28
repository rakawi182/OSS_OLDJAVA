<p align="center"><img src="icon-192.png" alt="Logo OSS ΩLDJAVA" width="120"></p>

<h1 align="center">OSS ΩLDJAVA-astro</h1>

<p align="center"><b>Jolotundo Research · <i>exploring the ancient sky</i></b></p>

Aplikasi astronomi berbasis web dalam **satu berkas HTML** untuk arkeoastronomi, kalender Jawa Kuno, dan konversi tanggal prasasti. Tidak perlu server, instalasi, atau koneksi internet: cukup buka berkas HTML di browser, termasuk di ponsel.

> _A single-file, offline astronomy web app for archaeoastronomy, Old Javanese calendrics, and inscription date conversion._

## Fitur

Halaman-halaman di dalam aplikasi:

| Halaman | Isi singkat |
|---|---|
| Beranda | Pintu masuk ke seluruh fitur |
| Real-time | Posisi Matahari dan Bulan saat ini |
| Gnomon | Gnomon (Śaṅku), waktu dari bayangan, lagna, dan muhurta Jawa Kuno |
| Rāśi Chakra | Lingkaran rāśi / zodiak |
| Grahacara | Posisi graha |
| Timeline | Garis waktu astronomis |
| Tanggal Spesifik | Perhitungan untuk satu tanggal dan jam (WIB), termasuk JD, ΔT, dan ayanamsa |
| Wuku & Wara | Siklus kalender Jawa-Bali |
| Konversi Prasasti | Pencocokan tanggal prasasti Jawa Kuno |
| Database Damais | Data tanggal prasasti dari Damais |
| Analisis Sistem Zodiak | Perbandingan sistem zodiak |
| Konversi Waktu · Offset Waktu · Unit Waktu | Alat bantu waktu |
| Referensi | Daftar pustaka, catatan teknis, dan hasil validasi |

Inti perhitungan:

- **Ephemeris:** VSOP87D (Matahari) dan ELP2000-82B (Bulan), dimuat utuh tanpa pemotongan suku.
- **Presesi dan nutasi:** model IAU 2006 / 2000A.
- **ΔT:** spline Morrison dkk. (2021) untuk −720 sampai 2019, tabel IERS/EOP setelahnya, dan model Espenak & Meeus sebagai cadangan.
- **EOP IERS:** DUT1 (UT1 − UTC) dan gerak kutub (xp, yp) untuk rentang 1972 sampai akhir tabel.

Hasil uji silang terhadap JPL Horizons (DE441) dan batas keterbatasannya tercantum di halaman **Referensi** di dalam aplikasi.

## Cara memakai

1. Unduh berkas `OSS_OLDJAVA_R2026_10.html` (atau versi terbaru) dari repositori ini.
2. Buka berkas itu di browser (Chrome, Firefox, Edge, dan sebagainya). Di Android, buka dari aplikasi pengelola berkas.

Ukuran berkas sekitar 7,6 MB karena seluruh data dan seri ephemeris sudah tertanam. Pengaturan seperti DUT1 manual tidak disimpan setelah halaman dimuat ulang.

## Pasang sebagai aplikasi (PWA)

Aplikasi ini bisa dibuka lewat GitHub Pages dan dipasang di layar utama seperti aplikasi biasa:

**<https://rakawi182.github.io/OSS_OLDJAVA/>**

1. Buka alamat di atas di Chrome (Android) atau Safari (iPhone).
2. Chrome: menu ⋮ → **Pasang aplikasi** / **Tambahkan ke layar utama**. Safari: **Bagikan** → **Tambah ke Layar Utama**.
3. Setelah dibuka sekali, aplikasi berjalan **offline**. Setiap kali dibuka, versi terbaru diperiksa di latar belakang dan dipakai pada pembukaan berikutnya.

Mengaktifkan GitHub Pages: **Settings → Pages → Deploy from a branch → main / (root)**.

Jika versi baru diunggah dengan nama berkas berbeda, ubah `APP_FILE` di `sw.js` dan `index.html`. Jika namanya sama, tidak ada yang perlu diubah.

## Memperbarui data EOP IERS

Data EOP di dalam aplikasi bisa diperbarui tanpa membangun ulang, memakai skrip `update_eop.py` (Python 3; sudah diuji di lingkungan biasa dan dirancang untuk **Pydroid 3** di Android).

1. Unduh berkas IERS terbaru:
   - **EOP 20 C04** (data final): <https://hpiers.obspm.fr/eoppc/eop/eopc04/> dan <https://datacenter.iers.org/eop.php>
   - **Bulletin A** (rapid dan prediksi): <https://datacenter.iers.org/eop.php> atau <https://maia.usno.navy.mil>
2. Taruh berkas itu di folder yang sama dengan `OSS_OLDJAVA_*.html` dan `update_eop.py`. Boleh salah satu jenis saja.
3. Jalankan `update_eop.py`.
4. Muat ulang aplikasi. Cakupan data baru terlihat di Referensi → **Orientasi Bumi (EOP)**.

Yang dilakukan skrip: menimpa data final dengan C04 terbaru, menambah rapid dan prediksi dari Bulletin A, lalu memeriksa kontinuitas data. Skrip berhenti tanpa mengubah apa pun jika ada celah hari, lonjakan UT1−TAI (tanda detik kabisat baru), atau TAI−UTC yang berbeda dari tabel detik kabisat di aplikasi. Berkas lama dicadangkan otomatis sebagai `*.bak-TANGGAL-JAM`. Opsi `--dry-run` hanya menampilkan hasil tanpa menulis.

## Akurasi dan keterbatasan

- Untuk era prasasti Jawa Kuno (abad ke-8 sampai ke-16 M), sumber ketidakpastian terbesar adalah **ΔT historis**, bukan ephemeris: orde puluhan sampai ratusan detik untuk 702–1299 M (Morrison dkk., 2021).
- Koreksi dX, dY (≈ 0,5 mas) dan LOD tidak diterapkan.
- Nilai prediksi EOP dari Bulletin A makin kurang pasti ke arah ujung tabel. Setelah tabel berakhir, UT1 diperlakukan ≈ UTC.
- Uji verifikasi membuktikan kesesuaian dengan berkas acuan resmi, bukan akurasi absolut.
- Aplikasi ini alat bantu penelitian. Untuk keperluan publikasi, verifikasi hasil kunci dengan sumber independen.

## Struktur repositori

```
.
├── OSS_OLDJAVA_R2026_10.html     # aplikasi (satu berkas)
├── update_eop.py                 # pembaru data EOP IERS
├── index.html                    # pintu masuk GitHub Pages
├── manifest.webmanifest          # metadata PWA
├── sw.js                         # service worker (offline)
├── icon-192.png  icon-512.png  maskable-512.png
├── apple-touch-icon.png  favicon.svg   # logo dan ikon
├── README.md
├── CHANGELOG.md
├── CITATION.cff                  # metadata sitasi (tombol "Cite this repository")
├── CITATIONS.md                  # daftar pustaka dan sumber data
├── LICENSE                       # MIT
└── .gitignore
```

## Sitasi

Jika Anda memakai OSS ΩLDJAVA dalam penelitian, kutip repositori ini (lihat `CITATION.cff` atau tombol **Cite this repository** di GitHub) dan juga pustaka ilmiah yang mendasarinya di [`CITATIONS.md`](CITATIONS.md).

## Lisensi

Kode di repositori ini dilisensikan di bawah [MIT License](LICENSE). Data dan model pihak ketiga (VSOP87D, ELP2000-82B, data IERS, katalog gerhana NASA, dan lainnya) tetap tunduk pada ketentuan penyedia masing-masing; lihat [`CITATIONS.md`](CITATIONS.md).

## Kontribusi

Laporan galat dan saran sangat disambut lewat [Issues](../../issues). Mohon sertakan versi berkas, tanggal dan jam masukan, serta hasil yang diharapkan beserta sumber pembandingnya.
