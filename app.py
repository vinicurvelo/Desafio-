import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Banco de dados SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, default=0)

# Modelo de Atividade
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=False)

# Rota da Página Inicial
@app.route('/')
def home():
    return render_template('home.html')

# Rota de Registro de Usuário
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Simples verificação (ideal: usar hash de senha)
            return redirect(url_for('dashboard', user_id=user.id))
    return render_template('login.html')

# Rota do Dashboard do Usuário
@app.route('/dashboard/<int:user_id>', methods=['GET', 'POST'])
def dashboard(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        activity_type = request.form['activity_type']
        points = calculate_points(activity_type)
        new_activity = Activity(user_id=user.id, activity_type=activity_type, points=points)
        db.session.add(new_activity)
        user.points += points
        db.session.commit()
    return render_template('dashboard.html', user=user)

# Função para calcular pontos
def calculate_points(activity_type):
    points_map = {
        'Musculação': 2,
        'Cardio': 1,
        'Yoga': 3,
        'Leitura': 1,
        'Alimentação Saudável': 1,
        'Hidratação': 1
    }
    return points_map.get(activity_type, 0)

# Rota do Ranking
@app.route('/ranking')
def ranking():
    users = User.query.order_by(User.points.desc()).all()
    return render_template('ranking.html', users=users)

# Criar o banco de dados se não existir
def setup_database():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    setup_database()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
