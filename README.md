# HelpDesk — Sistema de Chamados de TI

Aplicação web de portfólio desenvolvida com **Python, Flask, SQLite, HTML, CSS e JavaScript**, com gerenciamento de chamados (CRUD), dashboard, filtros de pesquisa, API REST e testes.

> **Projeto demonstrativo:** os nomes dos chamados iniciais são fictícios. Esta aplicação foi feita para execução local e **não possui autenticação**. Não publique a aplicação na internet ou insira dados reais sem implementar segurança e controle de acesso.

## Funcionalidades

- Criar, listar, editar e excluir chamados de suporte técnico;
- Filtrar por status e prioridade e pesquisar títulos, solicitantes e setores;
- Visualizar indicadores de chamados abertos, em andamento e resolvidos;
- Persistência de dados em SQLite (banco criado automaticamente);
- Validação no servidor, consultas parametrizadas e interface responsiva;
- Testes de integração com unittest e GitHub Actions.

## Executar no Windows

Instale o Python 3.10+ e execute estes comandos dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

Abra **http://127.0.0.1:5000** no navegador. Para encerrar, use Ctrl+C.

Em Linux/macOS, use `python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt` e `.venv/bin/python run.py`.

## Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Estrutura

```text
app/
  __init__.py       # Fábrica Flask
  db.py             # SQLite e dados de demonstração
  routes.py         # Endpoints REST
  templates/
    index.html      # Interface responsiva (HTML/CSS/JS)
tests/
  test_app.py        # Testes automatizados
.github/workflows/
  testes.yml         # GitHub Actions
requirements.txt
run.py
.gitignore
```

## Endpoints

| Método | Rota | Função |
| --- | --- | --- |
| GET | /api/saude | Saúde do sistema |
| GET | /api/chamados | Listagem com filtros |
| POST | /api/chamados | Criar |
| GET | /api/chamados/{id} | Detalhar |
| PUT | /api/chamados/{id} | Editar |
| PATCH | /api/chamados/{id}/status | Mudar status |
| DELETE | /api/chamados/{id} | Excluir |
| GET | /api/indicadores | Painel |

## Próximos passos

Login e autorização de usuários, histórico de mudanças, SLA, paginação e implantação segura.

*Projeto didático para apresentação de competências em desenvolvimento de software.*
