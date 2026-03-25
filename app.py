import sqlite3
from flask import Flask, request, session, redirect, url_for, render_template, Response
from models.db import init_db

app = Flask(__name__)
app.secret_key = "secret123"

# Initialize database when app starts
init_db()

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        try:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))
            conn.commit()
            conn.close()
            return redirect('/login')
        except sqlite3.IntegrityError:
            error = "Username already exists. Please choose a different one."

    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        data = cur.fetchone()
        conn.close()

        if data:
            session['user'] = user
            return redirect('/')
    
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect('/login')

    result = None
    error = None
    if request.method == 'POST':
        amount_str = request.form.get('amount', '').strip()
        try:
            amount = float(amount_str)
            if amount < 0:
                raise ValueError('Negative amount')
        except ValueError:
            error = 'Please enter a valid positive number for amount.'
            return render_template('index.html', result=result, error=error)

        from_currency = request.form.get('from_currency')
        to_currency = request.form.get('to_currency')

        rates = {
            'USD': {'INR': 83.0, 'EUR': 0.92, 'USD': 1.0},
            'INR': {'USD': 0.012, 'EUR': 0.011, 'INR': 1.0},
            'EUR': {'USD': 1.09, 'INR': 90.0, 'EUR': 1.0},
        }

        rate = rates.get(from_currency, {}).get(to_currency, 1.0)
        result = round(amount * rate, 2)

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO history (username, from_currency, to_currency, amount, result) VALUES (?, ?, ?, ?, ?)',
            (session['user'], from_currency, to_currency, amount, result)
        )
        conn.commit()
        conn.close()

    return render_template('index.html', result=result, error=error)


@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT from_currency, to_currency, amount, result FROM history WHERE username=?', (session['user'],))
    records = cur.fetchall()
    conn.close()

    return render_template('history.html', history=records)


@app.route('/download')
def download():
    if 'user' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM history WHERE username=?", (session['user'],))
    data = cur.fetchall()
    conn.close()

    def generate():
        yield 'From,To,Amount,Result\n'
        for row in data:
            yield f"{row[2]},{row[3]},{row[4]},{row[5]}\n"
    
    return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename="conversion_history.csv"'})


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)

from reportlab.platypus import SimpleDocTemplate

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

from flask import redirect, url_for
import os
import sqlite3

@app.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        # Get file from database
        cursor.execute("SELECT filename FROM files WHERE id = ?", (file_id,))
        file = cursor.fetchone()

        if file:
            filename = file[0]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Delete file from folder
            if os.path.exists(filepath):
                os.remove(filepath)

            # Delete record from database
            cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
            conn.commit()

    except Exception as e:
        print("Error deleting file:", e)

    finally:
        conn.close()

    return redirect(url_for('dashboard'))
@app.route('/favorite/<int:file_id>')
def favorite(file_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE files 
        SET is_favorite = CASE WHEN is_favorite=1 THEN 0 ELSE 1 END
        WHERE id=?
    """, (file_id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

import smtplib
from email.mime.text import MIMEText

@app.route('/send-email/<token>')
def send_email(token):
    receiver = request.args.get('email')

    link = f"http://127.0.0.1:5000/share/{token}"

    msg = MIMEText(f"Download your file: {link}")
    msg['Subject'] = 'File Share Link'
    msg['From'] = 'your_email@gmail.com'
    msg['To'] = receiver

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your_email@gmail.com', 'your_app_password')

    server.send_message(msg)
    server.quit()

    return "Email Sent!"

import os

UPLOAD_FOLDER = 'uploads'
DATABASE_FILE = 'database.db'

port = int(os.environ.get("PORT", 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)