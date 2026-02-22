from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
import uuid

app = Flask(__name__)
app.secret_key = "charro_secret"

UPLOAD_EVENTOS = "static/uploads"
UPLOAD_GALERIA = "static/galeria"

os.makedirs(UPLOAD_EVENTOS, exist_ok=True)
os.makedirs(UPLOAD_GALERIA, exist_ok=True)


# ======================
# DATABASE
# ======================

def db():
    return sqlite3.connect("database.db")


def init_db():

    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS eventos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        descripcion TEXT,
        fecha TEXT,
        hora TEXT,
        imagen TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS galeria(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imagen TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS equipos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        descripcion TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ======================
# HOME
# ======================

@app.route("/")
def index():

    conn = db()
    c = conn.cursor()

    eventos = c.execute("SELECT * FROM eventos ORDER BY id DESC").fetchall()
    galeria = c.execute("SELECT * FROM galeria ORDER BY id DESC").fetchall()
    equipos = c.execute("SELECT * FROM equipos").fetchall()

    conn.close()

    return render_template(
        "index.html",
        eventos=eventos,
        galeria=galeria,
        equipos=equipos
    )


# ======================
# LOGIN ADMIN
# ======================

@app.route("/admin", methods=["GET","POST"])
def admin():

    if request.method == "POST":

        if request.form["password"] == "1234":
            session["admin"] = True
            return redirect("/panel")

    return render_template("admin.html")


# ======================
# PANEL
# ======================

@app.route("/panel")
def panel():

    if not session.get("admin"):
        return redirect("/admin")

    conn = db()
    c = conn.cursor()

    eventos = c.execute("SELECT * FROM eventos").fetchall()
    galeria = c.execute("SELECT * FROM galeria").fetchall()
    equipos = c.execute("SELECT * FROM equipos").fetchall()

    conn.close()

    return render_template(
        "panel.html",
        eventos=eventos,
        galeria=galeria,
        equipos=equipos
    )


# ======================
# SUBIR EVENTO
# ======================

@app.route("/subir_evento", methods=["POST"])
def subir_evento():

    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    imagen = request.files["imagen"]

    filename = str(uuid.uuid4()) + imagen.filename
    imagen.save(os.path.join(UPLOAD_EVENTOS, filename))

    conn = db()
    c = conn.cursor()

    c.execute(
        "INSERT INTO eventos(titulo,descripcion,fecha,hora,imagen) VALUES(?,?,?,?,?)",
        (titulo,descripcion,fecha,hora,filename)
    )

    conn.commit()
    conn.close()

    return redirect("/panel")


# ======================
# SUBIR GALERIA
# ======================

@app.route("/subir_galeria", methods=["POST"])
def subir_galeria():

    imagen = request.files["imagen"]

    filename = str(uuid.uuid4()) + imagen.filename
    imagen.save(os.path.join(UPLOAD_GALERIA, filename))

    conn = db()
    c = conn.cursor()

    c.execute(
        "INSERT INTO galeria(imagen) VALUES(?)",
        (filename,)
    )

    conn.commit()
    conn.close()

    return redirect("/panel")


# ======================
# EDITAR EQUIPO
# ======================

@app.route("/editar_equipo", methods=["POST"])
def editar_equipo():

    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]

    conn = db()
    c = conn.cursor()

    c.execute(
        "INSERT INTO equipos(nombre,descripcion) VALUES(?,?)",
        (nombre,descripcion)
    )

    conn.commit()
    conn.close()

    return redirect("/panel")


# ======================
# RUN
# ======================

if __name__ == "__main__":
    app.run()
