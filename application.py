import os
import helpfunctions

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#main page to login and
@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method =="POST":
        username = request.form.get("username")
        password = request.form.get("password")

        #check validity of password and username
        if username == None:
            return render_template("error.html", message = "please enter a valid username")
        elif password == None:
            return render_template("error.html", message = "please enter a valid password")

        #check username and password against database
        rownum = db.execute("SELECT * FROM users WHERE username = :username", {"username" : username}).rowcount
        print(rownum)
        db.commit()

        if rownum == 0:
            return render_template("error.html", message = "invalid username")

        row = db.execute("SELECT * FROM users WHERE username = :username", {"username" : username}).fetchone()
        db.commit()

        if check_password_hash(row.passwordhash, password):
            return render_template("error.html", message = "invalid password")
        #log user in and send to homepage if they pass checks
        else:
            session["user_id"] = username
            return render_template("homepage.html")


    else:
        return render_template("loginpage.html")
@app.route("/newuser", methods=['POST','GET'])
def newuser():
    if request.method =="POST":
        #insert new user in to database
        username = request.form.get("username")
        password = request.form.get("password")
        hash = generate_password_hash("password")
        db.execute("INSERT INTO users (username, passwordhash) values (:username, :password_hash)", {"username" : username, "password_hash" : hash})
        db.commit()

        #log them in
        session["user_id"] = username
        return render_template("homepage.html")

    else:
        return render_template("newuser.html")
