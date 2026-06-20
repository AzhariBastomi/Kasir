# ============================================================
# config.py — Konfigurasi Printer Thermal & MQTT Pager
# ============================================================

import sys, json, os

# ── INFO TOKO (dari toko.json) ──
_toko_path = os.path.join(os.path.dirname(__file__), 'toko.json')
with open(_toko_path, encoding='utf-8') as _f:
    _toko = json.load(_f)

NAMA_TOKO    = _toko['nama_toko']
ALAMAT_TOKO  = _toko['alamat_toko']
TELP_TOKO    = _toko['telp_toko']
FOOTER_STRUK = _toko['footer_struk']

# ── PRINTER USB ──
PRINTER_VENDOR_ID  = 0x0fe6   # Vendor ID printer (lihat di Device Manager / lsusb)
PRINTER_PRODUCT_ID = 0x811e   # Product ID printer
PRINTER_INTERFACE  = 0
PRINTER_IN_EP      = 0x81
PRINTER_OUT_EP     = 0x01

# ── MOCK PRINT (True = skip printer, langsung sukses untuk testing) ──
MOCK_PRINT = False

# ── MQTT BROKER (Mosquitto lokal) ──
MQTT_HOST    = 'localhost'   # IP PC yang jalankan Mosquitto
MQTT_PORT    = 1883
MQTT_USER    = ''            # kosongkan jika tanpa auth
MQTT_PASS    = ''

# Topic format: kasir/pager/{nomor_meja}
# ESP01 subscribe ke: kasir/pager/+  (wildcard semua meja)
MQTT_TOPIC_PREFIX = 'kasir/pager'