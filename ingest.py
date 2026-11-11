"""Importar texto público verificado desde archivos locales.
Uso: python ingest.py archivo.json
Formato: lista de {source_id,title,url,article,page,text}.
No descarga ni reproduce automáticamente textos de sitios externos.
"""
import json,sqlite3,sys
from pathlib import Path
DB=Path(__file__).parent/"normativa.sqlite3"
def main(path):
    records=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(records,list):raise ValueError("Se requiere una lista de pasajes")
    with sqlite3.connect(DB) as con:
        con.execute("CREATE TABLE IF NOT EXISTS passages (source_id TEXT NOT NULL,title TEXT NOT NULL,url TEXT NOT NULL,article TEXT,page TEXT,text TEXT NOT NULL)")
        con.execute("CREATE INDEX IF NOT EXISTS ix_passages_source ON passages(source_id)")
        for r in records:
            if not all(r.get(k) for k in ("source_id","title","url","text")):raise ValueError("Faltan campos obligatorios")
            if not r["url"].startswith("https://"):raise ValueError("La fuente debe ser HTTPS")
            con.execute("INSERT INTO passages VALUES (?,?,?,?,?,?)",(r["source_id"],r["title"],r["url"],r.get("article"),r.get("page"),r["text"]))
    print(f"Importados {len(records)} pasajes")
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("Uso: python ingest.py archivo.json")
    main(sys.argv[1])
