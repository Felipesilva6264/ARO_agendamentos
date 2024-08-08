from app import app, db
from app.models import User
from werkzeug.security import generate_password_hash

# Criar um contexto de aplicação para acessar o banco de dados
with app.app_context():
    # Criar um novo usuário
    username = 'admin'
    password = 'senha123'
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    print('Usuário criado com sucesso!')

