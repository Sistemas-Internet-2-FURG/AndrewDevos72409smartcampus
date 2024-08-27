from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from models import db, Professor, Aluno, Turma, TurmaAluno
from flask_migrate import Migrate
from sqlalchemy.orm import Session
# Cria uma instância do Flask
app = Flask(__name__)

# Configurações do aplicativo Flask
app.config['SECRET_KEY'] = 'your_secret_key'  # Chave secreta para sessões
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # URI do banco de dados
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desativa o rastreamento de modificações do SQLAlchemy

# Inicializa o Bootstrap com o aplicativo Flask
Bootstrap(app)

# Inicializa o SQLAlchemy com o aplicativo Flask
db.init_app(app)

# Inicializa o Flask-Migrate com o aplicativo Flask e o banco de dados
migrate = Migrate(app, db)

# Cria todas as tabelas do banco de dados se ainda não existirem
with app.app_context():
    db.create_all()

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtém os dados do formulário de login
        username = request.form['username']
        password = request.form['password']
        # Verifica se o usuário é um professor
        user = Professor.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['user_role'] = 'professor'
            return redirect(url_for('dashboard'))
        # Verifica se o usuário é um aluno
        user = Aluno.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['user_role'] = 'aluno'
            return redirect(url_for('classes'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

# Rota para registro de novos usuários
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtém os dados do formulário de registro
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if role == 'professor':
            new_user = Professor(username=username, password=password)
        else:
            new_user = Aluno(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Rota para o dashboard do professor
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session and session['user_role'] == 'professor':
        alunos = Aluno.query.all()
        turmas = Turma.query.filter_by(professor_id=session['user_id']).all()
        return render_template('dashboard.html', alunos=alunos, turmas=turmas)
    return redirect(url_for('login'))

# Rota para criação de novas turmas
@app.route('/create_class', methods=['GET', 'POST'])
def create_class():
    if 'user_id' in session and session['user_role'] == 'professor':
        if request.method == 'POST':
            class_name = request.form['class_name']
            student_ids = request.form.getlist('students')
            new_class = Turma(name=class_name, professor_id=session['user_id'])
            db.session.add(new_class)
            db.session.commit()
            for student_id in student_ids:
                turma_aluno = TurmaAluno(turma_id=new_class.id, aluno_id=student_id)
                db.session.add(turma_aluno)
            db.session.commit()
            return redirect(url_for('dashboard'))
        alunos = Aluno.query.all()
        return render_template('create_class.html', students=alunos)
    return redirect(url_for('login'))

# Rota para visualização das turmas pelos alunos
@app.route('/classes')
def classes():
    if 'user_id' in session and session['user_role'] == 'aluno':
        turmas = Turma.query.all()
        return render_template('classes.html', turmas=turmas)
    return redirect(url_for('login'))

# Rota para exclusão de alunos
@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'user_id' in session and session['user_role'] == 'professor':
        aluno = Aluno.query.get(student_id)
        if aluno:
            TurmaAluno.query.filter_by(aluno_id=student_id).delete()
            db.session.delete(aluno)
            db.session.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Rota para exclusão de professores
@app.route('/delete_professor/<int:professor_id>', methods=['POST'])
def delete_professor(professor_id):
    if 'user_id' in session and session['user_role'] == 'professor':
        professor = Professor.query.get(professor_id)
        if professor:
            db.session.delete(professor)
            db.session.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Rota para limpar o banco de dados
@app.route('/clear_db', methods=['POST'])
def clear_db():
    if 'user_id' in session and session['user_role'] == 'professor':
        db.drop_all()
        db.create_all()
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Rota para criação de novos alunos
@app.route('/create_student', methods=['GET', 'POST'])
def create_student():
    if 'user_id' in session and session['user_role'] == 'professor':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            new_student = Aluno(username=username, password=password)
            db.session.add(new_student)
            db.session.commit()
            return redirect(url_for('dashboard'))
        return render_template('create_student.html')
    return redirect(url_for('login'))

# Rota para visualizar detalhes da turma
@app.route('/class/<int:class_id>', methods=['GET', 'POST'])
def class_details(class_id):
    if 'user_id' in session and session['user_role'] == 'professor':
        turma = Turma.query.get(class_id)
        if request.method == 'POST':
            # Adicionar aluno à turma
            student_id = request.form['student_id']
            turma_aluno = TurmaAluno(turma_id=class_id, aluno_id=student_id)
            db.session.add(turma_aluno)
            db.session.commit()
            return redirect(url_for('class_details', class_id=class_id))
        alunos = Aluno.query.all()
        return render_template('class_details.html', turma=turma, alunos=alunos)
    return redirect(url_for('login'))

# Rota para remover aluno da turma
@app.route('/class/<int:class_id>/remove_student/<int:student_id>', methods=['POST'])
def remove_student_from_class(class_id, student_id):
    if 'user_id' in session and session['user_role'] == 'professor':
        turma_aluno = TurmaAluno.query.filter_by(turma_id=class_id, aluno_id=student_id).first()
        if turma_aluno:
            db.session.delete(turma_aluno)
            db.session.commit()
        return redirect(url_for('class_details', class_id=class_id))
    return redirect(url_for('login'))

# Rota para editar o nome da turma
@app.route('/edit_class/<int:class_id>', methods=['GET', 'POST'])
def edit_class(class_id):
    turma = Turma.query.get(class_id)
    professores = Professor.query.all()
    
    if request.method == 'POST':
        turma.name = request.form['name']
        turma.professor_id = request.form['professor_id']
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('edit_class.html', turma=turma, professores=professores)


# Rota para editar o nome do aluno
@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    aluno = Aluno.query.get(student_id)
    if request.method == 'POST':
        aluno.username = request.form['username']
        db.session.commit()
        flash('Nome do aluno atualizado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_student.html', aluno=aluno)


# Rota para excluir a turma
@app.route('/delete_class/<int:class_id>', methods=['POST'])
def delete_class(class_id):
    with Session(db.engine) as session:
        turma = session.get(Turma, class_id)
        if turma:
            session.delete(turma)
            session.commit()
            flash('Turma excluída com sucesso!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/professor_dashboard')
def professor_dashboard():
    turmas = Turma.query.all()
    return render_template('professor_dashboard.html', turmas=turmas)

# Executa o aplicativo Flask
if __name__ == '__main__':
    app.run(debug=True)