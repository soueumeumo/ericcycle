
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','devkey')
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'os_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Mechanic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<Mechanic {self.name}>"

class ServiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Service {self.description}>"

order_services = db.Table('order_services',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('service_item.id'), primary_key=True)
)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    motorcycle_model = db.Column(db.String(200))
    client_name = db.Column(db.String(200))
    date = db.Column(db.Date, default=datetime.utcnow)
    plate = db.Column(db.String(20))
    km = db.Column(db.Integer)
    year = db.Column(db.String(10))
    color = db.Column(db.String(50))
    error_codes = db.Column(db.String(200))
    obs = db.Column(db.Text)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanic.id'))
    mechanic = db.relationship('Mechanic', backref=db.backref('orders', lazy=True))
    services = db.relationship('ServiceItem', secondary=order_services, lazy='subquery',
                               backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f"<Order {self.id} - {self.client_name}>"

# Create DB if not exists
@app.before_first_request
def create_tables():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Mechanics
@app.route('/mechanics')
def mechanics():
    mecs = Mechanic.query.all()
    return render_template('mechanics.html', mechanics=mecs)

@app.route('/mechanics/add', methods=['GET','POST'])
def add_mechanic():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Nome é obrigatório', 'danger')
            return redirect(url_for('add_mechanic'))
        m = Mechanic(name=name)
        db.session.add(m)
        db.session.commit()
        flash('Mecânico cadastrado', 'success')
        return redirect(url_for('mechanics'))
    return render_template('add_mechanic.html')

# Services
@app.route('/services')
def services():
    items = ServiceItem.query.all()
    return render_template('services.html', services=items)

@app.route('/services/add', methods=['GET','POST'])
def add_service():
    if request.method == 'POST':
        code = request.form.get('code')
        desc = request.form.get('description')
        if not desc:
            flash('Descrição é obrigatória', 'danger')
            return redirect(url_for('add_service'))
        s = ServiceItem(code=code, description=desc)
        db.session.add(s)
        db.session.commit()
        flash('Serviço cadastrado', 'success')
        return redirect(url_for('services'))
    return render_template('add_service.html')

# Orders (OS)
@app.route('/orders')
def orders():
    orders = Order.query.order_by(Order.date.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route('/orders/add', methods=['GET','POST'])
def add_order():
    mechanics = Mechanic.query.all()
    services = ServiceItem.query.all()
    if request.method == 'POST':
        motorcycle_model = request.form.get('motorcycle_model')
        client_name = request.form.get('client_name')
        date_str = request.form.get('date')
        plate = request.form.get('plate')
        km = request.form.get('km') or None
        year = request.form.get('year')
        color = request.form.get('color')
        error_codes = request.form.get('error_codes')
        obs = request.form.get('obs')
        mechanic_id = request.form.get('mechanic_id') or None
        selected_services = request.form.getlist('services')

        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception:
                date = datetime.utcnow().date()
        else:
            date = datetime.utcnow().date()

        order = Order(
            motorcycle_model=motorcycle_model,
            client_name=client_name,
            date=date,
            plate=plate,
            km=int(km) if km else None,
            year=year,
            color=color,
            error_codes=error_codes,
            obs=obs,
            mechanic_id=int(mechanic_id) if mechanic_id else None
        )
        # attach services
        for sid in selected_services:
            s = ServiceItem.query.get(int(sid))
            if s:
                order.services.append(s)

        db.session.add(order)
        db.session.commit()
        flash('Ordem de Serviço criada', 'success')
        return redirect(url_for('orders'))
    return render_template('add_order.html', mechanics=mechanics, services=services)

@app.route('/orders/<int:order_id>')
def view_order(order_id):
    o = Order.query.get_or_404(order_id)
    return render_template('view_order.html', order=o)


if __name__ == '__main__':
    # For local development use: python app.py (will use PORT env if set)
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)

    app.run(host='0.0.0.0', port=10000, debug=True)
