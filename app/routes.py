"""Rotas da interface e API REST do HelpDesk."""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, render_template, request
from .db import get_db

api = Blueprint("api", __name__)
PRIORITIES = {"Baixa","Média","Alta","Crítica"}
STATUSES = {"Aberto","Em andamento","Resolvido"}
CATEGORIES = {"Hardware","Software","Rede","Acesso","Outros"}
REQUIRED = {"title":120,"requester":80,"department":80}

def serialize(row): return dict(row)
def utc_now(): return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def validate_ticket(body):
    if not isinstance(body, dict): return None,"Envie um objeto JSON válido."
    result={}
    for field,limit in REQUIRED.items():
        value=body.get(field)
        if not isinstance(value,str) or not value.strip(): return None,f"O campo '{field}' é obrigatório."
        result[field]=value.strip()
        if len(result[field])>limit: return None,f"O campo '{field}' deve ter no máximo {limit} caracteres."
    desc=body.get("description","")
    if not isinstance(desc,str) or len(desc.strip())>1000: return None,"Descrição inválida (máximo de 1000 caracteres)."
    result["description"]=desc.strip()
    for field,values,default in (
        ("category",CATEGORIES,"Outros"),("priority",PRIORITIES,"Média"),("status",STATUSES,"Aberto")
    ):
        value=body.get(field,default)
        if not isinstance(value,str) or value not in values: return None,f"Valor inválido para '{field}'."
        result[field]=value
    return result,None

def ticket_by_id(ticket_id):
    return get_db().execute("SELECT * FROM tickets WHERE id = ?",(ticket_id,)).fetchone()

@api.get("/")
def index(): return render_template("index.html")

@api.get("/api/saude")
def health(): return jsonify({"status":"ok"})

@api.get("/api/chamados")
def list_tickets():
    filters=[]; args=[]
    status=request.args.get("status","").strip()
    priority=request.args.get("prioridade","").strip()
    search=request.args.get("busca","").strip()
    if status:
        if status not in STATUSES: return jsonify({"erro":"Filtro de status inválido."}),400
        filters.append("status = ?"); args.append(status)
    if priority:
        if priority not in PRIORITIES: return jsonify({"erro":"Filtro de prioridade inválido."}),400
        filters.append("priority = ?"); args.append(priority)
    if search:
        if len(search)>120: return jsonify({"erro":"Busca muito longa."}),400
        escaped=search.replace("\\","\\\\").replace("%","\\%").replace("_","\\_")
        filters.append("(title LIKE ? ESCAPE '\\' OR requester LIKE ? ESCAPE '\\' OR department LIKE ? ESCAPE '\\')")
        args.extend([f"%{escaped}%"]*3)
    sql="SELECT * FROM tickets"+(" WHERE "+" AND ".join(filters) if filters else "")+" ORDER BY created_at DESC, id DESC"
    rows=get_db().execute(sql,args).fetchall()
    return jsonify({"chamados":[serialize(row) for row in rows],"total":len(rows)})

@api.get("/api/chamados/<int:ticket_id>")
def get_ticket(ticket_id):
    row=ticket_by_id(ticket_id)
    return (jsonify(serialize(row)) if row else (jsonify({"erro":"Chamado não encontrado."}),404))

@api.post("/api/chamados")
def create_ticket():
    data,error=validate_ticket(request.get_json(silent=True))
    if error: return jsonify({"erro":error}),400
    db=get_db(); now=utc_now()
    cursor=db.execute("""INSERT INTO tickets
    (title,requester,department,category,description,priority,status,created_at,updated_at)
    VALUES (?,?,?,?,?,?,?,?,?)""",
    (data["title"],data["requester"],data["department"],data["category"],data["description"],data["priority"],data["status"],now,now))
    db.commit()
    return jsonify(serialize(ticket_by_id(cursor.lastrowid))),201

@api.put("/api/chamados/<int:ticket_id>")
def update_ticket(ticket_id):
    if ticket_by_id(ticket_id) is None: return jsonify({"erro":"Chamado não encontrado."}),404
    data,error=validate_ticket(request.get_json(silent=True))
    if error: return jsonify({"erro":error}),400
    db=get_db()
    db.execute("""UPDATE tickets SET title=?,requester=?,department=?,category=?,
    description=?,priority=?,status=?,updated_at=? WHERE id=?""",
    (data["title"],data["requester"],data["department"],data["category"],data["description"],data["priority"],data["status"],utc_now(),ticket_id))
    db.commit(); return jsonify(serialize(ticket_by_id(ticket_id)))

@api.patch("/api/chamados/<int:ticket_id>/status")
def change_status(ticket_id):
    if ticket_by_id(ticket_id) is None: return jsonify({"erro":"Chamado não encontrado."}),404
    data=request.get_json(silent=True)
    if not isinstance(data,dict) or data.get("status") not in STATUSES:
        return jsonify({"erro":"Status inválido."}),400
    db=get_db(); db.execute("UPDATE tickets SET status=?,updated_at=? WHERE id=?",(data["status"],utc_now(),ticket_id))
    db.commit(); return jsonify(serialize(ticket_by_id(ticket_id)))

@api.delete("/api/chamados/<int:ticket_id>")
def delete_ticket(ticket_id):
    db=get_db(); cursor=db.execute("DELETE FROM tickets WHERE id=?",(ticket_id,))
    if cursor.rowcount==0: return jsonify({"erro":"Chamado não encontrado."}),404
    db.commit(); return "",204

@api.get("/api/indicadores")
def metrics():
    row=get_db().execute("""SELECT COUNT(*) AS total,
    SUM(CASE WHEN status='Aberto' THEN 1 ELSE 0 END) AS abertos,
    SUM(CASE WHEN status='Em andamento' THEN 1 ELSE 0 END) AS andamento,
    SUM(CASE WHEN status='Resolvido' THEN 1 ELSE 0 END) AS resolvidos,
    SUM(CASE WHEN priority='Crítica' AND status!='Resolvido' THEN 1 ELSE 0 END) AS criticos
    FROM tickets""").fetchone()
    return jsonify(serialize(row))
