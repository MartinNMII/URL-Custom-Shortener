from flask import Flask, request, redirect, render_template_string
import sqlite3
import string
import random

app = Flask(__name__)

# Funkcija za generisanje skraćenog URL-a sa samo slovima
def generate_short_url(length=6):
    characters = string.ascii_letters  # Samo slova
    return ''.join(random.choice(characters) for _ in range(length))

# Početna stranica sa formom za unos URL-a
@app.route('/')
def index():
    return render_template_string('''
        <!doctype html>
        <title>Skraćivač URL-ova</title>
        <h1>Skraćivač URL-ova</h1>
        <form action="/shorten" method="post">
            <label for="url">Originalni URL:</label><br>
            <input type="text" id="url" name="url" required><br><br>
            <label for="custom_short">Prilagođeni kratki URL (opciono):</label><br>
            <input type="text" id="custom_short" name="custom_short"><br><br>
            <input type="submit" value="Skrati">
        </form>
    ''')

# Ruta za skraćivanje URL-a
@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form['url']
    custom_short = request.form.get('custom_short')

    # Ukloni specijalne karaktere i proksi za validaciju
    if custom_short:
        custom_short = ''.join(c for c in custom_short if c.isalnum())  # Ukloni specijalne karaktere
        if not custom_short:
            return 'Prilagođeni URL mora sadržati bar jedno slovo ili broj.'
        short_url = custom_short
    else:
        short_url = generate_short_url()

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Provera da li prilagođeni kratki URL već postoji
    c.execute('SELECT original FROM urls WHERE short = ?', (short_url,))
    if c.fetchone():
        return 'Prilagođeni kratki URL je već zauzet, molimo izaberite drugi.'

    c.execute('INSERT INTO urls (short, original) VALUES (?, ?)', (short_url, original_url))
    conn.commit()
    conn.close()

    # Prikaz skraćenog URL-a samo deo koji dolazi nakon /
    return f'Skraćeni URL: <a href="/{short_url}">{short_url}</a>'

# Ruta za preusmeravanje na originalni URL
@app.route('/<short_url>')
def redirect_to_url(short_url):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT original FROM urls WHERE short = ?', (short_url,))
    result = c.fetchone()
    conn.close()
    if result:
        return redirect(result[0])
    return 'URL nije pronađen'

# Inicijalizacija baze podataka
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short TEXT UNIQUE NOT NULL,
            original TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
