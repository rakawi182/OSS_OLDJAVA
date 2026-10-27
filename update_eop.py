#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_eop.py  --  Pembaru data EOP IERS untuk OSS ΩLDJAVA (Jolotundo Research)

Cara pakai (Pydroid 3):
  1. Taruh skrip ini di folder yang sama dengan berkas OSS_*.html.
  2. Taruh juga berkas IERS terbaru di folder itu:
       - EOP 20 C04   (mis. EOP_20u24_C04_one_file_1962-now.txt)  -> data final
       - Bulletin A   (mis. bulletina-xxxix-043.txt)              -> rapid + prediksi
     Boleh salah satu saja; yang tersedia akan dipakai.
  3. Jalankan skrip. Blok data "eop-data" di dalam OSS diperbarui di tempat.
     Berkas lama otomatis dicadangkan dulu (OSS_....html.bak-TANGGAL-JAM).

Yang dilakukan skrip:
  * C04            -> baris final (UT1-UTC, xp, yp, dX, dY, LOD), menimpa data lama.
  * Bulletin A     -> 7 hari "rapid" + prediksi ~365 hari (UT1-UTC, xp, yp);
                      dX, dY dari deret IAU2000A (mas -> detik busur), lalu ditahan
                      konstan setelah data terakhir; LOD = -d(UT1-TAI)/dt.
  * Hari yang tidak tercakup berkas baru tetap memakai nilai lama (tidak ada celah).
  * Metadata (c04, pr, source) ikut diperbarui; bagian lain HTML tidak disentuh.

Pemeriksaan keamanan (skrip berhenti tanpa menulis apa pun bila gagal):
  * tabel harus kontinu per hari, tanpa celah;
  * UT1-TAI tidak boleh melompat (tanda detik kabisat baru);
  * TAI-UTC di Bulletin A harus sama dengan tabel detik kabisat (LS) di OSS.
