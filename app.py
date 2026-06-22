from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import json, random, string
from config import NAMA_TOKO, ALAMAT_TOKO, TELP_TOKO, FOOTER_STRUK
from printer import cetak_struk
from mqtt_client import panggil_meja, reset_meja

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kasir.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kasir-secret-2024'
db = SQLAlchemy(app)

# ==================== MODELS ====================

class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.String(200))
    harga = db.Column(db.Float, nullable=False)
    kategori = db.Column(db.String(50))  # 'Makanan' atau 'Minuman'
    gambar = db.Column(db.String(300), default='')   # URL foto makanan
    tersedia = db.Column(db.Boolean, default=True)
    order_items = db.relationship('ItemPesanan', backref='menu', lazy=True)


class Pesanan(db.Model):
    __tablename__ = 'pesanan'
    id = db.Column(db.Integer, primary_key=True)
    nomor_pesanan = db.Column(db.String(20), unique=True, nullable=False)
    nama_pelanggan = db.Column(db.String(100), nullable=False)
    nomor_meja = db.Column(db.String(10))
    catatan = db.Column(db.String(300))
    total = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='selesai')  # langsung selesai setelah print
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('ItemPesanan', backref='pesanan', lazy=True)


class ItemPesanan(db.Model):
    __tablename__ = 'item_pesanan'
    id = db.Column(db.Integer, primary_key=True)
    pesanan_id = db.Column(db.Integer, db.ForeignKey('pesanan.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    harga_satuan = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)


class TransaksiHarian(db.Model):
    __tablename__ = 'transaksi_harian'
    id = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.Date, unique=True, nullable=False, default=date.today)
    total_pesanan = db.Column(db.Integer, default=0)       # jumlah transaksi
    total_item = db.Column(db.Integer, default=0)          # total item terjual
    pendapatan = db.Column(db.Float, default=0)            # total uang
    detail_menu = db.Column(db.Text, default='{}')         # JSON: {menu_id: {nama, jumlah, pendapatan}}

    def get_detail(self):
        return json.loads(self.detail_menu or '{}')

    def set_detail(self, data):
        self.detail_menu = json.dumps(data)

# ==================== HELPERS ====================

def generate_nomor_pesanan():
    prefix = datetime.now().strftime('%d%m')
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"KSR-{prefix}-{suffix}"


def update_transaksi_harian(pesanan):
    """Update/buat record transaksi harian setelah pesanan selesai"""
    hari_ini = date.today()
    transaksi = TransaksiHarian.query.filter_by(tanggal=hari_ini).first()
    if not transaksi:
        transaksi = TransaksiHarian(tanggal=hari_ini, total_pesanan=0, total_item=0, pendapatan=0)
        db.session.add(transaksi)

    transaksi.total_pesanan += 1
    transaksi.pendapatan += pesanan.total

    detail = transaksi.get_detail()
    for item in pesanan.items:
        mid = str(item.menu_id)
        if mid not in detail:
            detail[mid] = {'nama': item.menu.nama, 'kategori': item.menu.kategori,
                           'jumlah': 0, 'pendapatan': 0}
        detail[mid]['jumlah'] += item.jumlah
        detail[mid]['pendapatan'] += item.subtotal
        transaksi.total_item += item.jumlah

    transaksi.set_detail(detail)
    db.session.commit()


# ==================== ROUTES ====================

@app.route('/')
def index():
    return redirect(url_for('menu'))


@app.route('/menu')
def menu():
    kategori_list = db.session.query(Menu.kategori).distinct().all()
    kategori_list = [k[0] for k in kategori_list]
    menu_items = Menu.query.filter_by(tersedia=True).all()
    return render_template('menu.html', menu_items=menu_items, kategori_list=kategori_list)


@app.route('/checkout', methods=['POST'])
def checkout():
    """Buat pesanan dan langsung kembalikan data struk untuk print"""
    data = request.json
    cart = data.get('cart', [])
    nama_pelanggan = data.get('nama_pelanggan', 'Pelanggan')
    nomor_meja = data.get('nomor_meja', '-')
    catatan = data.get('catatan', '')

    if not cart:
        return jsonify({'success': False, 'message': 'Keranjang kosong!'})

    pesanan = Pesanan(
        nomor_pesanan=generate_nomor_pesanan(),
        nama_pelanggan=nama_pelanggan,
        nomor_meja=nomor_meja,
        catatan=catatan,
        status='selesai'
    )
    db.session.add(pesanan)
    db.session.flush()

    total = 0
    items_data = []
    for item_data in cart:
        menu_item = db.session.get(Menu, item_data['id'])
        if menu_item:
            subtotal = menu_item.harga * item_data['qty']
            total += subtotal
            oi = ItemPesanan(
                pesanan_id=pesanan.id,
                menu_id=menu_item.id,
                jumlah=item_data['qty'],
                harga_satuan=menu_item.harga,
                subtotal=subtotal
            )
            db.session.add(oi)
            items_data.append({
                'nama': menu_item.nama,
                'jumlah': item_data['qty'],
                'harga_satuan': menu_item.harga,
                'subtotal': subtotal
            })

    pesanan.total = total
    db.session.commit()

    # Update transaksi harian
    # Re-query agar items ter-load
    pesanan_reload = db.session.get(Pesanan, pesanan.id)
    update_transaksi_harian(pesanan_reload)

    waktu = pesanan.tanggal.strftime('%d/%m/%Y %H:%M')

    struk_data = {
        'nomor_pesanan': pesanan.nomor_pesanan,
        'nama_pelanggan': nama_pelanggan,
        'nomor_meja': nomor_meja,
        'catatan': catatan,
        'items': items_data,
        'total': total,
        'waktu': waktu
    }

    return jsonify({
        'success': True,
        'struk': struk_data
    })


@app.route('/print/<nomor_pesanan>', methods=['POST'])
def print_struk(nomor_pesanan):
    """Cetak struk langsung ke printer USB di Raspberry Pi"""
    pesanan = Pesanan.query.filter_by(nomor_pesanan=nomor_pesanan).first_or_404()
    struk_data = {
        'nomor_pesanan': pesanan.nomor_pesanan,
        'nama_pelanggan': pesanan.nama_pelanggan,
        'nomor_meja': pesanan.nomor_meja or '-',
        'catatan': pesanan.catatan or '',
        'waktu': pesanan.tanggal.strftime('%d/%m/%Y %H:%M'),
        'items': [
            {
                'nama': item.menu.nama,
                'jumlah': item.jumlah,
                'harga_satuan': item.harga_satuan,
                'subtotal': item.subtotal
            } for item in pesanan.items
        ],
        'total': pesanan.total
    }
    hasil = cetak_struk(struk_data)
    return jsonify(hasil)



@app.route('/admin')
def admin():
    pesanan_list = Pesanan.query.order_by(Pesanan.tanggal.desc()).limit(50).all()
    transaksi_hari_ini = TransaksiHarian.query.filter_by(tanggal=date.today()).first()
    return render_template('admin.html', pesanan_list=pesanan_list,
                           transaksi=transaksi_hari_ini)


@app.route('/laporan')
def laporan():
    transaksi_list = TransaksiHarian.query.order_by(TransaksiHarian.tanggal.desc()).limit(30).all()
    return render_template('laporan.html', transaksi_list=transaksi_list)


@app.route('/admin/menu')
def admin_menu():
    menu_list = Menu.query.order_by(Menu.kategori, Menu.nama).all()
    return render_template('admin_menu.html', menu_list=menu_list)


@app.route('/api/menu/toggle/<int:menu_id>', methods=['POST'])
def toggle_menu(menu_id):
    item = Menu.query.get_or_404(menu_id)
    item.tersedia = not item.tersedia
    db.session.commit()
    return jsonify({'success': True, 'tersedia': item.tersedia})


@app.route('/api/menu/tambah', methods=['POST'])
def tambah_menu():
    data = request.json
    item = Menu(
        nama=data['nama'],
        deskripsi=data.get('deskripsi', ''),
        harga=float(data['harga']),
        kategori=data['kategori'],
        gambar=data.get('gambar', '')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'success': True, 'id': item.id})


