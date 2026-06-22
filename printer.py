# ============================================================
# printer.py — Cetak struk ESC/POS via USB
# Butuh: pip install python-escpos
# ============================================================

from escpos.printer import Usb
from config import (PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID, PRINTER_INTERFACE,
                    PRINTER_IN_EP, PRINTER_OUT_EP,
                    NAMA_TOKO, ALAMAT_TOKO, TELP_TOKO, FOOTER_STRUK, MOCK_PRINT)

# ── LEBAR KERTAS (karakter per baris, 80mm = 48 char, 58mm = 32 char) ──
LEBAR = 32  # 58mm


def cetak_struk(struk: dict) -> dict:
    """
    Cetak struk ke printer thermal via USB.
    Jika MOCK_PRINT=True, skip printer dan langsung return sukses.

    struk: {
        nomor_pesanan, nama_pelanggan, nomor_meja,
        waktu, items: [{nama, jumlah, harga_satuan, subtotal}],
        total, catatan
    }
    """
    if MOCK_PRINT:
        print(f"[MOCK PRINT] Struk: {struk['nomor_pesanan']} — Total Rp{struk['total']:,.0f}")
        return {'success': True, 'mock': True}

    try:
        p = Usb(
            PRINTER_VENDOR_ID,
            PRINTER_PRODUCT_ID,
            PRINTER_INTERFACE,
            in_ep=PRINTER_IN_EP,
            out_ep=PRINTER_OUT_EP
        )

        # ── HEADER ──
        # GROOVY ~24pt: Font A, double height
        p.set(align='center', bold=True, font='a', custom_size=True, width=1, height=2)
        p.text(NAMA_TOKO + '\n')
        # Alamat ~20pt: Font A, double height (sedikit lebih kecil pakai bold off)
        p.set(align='center', bold=False, font='a', custom_size=True, width=1, height=2)
        p.text(ALAMAT_TOKO + '\n')
        # Telepon ~14pt: Font A normal
        p.set(align='center', bold=False, font='a', custom_size=True, width=1, height=1)
        p.text(TELP_TOKO + '\n')
        p.text('=' * LEBAR + '\n')

        # ── INFO PESANAN ~14pt ──
        p.set(align='left', font='a', custom_size=True, width=1, height=1)
        p.text(f"No  : {struk['nomor_pesanan']}\n")
        p.text(f"Tgl : {struk['waktu']}\n")
        p.text(f"Meja: {struk['nomor_meja']}   Pelanggan: {struk['nama_pelanggan']}\n")
        p.text('-' * LEBAR + '\n')

        # ── ITEMS ~14pt ──
        p.set(align='left', bold=True, font='a', custom_size=True, width=1, height=1)
        p.text(f"{'Item':<{LEBAR - 12}}{'Qty':>4}{'Harga':>8}\n")
        p.set(bold=False, font='a', custom_size=True, width=1, height=1)
        for item in struk['items']:
            nama = item['nama'][:LEBAR - 14]
            qty_str = f"x{item['jumlah']}"
            harga_str = f"Rp{item['subtotal']:,.0f}"
            sisa = LEBAR - len(qty_str) - len(harga_str)
            p.text(f"{nama:<{sisa}}{qty_str}{harga_str}\n")
            p.text(f"  @Rp{item['harga_satuan']:,.0f}/pcs\n")

        p.text('-' * LEBAR + '\n')

        # ── TOTAL ~14pt bold ──
        p.set(align='left', bold=True, font='a', custom_size=True, width=1, height=1)
        total_str = f"Rp{struk['total']:,.0f}"
        sisa_total = LEBAR - len('TOTAL') - len(total_str)
        p.text(f"TOTAL{' ' * sisa_total}{total_str}\n")
        p.set(bold=False, font='a', custom_size=True, width=1, height=1)
        p.text('=' * LEBAR + '\n')

        # ── CATATAN ~14pt ──
        if struk.get('catatan'):
            p.text(f"Catatan: {struk['catatan']}\n")
            p.text('-' * LEBAR + '\n')

        # ── FOOTER ~20pt: Font A bold ──
        p.set(align='center', bold=True, font='a', custom_size=True, width=1, height=2)
        p.text(FOOTER_STRUK + '\n')
        p.set(custom_size=False)

        # ── CUT ──
        p.cut()
        p.close()

        return {'success': True}

    except Exception as e:
        return {'success': False, 'error': str(e)}


def list_ports() -> list:
    """Kembalikan info printer USB yang dikonfigurasi"""
    return [{'port': f"USB {PRINTER_VENDOR_ID:#06x}:{PRINTER_PRODUCT_ID:#06x}",
             'deskripsi': 'Thermal Printer USB'}]
