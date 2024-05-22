from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for session management

# Configure the PostgreSQL connection
DATABASE = {
    'database': 'ambassador_sports',
    'user': 'postgres',
    'password': '******',
    'host': 'localhost',  # or the address of your database server
    'port': '5432'
}

def get_db_connection():
    conn = psycopg2.connect(**DATABASE)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('signup'))

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (fullname, email, username, password) VALUES (%s, %s, %s, %s)", 
                           (fullname, email, username, password))
            conn.commit()
        except psycopg2.Error as e:
            flash(f"Error: {e}")
            return redirect(url_for('signup'))
        finally:
            cursor.close()
            conn.close()
        
        flash('Signup successful! Please login.')
        return redirect(url_for('index'))
    
    return render_template('sign_up.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user:
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.')
    
    return render_template('index.html')

@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        flash('You need to login first.')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/G_product_window')
def product_window():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT * FROM gloves")
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('G_product_window.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)

