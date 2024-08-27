from app import db
from models import Class

# Verifica se a tabela Class contém a coluna name
columns = db.inspect(Class).columns
print(columns)