@app.route('/api/menu/edit/<int:menu_id>', methods=['POST'])
def edit_menu(menu_id):
    item = Menu.query.get_or_404(menu_id)
    data = request.json
    item.nama = data.get('nama', item.nama)
    item.deskripsi = data.get('deskripsi', item.deskripsi)
    item.harga = float(data.get('harga', item.harga))
    item.kategori = data.get('kategori', item.kategori)
    item.gambar = data.get('gambar', item.gambar)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/menu/hapus/<int:menu_id>', methods=['POST'])
def hapus_menu(menu_id):
    item = Menu.query.get_or_404(menu_id)
    item.tersedia = False  # soft delete
    db.session.commit()
    return jsonify({'success': True})


@app.route('/panggilan')
def panggilan():
    """Halaman kasir untuk panggil meja via pager ESP01"""
    # Ambil pesanan yang sudah masuk (status selesai) hari ini
    from datetime import date
    pesanan_aktif = Pesanan.query.filter(
        db.func.date(Pesanan.tanggal) == date.today()
    ).order_by(Pesanan.tanggal.desc()).all()
    return render_template('panggilan.html', pesanan_aktif=pesanan_aktif)


@app.route('/api/pager/panggil', methods=['POST'])
def api_panggil_meja():
    """Publish MQTT ke ESP01 untuk panggil meja"""
    data = request.json
    nomor_meja = data.get('nomor_meja', '')
    if not nomor_meja:
        return jsonify({'success': False, 'error': 'Nomor meja kosong'})
    result = panggil_meja(str(nomor_meja))
    return jsonify(result)


@app.route('/api/pager/reset', methods=['POST'])
def api_reset_meja():
    """Publish MQTT reset ke ESP01 (matikan buzzer+LED)"""
    data = request.json
    nomor_meja = data.get('nomor_meja', '')
    if not nomor_meja:
        return jsonify({'success': False, 'error': 'Nomor meja kosong'})
    result = reset_meja(str(nomor_meja))
    return jsonify(result)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)