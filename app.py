from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from config import Config
from app.models import db, Schedule, User, Invoice
import os
import logging
import secrets
import re
from logging.handlers import RotatingFileHandler
from flask_mail import Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///acai_schedule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)

db.init_app(app)

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.info('App startup')

def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    schedules = Schedule.query.all()
    total = len(schedules)
    confirmed = sum(1 for s in schedules if s.status == 'confirmado')
    canceled = sum(1 for s in schedules if s.status == 'cancelado')
    in_transit = sum(1 for s in schedules if s.status == 'em trânsito')
    
    if total > 0:
        confirmed_percentage = (confirmed / total) * 100
        canceled_percentage = (canceled / total) * 100
        in_transit_percentage = (in_transit / total) * 100
    else:
        confirmed_percentage = canceled_percentage = in_transit_percentage = 0
    
    return render_template('index.html', schedules=schedules,
                           confirmed_percentage=confirmed_percentage,
                           canceled_percentage=canceled_percentage,
                           in_transit_percentage=in_transit_percentage)

@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.debug(f'Método da requisição: {request.method}')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        app.logger.debug(f'Formulário recebido - Usuário: {username}')
        flash('Login successful!', 'success')
        session['logged_in'] = True
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cpf = request.form['cpf']
        
        if not is_valid_cpf(cpf):
            flash('CPF inválido. Deve ter 11 dígitos.', 'danger')
            return redirect(url_for('register'))
        
        existing_user = User.query.filter_by(cpf=cpf).first()
        if existing_user:
            flash('CPF já cadastrado. Tente outro.', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=generate_password_hash(password), cpf=cpf)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registro bem-sucedido!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

def is_valid_cpf(cpf):
    cpf_pattern = re.compile(r'\d{3}\.\d{3}\.\d{3}-\d{2}')
    return cpf_pattern.match(cpf) is not None

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_schedule():
    date = request.form.get('date')
    time = request.form.get('time')
    truck = request.form.get('truck')
    status = request.form.get('status')

    new_schedule = Schedule(date=date, time=time, truck=truck, status=status)
    db.session.add(new_schedule)
    db.session.commit()

    flash('Agendamento adicionado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_schedule(id):
    schedule = Schedule.query.get(id)
    db.session.delete(schedule)
    db.session.commit()

    flash('Agendamento deletado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['POST'])
def update_schedule(id):
    schedule = Schedule.query.get(id)
    schedule.date = request.form.get('date')
    schedule.time = request.form.get('time')
    schedule.truck = request.form.get('truck')
    schedule.status = request.form.get('status')

    db.session.commit()

    flash('Agendamento atualizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/schedules')
def view_schedules():
    schedules = Schedule.query.all()
    total = len(schedules)
    if total == 0:
        percentuais = {
            'confirmado': 0,
            'pendente': 0,
            'cancelado': 0
        }
    else:
        status_counts = {
            'confirmado': 0,
            'pendente': 0,
            'cancelado': 0
        }
        for schedule in schedules:
            status_counts[schedule.status] += 1
        
        percentuais = {
            status: (count / total) * 100 for status, count in status_counts.items()
        }
    
    return render_template('schedules.html', schedules=schedules, percentuais=percentuais)

@app.route('/api/schedules')
def api_schedules():
    schedules = Schedule.query.all()
    return jsonify([schedule.to_dict() for schedule in schedules])

@app.route('/register_schedule', methods=['GET', 'POST'])
def register_schedule():
    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time')
        truck = request.form.get('truck')
        status = request.form.get('status')

        new_schedule = Schedule(date=date, time=time, truck=truck, status=status)
        db.session.add(new_schedule)
        db.session.commit()

        flash('Agendamento adicionado com sucesso!', 'success')
        return redirect(url_for('index'))
    
    return render_template('register_schedule.html')

@app.route('/financeiro')
def financeiro():
    invoices = Invoice.query.filter_by(status='aberto').all()
    return render_template('financeiro.html', invoices=invoices)

@app.route('/generate_boleto_pdf/<int:invoice_id>')
def generate_boleto_pdf(invoice_id):
    invoice = Invoice.query.get(invoice_id)
    file_path = f"boleto_{invoice.id}.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    
    # Aqui você pode adicionar mais detalhes ao boleto conforme necessário
    c.drawString(100, 750, f"Nome: {invoice.customer_name}")
    c.drawString(100, 730, f"Valor: {invoice.amount}")
    c.drawString(100, 710, f"Data de Vencimento: {invoice.due_date}")

    c.showPage()
    c.save()
    
    return send_file(file_path, as_attachment=True)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Configurações de e-mail
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False

        # Inicializa o objeto Mail
        mail = Mail(app)

        # Verifica se o MAIL_USERNAME foi carregado corretamente
        if not app.config['MAIL_USERNAME']:
            flash('Erro: MAIL_USERNAME não foi configurado corretamente.', 'danger')
            return redirect(url_for('contact'))

        # Cria a mensagem de e-mail
        msg = Message(
            subject='Contact Form Submission',
            sender=app.config['MAIL_USERNAME'],  # Certifique-se de que o remetente está sendo configurado
            recipients=['silva.felipebarros@gmail.com']
        )
        
        msg.body = f"Name: {request.form['name']}\nEmail: {request.form['email']}\nMessage: {request.form['message']}"

        try:
            # Tenta enviar o e-mail
            mail.send(msg)
            flash('Sua mensagem foi enviada com sucesso!', 'success')
        except Exception as e:
            # Trata erros ao enviar o e-mail
            flash(f'Erro ao enviar mensagem: {str(e)}', 'danger')

        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/quem_somos_nos')
def quem_somos_nos():
    return render_template('quem_somos_nos.html')

@app.route('/planos')
def planos():
    return render_template('planos.html')

@app.route('/updates')
def updates():
    return render_template('updates.html')

@app.route('/visual_agendamentos')
def visual_agendamentos():
    return render_template('visual_agendamentos.html')

@app.route('/restricoes')
def restricoes():
    return render_template('restricoes.html')





if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
