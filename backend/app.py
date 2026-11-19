import os
import secrets
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, abort, g, jsonify, request, session
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("CODEGUARD_SECRET") or secrets.token_hex(32),
        DATABASE=os.environ.get("CODEGUARD_DB", str(Path(app.instance_path) / "records.db")),
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("CODEGUARD_HTTPS") == "1",
        MAX_CONTENT_LENGTH=8192,
    )
    app.config.update(config or {})
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close(_error):
        if "db" in g:
            g.db.close()

    with app.app_context():
        db().executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT UNIQUE,
            password_hash TEXT NOT NULL, role TEXT NOT NULL, display TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS records(id INTEGER PRIMARY KEY, owner INTEGER, title TEXT NOT NULL);
        """)

    def private(fn):
        @wraps(fn)
        def guarded(*args, **kwargs):
            if "uid" not in session:
                abort(401)
            if request.method != "GET" and not secrets.compare_digest(
                session["csrf"], request.headers.get("X-CSRF-Token", "")
            ):
                abort(403)
            return fn(*args, **kwargs)
        return guarded

    @app.after_request
    def headers(response):
        response.headers.update({"X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
            "Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})
        return response

    @app.errorhandler(HTTPException)
    def fail(error):
        return jsonify(error=error.name), error.code

    def body():
        value = request.get_json()
        if not isinstance(value, dict):
            abort(400)
        return value

    @app.post("/api/session")
    def login():
        data = body()
        name, password = data.get("name"), data.get("password")
        if not isinstance(name, str) or not isinstance(password, str):
            abort(400)
        user = db().execute("SELECT * FROM users WHERE name = ?", (name,)).fetchone()
        if not user or not check_password_hash(user["password_hash"], password):
            abort(401)
        session.clear()
        session.update(uid=user["id"], csrf=secrets.token_hex(32))
        return jsonify(csrf=session["csrf"])

    @app.delete("/api/session")
    @private
    def logout():
        session.clear()
        return "", 204

    @app.route("/api/profile", methods=["GET", "PATCH"])
    @private
    def profile():
        if request.method == "PATCH":
            display = body().get("display")
            if not isinstance(display, str) or not 1 <= len(display.strip()) <= 80:
                abort(400)
            db().execute("UPDATE users SET display=? WHERE id=?", (display.strip(), session["uid"]))
            db().commit()
        row = db().execute("SELECT display, role FROM users WHERE id=?", (session["uid"],)).fetchone()
        return jsonify(dict(row))

    @app.get("/api/records")
    @private
    def search():
        term = request.args.get("q", "")
        if len(term) > 120:
            abort(400)
        rows = db().execute("SELECT id,title FROM records WHERE owner=? AND instr(lower(title),lower(?))>0",
                            (session["uid"], term))
        return jsonify([dict(row) for row in rows])

    @app.get("/api/records/<int:key>")
    @private
    def record(key):
        row = db().execute("SELECT id,title FROM records WHERE id=? AND owner=?",
                           (key, session["uid"])).fetchone()
        if row is None:
            abort(404)
        return jsonify(dict(row))

    @app.get("/api/admin/summary")
    @private
    def admin():
        role = db().execute("SELECT role FROM users WHERE id=?", (session["uid"],)).fetchone()
        if role["role"] != "admin":
            abort(403)
        return jsonify(records=db().execute("SELECT count(*) FROM records").fetchone()[0])

    @app.cli.command("seed")
    def seed():
        with db():
            for name, role in [("river", "member"), ("fern", "member"), ("atlas", "admin")]:
                if db().execute("SELECT 1 FROM users WHERE name=?", (name,)).fetchone():
                    continue
                password = secrets.token_urlsafe(18)
                user = db().execute("INSERT INTO users(name,password_hash,role,display) VALUES(?,?,?,?)",
                    (name, generate_password_hash(password), role, name.title()))
                db().execute("INSERT INTO records(owner,title) VALUES(?,?)", (user.lastrowid, "Review notes"))
                print(f"Local fictional account {name} / {password}")
    return app
