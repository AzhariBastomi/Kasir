import webbrowser, os, tempfile

HTML = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>Test Struk</title>
<style>
  @page { size: 58mm auto; margin: 0; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 58mm;
    font-family: 'Courier New', Courier, monospace;
    font-size: 11px;
    line-height: 1.4;
    color: #000;
    background: #fff;
    padding: 4mm 3mm 0 3mm;
  }
  .center { text-align: center; }
  .toko-nama { font-size: 15px; font-weight: bold; text-transform: uppercase; }
  .toko-info { font-size: 10px; margin-top: 2px; }
  .garis { border-top: 1px dashed #000; margin: 6px 0; }
  .info-transaksi { font-size: 10px; margin-bottom: 4px; }
  .info-transaksi div { display: flex; justify-content: space-between; }
  table.item { width: 100%; border-collapse: collapse; }
  .item-row td { vertical-align: top; padding: 1px 0; font-size: 11px; }
  .item-nama { width: 100%; }
  .item-detail { font-size: 10px; padding-left: 2px; }
  .qty-col { white-space: nowrap; padding-right: 4px; }
  .harga-col { text-align: right; white-space: nowrap; }
  .ringkasan div { display: flex; justify-content: space-between; font-size: 11px; }
  .total { font-size: 13px; font-weight: bold; }
  .footer { margin-top: 8px; font-size: 10px; }
  .no-print { text-align: center; margin-bottom: 10px; }
  @media print { .no-print { display: none; } }
  .no-print button { font-family: Arial, sans-serif; padding: 8px 20px; font-size: 13px; cursor: pointer; }
</style>
</head>
<body>

<div class="no-print">
  <button onclick="window.print()">🖨️ Cetak Struk</button>
</div>

<div class="center toko-nama">GROOVY</div>
<div class="center toko-info">
  Gedung JB Tower B1<br>
  Telp: 0812-3456-7890
</div>
<div class="garis"></div>

<div class="info-transaksi">
  <div><span>No. Struk</span><span>KSR-2506-1234</span></div>
  <div><span>Tanggal</span><span>20/06/2026 09:55</span></div>
  <div><span>Meja</span><span>3</span></div>
  <div><span>Pelanggan</span><span>Budi</span></div>
</div>
<div class="garis"></div>

<table class="item">
  <tr class="item-row">
    <td colspan="3" class="item-nama">Soto Betawi</td>
  </tr>
  <tr class="item-row">
    <td class="qty-col item-detail">2 x 15.000</td>
    <td></td>
    <td class="harga-col">30.000</td>
  </tr>
  <tr class="item-row">
    <td colspan="3" class="item-nama">Es Teh Manis</td>
  </tr>
  <tr class="item-row">
    <td class="qty-col item-detail">3 x 5.000</td>
    <td></td>
    <td class="harga-col">15.000</td>
  </tr>
  <tr class="item-row">
    <td colspan="3" class="item-nama">Nasi Goreng</td>
  </tr>
  <tr class="item-row">
    <td class="qty-col item-detail">1 x 18.000</td>
    <td></td>
    <td class="harga-col">18.000</td>
  </tr>
</table>
<div class="garis"></div>

<div class="ringkasan total">
  <div><span>TOTAL</span><span>Rp 63.000</span></div>
</div>
<div class="garis"></div>

<div class="center footer">
  Terima kasih, selamat menikmati!<br>
  Simpan struk ini sebagai bukti pembelian.
</div>

</body>
</html>"""

# Simpan ke file sementara lalu buka di browser
tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8')
tmp.write(HTML)
tmp.close()

webbrowser.open('file://' + tmp.name)
print(f"Struk dibuka di browser: {tmp.name}")
