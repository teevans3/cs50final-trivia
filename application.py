import os
import random

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from operator import itemgetter

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///trivia.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return render_template("index.html")


@app.route("/addscore", methods=["GET"])
@login_required
def addscore():
    """Function to add to user's score (if answer is correct)"""

    # variable for current user
    user_id = session["user_id"]

    # select current score from user to update
    result = db.execute("SELECT score FROM users WHERE id = :user_id", user_id=user_id)
    score = result[0]["score"]
    # user adds 10 to score when selecting correct answer
    newscore = score + 10

    db.execute("UPDATE users SET score = :newscore WHERE id = :user_id", newscore=newscore, user_id=user_id)

    return None


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    username = str(request.args.get("username"))

    rows = len(db.execute("SELECT * FROM users WHERE username = :username", username=username))

    # if username is not length 0 and username is not found in users table (thus having a length of 0), then it is available
    if len(username) != 0 and rows < 1:
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/checkuser", methods=["GET"])
def checkuser():
    """Return true if username exists, else false, in JSON format"""

    username = str(request.args.get("username"))

    rows = len(db.execute("SELECT * FROM users WHERE username = :username", username=username))

    # if username is not length 0 and length of rows = 0, then username does not exist
    if len(username) != 0 and rows < 1:
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/checkpassword", methods=["GET"])
def checkpassword():
    """Return true if password exists, else false, in JSON format"""

    # get username to correct corresponding password (thus NOT JUST ANY password within users table)
    username = str(request.args.get("username"))

    # get password (can't recreate the exact same password hash!(i don't think?), just use check_password_hash function instead!)
    password = str(request.args.get("password"))


    # grab the row from the correct user
    userinfo = db.execute("SELECT * FROM users WHERE username = :username", username=username)

    # get actual username and actual hashed password to compare and check
    realuser = userinfo[0]["username"]
    realhash = userinfo[0]["hash"]

    if len(username) != 0 and (username == realuser) and check_password_hash(realhash, password):
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """View list of categories for creating user's own trivia questions"""

    return render_template("create.html")


@app.route("/createhistory", methods=["GET", "POST"])
@login_required
def createhistory():
    """Collect user info for history trivia questions"""

    if request.method == "POST":
        # variables for inserting questions, answer, and wrong answers
        question = request.form.get("question")
        correct = request.form.get("correct")
        wrong1 = request.form.get("wrong1")
        wrong2 = request.form.get("wrong2")
        wrong3 = request.form.get("wrong3")

        # ensure user entered info for all forms (MAY CHANGE THIS LATER TO LOOK NICER, VIA BOOTSTRAP)
        if len(question) < 1 or len(correct) < 1 or len(wrong1) < 1 or len(wrong2) < 1 or len(wrong3) < 1:
            return apology("SORRY")

        # insert forms into moviestv table
        else:
            db.execute("INSERT INTO history (question, correct, wrong1, wrong2, wrong3) VALUES (:question, :correct, :wrong1, :wrong2, :wrong3)",
                        question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)

        return render_template("createhistory.html")

    else:
        return render_template("createhistory.html")


@app.route("/createmoviestv", methods=["GET", "POST"])
@login_required
def createmoviestv():
    """Collect user info for movie/tv trivia questions"""

    if request.method == "POST":
        # variables for inserting questions, answer, and wrong answers
        question = request.form.get("question")
        correct = request.form.get("correct")
        wrong1 = request.form.get("wrong1")
        wrong2 = request.form.get("wrong2")
        wrong3 = request.form.get("wrong3")

        # ensure user entered info for all forms (MAY CHANGE THIS LATER TO LOOK NICER, VIA BOOTSTRAP)
        if len(question) < 1 or len(correct) < 1 or len(wrong1) < 1 or len(wrong2) < 1 or len(wrong3) < 1:
            return apology("SORRY")

        # insert forms into moviestv table
        else:
            db.execute("INSERT INTO moviestv (question, correct, wrong1, wrong2, wrong3) VALUES (:question, :correct, :wrong1, :wrong2, :wrong3)",
                        question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)

        return render_template("createmoviestv.html")

    else:
        return render_template("createmoviestv.html")


