from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for using flash messages

# Admin key (you can store it in an environment variable for better security)
ADMIN_KEY = "admin1"

# Database setup
def init_db():
    with sqlite3.connect('pickups.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pickups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                email TEXT NOT NULL,
                contact TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                description TEXT NOT NULL,
                weight REAL NOT NULL,
                status TEXT DEFAULT 'getting sorted',
                completed_time TEXT
            )
        ''')
    print("Database initialized")

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for scheduling a pickup
@app.route('/schedule', methods=['POST'])
def schedule():
    name = request.form['name']
    address = request.form['address']
    email = request.form['email']
    contact = request.form['contact']
    date = request.form['date']
    time = request.form['time']
    description = request.form['description']
    weight = request.form['weight']

    with sqlite3.connect('pickups.db') as conn:
        conn.execute('''
            INSERT INTO pickups (name, address, email, contact, date, time, description, weight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, address, email, contact, date, time, description, weight))
        conn.commit()

    return "Successfully scheduled!"

# Route for checking the status of a pickup
@app.route('/check_status', methods=['POST'])
def check_status():
    email = request.form['email']
    with sqlite3.connect('pickups.db') as conn:
        cursor = conn.execute('SELECT name, date, time, status, completed_time FROM pickups WHERE email = ?', (email,))
        pickup = cursor.fetchone()
    if pickup:
        return render_template('status.html', pickup=pickup)
    else:
        return "No pickup found with that email."

# Route to handle admin login
@app.route('/admin_login', methods=['POST'])
def admin_login():
    admin_key = request.form['admin_key']
    if admin_key == ADMIN_KEY:
        return redirect(url_for('admin'))
    else:
        flash("Incorrect Admin Key! Access Denied.")
        return redirect(url_for('index'))

# Route for admin to view pickups
@app.route('/admin')
def admin():
    with sqlite3.connect('pickups.db') as conn:
        cursor = conn.execute('SELECT * FROM pickups')
        pickups = cursor.fetchall()
    return render_template('admin.html', pickups=pickups)

# Route for clearing database
@app.route('/clear', methods=['POST'])
def clear_database():
    with sqlite3.connect('pickups.db') as conn:
        conn.execute('DELETE FROM pickups')
        conn.commit()
    return "All entries have been cleared!"

# Route to update the status of a pickup
@app.route('/update_status/<int:pickup_id>', methods=['POST'])
def update_status(pickup_id):
    new_status = request.form['status']
    completed_time = request.form['completed_time'] if new_status == "completed" else None
    with sqlite3.connect('pickups.db') as conn:
        conn.execute('UPDATE pickups SET status = ?, completed_time = ? WHERE id = ?', (new_status, completed_time, pickup_id))
        conn.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
