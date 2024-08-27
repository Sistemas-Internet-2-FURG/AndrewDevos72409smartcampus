from flask import Flask
app = Flask(__name__)
@app.route("/")
def olaMundo():
   saida = "<h1>Surpreenda-se com o mundo Flask!</h1><p>CACETA</p>"* 100
   return saida

app.run()