@app.route("/createother", methods=["GET", "POST"])
@login_required
def createother():
    """Collect user info for other trivia questions"""

    if request.method == "POST":
        # variables for inserting questions, answer, and wrong answers
        question = request.form.get("question")
        correct = request.form.get("correct")
        wrong1 = request.form.get("wrong1")
        wrong2 = request.form.get("wrong2")
        wrong3 = request.form.get("wrong3")

        # ensure user entered info for all forms (MAY CHANGE THIS LATER TO LOOK NICER, VIA BOOTSTRAP)
        if len(question) < 1 or len(correct) < 1 or len(wrong1) < 1 or len(wrong2) < 1 or len(wrong3) < 1:
            return apology("SORRY")

        # insert forms into moviestv table
        else:
            db.execute("INSERT INTO other (question, correct, wrong1, wrong2, wrong3) VALUES (:question, :correct, :wrong1, :wrong2, :wrong3)",
                        question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)

        return render_template("createother.html")

    else:
        return render_template("createother.html")


@app.route("/createpopculture", methods=["GET", "POST"])
@login_required
def createpopculture():
    """Collect user info for pop culture trivia questions"""

    if request.method == "POST":
        # variables for inserting questions, answer, and wrong answers
        question = request.form.get("question")
        correct = request.form.get("correct")
        wrong1 = request.form.get("wrong1")
        wrong2 = request.form.get("wrong2")
        wrong3 = request.form.get("wrong3")

        # ensure user entered info for all forms (MAY CHANGE THIS LATER TO LOOK NICER, VIA BOOTSTRAP)
        if len(question) < 1 or len(correct) < 1 or len(wrong1) < 1 or len(wrong2) < 1 or len(wrong3) < 1:
            return apology("SORRY")

        # insert forms into moviestv table
        else:
            db.execute("INSERT INTO popculture (question, correct, wrong1, wrong2, wrong3) VALUES (:question, :correct, :wrong1, :wrong2, :wrong3)",
                        question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)

        return render_template("createpopculture.html")

    else:
        return render_template("createpopculture.html")


@app.route("/createscience", methods=["GET", "POST"])
@login_required
def createscience():
    """Collect user info for science trivia questions"""

    if request.method == "POST":
        # variables for inserting questions, answer, and wrong answers
        question = request.form.get("question")
        correct = request.form.get("correct")
        wrong1 = request.form.get("wrong1")
        wrong2 = request.form.get("wrong2")
        wrong3 = request.form.get("wrong3")

        # ensure user entered info for all forms (MAY CHANGE THIS LATER TO LOOK NICER, VIA BOOTSTRAP)
        if len(question) < 1 or len(correct) < 1 or len(wrong1) < 1 or len(wrong2) < 1 or len(wrong3) < 1:
            return apology("SORRY")

        # insert forms into moviestv table
        else:
            db.execute("INSERT INTO science (question, correct, wrong1, wrong2, wrong3) VALUES (:question, :correct, :wrong1, :wrong2, :wrong3)",
                        question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)

        return render_template("createscience.html")

    else:
        return render_template("createscience.html")


@app.route("/createsports", methods=["GET", "POST"])
@login_required
def createsports():
    """Collect user info for sports trivia questions"""

    if request.method == "POST":
        # variables for inserting questions, answer, and wrong answers
        question = request.form.get("question")
        correct = request.form.get("correct")
        wrong1 = request.form.get("wrong1")
        wrong2 = request.form.get("wrong2")
        wrong3 = request.form.get("wrong3")

        # ensure user entered info for all forms (MAY CHANGE THIS LATER TO LOOK NICER, VIA BOOTSTRAP)
        if len(question) < 1 or len(correct) < 1 or len(wrong1) < 1 or len(wrong2) < 1 or len(wrong3) < 1:
            return apology("SORRY")

        # insert forms into moviestv table
        else:
            db.execute("INSERT INTO sports (question, correct, wrong1, wrong2, wrong3) VALUES (:question, :correct, :wrong1, :wrong2, :wrong3)",
                        question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)

        return render_template("createsports.html")

    else:
        return render_template("createsports.html")


@app.route("/highscores", methods=["GET", "POST"])
@login_required
def highscores():
    """Display highscores table"""


    # put this in order from hgihest to lowest
    scores = db.execute("SELECT score, username FROM users")
    # sort the list in descending order by score
    scores = sorted(scores, key=itemgetter("score"), reverse = True)

    return render_template("highscores.html", scores=scores)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    """Layout for user to choose which category of trivia to play"""
    return render_template("play.html")


@app.route("/playall", methods=["GET", "POST"])
@login_required
def playall():
    """Pick random questions out of all tables in trivia database """
    # combine all questions into a list
    questionlist = db.execute("SELECT * FROM history UNION SELECT * FROM moviestv UNION SELECT * FROM other UNION SELECT * FROM popculture UNION SELECT * FROM science UNION SELECT * FROM sports")
    # choose a random question from the list; first generate random number from length of questionlist
    randomnum = random.randint(1, (len(questionlist) - 1))
    # get question from questionlist associated with randomnum
    randomquestion = questionlist[randomnum]
    # assign variables for question, correct, and wrong answers
    question = randomquestion["question"]
    correct = randomquestion["correct"]
    wrong1 = randomquestion["wrong1"]
    wrong2 = randomquestion["wrong2"]
    wrong3 = randomquestion["wrong3"]

    return render_template("playall.html", question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)

