# Exemplos de Emails para Teste

Este arquivo contém exemplos de emails para testar o classificador.

## 📧 Emails Produtivos

### Exemplo 1: Solicitação de Suporte Técnico
```
Assunto: Problema urgente com acesso ao sistema

Olá,

Estou tendo problemas para acessar o sistema desde ontem. Quando tento fazer login, aparece a mensagem "Erro de autenticação".

Já tentei redefinir minha senha mas o problema persiste. Preciso acessar urgentemente pois tenho um relatório para entregar hoje às 17h.

Meu usuário é: joao.silva@empresa.com

Aguardo retorno.

Atenciosamente,
João Silva
```

### Exemplo 2: Atualização de Status
```
Assunto: Status do processo #12345

Prezados,

Gostaria de saber o andamento do meu processo de solicitação #12345 aberto em 10/01/2026.

Já se passaram 5 dias úteis e ainda não recebi nenhuma atualização.

Poderiam me informar a previsão de conclusão?

Grato,
Maria Oliveira
```

### Exemplo 3: Dúvida sobre Funcionalidade
```
Assunto: Como exportar relatórios em PDF?

Bom dia,

Estou com dificuldade para exportar os relatórios mensais em formato PDF.

O botão de exportação está desabilitado na minha tela. Há alguma permissão específica necessária?

Preciso enviar esse relatório para a diretoria amanhã.

Obrigado,
Pedro Santos
```

### Exemplo 4: Solicitação de Informação
```
Assunto: Documentação sobre integração via API

Olá equipe técnica,

Estou desenvolvendo uma integração com o sistema de vocês e preciso da documentação completa da API REST.

Especificamente, preciso entender:
- Endpoints disponíveis
- Formato de autenticação
- Limites de rate limiting
- Exemplos de requisições

Onde posso encontrar essa documentação?

Abraços,
Ana Costa
```

---

## 🎉 Emails Improdutivos

### Exemplo 1: Mensagem de Felicitações
```
Assunto: Feliz Natal!

Olá pessoal,

Desejo a todos um Feliz Natal e um Ano Novo cheio de realizações!

Que 2026 seja um ano próspero para todos nós.

Abraços,
Carlos
```

### Exemplo 2: Agradecimento Genérico
```
Assunto: Obrigado!

Oi,

Só queria agradecer pelo excelente trabalho de vocês.

O sistema está funcionando perfeitamente!

Valeu!
Roberto
```

### Exemplo 3: Mensagem Informal
```
Assunto: Café depois do trabalho?

E aí galera,

Alguém topa tomar um café hoje depois do expediente?

Abs,
Juliana
```

### Exemplo 4: Saudação
```
Assunto: Bom dia!

Bom dia a todos!

Espero que tenham uma ótima semana.

:)
```

---

## 📝 Como Usar

1. **Via Interface Web:**
   - Copie qualquer exemplo acima
   - Cole na aba "Colar Texto"
   - Clique em "Analisar Email"

2. **Via Arquivo TXT:**
   - Salve um exemplo em arquivo `.txt`
   - Faça upload na aba "Upload de Arquivo"

3. **Via API (cURL):**
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@email_exemplo.txt" \
  -H "Content-Type: multipart/form-data"
```

---

## 🎯 Resultados Esperados

### Para Emails Produtivos:
- **Categoria:** Produtivo
- **Confiança:** Alta (70-95%)
- **Resposta:** Ação específica ou orientação técnica

### Para Emails Improdutivos:
- **Categoria:** Improdutivo
- **Confiança:** Alta (80-95%)
- **Resposta:** Agradecimento cordial ou resposta genérica

---

## 💡 Dicas para Testes

- **Teste edge cases:** Emails muito curtos, muito longos, ou com conteúdo misto
- **Teste diferentes idiomas:** O sistema foi otimizado para português
- **Teste PDFs:** Crie PDFs a partir dos exemplos acima
- **Teste OCR:** PDFs escaneados (requer OCR_SPACE_API_KEY configurada)
