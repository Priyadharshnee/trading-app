from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from utils.price_simulator import get_price

app = Flask(__name__)
DB_PATH = 'database/trading.db'

def init_db():
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS portfolio (
                        id INTEGER PRIMARY KEY,
                        stock TEXT,
                        quantity INTEGER,
                        price REAL,
                        total REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY,
                        action TEXT,
                        stock TEXT,
                        quantity INTEGER,
                        price REAL,
                        total REAL,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    stock_price = get_price("XYZ")
    return render_template('index.html', price=stock_price)

@app.route('/trade', methods=['GET', 'POST'])
def trade():
    if request.method == 'POST':
        stock = request.form['stock']
        action = request.form['action']
        quantity = int(request.form['quantity'])
        price = get_price(stock)
        total = round(price * quantity, 2)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if action == 'buy':
            cursor.execute("INSERT INTO portfolio (stock, quantity, price, total) VALUES (?, ?, ?, ?)",
                           (stock, quantity, price, total))
        cursor.execute("INSERT INTO history (action, stock, quantity, price, total) VALUES (?, ?, ?, ?, ?)",
                       (action, stock, quantity, price, total))
        conn.commit()
        conn.close()
        return redirect(url_for('portfolio'))
    return render_template('trade.html')

@app.route('/portfolio')
def portfolio():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT stock, SUM(quantity), SUM(total) FROM portfolio GROUP BY stock")
    data = cursor.fetchall()
    conn.close()
    return render_template('portfolio.html', data=data)

@app.route('/history')
def history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ORDER BY date DESC")
    records = cursor.fetchall()
    conn.close()
    return render_template('history.html', records=records)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5050)