@app.route("/playhistory", methods=["GET", "POST"])
@login_required
def playhistory():
    """Pick random questions from history table"""

    # to randomize the question, we need to...
    # creat a variable for start range for randomizer
    result = db.execute("SELECT MIN(id) FROM history")
    start = result[0]["MIN(id)"]
    # create a variable for end range for randomizer
    result = db.execute("SELECT MAX(id) FROM history")
    end = result[0]["MAX(id)"]
    randomid = random.randint(start, end)

    # variables for question, correct answer, and wrong answers
    result = db.execute("SELECT question FROM history WHERE id = :randomid", randomid=randomid)
    question = result[0]["question"]
    result = db.execute("SELECT correct FROM history WHERE id = :randomid", randomid=randomid)
    correct = result[0]["correct"]
    result = db.execute("SELECT wrong1 FROM history WHERE id = :randomid", randomid=randomid)
    wrong1 = result[0]["wrong1"]
    result = db.execute("SELECT wrong2 FROM history WHERE id = :randomid", randomid=randomid)
    wrong2 = result[0]["wrong2"]
    result = db.execute("SELECT wrong3 FROM history WHERE id = :randomid", randomid=randomid)
    wrong3 = result[0]["wrong3"]

    return render_template("playhistory.html", question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)


@app.route("/playmoviestv", methods=["GET", "POST"])
@login_required
def playmoviestv():
    """Pick random questions from movietv table"""

    # to randomize the question, we need to...
    # creat a variable for start range for randomizer
    result = db.execute("SELECT MIN(id) FROM moviestv")
    start = result[0]["MIN(id)"]
    # create a variable for end range for randomizer
    result = db.execute("SELECT MAX(id) FROM moviestv")
    end = result[0]["MAX(id)"]
    randomid = random.randint(start, end)

    # variables for question, correct answer, and wrong answers
    result = db.execute("SELECT question FROM moviestv WHERE id = :randomid", randomid=randomid)
    question = result[0]["question"]
    result = db.execute("SELECT correct FROM moviestv WHERE id = :randomid", randomid=randomid)
    correct = result[0]["correct"]
    result = db.execute("SELECT wrong1 FROM moviestv WHERE id = :randomid", randomid=randomid)
    wrong1 = result[0]["wrong1"]
    result = db.execute("SELECT wrong2 FROM moviestv WHERE id = :randomid", randomid=randomid)
    wrong2 = result[0]["wrong2"]
    result = db.execute("SELECT wrong3 FROM moviestv WHERE id = :randomid", randomid=randomid)
    wrong3 = result[0]["wrong3"]

    return render_template("playmoviestv.html", question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)


@app.route("/playother", methods=["GET", "POST"])
@login_required
def playother():
    """Pick random questions from other table"""

    # to randomize the question, we need to...
    # creat a variable for start range for randomizer
    result = db.execute("SELECT MIN(id) FROM other")
    start = result[0]["MIN(id)"]
    # create a variable for end range for randomizer
    result = db.execute("SELECT MAX(id) FROM other")
    end = result[0]["MAX(id)"]
    randomid = random.randint(start, end)

    # variables for question, correct answer, and wrong answers
    result = db.execute("SELECT question FROM other WHERE id = :randomid", randomid=randomid)
    question = result[0]["question"]
    result = db.execute("SELECT correct FROM other WHERE id = :randomid", randomid=randomid)
    correct = result[0]["correct"]
    result = db.execute("SELECT wrong1 FROM other WHERE id = :randomid", randomid=randomid)
    wrong1 = result[0]["wrong1"]
    result = db.execute("SELECT wrong2 FROM other WHERE id = :randomid", randomid=randomid)
    wrong2 = result[0]["wrong2"]
    result = db.execute("SELECT wrong3 FROM other WHERE id = :randomid", randomid=randomid)
    wrong3 = result[0]["wrong3"]

    return render_template("playother.html", question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)


