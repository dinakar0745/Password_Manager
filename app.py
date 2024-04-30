from flask import Flask, render_template, request, redirect, session
import mysql.connector
from bcrypt import hashpw, gensalt
from cryptography.fernet import Fernet
from functools import wraps


app = Flask(__name__)
app.secret_key = "your_secret_key"

# Connect to MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="password_manager"
)

mycursor = mydb.cursor()

# Check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "email" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

mycursor.execute("SELECT encryption_key FROM encryption_keys")
encryption_key_row = mycursor.fetchone()
if encryption_key_row:
    key = encryption_key_row[0]
else:
    key = Fernet.generate_key()
    mycursor.execute("INSERT INTO encryption_keys (encryption_key) VALUES (%s)", (key,))
    mydb.commit()

cipher_suite = Fernet(key)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        # Retrieve user from MySQL using email instead of username
        mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = mycursor.fetchone()
        if user and user[1] == password:
            session["email"] = email
            return redirect("/dashboard")
        else:
            return render_template("login.html", message="Invalid email or password.")
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "email" in session:
        email = session["email"]
        # Retrieve user data from MySQL using email
        mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = mycursor.fetchone()
        if user:
            first_name = user[1]
            last_name = user[2]
            return render_template("dashboard.html", first_name=first_name, last_name=last_name)
        else:
            # Handle case where user data is not found
            return render_template("error.html", message="User data not found.")
    return redirect("/")

@app.route("/passwords")
def list_passwords():
    if "email" in session:
        email = session["email"]
        # Retrieve passwords from MySQL using email
        mycursor.execute("SELECT website, username, password FROM passwords WHERE user_email = %s", (email,))
        password_data = mycursor.fetchall()

        # Decrypt passwords
        decrypted_passwords = []
        for data in password_data:
            website = data[0]
            username = data[1]
            encrypted_password = data[2]
            
            # Decrypt the password
            decrypted_password = cipher_suite.decrypt(encrypted_password.encode()).decode()
            decrypted_passwords.append((website, username, decrypted_password))

        return render_template("passwords.html", password_data=decrypted_passwords)
    return redirect("/")


@app.route("/add_password", methods=["POST"])
def add_password():
    if "email" in session:
        email = session["email"]
        website = request.form["for"]
        username = request.form["username"]
        new_password = request.form["new_password"]
        r_new_password = request.form["r_new_password"]

        # Check if password and re-entered password match
        if new_password != r_new_password:
            return render_template("error.html", message="Passwords do not match.")

        # Encrypt the password with the user's phone number
        encrypted_password = cipher_suite.encrypt(new_password.encode()).decode()

        # Insert new password into MySQL
        mycursor.execute("INSERT INTO passwords (user_email, website, username, password) VALUES (%s, %s, %s, %s)", (email, website, username, encrypted_password))
        mydb.commit()
        return redirect("/dashboard")
    return redirect("/")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        fname = request.form["fname"]
        lname = request.form["lname"]
        email = request.form["email"]
        phone = request.form["phoneno"]
        password = request.form["password"]
        rpassword = request.form["rpassword"]

        # Check if password and re-entered password match
        if password != rpassword:
            return render_template("signup.html", message="Passwords do not match.")
        
        # Check if email already exists
        mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = mycursor.fetchone()
        if existing_user:
            return render_template("signup.html", message="Email already exists. Please choose a different one.")
        else:
            # Insert new user into MySQL
            hashed_password = hash_password(password.encode())
            mycursor.execute("INSERT INTO users (first_name, last_name, email, phone, password) VALUES (%s, %s, %s, %s, %s)", (fname, lname, email, phone, hashed_password))
            mydb.commit()
            session["email"] = email
            return redirect("/dashboard")
    return render_template("signup.html")

def logout():
    session.pop("email", None)
    return redirect("/")
    

def hash_password(password):
    return hashpw(password, gensalt()).decode()

def check_password(password, hashed_password):
    return hashpw(password, hashed_password) == hashed_password

if __name__ == "__main__":
    app.run(debug=True)
