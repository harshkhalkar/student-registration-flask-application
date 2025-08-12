from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)

# Load environment variables (optional: only if using a .env file)
# from dotenv import load_dotenv
# load_dotenv()

# Database configuration from environment or defaults
db_config = {
    'host': os.getenv('DB_HOST', 'db'),        # or 'db' for Docker
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'MySec@123'),
    'database': os.getenv('DB_NAME', 'studentsdb')
}

# Home page: Registration form
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        course = request.form.get('course', '').strip()
        address = request.form.get('address', '').strip()
        contact = request.form.get('contact', '').strip()

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = '''
                INSERT INTO students (name, email, phone, course, address, contact)
                VALUES (%s, %s, %s, %s, %s, %s)
            '''
            values = (name, email, phone, course, address, contact)
            cursor.execute(query, values)
            conn.commit()
        except mysql.connector.Error as err:
            return f"Database error: {err}"
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('view_students'))

    return render_template('register.html')

# View all registered students
@app.route('/students')
def view_students():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
    except mysql.connector.Error as err:
        return f"Database error: {err}"
    finally:
        cursor.close()
        conn.close()

    return render_template('student.html', students=students)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