@app.route("/playpopculture", methods=["GET", "POST"])
@login_required
def playpopculture():
    """Pick random questions from popculture table"""

    # to randomize the question, we need to...
    # creat a variable for start range for randomizer
    result = db.execute("SELECT MIN(id) FROM popculture")
    start = result[0]["MIN(id)"]
    # create a variable for end range for randomizer
    result = db.execute("SELECT MAX(id) FROM popculture")
    end = result[0]["MAX(id)"]
    randomid = random.randint(start, end)

    # variables for question, correct answer, and wrong answers
    result = db.execute("SELECT question FROM popculture WHERE id = :randomid", randomid=randomid)
    question = result[0]["question"]
    result = db.execute("SELECT correct FROM popculture WHERE id = :randomid", randomid=randomid)
    correct = result[0]["correct"]
    result = db.execute("SELECT wrong1 FROM popculture WHERE id = :randomid", randomid=randomid)
    wrong1 = result[0]["wrong1"]
    result = db.execute("SELECT wrong2 FROM popculture WHERE id = :randomid", randomid=randomid)
    wrong2 = result[0]["wrong2"]
    result = db.execute("SELECT wrong3 FROM popculture WHERE id = :randomid", randomid=randomid)
    wrong3 = result[0]["wrong3"]

    return render_template("playpopculture.html", question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)


@app.route("/playscience", methods=["GET", "POST"])
@login_required
def playscience():
    """Pick random questions from science table"""

    # to randomize the question, we need to...
    # creat a variable for start range for randomizer
    result = db.execute("SELECT MIN(id) FROM science")
    start = result[0]["MIN(id)"]
    # create a variable for end range for randomizer
    result = db.execute("SELECT MAX(id) FROM science")
    end = result[0]["MAX(id)"]
    randomid = random.randint(start, end)

    # variables for question, correct answer, and wrong answers
    result = db.execute("SELECT question FROM science WHERE id = :randomid", randomid=randomid)
    question = result[0]["question"]
    result = db.execute("SELECT correct FROM science WHERE id = :randomid", randomid=randomid)
    correct = result[0]["correct"]
    result = db.execute("SELECT wrong1 FROM science WHERE id = :randomid", randomid=randomid)
    wrong1 = result[0]["wrong1"]
    result = db.execute("SELECT wrong2 FROM science WHERE id = :randomid", randomid=randomid)
    wrong2 = result[0]["wrong2"]
    result = db.execute("SELECT wrong3 FROM science WHERE id = :randomid", randomid=randomid)
    wrong3 = result[0]["wrong3"]

    return render_template("playscience.html", question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)


@app.route("/playsports", methods=["GET", "POST"])
@login_required
def playsports():
    """Pick random questions from sports table"""

    # to randomize the question, we need to...
    # creat a variable for start range for randomizer
    result = db.execute("SELECT MIN(id) FROM sports")
    start = result[0]["MIN(id)"]
    # create a variable for end range for randomizer
    result = db.execute("SELECT MAX(id) FROM sports")
    end = result[0]["MAX(id)"]
    randomid = random.randint(start, end)

    # variables for question, correct answer, and wrong answers
    result = db.execute("SELECT question FROM sports WHERE id = :randomid", randomid=randomid)
    question = result[0]["question"]
    result = db.execute("SELECT correct FROM sports WHERE id = :randomid", randomid=randomid)
    correct = result[0]["correct"]
    result = db.execute("SELECT wrong1 FROM sports WHERE id = :randomid", randomid=randomid)
    wrong1 = result[0]["wrong1"]
    result = db.execute("SELECT wrong2 FROM sports WHERE id = :randomid", randomid=randomid)
    wrong2 = result[0]["wrong2"]
    result = db.execute("SELECT wrong3 FROM sports WHERE id = :randomid", randomid=randomid)
    wrong3 = result[0]["wrong3"]

    return render_template("playsports.html", question=question, correct=correct, wrong1=wrong1, wrong2=wrong2, wrong3=wrong3)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Get stock quote."""

    return render_template("profile.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget user_id
    session.clear()

    username = request.form.get("username")
    password = request.form.get("password")
    passwordconf = request.form.get("confirmation")

    if request.method == "POST":
        # ensure fields are not left blank
        if not username:
            return apology("You must enter a username!", 400)
        elif not password:
            return apology("You must enter a password!", 400)

        # ensure password matches confirmation password
        elif password != passwordconf:
            return apology("Password not confirmed!", 400)

        # ensure username is not already taken
        elif len(db.execute("SELECT id FROM users WHERE username = :username", username=username)) == 1:
            return apology("Username already taken.", 400)

        # else, store user in database
        else:
            # hash the password (pwd_context.encrypt)
            passwordhash = generate_password_hash(password)

            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=passwordhash)

            # once they register successfully, log them in automatically and store their id in session
            user_row = db.execute("SELECT id FROM users WHERE username = :username", username=username)
            session["user_id"] = user_row[0]["id"]

            return redirect("/")
    else:
        return render_template("register.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search for movies/tv shows"""

    return render_template("search.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
