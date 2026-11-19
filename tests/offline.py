"""Execute the actual handler bodies with SQLite and small request/response test doubles.
This suite covers handler logic. Flask routing, decorators and sessions require pytest.
"""
import ast
from pathlib import Path
import sqlite3
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Denied(Exception):
    pass


def abort(status):
    raise Denied(status)


class Controls(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.row_factory = sqlite3.Row
        tree = ast.parse((ROOT/"backend/app.py").read_text())
        schema = next(n.value for n in ast.walk(tree) if isinstance(n,ast.Constant)
                      and isinstance(n.value,str) and "CREATE TABLE IF NOT EXISTS users" in n.value)
        self.db.executescript(schema)
        self.db.executemany("INSERT INTO users VALUES(?,?,?,?,?)",
            [(1,"river","fixture","member","River"),(2,"atlas","fixture","admin","Atlas")])
        self.db.executemany("INSERT INTO records VALUES(?,?,?)",[(1,1,"Notes"),(2,2,"Memo")])
        self.request = SimpleNamespace(method="GET")
        self.session = {"uid":1}
        self.data = {}
        self.handlers = dict(db=lambda:self.db,session=self.session,abort=abort,request=self.request,
                             body=lambda:self.data,jsonify=lambda *args,**kwargs:args[0] if args else kwargs)
        for node in ast.walk(tree):
            if isinstance(node,ast.FunctionDef) and node.name in {"record","profile","admin"}:
                node.decorator_list = []
                module = ast.Module(body=[node],type_ignores=[])
                exec(compile(module,"backend/app.py","exec"),self.handlers)

    def test_owner_boundary(self):
        self.assertEqual(self.handlers["record"](1),{"id":1,"title":"Notes"})
        with self.assertRaisesRegex(Denied,"404"):
            self.handlers["record"](2)

    def test_profile_projection(self):
        self.assertEqual(self.handlers["profile"](),{"display":"River","role":"member"})

    def test_display_validation(self):
        self.request.method="PATCH"
        for value in [None,"   ","x"*81,12]:
            self.data["display"]=value
            with self.assertRaisesRegex(Denied,"400"):
                self.handlers["profile"]()
        self.data["display"]="  New name  "
        self.assertEqual(self.handlers["profile"]()["display"],"New name")

    def test_admin_boundary(self):
        with self.assertRaisesRegex(Denied,"403"):
            self.handlers["admin"]()
        self.session["uid"]=2
        self.assertEqual(self.handlers["admin"](),{"records":2})


if __name__=="__main__":
    unittest.main(verbosity=2)
