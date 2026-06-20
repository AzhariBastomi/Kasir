# ============================================================
# printer.py — Cetak struk ESC/POS via Serial Port
# Support: Windows (COMx) & Linux (/dev/ttyUSBx)
# Butuh: pip install pyserial
# ============================================================

import serial
import serial.tools.list_ports
from config import PRINTER_PORT, PRINTER_BAUDRATE, NAMA_TOKO, ALAMAT_TOKO, TELP_TOKO, FOOTER_STRUK, MOCK_PRINT

# ── ESC/POS COMMANDS ──
ESC  = b'\x1b'
GS   = b'\x1d'
INIT = ESC + b'@'                  # Reset printer
FEED = b'\n'

# Align
ALIGN_LEFT   = ESC + b'a\x00'
ALIGN_CENTER = ESC + b'a\x01'
ALIGN_RIGHT  = ESC + b'a\x02'

# Font size
BOLD_ON      = ESC + b'E\x01'
BOLD_OFF     = ESC + b'E\x00'
DOUBLE_ON    = GS  + b'!\x11'     # Double width + height
DOUBLE_OFF   = GS  + b'!\x00'     # Normal size

# Cut
CUT_FULL     = GS  + b'V\x00'
CUT_PARTIAL  = GS  + b'V\x01'

# Feed lines
def feed(n=1):
    return FEED * n

# ── LEBAR KERTAS (karakter per baris, 80mm = 48 char, 58mm = 32 char) ──
LEBAR = 48  # ganti 32 kalau kertas 58mm

def baris_tengah(teks):
    """Teks rata tengah sesuai lebar kertas"""
    return teks.center(LEBAR).encode('utf-8') + FEED

def baris_kiri(teks):
    return teks.ljust(LEBAR).encode('utf-8')[:LEBAR] + FEED

def baris_kanan(teks):
    return teks.rjust(LEBAR).encode('utf-8')[:LEBAR] + FEED

def garis(karakter='-'):
    return (karakter * LEBAR).encode('utf-8') + FEED

def baris_dua_kolom(kiri, kanan):
    """Kiri rata kiri, kanan rata kanan dalam satu baris"""
    sisa = LEBAR - len(kanan)
    kiri_crop = kiri[:sisa].ljust(sisa)
    return (kiri_crop + kanan).encode('utf-8') + FEED

def baris_item(nama, qty, harga_satuan, subtotal):
    """
    Baris item pesanan:
    Nama item (maks 24 char)     x2   Rp12.000
    """
    # Baris pertama: nama + qty + subtotal
    subtotal_str = f"Rp{subtotal:,.0f}"
    qty_str      = f"x{qty}"
    sisa         = LEBAR - len(subtotal_str)
    nama_crop    = nama[:sisa - len(qty_str) - 1].ljust(sisa - len(qty_str) - 1)
    baris1       = (nama_crop + ' ' + qty_str + subtotal_str).encode('utf-8') + FEED
    # Baris kedua: harga satuan (indent)
    baris2       = f"  @Rp{harga_satuan:,.0f}/pcs".encode('utf-8') + FEED
    return baris1 + baris2


def build_struk(struk: dict) -> bytes:
    """
    Bangun bytes ESC/POS dari dict struk:
    {
        nomor_pesanan, nama_pelanggan, nomor_meja,
        waktu, items: [{nama, jumlah, harga_satuan, subtotal}],
        total, catatan
    }
    """
    data = bytearray()
    data += INIT

    # ── HEADER ──
    data += ALIGN_CENTER
    data += DOUBLE_ON
    data += (NAMA_TOKO + '\n').encode('utf-8')
    data += DOUBLE_OFF
    data += (ALAMAT_TOKO + '\n').encode('utf-8')
    data += (TELP_TOKO   + '\n').encode('utf-8')
    data += garis('=')

    # ── INFO PESANAN ──
    data += ALIGN_LEFT
    data += baris_dua_kolom('No  : ' + struk['nomor_pesanan'], '')
    data += baris_dua_kolom('Tgl : ' + struk['waktu'],         '')
    data += baris_dua_kolom('Meja: ' + str(struk['nomor_meja']),
                             'Kasir: ' + struk['nama_pelanggan'])
    data += garis('-')

    # ── ITEMS ──
    data += BOLD_ON
    data += baris_kiri('ITEM')
    data += BOLD_OFF
    for item in struk['items']:
        data += baris_item(
            item['nama'],
            item['jumlah'],
            item['harga_satuan'],
            item['subtotal']
        )

    data += garis('-')

    # ── TOTAL ──
    data += BOLD_ON
    data += DOUBLE_ON
    data += baris_dua_kolom('TOTAL', f"Rp{struk['total']:,.0f}")
    data += DOUBLE_OFF
    data += BOLD_OFF
    data += garis('=')

    # ── CATATAN ──
    if struk.get('catatan'):
        data += ALIGN_LEFT
        data += ('Catatan: ' + struk['catatan'] + '\n').encode('utf-8')
        data += garis('-')

    # ── FOOTER ──
    data += ALIGN_CENTER
    data += (FOOTER_STRUK + '\n').encode('utf-8')
    data += feed(3)

    # ── CUT ──
    data += CUT_PARTIAL

    return bytes(data)


def cetak_struk(struk: dict) -> dict:
    """
    Kirim struk ke printer thermal via serial.
    Jika MOCK_PRINT=True, skip printer dan langsung return sukses.
    """
    if MOCK_PRINT:
        print(f"[MOCK PRINT] Struk: {struk['nomor_pesanan']} — Total Rp{struk['total']:,.0f}")
        return {'success': True, 'mock': True}

    try:
        with serial.Serial(
            port=PRINTER_PORT,
            baudrate=PRINTER_BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=3
        ) as ser:
            data = build_struk(struk)
            ser.write(data)
            ser.flush()
        return {'success': True}

    except serial.SerialException as e:
        return {'success': False, 'error': f'Port {PRINTER_PORT} tidak ditemukan: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def list_ports() -> list:
    """List semua serial port yang tersedia di sistem"""
    ports = serial.tools.list_ports.comports()
    return [{'port': p.device, 'deskripsi': p.description} for p in ports]