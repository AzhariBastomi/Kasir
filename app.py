from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json, os, random, string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kantin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kantin-secret-2024'

db = SQLAlchemy(app)

# ==================== MODELS ====================

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    image_emoji = db.Column(db.String(10), default='🍽️')
    available = db.Column(db.Boolean, default=True)
    orders = db.relationship('OrderItem', backref='menu_item', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    table_number = db.Column(db.String(10))
    status = db.Column(db.String(30), default='pending')  # pending, paid, preparing, ready, done
    total_amount = db.Column(db.Float, default=0)
    payment_method = db.Column(db.String(30))
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, paid
    pager_number = db.Column(db.Integer)
    notes = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

class PagerDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pager_number = db.Column(db.Integer, unique=True, nullable=False)
    status = db.Column(db.String(20), default='available')  # available, in_use, calling, charging
    battery = db.Column(db.Integer, default=100)
    last_called = db.Column(db.DateTime)
    current_order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)

# ==================== HELPERS ====================

def generate_order_number():
    prefix = datetime.now().strftime('%m%d')
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"KTN-{prefix}-{suffix}"

def seed_data():
    if MenuItem.query.count() == 0:
        items = [
            MenuItem(name="Nasi Goreng Spesial", description="Nasi goreng dengan telur, ayam, dan sayuran segar", price=18000, category="Makanan Berat", image_emoji="🍳"),
            MenuItem(name="Mie Ayam Bakso", description="Mie kuning dengan potongan ayam dan bakso sapi", price=15000, category="Makanan Berat", image_emoji="🍜"),
            MenuItem(name="Ayam Geprek", description="Ayam goreng crispy geprek dengan sambal level", price=20000, category="Makanan Berat", image_emoji="🍗"),
            MenuItem(name="Soto Ayam", description="Soto kuning dengan ayam suwir dan pelengkap", price=14000, category="Makanan Berat", image_emoji="🥣"),
            MenuItem(name="Gado-Gado", description="Sayuran rebus dengan saus kacang khas", price=13000, category="Makanan Ringan", image_emoji="🥗"),
            MenuItem(name="Pisang Goreng", description="Pisang goreng crispy dengan taburan gula", price=8000, category="Snack", image_emoji="🍌"),
            MenuItem(name="Tempe Mendoan", description="Tempe tipis goreng tepung krispy", price=6000, category="Snack", image_emoji="🟤"),
            MenuItem(name="Es Teh Manis", description="Teh manis dingin segar", price=5000, category="Minuman", image_emoji="🧋"),
            MenuItem(name="Es Jeruk", description="Jeruk peras segar dengan es", price=7000, category="Minuman", image_emoji="🍊"),
            MenuItem(name="Jus Alpukat", description="Jus alpukat creamy dengan susu", price=12000, category="Minuman", image_emoji="🥑"),
            MenuItem(name="Air Mineral", description="Air mineral dingin", price=3000, category="Minuman", image_emoji="💧"),
            MenuItem(name="Kopi Hitam", description="Kopi robusta murni", price=6000, category="Minuman", image_emoji="☕"),
        ]
        db.session.bulk_save_objects(items)

    if PagerDevice.query.count() == 0:
        pagers = [PagerDevice(pager_number=i, battery=random.randint(60, 100)) for i in range(1, 21)]
        db.session.bulk_save_objects(pagers)

    db.session.commit()

# ==================== ROUTES ====================

@app.route('/')
def index():
    return redirect(url_for('menu'))

@app.route('/menu')
def menu():
    categories = db.session.query(MenuItem.category).distinct().all()
    categories = [c[0] for c in categories]
    menu_items = MenuItem.query.filter_by(available=True).all()
    return render_template('menu.html', menu_items=menu_items, categories=categories)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        data = request.json
        cart = data.get('cart', [])
        customer_name = data.get('customer_name', 'Pelanggan')
        table_number = data.get('table_number', '-')
        notes = data.get('notes', '')

        if not cart:
            return jsonify({'success': False, 'message': 'Keranjang kosong!'})

        order = Order(
            order_number=generate_order_number(),
            customer_name=customer_name,
            table_number=table_number,
            notes=notes,
            status='pending',
            payment_status='unpaid'
        )
        db.session.add(order)
        db.session.flush()

        total = 0
        for item_data in cart:
            menu_item = MenuItem.query.get(item_data['id'])
            if menu_item:
                subtotal = menu_item.price * item_data['qty']
                total += subtotal
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=menu_item.id,
                    quantity=item_data['qty'],
                    unit_price=menu_item.price,
                    subtotal=subtotal
                )
                db.session.add(order_item)

        order.total_amount = total
        db.session.commit()
        return jsonify({'success': True, 'order_id': order.id, 'order_number': order.order_number})

    return render_template('checkout.html')

