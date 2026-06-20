# ============================================================
# config.py — Konfigurasi Printer Thermal & MQTT Pager
# ============================================================

import sys

# ── PORT PRINTER ──
if sys.platform == 'win32':
    PRINTER_PORT = 'COM3'          # Ganti sesuai Device Manager
else:
    PRINTER_PORT = '/dev/ttyUSB0'  # Ganti sesuai: ls /dev/tty*

PRINTER_BAUDRATE = 9600

# ── MOCK PRINT (True = skip printer, langsung sukses untuk testing) ──
MOCK_PRINT = True

# ── INFO TOKO ──
NAMA_TOKO    = 'WARUNG MAKAN BAROKAH'
ALAMAT_TOKO  = 'Jl. Merdeka No. 10, Jakarta'
TELP_TOKO    = '0812-3456-7890'
FOOTER_STRUK = 'Terima kasih, selamat menikmati!'

# ── MQTT BROKER (Mosquitto lokal) ──
MQTT_HOST    = 'localhost'   # IP PC yang jalankan Mosquitto
MQTT_PORT    = 1883
MQTT_USER    = ''            # kosongkan jika tanpa auth
MQTT_PASS    = ''

# Topic format: kasir/pager/{nomor_meja}
# ESP01 subscribe ke: kasir/pager/+  (wildcard semua meja)
MQTT_TOPIC_PREFIX = 'kasir/pager'