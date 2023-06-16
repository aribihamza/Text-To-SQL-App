from flask import Flask, flash, render_template, redirect, url_for, session , request, url_for
from classes import QueryForm, LoginForm, QuestionForm
from db_connector import DBConnector
from generatesql import GenerateSQL
from datetime import timedelta
from functools import wraps
import secrets
sql_generator = GenerateSQL()
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.permanent_session_lifetime = timedelta(minutes=5)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('logout', next=request.url))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route("/", methods=["GET", "POST"])
def home():
    form = LoginForm()
    if form.validate_on_submit():
        session["server"] = form.server.data
        session["database"] = form.database.data
        session["username"] = form.username.data
        session["password"] = form.password.data
        session["db_type"] = form.db_type.data
        db = DBConnector(session["db_type"], session["server"], session["database"], session["username"], session["password"])

        try:
            connection = db.connect()
            connection.close()
            session.permanent = True
            flash('You were successfully logged in')
            return redirect(url_for("query"))
        except Exception as e:
            flash('Invalid credentials'+str(e))
    return render_template("connect.html", form=form)


@app.route("/query", methods=["GET", "POST"])
@login_required
def query():
    form = QueryForm()
    results = None
    structure = None
    query_text = ""
    if form.validate_on_submit():
        query_text = form.query.data.strip().upper()
        if not query_text.startswith("SELECT"):
            flash('Only SELECT queries are allowed')
            return render_template("query.html", form=form, previous_query=query_text, question=session.get("question", ""))
        session["query"] = query_text
        db = DBConnector(session["db_type"], session["server"], session["database"], session["username"], session["password"])
        connection = db.connect()
        structure = db.get_db_structure()
        print(structure)

        cursor = connection.cursor()
        try:
            cursor.execute(query_text)
            results = cursor.fetchall()
        except Exception as e:
            flash('Failed to execute SQL query')

        cursor.close()
        db.close()

    return render_template("query.html", form=form, results=results, previous_query=query_text, question=session.get("question", ""))


@app.route("/question", methods=["GET", "POST"])
@login_required
def question():
    form = QuestionForm()
    results = None
    structure = None
    query_text = session.get("query", "")  
    question_text = ""
    if form.validate_on_submit():
        question_text = form.question.data
        session["question"] = question_text  

        query_text = form.query.data 

        db = DBConnector(session["db_type"], session["server"], session["database"], session["username"], session["password"])
        connection = db.connect()
        structure = db.get_db_structure()
        print(structure)

        query = sql_generator.generate_sql(question_text, structure)
        if query is not None:
            query = query.strip().upper()  
            if not query.startswith("SELECT"):
                flash('Only SELECT queries are allowed')
                return render_template("query.html", form=form, previous_query=query_text, question=session.get("question", ""))
            try:
                cursor = connection.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()
                session["query"] = query  
                query_text = query  
            except Exception as e:
                flash('Failed to execute SQL query')
        else:
            flash('Failed to generate a valid SQL query from the given question')

        db.close()

    return render_template("query.html", form=form, results=results, previous_query=query_text,
                           question=session.get("question", ""))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
