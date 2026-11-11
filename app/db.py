"""Persistência SQLite e chamados fictícios de demonstração."""
import sqlite3
from datetime import datetime, timedelta, timezone
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL, requester TEXT NOT NULL, department TEXT NOT NULL,
category TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
priority TEXT NOT NULL CHECK(priority IN ('Baixa','Média','Alta','Crítica')),
status TEXT NOT NULL CHECK(status IN ('Aberto','Em andamento','Resolvido')),
created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);
"""

DEMO_TICKETS = [
("Notebook não conecta ao Wi-Fi","Ana Martins","Comercial","Rede","Conexão intermitente com a rede.","Alta","Aberto"),
("Instalar impressora do setor","Rafael Costa","Financeiro","Hardware","Configurar impressora compartilhada.","Média","Em andamento"),
("Redefinir senha do e-mail","Camila Rocha","Recursos Humanos","Acesso","A conta institucional não abre.","Baixa","Resolvido"),
("Sistema ERP indisponível","Pedro Lima","Operações","Software","Sistema apresenta erro ao iniciar.","Crítica","Aberto"),
("Monitor com tela piscando","Beatriz Alves","Marketing","Hardware","Imagem intermitente.","Média","Aberto"),
("Acesso à pasta compartilhada","João Ribeiro","Jurídico","Acesso","Solicitação de permissão.","Baixa","Resolvido"),
]

def get_db():
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db

def close_db(_error=None):
    conn = g.pop("db",None)
    if conn is not None: conn.close()

def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    if current_app.config.get("SEED_DEMO",False) and db.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] == 0:
        now = datetime.now(timezone.utc)
        rows=[]
        for i, fields in enumerate(DEMO_TICKETS):
            ts=(now-timedelta(hours=i*4+1)).strftime("%Y-%m-%d %H:%M:%S")
            rows.append((*fields,ts,ts))
        db.executemany("""INSERT INTO tickets
        (title,requester,department,category,description,priority,status,created_at,updated_at)
        VALUES (?,?,?,?,?,?,?,?,?)""",rows)
    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context(): init_db()
