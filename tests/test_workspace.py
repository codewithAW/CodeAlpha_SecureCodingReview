import sqlite3
import pytest
from werkzeug.security import generate_password_hash
from backend.app import create_app


@pytest.fixture
def site(tmp_path):
    path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE": str(path)})
    with sqlite3.connect(path) as db:
        for name, role in [("alice","member"), ("bea","member"), ("chief","admin")]:
            db.execute("INSERT INTO users(name,password_hash,role,display) VALUES(?,?,?,?)",
                       (name, generate_password_hash("local-test", method="pbkdf2:sha256:1000"), role, name))
        db.executemany("INSERT INTO records(owner,title) VALUES(?,?)", [(1,"Review"),(2,"Memo")])
    return app.test_client()


def login(site, name="alice"):
    response = site.post("/api/session", json={"name": name, "password":"local-test"})
    assert response.status_code == 200
    return {"X-CSRF-Token":response.json["csrf"]}


def test_owner_boundary(site):
    login(site)
    assert site.get("/api/records/1").json["title"] == "Review"
    assert site.get("/api/records/2").status_code == 404


def test_profile_projection(site):
    login(site)
    assert site.get("/api/profile").json == {"display":"alice","role":"member"}


def test_display_validation(site):
    token = login(site)
    for value in ["  ", None, 5, "x"*81]:
        assert site.patch("/api/profile", headers=token,json={"display":value}).status_code == 400
    assert site.patch("/api/profile",headers=token,json={"display":"River"}).json["display"] == "River"


def test_admin_boundary(site):
    login(site)
    assert site.get("/api/admin/summary").status_code == 403
    login(site, "chief")
    assert site.get("/api/admin/summary").json == {"records":2}


def test_search(site):
    login(site)
    assert site.get("/api/records?q=view").json == [{"id":1,"title":"Review"}]
    assert site.get("/api/records",query_string={"q":"River's notes"}).json == []
    assert site.get("/api/records?q=Memo").json == []


def test_csrf_and_logout(site):
    token = login(site)
    assert site.delete("/api/session").status_code == 403
    assert site.delete("/api/session",headers=token).status_code == 204
    assert site.get("/api/profile").status_code == 401


def test_content_and_session(site):
    reply = site.post("/api/session",json={"name":"alice","password":"local-test"})
    assert "HttpOnly" in reply.headers["Set-Cookie"]
    assert "SameSite=Lax" in reply.headers["Set-Cookie"]
    assert reply.headers["X-Content-Type-Options"] == "nosniff"
    assert reply.is_json
    assert "frame-ancestors 'none'" in reply.headers["Content-Security-Policy"]


def test_bad_login(site):
    assert site.post("/api/session",json={"name":"alice","password":"incorrect"}).status_code == 401
    assert site.get("/api/profile").status_code == 401