"""

import os
import re
import sys
import json
import glob
import shutil
import datetime

# =============================== PENGATURAN ===============================
FOLDER = None          # None = folder skrip ini (cadangan: folder kerja)
HTML_NAME = None       # None = cari otomatis OSS*.html yang memuat blok eop-data
C04_NAME = None        # None = cari otomatis (*C04*.txt / EOP*.txt)
BULLETIN_NAME = None   # None = cari otomatis (bulletin*.txt)
DRY_RUN = False        # True = hanya melapor, tidak menulis apa pun
FORCE = False          # True = proses walau data tampak tidak lebih baru
KEEP_BACKUPS = 3       # jumlah cadangan terbaru yang disimpan
# ==========================================================================

TAG_OPEN = '<script type="text/plain" id="eop-data">'
TAG_CLOSE = '</script>'
NUM = r'[-+]?\d*\.\d+'
RE_RAPID = re.compile(r'^\s+\d{2}\s+\d{1,2}\s+\d{1,2}\s+(\d{5})\s+(%s)\s+%s\s+(%s)\s+%s\s+(%s)\s+%s\s*$'
                      % (NUM, NUM, NUM, NUM, NUM, NUM))
RE_PRED = re.compile(r'^\s+\d{4}\s+\d{1,2}\s+\d{1,2}\s+(\d{5})\s+(%s)\s+(%s)\s+(%s)\s*$' % (NUM, NUM, NUM))
RE_CPO = re.compile(r'^\s+(\d{5})\s+(%s)\s+%s\s+(%s)\s+%s\s*$' % (NUM, NUM, NUM, NUM))
RE_ISSUE = re.compile(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s+Vol\.\s+([IVXLC]+)\s+No\.\s+(\d+)')
RE_TAI = re.compile(r'TAI-UTC\(MJD\s+(\d+)\)\s*=\s*([\d.]+)')


class Gagal(Exception):
    pass


def info(*a):
    print(*a)
    sys.stdout.flush()


# ------------------------------- utilitas ---------------------------------
def mjd_dari_tanggal(y, m, d):
    return datetime.date(y, m, d).toordinal() - datetime.date(1858, 11, 17).toordinal()


def mjd_hari_ini():
    t = datetime.datetime.now(datetime.timezone.utc).date()
    return t.toordinal() - datetime.date(1858, 11, 17).toordinal()


def tanggal_dari_mjd(m):
    return datetime.date.fromordinal(m + datetime.date(1858, 11, 17).toordinal()).isoformat()


def baca_teks(path):
    with open(path, 'r', encoding='utf-8', errors='replace', newline='') as f:
        return f.read()


def cari_folder():
    kandidat = []
    if FOLDER:
        kandidat.append(os.path.abspath(FOLDER))
    else:
        try:
            kandidat.append(os.path.dirname(os.path.abspath(__file__)))
        except NameError:
            pass
        kandidat.append(os.getcwd())
    for k in kandidat:
        if glob.glob(os.path.join(k, '*.html')) or glob.glob(os.path.join(k, '*.HTML')):
            return k
    raise Gagal('Folder OSS tidak ditemukan. Taruh skrip ini di folder yang sama dengan OSS_*.html, '
                'atau isi FOLDER di bagian PENGATURAN.')


def daftar(folder, nama, pola):
    if nama:
        p = os.path.join(folder, nama)
        return [p] if os.path.isfile(p) else []
    hasil = []
    for f in os.listdir(folder):
        low = f.lower()
        if any(re.match(pp, low) for pp in pola):
            hasil.append(os.path.join(folder, f))
    return sorted(hasil, key=os.path.getmtime, reverse=True)


# ---------------------------- baca HTML OSS -------------------------------
def muat_html(folder):
    cands = daftar(folder, HTML_NAME, [r'^oss.*\.html?$'])
    for p in cands:
        text = baca_teks(p)
        i = text.find(TAG_OPEN)
        if i < 0:
            continue
        i0 = i + len(TAG_OPEN)
        i1 = text.find(TAG_CLOSE, i0)
        if i1 < 0:
            continue
        try:
            J = json.loads(text[i0:i1])
            M0 = int(J['meta']['mjd0'])
            rows = J['d']
            int(J['meta']['c04'])
            int(J['meta']['pr'])
        except Exception as e:
            raise Gagal('Blok eop-data di %s tidak terbaca (%s).' % (os.path.basename(p), e))
        m = re.search(r'const LS = (\[\[.*?\]\]);', text)
        if not m:
            raise Gagal('Tabel detik kabisat (const LS) tidak ditemukan di OSS.')
        LS = json.loads(m.group(1))
        return {'path': p, 'text': text, 'i0': i0, 'i1': i1, 'J': J, 'M0': M0, 'rows': rows, 'LS': LS}
    raise Gagal('Berkas OSS_*.html yang memuat blok "eop-data" tidak ditemukan di %s.' % folder)


# ------------------------------ baca C04 ----------------------------------
def baca_c04(path):
    rows = {}
    header_ok = False
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for ln in f:
            s = ln.strip()
            if not s:
                continue
            if s.startswith('#'):
                if 'MJD' in s and 'UT1-UTC' in s:
                    pos = [s.find(k) for k in ('x(', 'y(', 'UT1-UTC', 'dX', 'dY', 'LOD')]
                    header_ok = all(p >= 0 for p in pos) and pos == sorted(pos)
                continue
            p = s.split()
            if len(p) < 13:
                continue
            try:
                y, mo, d = int(p[0]), int(p[1]), int(p[2])
                mjd = int(round(float(p[4])))
                v = [float(p[7]), float(p[5]), float(p[6]), float(p[8]), float(p[9]), float(p[12])]
            except ValueError:
                continue
            if mjd_dari_tanggal(y, mo, d) != mjd:
                raise Gagal('C04: tanggal dan MJD tidak cocok pada baris "%s".' % s[:40])
            rows[mjd] = v
    if not header_ok or len(rows) < 1000:
        raise Gagal('%s bukan format EOP 20 C04 yang dikenal (kolom: YR MM DD HH MJD x y UT1-UTC dX dY ... LOD).'
                    % os.path.basename(path))
    return rows


def pilih_c04(folder):
    best = None
    for p in daftar(folder, C04_NAME, [r'.*c04.*\.txt$', r'^eop.*\.txt$']):
        try:
            r = baca_c04(p)
        except Gagal:
            continue
        if best is None or max(r) > max(best[1]):
            best = (p, r)
    return best


# --------------------------- baca Bulletin A ------------------------------
def baca_bulletin(path):
    text = baca_teks(path)
    if 'Rapid Service/Prediction' not in text:
        raise Gagal('%s bukan IERS Bulletin A.' % os.path.basename(path))
    mi = RE_ISSUE.search(text)
    b = {'issue': mi.group(1) if mi else '?', 'vol': mi.group(2) if mi else '?',
         'no': int(mi.group(3)) if mi else 0, 'rapid': {}, 'pred': {}, 'cpo': {}, 'tai': None}
    mt = RE_TAI.search(text)
    if mt:
        b['tai'] = (int(mt.group(1)), float(mt.group(2)))
    in_cpo = False
    for ln in text.splitlines():
        if 'IAU2000A Celestial Pole Offset' in ln:
            in_cpo = True
            continue
        m = RE_RAPID.match(ln)
        if m:
            b['rapid'][int(m.group(1))] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))
            continue
        m = RE_PRED.match(ln)
        if m:
            b['pred'][int(m.group(1))] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))
            continue
        if in_cpo:
            m = RE_CPO.match(ln)
            if m:
                b['cpo'][int(m.group(1))] = (float(m.group(2)) / 1000.0, float(m.group(3)) / 1000.0)
    if not b['rapid'] or not b['pred']:
        raise Gagal('%s: bagian rapid/prediksi tidak ditemukan.' % os.path.basename(path))
    return b


def pilih_bulletin(folder):
    best = None
    for p in daftar(folder, BULLETIN_NAME, [r'^bulletin.*\.txt$']):
        try:
            b = baca_bulletin(p)
        except Gagal:
            continue
        if best is None or max(b['rapid']) > max(best[1]['rapid']):
            best = (p, b)
    return best


# ------------------------------- penggabungan -----------------------------
def gabung(H, c04, bul, dAT):
    meta = H['J']['meta']
    M0 = H['M0']
    T = {M0 + i: list(r) for i, r in enumerate(H['rows'])}
    old = {m: list(r) for m, r in T.items()}
    c04_lama, pr_lama, end_lama = int(meta['c04']), int(meta['pr']), M0 + len(H['rows']) - 1

    pakai_c04 = bool(c04) and (FORCE or max(c04) > c04_lama)
    pakai_bul = bool(bul) and (FORCE or max(bul['rapid']) > pr_lama)
    if c04 and not pakai_c04:
        info('  - C04: tidak lebih baru dari data di OSS (MJD %d), dilewati.' % c04_lama)
    if bul and not pakai_bul:
        info('  - Bulletin A: tidak lebih baru dari data di OSS (rapid s.d. MJD %d), dilewati.' % pr_lama)
    if not pakai_c04 and not pakai_bul:
        return None

    c04_akhir = c04_lama
    pr_baru = pr_lama
    end_baru = end_lama

    # --- lapisan Bulletin A (rapid + prediksi) ---
    if pakai_bul:
        bm = {}
        bm.update(bul['pred'])
        bm.update(bul['rapid'])
        cpo = bul['cpo']
        if cpo:
            last_s = max(cpo)
            first_s = min(cpo)
            hold = cpo[last_s]
        else:
            last_s, first_s, hold = None, None, None
        pr_baru = max(bul['rapid'])
        end_baru = max(bm)
        for m in sorted(bm):
            x, y, u = bm[m]
            row = T.get(m, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            row[0], row[1], row[2] = u, x, y
            if cpo:
                if m in cpo:
                    row[3], row[4] = cpo[m]
                elif m > last_s:
                    row[3], row[4] = hold
                elif m < first_s and m not in T:
                    row[3], row[4] = cpo[first_s]
            elif m not in T:
                pass
            T[m] = row
        # dX, dY dari deret baru untuk hari yang tidak tercakup rapid/prediksi
        for m, (dx, dy) in cpo.items():
            if m in T and m not in bm and m > c04_lama:
                T[m][3], T[m][4] = dx, dy
        # buang sisa prediksi lama di luar akhir bulletin baru
        for m in [k for k in T if k > end_baru]:
            del T[m]

    # --- lapisan C04 (final) ---
    if pakai_c04:
        for m, v in c04.items():
            if m >= M0:
                T[m] = list(v)
        c04_akhir = max(max(c04), c04_lama)
        if c04_akhir > pr_baru:
            pr_baru = c04_akhir

    end = max(T)
    # --- kontinuitas ---
    hilang = [m for m in range(M0, end + 1) if m not in T]
    if hilang:
        raise Gagal('Ada celah data (%d hari, mulai MJD %d). Data baru tidak menyambung dengan tabel di OSS; '
                    'butuh berkas C04 atau Bulletin A yang lebih lengkap.' % (len(hilang), hilang[0]))

    # --- LOD untuk hari non-C04: LOD = -d(UT1-TAI)/dt (selisih mundur) ---
    # dihitung ulang hanya untuk baris dari Bulletin A dan baris sambungan tepat setelah C04
    hitung = set([c04_akhir + 1])
    if pakai_bul:
        hitung |= set(bm.keys())
    for m in sorted(x for x in hitung if c04_akhir < x <= end):
        if m - 1 in T:
            a = T[m][0] - dAT(m)
            b = T[m - 1][0] - dAT(m - 1)
            T[m][5] = round(-(a - b), 7)

    # --- pembulatan agar bersih dari derau float ---
    for m in T:
        r = T[m]
        T[m] = [round(r[0], 7), round(r[1], 6), round(r[2], 6), round(r[3], 7), round(r[4], 7), round(r[5], 7)]

    # --- pemeriksaan kewajaran pada daerah yang berubah ---
    berubah = [m for m in T if m not in old or max(abs(T[m][k] - old[m][k]) for k in range(6)) > 5e-8]
    if berubah:
        lo = max(M0 + 1, min(berubah) - 1)
        for m in range(lo, end + 1):
            d = (T[m][0] - dAT(m)) - (T[m - 1][0] - dAT(m - 1))
            if abs(d) > 0.02:
                raise Gagal('UT1-TAI melompat %.3f s pada MJD %d. Kemungkinan ada detik kabisat baru: perbarui tabel '
                            '"const LS" di blok eop-src OSS lebih dulu.' % (d, m))
    for m, r in T.items():
        if abs(r[0]) > 1.0 or abs(r[1]) > 1.0 or abs(r[2]) > 1.0:
            raise Gagal('Nilai tidak wajar pada MJD %d: %s' % (m, r))

    return {'T': T, 'old': old, 'berubah': sorted(berubah), 'c04': c04_akhir, 'pr': pr_baru, 'end': end,
            'pakai_c04': pakai_c04, 'pakai_bul': pakai_bul}


# --------------------------------- tulis ----------------------------------
def tulis(H, hasil, bul, c04_path, bul_path):
    J = H['J']
    M0 = H['M0']
    T = hasil['T']
    meta = J['meta']
    meta['c04'] = hasil['c04']
    meta['pr'] = hasil['pr']
    meta['source'] = ('IERS EOP 20 C04 (final, to MJD %d), IERS Bulletin A rapid (to MJD %d), '
                      'Bulletin A predictions (to MJD %d); daily values at 0h UTC'
                      % (hasil['c04'], hasil['pr'], hasil['end']))
    if hasil['pakai_bul'] and bul:
        meta['bulletin'] = 'Bulletin A Vol. %s No. %03d (%s)' % (bul['vol'], bul['no'], bul['issue'])
    if hasil['pakai_c04'] and c04_path:
        meta['c04_file'] = os.path.basename(c04_path)
    meta['updated'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    J['d'] = [T[m] for m in range(M0, hasil['end'] + 1)]

    blok = json.dumps(J, separators=(',', ':'))
    baru = H['text'][:H['i0']] + blok + H['text'][H['i1']:]

    path = H['path']
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    cadangan = path + '.bak-' + stamp
    shutil.copy2(path, cadangan)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='') as f:
        f.write(baru)
    # verifikasi: baca ulang dan periksa
    cek = baca_teks(tmp)
    i0 = cek.find(TAG_OPEN) + len(TAG_OPEN)
    i1 = cek.find(TAG_CLOSE, i0)
    Jc = json.loads(cek[i0:i1])
    ok = (cek == baru and len(Jc['d']) == len(J['d']) and Jc['meta']['c04'] == hasil['c04']
          and cek[:H['i0']] == H['text'][:H['i0']] and cek[i1:] == H['text'][H['i1']:])
    if not ok:
        os.remove(tmp)
        raise Gagal('Verifikasi berkas hasil gagal; OSS asli tidak diubah.')
    os.replace(tmp, path)

    # rapikan cadangan lama
    baks = sorted(glob.glob(path + '.bak-*'), key=os.path.getmtime, reverse=True)
    for b in baks[KEEP_BACKUPS:]:
        try:
            os.remove(b)
        except OSError:
            pass
    return cadangan


# ---------------------------------- main ----------------------------------
def main():
    global DRY_RUN, FORCE
    if '--dry-run' in sys.argv:
        DRY_RUN = True
    if '--force' in sys.argv:
        FORCE = True

    info('=== Pembaru EOP IERS untuk OSS ΩLDJAVA ===')
    folder = cari_folder()
    info('Folder      :', folder)

    H = muat_html(folder)
    M0 = H['M0']
    meta = H['J']['meta']
    n = len(H['rows'])
    info('OSS         : %s' % os.path.basename(H['path']))
    info('  tabel lama: MJD %d..%d  (C04 s.d. %d, rapid s.d. %d)' % (M0, M0 + n - 1, meta['c04'], meta['pr']))

    LS = H['LS']

    def dAT(m):
        o = 10
        for a, b in LS:
            if m >= a:
                o = b
            else:
                break
        return o

    c = pilih_c04(folder)
    b = pilih_bulletin(folder)
    if not c and not b:
        raise Gagal('Tidak ada berkas C04 atau Bulletin A di folder ini.')
    if c:
        info('C04         : %s  (s.d. MJD %d = %s)' % (os.path.basename(c[0]), max(c[1]), tanggal_dari_mjd(max(c[1]))))
    else:
        info('C04         : (tidak ada)')
    if b:
        bb = b[1]
        info('Bulletin A  : %s  (Vol. %s No. %03d, %s; rapid s.d. MJD %d, prediksi s.d. MJD %d)'
             % (os.path.basename(b[0]), bb['vol'], bb['no'], bb['issue'], max(bb['rapid']), max(bb['pred'])))
        if bb['tai']:
            mt, vt = bb['tai']
            if abs(dAT(mt) - vt) > 1e-6:
                raise Gagal('TAI-UTC di Bulletin A (%.1f s pada MJD %d) berbeda dari tabel LS di OSS (%d s). '
                            'Ada detik kabisat baru: perbarui "const LS" di blok eop-src OSS lebih dulu.'
                            % (vt, mt, dAT(mt)))
    else:
        info('Bulletin A  : (tidak ada)')

    hasil = gabung(H, c[1] if c else None, b[1] if b else None, dAT)
    if hasil is None:
        info('\nOSS sudah memakai data terbaru dari berkas-berkas ini. Tidak ada yang diubah.')
        return

    ch = hasil['berubah']
    info('\nHasil penggabungan:')
    info('  tabel baru: MJD %d..%d  (C04 s.d. %d, rapid s.d. %d)'
         % (M0, hasil['end'], hasil['c04'], hasil['pr']))
    info('  baris berubah/baru: %d' % len(ch))
    bd = [m for m in ch if m in hasil['old']]
    if bd:
        old, T = hasil['old'], hasil['T']
        names = ['UT1-UTC (s)', 'xp (")', 'yp (")', 'dX (")', 'dY (")', 'LOD (s)']
        for k in range(6):
            mx = max(abs(T[m][k] - old[m][k]) for m in bd)
            info('    selisih maks %-11s: %.2e' % (names[k], mx))
    baru_n = len([m for m in ch if m not in hasil['old']])
    if baru_n:
        info('  hari baru ditambahkan di ujung: %d' % baru_n)

    hi = mjd_hari_ini()
    if hi in hasil['T']:
        r = hasil['T'][hi]
        sumber = 'C04' if hi <= hasil['c04'] else ('rapid' if hi <= hasil['pr'] else 'prediksi')
        info('  hari ini (MJD %d, %s): UT1-UTC = %+.5f s, xp = %.4f", yp = %.4f"  [%s]'
             % (hi, tanggal_dari_mjd(hi), r[0], r[1], r[2], sumber))

    if DRY_RUN:
        info('\nDRY_RUN aktif: tidak ada berkas yang ditulis.')
        return

    cad = tulis(H, hasil, b[1] if b else None, c[0] if c else None, b[0] if b else None)
    info('\nSELESAI. OSS diperbarui di tempat.')
    info('Cadangan    : %s' % os.path.basename(cad))
    info('Muat ulang halaman OSS di browser agar data baru terbaca.')


if __name__ == '__main__':
    try:
        main()
    except Gagal as e:
        print('\nGAGAL: %s' % e)
        print('Tidak ada berkas yang diubah.')
