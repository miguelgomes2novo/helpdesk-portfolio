"""Testes de integração da API HelpDesk com banco SQLite temporário."""
import os
import tempfile
import unittest
from app import create_app

class HelpDeskTests(unittest.TestCase):
    def setUp(self):
        fd,self.db_path=tempfile.mkstemp(suffix=".sqlite3")
        os.close(fd)
        self.app=create_app({"TESTING":True,"DATABASE":self.db_path,"SEED_DEMO":False})
        self.client=self.app.test_client()
        self.payload={"title":"Configurar VPN","requester":"Pessoa Exemplo",
                      "department":"Suporte","category":"Rede","description":"Teste",
                      "priority":"Alta","status":"Aberto"}

    def tearDown(self):
        if os.path.exists(self.db_path): os.remove(self.db_path)

    def test_health(self):
        response=self.client.get("/api/saude")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["status"],"ok")

    def test_crud(self):
        created=self.client.post("/api/chamados",json=self.payload)
        self.assertEqual(created.status_code,201)
        ticket_id=created.json["id"]
        self.assertEqual(self.client.get(f"/api/chamados/{ticket_id}").json["title"],"Configurar VPN")
        self.assertEqual(self.client.get("/api/chamados").json["total"],1)
        updated=self.client.patch(f"/api/chamados/{ticket_id}/status",json={"status":"Resolvido"})
        self.assertEqual(updated.json["status"],"Resolvido")
        self.assertEqual(self.client.delete(f"/api/chamados/{ticket_id}").status_code,204)
        self.assertEqual(self.client.get("/api/chamados").json["total"],0)

    def test_validation(self):
        self.assertEqual(self.client.post("/api/chamados",json={}).status_code,400)
        self.assertEqual(self.client.post("/api/chamados",json={**self.payload,"priority":"Inválida"}).status_code,400)

    def test_dashboard(self):
        data=self.client.get("/api/indicadores").json
        self.assertEqual(data["total"],0)

if __name__=="__main__":
    unittest.main()
