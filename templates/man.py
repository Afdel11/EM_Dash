from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import sqlite3
import datetime

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'votre_clé_secrète'
app.config['DATABASE'] = 'library.db'


@app.route('/')
def index():
    images = ['./sqlite.jpg', './algo.jpeg', '/deep.jpeg', './arduino.jpeg', './artificielle.jpeg', "./facial.avif"]
    return render_template('index.html', images=images)


@app.route('/Apropos')
def apropos():
    return render_template('Apropos.html', images=images)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user_name = request.form["user_name"]
        email = request.form["e_mail"]
        password = request.form["password"]
        confirm_password = request.form["Confirmer"]

        if password != confirm_password:
            return render_template("signup.html", error_message="Les mots de passe ne correspondent pas")

        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE user_name = ?", (user_name,))
        if cursor.fetchone():
            return render_template("signup.html", error_message="Ce nom d'utilisateur est déjà utilisé")

        cursor.execute("SELECT * FROM users WHERE e_mail = ?", (email,))
        if cursor.fetchone():
            return render_template("signup.html", error_message="Cette adresse e-mail est déjà utilisée")

        cursor.execute("INSERT INTO users (user_name, e_mail, password) VALUES (?, ?, ?)", (user_name, email, password))
        conn.commit()
        conn.close()

        return redirect(url_for("Login", success_message="Inscription réussie. Veuillez vous connecter."))
    else:
        return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def Login():
    if 'id_user' in session:
        return redirect(url_for("Biblio"))

    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")

        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password = ?", (user_name, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session['id_user'] = user[0]
            session['Role'] = user[-1]

            if user[-1] == "admin":
                return redirect(url_for("Admin"))
            else:
                return redirect(url_for("Biblio"))
        else:
            return render_template("login.html", error_message="Nom d'utilisateur ou mot de passe incorrect")

    return render_template("login.html")


@app.route('/biblio', methods=["GET", "POST"])
def Biblio():
    if 'id_user' not in session:
        return redirect(url_for('Login'))

    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Livre')
    Livre = cursor.fetchall()

    if request.method == "POST":
        livre_id = request.form.get('livre_id')

        borrow_date = datetime.date.today()
        borrow_hour = datetime.datetime.now().strftime("%H:%M")
        return_date = borrow_date + datetime.timedelta(days=20)

        cursor.execute("SELECT * FROM Livre WHERE Id_book = ?", (livre_id,))
        book = cursor.fetchone()

        if book[4] == 'Disponible':
            cursor.execute("INSERT INTO emprunt (id_book, borrow_date, borrow_hour, return_date, Id_user) "
                           "VALUES (?, ?, ?, ?, ?)",
                           (book[0], borrow_date, borrow_hour, return_date, session['id_user']))

            cursor.execute("UPDATE Livre SET Disponibilité = ? WHERE Id_book = ?", ('Indisponible', book[0]))
            conn.commit()

            cursor.execute('SELECT * FROM Livre')
            Livre = cursor.fetchall()
            success_message = "Votre réservation du livre a bien été enregistrée."
            return render_template('biblio.html', Livre=Livre, success_message="Votre réservation du livre a bien été enregistrée.")

    conn.close()

    return render_template('biblio.html', Livre=Livre)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id_user' in session:
            if session['Role'] == "admin":
                return f(*args, **kwargs)

        return render_template('error.html', error_message="Vous n'avez pas les droits d'administrateur pour effectuer cette action.")
    return decorated_function


@app.route('/admin', methods=["POST", "GET"])
@admin_required
def Admin():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Livre.Titre, users.user_name, borrow_date, return_date,Livre.Disponibilité, Livre.id_book
        FROM emprunt
        JOIN users ON users.id_user = emprunt.Id_user
        JOIN Livre ON Livre.id_book = emprunt.id_book
        ORDER BY borrow_date DESC
    """)
    emprunts = cursor.fetchall()

    if request.method == "POST":
        id_book = request.form.get("id_book")
        cursor.execute("UPDATE Livre SET Disponibilité = ? WHERE Id_book = ?", ('Disponible', id_book))
        conn.commit()

        cursor.execute("""
                SELECT Livre.Titre, users.user_name, borrow_date, return_date,Livre.Disponibilité, Livre.id_book
                FROM emprunt
                JOIN users ON users.id_user = emprunt.Id_user
                JOIN Livre ON Livre.id_book = emprunt.id_book
                ORDER BY borrow_date DESC
            """)
        emprunts = cursor.fetchall()
        success_message = "Le livre a bien été marqué comme rendu."
        return render_template('admin.html', emprunts=emprunts, success_message=success_message)

    conn.close()

    return render_template('admin.html', emprunts=emprunts)


@app.route("/Dashboard")
def shiny_app():
    return render_template('shiny_app.html')


@app.route('/logout')
def logout():
    if session.get('id_user'):
        session.pop('id_user', None)
        #flash('Vous avez été déconnecté.')
    else:
        #flash('Vous n\'êtes pas connecté.', 'error')

        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
