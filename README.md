# b2bflow WhatsApp Sender

Projeto do desafio técnico da b2bflow: lê contatos do Supabase e envia mensagens personalizadas via Z-API (WhatsApp).

## Pré-requisitos

- Python 3.10+
- Conta gratuita no [Supabase](https://supabase.com)
- Conta gratuita na [Z-API](https://z-api.io)

---

## Setup do Supabase

1. Crie um projeto no Supabase.
2. No **SQL Editor**, execute:

```sql
CREATE TABLE contacts (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT NOT NULL
);

INSERT INTO contacts (name, phone) VALUES
  ('João Silva', '5511999990001'),
  ('Maria Souza', '5511999990002'),
  ('Carlos Lima', '5511999990003');
```

> O campo `phone` deve estar no formato internacional sem `+` (ex: `5511999990001`). O script valida que o telefone tenha apenas dígitos (10 a 15 caracteres) antes de enviar; contatos com formato inválido são pulados e registrados como falha no log.

3. Acesse **Project Settings → API** e copie a **Project URL** e a chave de API (pode ser a **anon public key** ou a **secret key**, no novo padrão do Supabase).

---

## Setup da Z-API

1. Crie uma instância gratuita em [z-api.io](https://z-api.io).
2. Conecte seu WhatsApp via QR Code.
3. No painel da instância, copie:
   - **Instance ID**
   - **Instance Token**

> O **Client Token** (em *Security*) não está disponível no plano Trial e não é exigido por este script.

---

## Variáveis de Ambiente

Copie o `.env.example` e preencha com suas credenciais:

```bash
cp .env.example .env
```

```env
# Supabase
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=your_supabase_key

# Z-API
ZAPI_INSTANCE_ID=your_instance_id
ZAPI_TOKEN=your_instance_token
```

---

## Como Rodar

```bash
# Crie e ative um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute
python main.py
```

## Testes

O projeto tem testes unitários para a validação de telefone e os cenários de envio via Z-API (sucesso, erro HTTP, erro de conexão, credenciais ausentes), usando mocks para não depender de rede real.

```bash
pytest tests/ -v
```

### Saída real (evidência de execução)

```
2026-06-19 18:26:14,208 [INFO] === Iniciando envio de mensagens ===
2026-06-19 18:26:14,292 [INFO] Buscando contatos no Supabase...
2026-06-19 18:26:14,995 [INFO] HTTP Request: GET https://oarqwzrsbpbaxyuhtxtl.supabase.co/rest/v1/contacts?select=name%2Cphone&limit=3 "HTTP/2 200 OK"
2026-06-19 18:26:14,995 [INFO] 3 contato(s) encontrado(s).
2026-06-19 18:26:15,069 [INFO] ✅ Mensagem enviada para 553198472**** (messageId=3EB0A1A4625FBCD1325E7F)
2026-06-19 18:26:15,131 [INFO] ✅ Mensagem enviada para 553182988*** (messageId=3EB062D1B8974182EE6213)
2026-06-19 18:26:15,192 [INFO] ✅ Mensagem enviada para 553198531*** (messageId=3EB0E28D750AD72D32A716)
2026-06-19 18:26:15,193 [INFO] === Concluído: 3 enviado(s), 0 falha(s) ===
```

> Números mascarados parcialmente para preservar a privacidade dos contatos reais usados no teste. A instância Trial da Z-API usada neste teste expira poucos dias após a criação, por isso este log foi capturado como evidência fixa em vez de algo reproduzível a qualquer momento.

A mensagem enviada para cada contato será:

```
Olá, João Silva tudo bem com você?
```

---

## Estrutura do Projeto

```
├── main.py          # Script principal
├── requirements.txt # Dependências
├── .env.example     # Template de variáveis de ambiente
└── README.md
```