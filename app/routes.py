from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessário para usar flash messages

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Aqui você pode processar o formulário de registro
        username = request.form['username']
        password = request.form['password']
        # Faça algo com os dados do formulário, como salvar no banco de dados

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/financeiro')
def financeiro():
    invoices = Invoice.query.filter_by(status='aberto').all()
    return render_template('financeiro.html', invoices=invoices)

@app.route('/generate_boleto/<int:id>', methods=['POST'])
def generate_boleto(id):
    invoice = Invoice.query.get(id)
    if not invoice:
        flash('Fatura não encontrada.', 'danger')
        return redirect(url_for('financeiro'))

@app.route('/updates')
def updates():
    return render_template('updates.html')




if __name__ == '__main__':
    app.run(debug=True)