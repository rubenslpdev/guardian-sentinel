# 🛡️ Guardian Sentinel

**Guardian Sentinel** é um sistema leve de monitoramento e auto-reparo de servidores Linux. O projeto foi desenvolvido como um estudo prático de integração entre Shell Script, Python e SQLite, focado em garantir a disponibilidade de serviços essenciais e análise de performance a longo prazo.

## 🚀 Funcionalidades

### 1. Monitoramento em Tempo Real

O sistema analisa métricas críticas do servidor em intervalos programados:

* **Recursos de Sistema:** Uso de CPU, Memória RAM, Espaço em Disco e SWAP.
* **Serviços Críticos:** Status do Apache (`httpd`) e MariaDB/MySQL.
* **Aplicação:** Tempo de resposta HTTP e códigos de status (ex: 200 OK).

### 2. Auto-Reparo Inteligente

Se o Sentinel detectar que um serviço essencial (Apache ou MariaDB) caiu, ele tenta automaticamente o reinício via `systemctl` e notifica o administrador sobre o sucesso ou falha da intervenção.

### 3. Alertas via Telegram

Integração com a API de Bot do Telegram para envio de alertas imediatos quando:

* Métricas excedem limites de segurança (ex: CPU > 80%).
* Serviços caem ou falham ao reiniciar.
* Novas atualizações de segurança do sistema estão disponíveis.

### 4. Persistência e Histórico

Utiliza **SQLite** para armazenar dados de forma eficiente:

* **Status Diário:** Um snapshot diário da saúde do servidor para análise de tendência (retenção de 90 dias).
* **Logs de Erro:** Registro detalhado de todas as falhas detectadas (retenção de 15 dias).

### 5. Relatórios Semanais

Um script dedicado consolida os dados da semana e envia um resumo executivo com médias de performance e ranking dos componentes mais instáveis.

---

## Tecnologias Utilizadas

* **Shell Script (BASH):** Coleta de dados brutos do sistema.
* **Python 3.12+:** Lógica de análise, tratamento de dados e alertas.
* **SQLite:** Banco de dados relacional leve.
* **Requests & Dotenv:** Comunicação com API e gestão de variáveis de ambiente.

---

## Estrutura do Projeto

```text
guardian-sentinel/
├── .venv/               # Ambiente virtual Python
├── database/            # Armazenamento do sentinel.db
├── .env                 # Credenciais (Token e Chat ID do Telegram)
├── collector.sh         # Script Shell de coleta (Raw Data)
├── sentinel.py          # O "Worker" (Análise e Auto-reparo)
├── gerador_semanal.py   # O "Reporter" (Consolidação de dados)
└── README.md

```

---

## Configuração e Instalação

1. **Clonar o repositório:**
```bash
git clone https://github.com/rubenslpdev/guardian-sentinel.git

```


2. **Configurar o ambiente virtual:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests python-dotenv

```


3. **Configurar Variáveis de Ambiente:**
Crie um arquivo `.env` e adicione suas credenciais do Telegram:
```env
TELEGRAM_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui

```


4. **Agendar no Cron (`crontab -e`):**
```bash
# Coleta e Análise de hora em hora
00 * * * * /bin/bash /caminho/projeto/collector.sh
01 * * * * /caminho/projeto/.venv/bin/python3 /caminho/projeto/sentinel.py

# Relatório Semanal (Segunda-feira às 08:00)
00 08 * * 1 /caminho/projeto/.venv/bin/python3 /caminho/projeto/gerador_semanal.py

```



---

## 📝 Licença

Este projeto foi desenvolvido para fins didáticos. Sinta-se à vontade para usar, modificar e distribuir.

