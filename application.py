from flask import Flask, render_template, request, redirect, url_for

from upload_handler import process_upload
from get_notas import get_notas

app = Flask(__name__)

@app.route('/')
def index():
    notas = get_notas()
    return render_template('index.html', notas=notas)

@app.route('/add-nota', methods=['POST'])
def add_nota():
    texto = request.form['texto']
    imagem = request.files['imagem']

    if imagem or texto:
        process_upload(texto, imagem)

    return redirect(url_for('index'))

@app.route('/nova-nota', methods=['POST'])
def nova_nota():
    return render_template('nota.html')

app.run()