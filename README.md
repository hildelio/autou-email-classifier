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
# Google Gemini API Key
GEMINI_API_KEY=sua_chave_aqui

# Model selection (opcional, default: gemini-2.5-flash)
GEMINI_MODEL=gemini-2.5-flash

# Application environment
ENVIRONMENT=production
DEBUG=false
```

### Gerenciamento de Configuração

A aplicação usa **Pydantic Settings** (`src/config.py`) para gerenciar configurações:

- **Carregamento centralizado**: Todas as settings em um único arquivo
- **Type-safe**: Validação automática de tipos
- **Environment-aware**: Diferentes valores por ambiente (dev/prod)
- **Easy maintenance**: Trocar o modelo Gemini sem alterar código

**Exemplo**: Para usar `gemini-3.0-pro` em produção:
```bash
export GEMINI_MODEL=gemini-3.0-pro
docker-compose up
```

Pronto! A API usará o novo modelo sem mexer no código.

## 📝 Roadmap

- [x] **Fase 1**: Fundação e CI ✅ COMPLETA
  - [x] Estrutura de pastas
  - [x] Dockerfile otimizado (multi-stage build)
  - [x] GitHub Actions CI (ruff + pytest + coverage)
- [ ] **Fase 2**: Backend Core
  - [x] File Parser (PDF/TXT)
  - [ ] AI Service (Gemini integration)
  - [ ] Endpoints (POST /analyze)
- [ ] **Fase 3**: Frontend
  - [ ] Interface Web (HTML/CSS/JS)
  - [ ] Integração Frontend-Backend
- [ ] **Fase 4**: Deploy
  - [ ] Deploy em produção (Render/Railway)
  - [ ] Documentação final
  - [ ] Vídeo demonstrativo

## 📄 Licença

Ver arquivo LICENSE

## 👨‍💻 Desenvolvimento

Contribuições são bem-vindas! Siga o Git Flow e certifique-se de que:
- Código passa no `ruff`
- Testes cobrem novas funcionalidades
- Commit messages são descritivas
