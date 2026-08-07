# DNS RPZ Manager

Sistema completo de gerenciamento de DNS Response Policy Zone (RPZ) com interface web, API RESTful e integração com ferramentas de automação.

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DNS RPZ Manager                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   Frontend   │───▶│   Backend    │───▶│   Postgres   │                  │
│  │   Next.js    │    │   FastAPI    │    │   Database   │                  │
│  │   Port 3000  │    │   Port 8000  │    │   Port 5432  │                  │
│  └──────────────┘    └──────┬───────┘    └──────────────┘                  │
│                             │                                               │
│                             ▼                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │     n8n      │    │    BIND9     │    │    Redis     │                  │
│  │  Workflow    │    │  DNS Server  │    │   Cache      │                  │
│  │  Port 5678   │    │  Port 53     │    │   Port 6379  │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Funcionalidades

- **Gerenciamento de Domínios**: Adicionar, editar e remover domínios do RPZ
- **Ações RPZ**: Suporte a NXDOMAIN, NODATA, PASSTHRU, DROP e outras políticas
- **API RESTful**: API completa para integração com outras ferramentas
- **Autenticação JWT**: Sistema de usuários com roles e permissões
- **Auditoria**: Log completo de todas as ações realizadas
- **Notificações**: Integração com Telegram e Microsoft Teams
- **n8n Integration**: Workflows automatizados para monitoramento de e-mail
- **Interface Web**: Dashboard moderno e responsivo

## Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Git
- 4GB de RAM mínimo (recomendado: 8GB)
- 20GB de espaço em disco

## Instalação

### 1. Clone o Repositório

```bash
git clone <repository-url>
cd dns-rpz-manager
```

### 2. Configure as Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```bash
# Gere uma chave secreta segura
openssl rand -hex 32

# Atualize SECRET_KEY no arquivo .env
```

### 3. Inicie os Serviços

```bash
# Inicie todos os serviços
docker-compose up -d

# Verifique o status
docker-compose ps
```

### 4. Inicialize o Banco de Dados

```bash
# Execute o script de inicialização
docker-compose exec backend python /app/scripts/init_db.py
```

### 5. Acesse a Aplicação

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **n8n**: http://localhost:5678

## Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `POSTGRES_USER` | Usuário do PostgreSQL | `dnsadmin` |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL | `changeme` |
| `POSTGRES_DB` | Nome do banco de dados | `dns_rpz_manager` |
| `SECRET_KEY` | Chave secreta JWT | `changeme-generate-random` |
| `TELEGRAM_BOT_TOKEN` | Token do bot Telegram | (vazio) |
| `TELEGRAM_CHAT_ID` | ID do chat Telegram | (vazio) |
| `TEAMS_WEBHOOK_URL` | URL webhook Teams | (vazio) |

### BIND9 RPZ

O arquivo de configuração do BIND9 está em `bind/config/named.conf.rpz`.

Para adicionar regras manualmente ao RPZ, edite `bind/rpz/rpz.zone.db`:

```
; Bloquear domínio malicioso
malware-example.com CNAME .

; Permitir domínio (whitelist)
good-example.com CNAME rpz-passthru.

; Retornar vazio
empty-example.com CNAME *.
```

Após alterações, recarregue o BIND9:

```bash
docker-compose exec bind9 rndc reload rpz
```

## Uso

### Usando a Interface Web

1. Acesse http://localhost:3000
2. Faça login com as credenciais padrão:
   - Usuário: `admin`
   - Senha: `admin123`
3. Navegue pelo dashboard para gerenciar domínios
4. Use a seção "Domínios" para adicionar/remover regras

### Usando a API

#### Autenticação

```bash
# Obter token de acesso
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

#### Gerenciar Domínios

```bash
# Listar domínios
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/domains

# Adicionar domínio
curl -X POST http://localhost:8000/api/v1/domains \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"domain": "malware-example.com", "action": "nxdomain", "reason": "Malware detected"}'

# Remover domínio
curl -X DELETE http://localhost:8000/api/v1/domains/<id> \
  -H "Authorization: Bearer <token>"
```

#### Gerar RPZ Manualmente

```bash
# Gerar arquivo RPZ a partir do banco de dados
docker-compose exec backend python /app/scripts/generate_rpz.py
```

## Documentação da API

A documentação completa da API está disponível em:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Principais Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/auth/login` | Autenticar usuário |
| GET | `/api/v1/domains` | Listar domínios |
| POST | `/api/v1/domains` | Adicionar domínio |
| PUT | `/api/v1/domains/{id}` | Atualizar domínio |
| DELETE | `/api/v1/domains/{id}` | Remover domínio |
| POST | `/api/v1/reports` | Enviar relatório |
| GET | `/api/v1/audit` | Logs de auditoria |

## Integração com n8n

### Configuração Inicial

1. Acesse http://localhost:5678
2. Faça login com as credenciais:
   - Usuário: `admin`
   - Senha: `n8n_admin_2026`
3. Crie um novo workflow

### Workflow de Monitoramento de E-mail

#### Passo 1: Criar Trigger de E-mail

1. Adicione um nó "Email Trigger (IMAP)"
2. Configure:
   - Host: `imap.seu-servidor.com`
   - Porta: `993`
   - Usuário: `seu-email@dominio.com`
   - Senha: `sua-senha-app`
   - Caixa de entrada: `INBOX`
   - Critérios de busca: `UNSEEN SUBJECT "DNS Report"`

#### Passo 2: Processar Conteúdo do E-mail

1. Adicione um nó "Function"
2. Use o seguinte código:

```javascript
// Extrair domínios do conteúdo do e-mail
const domains = [];
const emailBody = $input.first().json.text;

