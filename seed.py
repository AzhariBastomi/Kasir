"""
seed_db.py — Inject dummy data langsung ke kantin.db
Jalankan SATU KALI sebelum menjalankan app.py:
    python seed_db.py
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
import json
import random
import string

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'kasir.db')

# ─────────────────────────────────────────────
# DATA DUMMY MENU (nama, deskripsi, harga, kategori, gambar)
# Gambar pakai Unsplash source — stabil & gratis
# ─────────────────────────────────────────────
MENU_DUMMY = [
    # ── MAKANAN ──
    {
        "nama": "Nasi Goreng Kampung",
        "deskripsi": "Nasi goreng kecap dengan telur ceplok, kol, dan acar timun",
        "harga": 15000,
        "kategori": "Makanan",
        "gambar": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400&h=300&fit=crop"
    },
    {
        "nama": "Nasi Pecel Ayam",
        "deskripsi": "Nasi putih + ayam goreng + lalapan + sambal",
        "harga": 18000,
        "kategori": "Makanan",
        "gambar": "https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=400&h=300&fit=crop"
    },
    {
        "nama": "Soto Betawi",
        "deskripsi": "Soto kuah santan gurih, daging sapi, tomat, emping",
        "harga": 17000,
        "kategori": "Makanan",
        "gambar": "https://images.unsplash.com/photo-1547592180-85f173990554?w=400&h=300&fit=crop"
    },
    {
        "nama": "Mie Goreng Jawa",
        "deskripsi": "Mie kuning goreng bumbu Jawa, telur, sayuran",
        "harga": 14000,
        "kategori": "Makanan",
        "gambar": "https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=400&h=300&fit=crop"
    },
    {
        "nama": "Lontong Sayur",
        "deskripsi": "Lontong dengan kuah santan, labu siam, tempe, dan telur",
        "harga": 13000,
        "kategori": "Makanan",
        "gambar": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=400&h=300&fit=crop"
    },
    {
        "nama": "Nasi Uduk Komplit",
        "deskripsi": "Nasi uduk + ayam goreng + tempe orek + sambal",
        "harga": 20000,
        "kategori": "Makanan",
        "gambar": "https://images.unsplash.com/photo-1574653853027-5382a3d23a15?w=400&h=300&fit=crop"
    },
    {
        "nama": "Gado-Gado",
        "deskripsi": "Sayuran rebus + tahu + lontong + saus kacang + kerupuk",
        "harga": 13000,
        "kategori": "Makanan",
        "gambar": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=400&h=300&fit=crop"
    },
    {
        "nama": "Tempe & Tahu Goreng",
        "deskripsi": "Tempe mendoan + tahu goreng crispy, cocok jadi lauk",
        "harga": 7000,
        "kategori": "Makanan",
        "gambar": "https://images.unsplash.com/photo-1637806930700-bb45e3fc583d?w=400&h=300&fit=crop"
    },
    # ── MINUMAN ──
    {
        "nama": "Es Teh Manis",
        "deskripsi": "Teh manis dingin segar, minuman wajib warung",
        "harga": 5000,
        "kategori": "Minuman",
        "gambar": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=300&fit=crop"
    },
    {
        "nama": "Es Jeruk Peras",
        "deskripsi": "Jeruk segar diperas langsung, tanpa pemanis buatan",
        "harga": 8000,
        "kategori": "Minuman",
        "gambar": "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=400&h=300&fit=crop"
    },
    {
        "nama": "Kopi Tubruk",
        "deskripsi": "Kopi robusta asli diseduh panas, kental dan mantap",
        "harga": 6000,
        "kategori": "Minuman",
        "gambar": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&h=300&fit=crop"
    },
    {
        "nama": "Jus Alpukat",
        "deskripsi": "Alpukat segar diblender dengan susu dan sedikit gula",
        "harga": 12000,
        "kategori": "Minuman",
        "gambar": "https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?w=400&h=300&fit=crop"
    },
    {
        "nama": "Air Mineral",
        "deskripsi": "Air mineral botol dingin",
        "harga": 4000,
        "kategori": "Minuman",
        "gambar": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400&h=300&fit=crop"
    },
]

# ─────────────────────────────────────────────
# DUMMY PESANAN (3 hari terakhir)
# ─────────────────────────────────────────────
def gen_nomor(tgl):
    prefix = tgl.strftime('%d%m')
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"KSR-{prefix}-{suffix}"

NAMA_PELANGGAN = ["Budi", "Siti", "Andi", "Rina", "Joko",
                  "Dewi", "Agus", "Maya", "Fajar", "Lina"]

def build_pesanan_dummy(menu_rows):
    """Buat pesanan dummy 3 hari terakhir"""
    pesanan_list = []
    item_list = []
    transaksi_map = {}  # date -> {total_pesanan, total_item, pendapatan, detail}

    for hari_lalu in range(2, -1, -1):  # 2 hari lalu, 1 hari lalu, hari ini
        tgl = date.today() - timedelta(days=hari_lalu)
        jumlah_pesanan = random.randint(8, 15)
        transaksi_map[tgl] = {
            'total_pesanan': 0, 'total_item': 0,
            'pendapatan': 0.0, 'detail': {}
        }

        for _ in range(jumlah_pesanan):
            meja = str(random.randint(1, 10))
            nama = random.choice(NAMA_PELANGGAN)
            jam = random.randint(8, 20)
            menit = random.randint(0, 59)
            waktu = datetime(tgl.year, tgl.month, tgl.day, jam, menit, 0)

            nomor = gen_nomor(tgl)
            # pilih 1-3 menu random
            pilihan = random.sample(menu_rows, k=random.randint(1, 3))
            total = 0
            item_rows = []
            for m in pilihan:
                qty = random.randint(1, 3)
                subtotal = m['harga'] * qty
                total += subtotal
                item_rows.append({
                    'menu_id': m['id'], 'jumlah': qty,
                    'harga_satuan': m['harga'], 'subtotal': subtotal,
                    'nama': m['nama'], 'kategori': m['kategori']
                })

            pesanan_list.append({
                'nomor_pesanan': nomor, 'nama_pelanggan': nama,
                'nomor_meja': meja, 'catatan': '',
                'total': total, 'status': 'selesai',
                'tanggal': waktu.isoformat()
            })
            item_list.append(item_rows)

            # Update transaksi harian
            t = transaksi_map[tgl]
            t['total_pesanan'] += 1
            t['pendapatan'] += total
            for ir in item_rows:
                t['total_item'] += ir['jumlah']
                mid = str(ir['menu_id'])
                if mid not in t['detail']:
                    t['detail'][mid] = {'nama': ir['nama'], 'kategori': ir['kategori'],
                                        'jumlah': 0, 'pendapatan': 0}
                t['detail'][mid]['jumlah'] += ir['jumlah']
                t['detail'][mid]['pendapatan'] += ir['subtotal']

    return pesanan_list, item_list, transaksi_map


# ─────────────────────────────────────────────
# INJECT KE DATABASE
# ─────────────────────────────────────────────
def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Buat tabel kalau belum ada
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS menu (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nama      TEXT    NOT NULL,
            deskripsi TEXT,
            harga     REAL    NOT NULL,
            kategori  TEXT,
            gambar    TEXT    DEFAULT '',
            tersedia  INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS pesanan (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            nomor_pesanan  TEXT    UNIQUE NOT NULL,
            nama_pelanggan TEXT    NOT NULL,
            nomor_meja     TEXT,
            catatan        TEXT,
            total          REAL    DEFAULT 0,
            status         TEXT    DEFAULT 'selesai',
            tanggal        TEXT
        );

        CREATE TABLE IF NOT EXISTS item_pesanan (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            pesanan_id   INTEGER NOT NULL REFERENCES pesanan(id),
            menu_id      INTEGER NOT NULL REFERENCES menu(id),
            jumlah       INTEGER NOT NULL,
            harga_satuan REAL    NOT NULL,
            subtotal     REAL    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS transaksi_harian (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal        TEXT    UNIQUE NOT NULL,
            total_pesanan  INTEGER DEFAULT 0,
            total_item     INTEGER DEFAULT 0,
            pendapatan     REAL    DEFAULT 0,
            detail_menu    TEXT    DEFAULT '{}'
        );
    """)

    # ── 1. Insert menu ──
    cur.execute("SELECT COUNT(*) FROM menu")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO menu (nama, deskripsi, harga, kategori, gambar, tersedia) VALUES (?,?,?,?,?,1)",
            [(m['nama'], m['deskripsi'], m['harga'], m['kategori'], m['gambar']) for m in MENU_DUMMY]
        )
        print(f"✅ {len(MENU_DUMMY)} menu berhasil diinsert")
    else:
        print("ℹ️  Tabel menu sudah ada data, skip insert menu")

    conn.commit()

    # Ambil menu rows untuk referensi ID
    cur.execute("SELECT id, nama, harga, kategori FROM menu")
    menu_rows = [{'id': r[0], 'nama': r[1], 'harga': r[2], 'kategori': r[3]}
                 for r in cur.fetchall()]

    # ── 2. Insert pesanan dummy ──
    cur.execute("SELECT COUNT(*) FROM pesanan")
    if cur.fetchone()[0] == 0:
        pesanan_list, item_list, transaksi_map = build_pesanan_dummy(menu_rows)

        for i, p in enumerate(pesanan_list):
            cur.execute(
                "INSERT INTO pesanan (nomor_pesanan, nama_pelanggan, nomor_meja, catatan, total, status, tanggal) VALUES (?,?,?,?,?,?,?)",
                (p['nomor_pesanan'], p['nama_pelanggan'], p['nomor_meja'],
                 p['catatan'], p['total'], p['status'], p['tanggal'])
            )
            pesanan_id = cur.lastrowid
            for item in item_list[i]:
                cur.execute(
                    "INSERT INTO item_pesanan (pesanan_id, menu_id, jumlah, harga_satuan, subtotal) VALUES (?,?,?,?,?)",
                    (pesanan_id, item['menu_id'], item['jumlah'],
                     item['harga_satuan'], item['subtotal'])
                )

        # ── 3. Insert transaksi harian ──
        for tgl, data in transaksi_map.items():
            cur.execute(
                "INSERT OR REPLACE INTO transaksi_harian (tanggal, total_pesanan, total_item, pendapatan, detail_menu) VALUES (?,?,?,?,?)",
                (tgl.isoformat(), data['total_pesanan'], data['total_item'],
                 data['pendapatan'], json.dumps(data['detail']))
            )

        conn.commit()
        total_p = len(pesanan_list)
        print(f"✅ {total_p} pesanan dummy berhasil diinsert (3 hari terakhir)")
        print(f"✅ Transaksi harian untuk {len(transaksi_map)} hari berhasil diinsert")
    else:
        print("ℹ️  Tabel pesanan sudah ada data, skip insert pesanan dummy")

    conn.close()

    print("\n🎉 Selesai! Database siap digunakan.")
    print(f"📁 Lokasi DB: {DB_PATH}")
    print("▶️  Sekarang jalankan: python app.py")


if __name__ == '__main__':
    main()