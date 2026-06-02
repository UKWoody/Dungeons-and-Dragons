import json
import sqlite3
import uuid
from pathlib import Path

root = Path(__file__).resolve().parent
pack_dir = root / "packs" / "artifacts"
db_path = root / "packs" / "artifacts.db"

json_files = sorted(pack_dir.glob("*.json"))
if not json_files:
    raise SystemExit("No JSON item files found in packs/artifacts")

if db_path.exists():
    db_path.unlink()

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("CREATE TABLE metadata (key TEXT UNIQUE, value TEXT)")
cur.execute("CREATE TABLE documents (key TEXT UNIQUE, type TEXT, document TEXT)")
metadata = [
    ("system", "dnd5e"),
    ("package", "the-obelisk-sage"),
    ("name", "artifacts"),
    ("label", "Artifacts"),
    ("type", "Item")
]
cur.executemany("INSERT INTO metadata (key, value) VALUES (?, ?)", metadata)
for path in json_files:
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc_id = str(uuid.uuid4())
    doc["_id"] = doc_id
    doc.setdefault("img", "")
    doc.setdefault("permission", {"default": 0})
    doc.setdefault("sort", 0)
    doc.setdefault("flags", {})
    packed = json.dumps(doc, separators=(",", ":"), ensure_ascii=False)
    cur.execute("INSERT INTO documents (key, type, document) VALUES (?, ?, ?)", (doc_id, "Item", packed))
conn.commit()
conn.close()
print(f"Created {db_path} with {len(json_files)} documents")
