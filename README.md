# AutoU Email Classifier 📧🤖

> **Classificação Inteligente de Emails com IA**
> 
> Solução desenvolvida para o desafio técnico da AutoU - Automatizando a triagem e classificação de emails corporativos usando Google Gemini AI.

[![Tests](https://img.shields.io/badge/tests-74%20passing-success)](https://github.com)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-00a393)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## 🎯 Sobre o Desafio Técnico

Este projeto foi desenvolvido como resposta ao **Desafio Técnico da AutoU** para automatizar a leitura e classificação de emails corporativos.

### O Problema
Empresas do setor financeiro lidam com **alto volume de emails** diariamente:
- 📨 Solicitações de suporte técnico
- 📊 Pedidos de atualização de status
- 💬 Mensagens improdutivas (felicitações, agradecimentos)

### A Solução
Sistema inteligente que:
1. **Classifica** automaticamente emails em categorias
2. **Sugere respostas** adequadas para cada tipo
3. **Libera tempo** da equipe para tarefas mais estratégicas

---

## 🏆 Categorias de Classificação

### 📌 Produtivo
Emails que **requerem ação ou resposta específica**:
- ✅ Solicitações de suporte técnico
- ✅ Atualizações sobre casos em aberto
- ✅ Dúvidas sobre o sistema
- ✅ Pedidos de informação

**Exemplo:**
```
"Estou com problema para acessar o sistema.
Quando faço login aparece erro de autenticação..."
```

### 🎉 Improdutivo
Emails que **não necessitam ação imediata**:
- ✉️ Mensagens de felicitações
- ✉️ Agradecimentos genéricos
- ✉️ Comunicados informais

**Exemplo:**
```
"Feliz Natal a todos!
Desejo um ano novo cheio de realizações..."
```

---

## ✨ Funcionalidades

- ✅ **Upload de arquivos** (.txt, .pdf)
- ✅ **Inserção direta** de texto
- ✅ **OCR automático** para PDFs escaneados
- ✅ **Classificação com IA** (Google Gemini 2.5 Flash)
- ✅ **Respostas sugeridas** personalizadas
- ✅ **Interface web** moderna e responsiva
- ✅ **API REST** completa e documentada
- ✅ **Rate limiting** e segurança integrados
- ✅ **95% de cobertura** de testes

---

## 🏗️ Arquitetura

```
┌─────────────────┐
│  Cliente Web    │
│  (HTML/JS)      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   FastAPI       │
│   Application   │
├─────────────────┤
│  • Routes       │ ← Endpoints HTTP
│  • Services     │ ← Lógica de negócio
│  • Security     │ ← Rate limiting
└────────┬────────┘
         │
         ├──→ 📄 File Parser (PDF/TXT)
         ├──→ 🔍 OCR Service (OCR.space)
         └──→ 🤖 AI Service (Gemini)
                      │
                      ↓
              ┌───────────────┐
              │ Google Gemini │
              │  2.5 Flash    │
              └───────────────┘
```

### Decisões Arquiteturais

**Por que FastAPI?**
- ⚡ Alta performance (async/await nativo)
- 📚 Documentação automática (Swagger/ReDoc)
- 🔒 Type hints para segurança de tipos
- 🚀 Fácil deployment

**Por que Google Gemini?**
- 🧠 Modelo avançado de linguagem natural
- 🆓 API gratuita (tier generoso)
- 🇧🇷 Suporte nativo a português
- 📊 Alta qualidade de respostas

**Por que OCR.space?**
- 📸 Fallback para PDFs escaneados
- 🆓 API gratuita disponível
- 🔌 Fácil integração
- ✅ Boa precisão em português

---

## 🚀 Quick Start

### Pré-requisitos
- Python 3.10+
- Chave API do Google Gemini ([obter aqui](https://makersuite.google.com/app/apikey))
- (Opcional) Chave OCR.space para PDFs escaneados

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/autou-email-classifier.git
cd autou-email-classifier

# 2. Crie ambiente virtual
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua GEMINI_API_KEY
```

### Executar Aplicação

```bash
# Desenvolvimento
uvicorn src.main:app --reload

# A aplicação estará em: http://localhost:8000
```

### Com Docker

```bash
docker-compose up
# Acesse: http://localhost:8000
```

---

## 📖 Uso

### Interface Web

1. Acesse `http://localhost:8000`
2. Escolha uma opção:
   - **Upload de Arquivo**: Arraste um .txt ou .pdf
   - **Colar Texto**: Cole o conteúdo do email
3. Clique em "Analisar Email"
4. Veja os resultados:
   - Categoria (Produtivo/Improdutivo)
   - Nível de confiança
   - Resposta sugerida
   - Análise detalhada

### API REST

#### Analisar Email (Upload)
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@email.txt" \
  -H "Content-Type: multipart/form-data"
```

#### Resposta
```json
{
  "category": "Produtivo",
  "confidence": 0.92,
  "suggested_reply": "Olá! Estou verificando o status do seu caso...",
  "reasoning": "Email solicita informação específica sobre processo em andamento..."
}
```

### Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Apenas testes específicos
pytest tests/test_ai_service.py -v
```

**Cobertura Atual:** 95% (74 testes passando)

---

## 📁 Estrutura do Projeto

```
.
├── frontend/                 # Interface Web
│   ├── index.html           # Página principal
│   └── script.js            # Lógica do cliente
│
├── src/                     # Código fonte Python
│   ├── main.py             # Aplicação FastAPI
│   ├── config.py           # Configurações
│   │
│   ├── routes/             # Endpoints HTTP
│   │   └── classifier.py   # Rota de classificação
│   │
│   └── services/           # Lógica de negócio
│       ├── ai_service.py       # Integração Gemini
│       ├── file_parser.py      # Parse de PDF/TXT
│       ├── ocr_service.py      # OCR para PDFs escaneados
│       └── security_service.py # Rate limiting
│
├── tests/                   # Testes unitários
│   ├── test_ai_service.py
│   ├── test_file_parser.py
│   ├── test_ocr_service.py
│   └── ...
│
├── .env.example            # Exemplo de variáveis de ambiente
├── requirements.txt        # Dependências Python
├── Dockerfile             # Container Docker
├── docker-compose.yml     # Orquestração
├── EXAMPLES.md            # Exemplos de emails
└── README.md              # Este arquivo
```

**Nota:** Pastas `controllers/` e `utils/` foram removidas pois seguimos o padrão FastAPI onde `routes/` atua como controllers.

---

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado em `.env.example`:

```env
# OBRIGATÓRIO: Chave API do Google Gemini
GEMINI_API_KEY=sua_chave_aqui

# OPCIONAL: Modelo Gemini (padrão: gemini-2.5-flash)
GEMINI_MODEL=gemini-2.5-flash

# OPCIONAL: OCR para PDFs escaneados
OCR_SPACE_API_KEY=sua_chave_ocr_aqui

# Ambiente
ENVIRONMENT=production
DEBUG=false
```

### Obter Chaves de API

#### Google Gemini (Obrigatório)
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Clique em "Create API Key"
3. Copie a chave gerada

#### OCR.space (Opcional - para PDFs escaneados)
1. Acesse [OCR.space API](https://ocr.space/ocrapi)
2. Registre-se gratuitamente
3. Copie sua API key

---

## 🎨 Exemplos de Uso

Veia [EXAMPLES.md](EXAMPLES.md) para exemplos completos de emails produtivos e improdutivos.

**Teste Rápido:**
```
Assunto: Problema com login

Não consigo acessar o sistema. Aparece erro de autenticação.
Preciso urgentemente pois tenho relatório para entregar hoje.

Aguardo retorno.
```

**Resultado Esperado:**
- Categoria: **Produtivo** ✅
- Confiança: ~90%
- Resposta: Orientação técnica para resolver o problema

---

## 🚀 Deploy

### Render.com (Recomendado)

1. Crie conta no [Render](https://render.com)
2. Conecte seu repositório GitHub
3. Configure variáveis de ambiente:
   - `GEMINI_API_KEY`
   - `OCR_SPACE_API_KEY` (opcional)
4. Deploy automático!

### Railway.app

```bash
# Instale o Railway CLI
npm install -g @railway/cli

# Login e deploy
railway login
railway init
railway up
```

### Heroku

```bash
# Crie app Heroku
heroku create autou-email-classifier

# Configure variáveis
heroku config:set GEMINI_API_KEY=sua_chave

# Deploy
git push heroku main
```

---

## 📊 Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web assíncrono
- **Google Gemini AI** - Modelo de linguagem natural
- **PyPDF** - Parsing de PDFs
- **httpx** - Cliente HTTP assíncrono
- **Pydantic** - Validação de dados

### Frontend
- **HTML5/CSS3** - Estrutura e estilo
- **Tailwind CSS** - Framework CSS utilitário
- **Vanilla JavaScript** - Sem dependências pesadas

### DevOps
- **Docker** - Containerização
- **GitHub Actions** - CI/CD
- **pytest** - Framework de testes
- **ruff** - Linter e formatter

---

## 🧠 Como Funciona a IA

### Estratégia de Classificação

1. **Few-Shot Learning**
   - Fornecemos exemplos de emails produtivos e improdutivos
   - IA aprende padrões e contexto

2. **Prompt Estruturado**
   ```python
   # Exemplo simplificado
   prompt = """
   Classifique este email como Produtivo ou Improdutivo.
   
   PRODUTIVO: requer ação (suporte, dúvidas, atualizações)
   IMPRODUTIVO: não requer ação (felicitações, agradecimentos)
   
   Email: {conteúdo}
   
   Responda em JSON com categoria, confiança e resposta sugerida.
   """
   ```

3. **Validação de Resposta**
   - Parsing JSON estruturado
   - Validação com Pydantic
   - Tratamento de erros robusto

---

## 🔒 Segurança

- ✅ **Rate Limiting**: 10 requisições/minuto por IP
- ✅ **Validação de Input**: Tamanho e tipo de arquivo
- ✅ **Sanitização**: Limpeza de conteúdo malicioso
- ✅ **Variáveis de Ambiente**: Chaves sensíveis protegidas
- ✅ **CORS Configurado**: Apenas origens permitidas
- ✅ **Timeout**: Requisições limitadas a 60s

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`feature/nova-funcionalidade`)
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

### Checklist PR
- [ ] Código passa no `ruff check`
- [ ] Testes cobrem nova funcionalidade
- [ ] Cobertura >= 90%
- [ ] Documentação atualizada

---

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👨‍💻 Autor

**Hildelio**

- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [Seu Nome](https://linkedin.com/in/seu-perfil)

---

## 🙏 Agradecimentos

- **AutoU** - Pelo desafio técnico inspirador
- **Google** - Pela API Gemini gratuita
- **FastAPI Community** - Pela documentação excepcional
- **Você!** - Por testar este projeto

---

## 📞 Suporte

Encontrou um bug? Tem uma sugestão?

- 🐛 [Abra uma issue](https://github.com/seu-usuario/autou-email-classifier/issues)
- 💬 [Inicie uma discussão](https://github.com/seu-usuario/autou-email-classifier/discussions)
- 📧 Email: seu-email@exemplo.com

---

<div align="center">

**⭐ Se este projeto te ajudou, considere dar uma estrela!**

Made with ❤️ and ☕ for the AutoU Technical Challenge

</div>
