from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
app.secret_key = "student123"

# -----------------------------
# MySQL Configuration
# -----------------------------
app.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
app.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT", 3306))
app.config["MYSQL_SSL_MODE"] = "REQUIRED"

mysql = MySQL(app)
# -----------------------------
# Login Page
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cur.fetchone()

        cur.close()
        

        if user:
            session["admin"] = username
            return redirect("/dashboard")
        else:
            return "Invalid Username or Password"

    return render_template("login.html")


# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/")

    cur = mysql.connection.cursor()

    # Total Students
    cur.execute("SELECT COUNT(*) FROM students")
    total = cur.fetchone()[0]

    # Hostelers
    cur.execute("SELECT COUNT(*) FROM students WHERE student_type='Hosteler'")
    hostel = cur.fetchone()[0]

    # Day Scholars
    cur.execute("SELECT COUNT(*) FROM students WHERE student_type='Day Scholar'")
    day = cur.fetchone()[0]

    # Department Counts
    cur.execute("SELECT COUNT(*) FROM students WHERE department='ECE'")
    ece = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students WHERE department='CSE'")
    cse = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students WHERE department='EEE'")
    eee = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students WHERE department='MECH'")
    mech = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students WHERE department='CIVIL'")
    civil = cur.fetchone()[0]

    cur.close()

    return render_template(
        "dashboard.html",
        total=total,
        hostel=hostel,
        day=day,
        ece=ece,
        cse=cse,
        eee=eee,
        mech=mech,
        civil=civil
    )
# -----------------------------
# Add Student
# -----------------------------
@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if "admin" not in session:
        return redirect("/")

    if request.method == "POST":

        name = request.form["name"]
        roll_no = request.form["roll_no"]
        department = request.form["department"]
        student_type = request.form["student_type"]

        cur = mysql.connection.cursor()

        # Check duplicate roll number
        cur.execute("SELECT * FROM students WHERE roll_no=%s", (roll_no,))
        existing = cur.fetchone()

        if existing:
            cur.close()
            return "Roll Number already exists!"

        cur.execute(
            """
            INSERT INTO students(name, roll_no, department, student_type)
            VALUES(%s, %s, %s, %s)
            """,
            (name, roll_no, department, student_type)
        )

        mysql.connection.commit()
        cur.close()
       
        flash("Student added successfully!")


        return redirect("/dashboard")

    return render_template("add_student.html")
@app.route("/search", methods=["GET", "POST"])
def search():

    if "admin" not in session:
        return redirect("/")

    student = None

    if request.method == "POST":
        roll_no = request.form["roll_no"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE roll_no=%s", (roll_no,))
        student = cur.fetchone()
        cur.close()

    return render_template("search.html", student=student)
# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

# -----------------------------
# View Students
# -----------------------------
@app.route("/view_students")
def view_students():

    if "admin" not in session:
        return redirect("/")

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM students ORDER BY roll_no")

    students = cur.fetchall()

    cur.close()

    return render_template("view_students.html", students=students)


# -----------------------------
# Edit Student
# -----------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    if "admin" not in session:
        return redirect("/")

    cur = mysql.connection.cursor()

    if request.method == "POST":

        name = request.form["name"]
        roll_no = request.form["roll_no"]
        department = request.form["department"]
        student_type = request.form["student_type"]

        # Check duplicate roll number
        cur.execute(
            "SELECT * FROM students WHERE roll_no=%s AND id!=%s",
            (roll_no, id)
        )

        existing = cur.fetchone()

        if existing:
            cur.close()
            return "Roll Number already exists!"

        # Update student
        cur.execute("""
            UPDATE students
            SET name=%s,
                roll_no=%s,
                department=%s,
                student_type=%s
            WHERE id=%s
        """, (name, roll_no, department, student_type, id))

        mysql.connection.commit()
        cur.close()

        flash("Student updated successfully!")
        return redirect("/view_students")

    # Get student details
    cur.execute(
        "SELECT * FROM students WHERE id=%s",
        (id,)
    )

    student = cur.fetchone()

    cur.close()

    return render_template(
        "edit_student.html",
        student=student
    )


# -----------------------------
# Delete Student
# -----------------------------
@app.route("/delete/<int:id>")
def delete_student(id):

    if "admin" not in session:
        return redirect("/")

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM students WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.close()
    
    flash("Student deleted successfully!")


    return redirect("/view_students")


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)