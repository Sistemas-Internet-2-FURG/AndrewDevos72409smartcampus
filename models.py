from flask_sqlalchemy import SQLAlchemy

# Inicializa o objeto SQLAlchemy
db = SQLAlchemy()

# Modelo para a tabela Professor
class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Modelo para a tabela Aluno
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Modelo para a tabela Turma
class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    professor = db.relationship('Professor', backref=db.backref('turmas', lazy=True))
    alunos = db.relationship('Aluno', secondary='turma_aluno', backref=db.backref('turmas', lazy=True))

# Modelo para a tabela de associação entre Turma e Aluno
class TurmaAluno(db.Model):
    __tablename__ = 'turma_aluno'
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), primary_key=True)