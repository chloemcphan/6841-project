#!/usr/bin/env python3
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, session
from hashlib import sha256


app = Flask(__name__)
app.config['SECRET_KEY'] = 'sasflkj5alkfjew678oiajfldk75mglkdsamge3524asfjkler321'


def login(username, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                        (username, password,)).fetchone()
    conn.commit()
    conn.close()
    if user:
        session['username'] = username
        conn = get_db_connection()
        conn.execute('UPDATE users SET active = TRUE  WHERE username = ?',
                           (username,))
        conn.commit()
        conn.close()
    return user

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        print('logging in')
        username = request.form['username']
        password = sha256(request.form['password'].encode("ascii")).digest()
        user = login(username, password)
        if user:
            print('success')
            return redirect(url_for('start_chat'))

    return render_template('index.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = sha256(request.form['password'].encode("ascii")).digest()
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.commit()
        conn.close()
        if user:
            flash("username already exists")
            return redirect(url_for('register'))
        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, password, active) VALUES (?, ?, TRUE)", (username, password))
        conn.commit()
        conn.close()
        session['username'] = username
        return redirect(url_for('start_chat'))
    return render_template('register.html')

@app.route('/start-chat', methods=('GET', 'POST'))
def start_chat():
    if request.method == 'POST':
        username = request.form['reciever']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND active = TRUE', (username,)).fetchone()
        conn.commit()
        conn.close()
        if not user:
            flash('User unavailable')
            return render_template('chat.html', username=session['username'])
        
    if session['username']:
        return render_template('chat.html', username=session['username'])
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    if session['username']:
        conn = get_db_connection()
        conn.execute('UPDATE users SET active = FALSE WHERE username = ?',
                           (session['username'],))
        conn.commit()
        conn.close()
        session.pop('username', default=None)
    return redirect(url_for('index'))


