# Autou Email Classifier

Solução inteligente para classificação de emails usando FastAPI e Google Gemini.

## 📋 Arquitetura

```
Cliente (Navegador)
    ↓
FastAPI Server (Docker Container)
    ├── File Parser Service (PDF/TXT)
    ├── Prompt Engineer Service
    └── Google Gemini Client
            ↓
        Google Gemini API (gemini-2.5-flash)
```

## 🚀 Quick Start

### Pré-requisitos
- Python 3.10+
- Docker e Docker Compose
- Chave API do Google Gemini

### Instalação Local

```bash
# Clone o repositório
git clone <repo-url>
cd autou-email-classifier

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua GEMINI_API_KEY
```

### Executar localmente

```bash
uvicorn src.main:app --reload
```

A API estará disponível em `http://localhost:8000`

### Documentação Interativa
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Com Docker Compose

```bash
docker-compose up
```

## 🧪 Testes

```bash
pytest tests/ -v --cov=src
```

## 📐 Estrutura do Projeto

```
.
├── src/
│   ├── main.py              # FastAPI app
│   ├── services/            # Lógica de negócio
│   │   ├── file_parser.py
│   │   └── ai_service.py
│   ├── routes/              # Endpoints
│   ├── controllers/         # Controladores
│   └── utils/               # Utilitários
├── frontend/                # Interface Web
│   ├── index.html
│   └── script.js
├── tests/                   # Testes unitários
├── .github/workflows/       # CI/CD
├── Dockerfile               # Container
├── docker-compose.yml       # Orquestração
├── requirements.txt         # Dependências
└── README.md               # Este arquivo
```

## 🔄 Git Flow

```
main (producão)
  ↓
develop (staging)
  ↓
feature/* (desenvolvimento)
```

Fluxo de trabalho:
1. Crie uma branch `feature/seu-recurso` a partir de `develop`
2. Faça commits pequenos e descritivos
3. Push para a branch e abra um Pull Request
4. Após aprovação, merge para `develop` e depois para `main`

## 🔒 Variáveis de Ambiente

```env
GEMINI_API_KEY=sua_chave_aqui
ENVIRONMENT=production
DEBUG=false
```

## 📝 Roadmap

- [ ] **Fase 1**: Fundação e CI
  - [x] Estrutura de pastas
  - [ ] Dockerfile otimizado
  - [ ] GitHub Actions CI
- [ ] **Fase 2**: Backend Core
  - [ ] File Parser
  - [ ] AI Service
  - [ ] Endpoints
- [ ] **Fase 3**: Frontend
  - [ ] Interface Web
  - [ ] Integração Frontend-Backend
- [ ] **Fase 4**: Deploy
  - [ ] Deploy em produção
  - [ ] Documentação
  - [ ] Vídeo demonstrativo

## 📄 Licença

Ver arquivo LICENSE

## 👨‍💻 Desenvolvimento

Contribuições são bem-vindas! Siga o Git Flow e certifique-se de que:
- Código passa no `ruff`
- Testes cobrem novas funcionalidades
- Commit messages são descritivas
