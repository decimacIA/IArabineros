import json, sqlite3, unicodedata, re
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

ROOT=Path(__file__).parent
DB=ROOT/"normativa.sqlite3"
app=FastAPI(title="IArabineros",description="Consulta documental pública de normativa policial chilena")

def normalize(s):
    return "".join(c for c in unicodedata.normalize("NFD",s.casefold()) if unicodedata.category(c)!="Mn")

class Ask(BaseModel):
    question:str=Field(min_length=1,max_length=1000)

@app.get("/")
def home():return FileResponse(ROOT/"index.html")

@app.get("/api/status")
def status():
    if not DB.exists():return {"indexed_documents":0,"indexed_passages":0,"ready":False}
    with sqlite3.connect(DB) as c:
        return {"indexed_documents":c.execute("SELECT count(DISTINCT source_id) FROM passages").fetchone()[0],"indexed_passages":c.execute("SELECT count(*) FROM passages").fetchone()[0],"ready":True}

@app.post("/api/ask")
def ask(q:Ask):
    if not DB.exists():
        return {"answer":"La biblioteca está preparada, pero todavía no se han incorporado documentos oficiales verificables. No inventaré artículos ni funciones.","citations":[]}
    terms=list(dict.fromkeys(re.findall(r"[^\\W_]+",normalize(q.question))))
    stop={"que","cual","cuales","las","los","del","una","para","como","son","por","con","sobre","segun","de","la","el","en","y","un","se","me","sus"}
    terms=[t for t in terms if t not in stop and len(t)>1]
    if not terms:return {"answer":"Escribe una palabra o pregunta concreta.","citations":[]}
    with sqlite3.connect(DB) as c:
        rows=c.execute("SELECT source_id,title,url,article,page,text FROM passages").fetchall()
    scored=[]
    for source_id,title,url,article,page,body in rows:
        hay=normalize(body+" "+(article or "")+" "+title)
        matches=sum(1 for t in terms if t in hay)
        if matches:scored.append((matches,source_id,title,url,article,page,body))
    scored.sort(key=lambda x:x[0],reverse=True)
    results=[{"source_id":s,"title":title,"url":url,"article":article,"page":page,"excerpt":body[:2200]} for _,s,title,url,article,page,body in scored[:5]]
    if not results:return {"answer":"No encontré coincidencias en los documentos incorporados. Esto no significa que la materia no esté regulada.","citations":[]}
    return {"answer":"Encontré los siguientes pasajes documentales. Revisa las fuentes originales para confirmar contexto y vigencia.","citations":results}