// Regex para extrair domínios
const domainRegex = /\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b/gi;
const matches = emailBody.match(domainRegex);

if (matches) {
  for (const domain of matches) {
    domains.push({
      domain: domain.toLowerCase(),
      reason: 'Detectado via monitoramento de e-mail',
      source: 'email-monitoring'
    });
  }
}

return domains.map(d => ({json: d}));
```

#### Passo 3: Adicionar ao RPZ via API

1. Adicione um nó "HTTP Request"
2. Configure:
   - Método: `POST`
   - URL: `http://backend:8000/api/v1/domains`
   - Headers: `Authorization: Bearer {{token}}`
   - Body: JSON com os dados do domínio

### Outros Workflows Úteis

- **Processamento de Relatórios CERT**: Receber relatórios de segurança via e-mail
- **Notificação de Bloqueio**: Enviar notificação quando um domínio for bloqueado
- **Relatório Diário**: Gerar relatório diário de domínios bloqueados
- **Verificação de Domínio**: Verificar se domínios específicos estão no RPZ

## Solução de Problemas

### Serviços Não Iniciam

```bash
# Verificar logs
docker-compose logs backend
docker-compose logs postgres

# Reiniciar serviços
docker-compose down
docker-compose up -d
```

### Erro de Conexão com Banco de Dados

```bash
# Verificar se o PostgreSQL está rodando
docker-compose ps postgres

# Verificar logs do PostgreSQL
docker-compose logs postgres

# Testar conexão
docker-compose exec postgres psql -U dnsadmin -d dns_rpz_manager
```

### BIND9 Não Resolve Consultas

```bash
# Verificar status do BIND9
docker-compose exec bind9 rndc status

# Verificar logs
docker-compose logs bind9

# Testar zona RPZ
docker-compose exec bind9 named-checkzone rpz /var/cache/bind/rpz/rpz.zone.db

# Recarregar zona
docker-compose exec bind9 rndc reload rpz
```

### Frontend Não Carrega

```bash
# Verificar logs do frontend
docker-compose logs frontend

# Verificar se o backend está acessível
curl http://localhost:8000/health
```

### n8n Não Conecta ao Banco de Dados

```bash
# Verificar logs do n8n
docker-compose logs n8n

# Verificar variáveis de ambiente
docker-compose exec n8n env | grep DB
```

### Permissões de Arquivos

```bash
# Corrigir permissões do RPZ
docker-compose exec bind9 chown -R bind:bind /var/cache/bind/rpz
docker-compose exec bind9 chmod -R 755 /var/cache/bind/rpz

# Corrigir permissões de log
docker-compose exec bind9 chown -R bind:bind /var/log/bind
```

### Limpar Dados e Recomeçar

```bash
# Parar e remover todos os containers e volumes
docker-compose down -v

# Remover imagens (opcional)
docker-compose down --rmi all

# Recomeçar do zero
docker-compose up -d
docker-compose exec backend python /app/scripts/init_db.py
```

## Desenvolvimento

### Estrutura do Projeto

```
dns-rpz-manager/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints da API
│   │   ├── core/           # Configurações e segurança
│   │   ├── models/         # Modelos do banco de dados
│   │   ├── schemas/        # Schemas Pydantic
│   │   └── services/       # Lógica de negócio
│   ├── scripts/            # Scripts auxiliares
│   ├── requirements.txt    # Dependências Python
│   └── Dockerfile          # Dockerfile do backend
├── frontend/               # Interface Next.js
│   ├── src/
│   │   ├── app/           # Páginas Next.js
│   │   ├── components/    # Componentes React
│   │   └── lib/           # Utilitários
│   ├── package.json       # Dependências Node.js
│   └── Dockerfile         # Dockerfile do frontend
├── bind/                  # Configuração do BIND9
│   ├── config/           # Arquivos de configuração
│   └── rpz/              # Zonas RPZ
├── n8n/                   # Configuração do n8n
├── docker-compose.yml     # Orquestração Docker
├── .env.example          # Variáveis de ambiente exemplo
└── README.md             # Esta documentação
```

### Comandos de Desenvolvimento

```bash
# Modo desenvolvimento (com hot-reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Executar testes
docker-compose exec backend pytest

# Formatar código
docker-compose exec backend black .
docker-compose exec frontend npm run format

# Verificar tipos
docker-compose exec frontend npm run type-check
```

## Licença

MIT License - Veja o arquivo LICENSE para mais detalhes.

## Suporte

Para problemas e sugestões, abra uma issue no repositório ou entre em contato com a equipe de desenvolvimento.