@app.route('/payment/<int:order_id>')
def payment(order_id):
    order = Order.query.get_or_404(order_id)
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    return render_template('payment.html', order=order, order_items=order_items)

@app.route('/api/pay/<int:order_id>', methods=['POST'])
def process_payment(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.json
    payment_method = data.get('method', 'cash')

    # Assign pager
    pager = PagerDevice.query.filter_by(status='available').first()
    if pager:
        pager.status = 'in_use'
        pager.current_order_id = order.id
        order.pager_number = pager.pager_number

    order.payment_method = payment_method
    order.payment_status = 'paid'
    order.status = 'preparing'
    order.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'pager_number': order.pager_number,
        'order_number': order.order_number,
        'message': f'Pembayaran berhasil! Ambil pager nomor {order.pager_number}'
    })

@app.route('/pager')
def pager_dashboard():
    pagers = PagerDevice.query.order_by(PagerDevice.pager_number).all()
    orders_preparing = Order.query.filter_by(status='preparing').all()
    orders_ready = Order.query.filter_by(status='ready').all()
    return render_template('pager.html', pagers=pagers,
                           orders_preparing=orders_preparing,
                           orders_ready=orders_ready)

@app.route('/api/pager/call/<int:pager_number>', methods=['POST'])
def call_pager(pager_number):
    pager = PagerDevice.query.filter_by(pager_number=pager_number).first_or_404()
    pager.status = 'calling'
    pager.last_called = datetime.utcnow()

    # Update related order
    order = Order.query.filter_by(pager_number=pager_number, status='preparing').first()
    if order:
        order.status = 'ready'
        order.updated_at = datetime.utcnow()

    db.session.commit()
    return jsonify({'success': True, 'message': f'Pager {pager_number} dipanggil!'})

@app.route('/api/pager/reset/<int:pager_number>', methods=['POST'])
def reset_pager(pager_number):
    pager = PagerDevice.query.filter_by(pager_number=pager_number).first_or_404()
    pager.status = 'available'
    pager.current_order_id = None

    order = Order.query.filter_by(pager_number=pager_number).filter(
        Order.status.in_(['ready', 'preparing'])).first()
    if order:
        order.status = 'done'
        order.updated_at = datetime.utcnow()

    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/pager/battery/<int:pager_number>', methods=['POST'])
def update_battery(pager_number):
    pager = PagerDevice.query.filter_by(pager_number=pager_number).first_or_404()
    data = request.json
    pager.battery = data.get('battery', pager.battery)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin')
def admin():
    orders = Order.query.order_by(Order.created_at.desc()).limit(50).all()
    total_today = db.session.query(db.func.sum(Order.total_amount)).filter(
        db.func.date(Order.created_at) == datetime.now().date(),
        Order.payment_status == 'paid'
    ).scalar() or 0
    count_today = Order.query.filter(
        db.func.date(Order.created_at) == datetime.now().date()).count()
    return render_template('admin.html', orders=orders,
                           total_today=total_today, count_today=count_today)

@app.route('/api/orders')
def api_orders():
    orders = Order.query.order_by(Order.created_at.desc()).limit(20).all()
    result = []
    for o in orders:
        result.append({
            'id': o.id, 'order_number': o.order_number,
            'customer_name': o.customer_name, 'status': o.status,
            'payment_status': o.payment_status, 'total_amount': o.total_amount,
            'pager_number': o.pager_number, 'table_number': o.table_number,
            'created_at': o.created_at.strftime('%H:%M')
        })
    return jsonify(result)

@app.route('/api/pagers')
def api_pagers():
    pagers = PagerDevice.query.all()
    return jsonify([{
        'pager_number': p.pager_number, 'status': p.status,
        'battery': p.battery, 'current_order_id': p.current_order_id
    } for p in pagers])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
