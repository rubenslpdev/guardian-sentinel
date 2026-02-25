# 🛡️ Guardian Sentinel LAMP

O **Guardian Sentinel** é um ecossistema de monitoramento inteligente e auto-recuperável projetado para servidores LAMP (Linux, Apache, MySQL/MariaDB, PHP). Diferente de ferramentas de monitoramento passivas, o Sentinel atua como um "vigilante" que não apenas coleta dados, mas toma decisões autônomas para garantir a disponibilidade do serviço.

## Funcionalidades Principais

* **Coleta de Métricas em Tempo Real:** Monitoramento de CPU, RAM, Disco e SWAP via Shell Script de baixa latência.
* **Health Check de Serviços:** Verificação constante do status do Apache e MariaDB.
* **Inteligência de Auto-reparo:** Reinicialização automática de serviços caídos (Watchdog).
* **Alertas Inteligentes:** Notificações via Telegram Bot API sobre falhas, reparos e atualizações pendentes.
* **Análise de Segurança:** Verificação de pacotes `apt` que necessitam de atualização.
* **Persistência e BI:** Histórico de performance armazenado em SQLite para análise de dados a longo prazo com Pandas.

---

## Arquitetura do Sistema

O projeto é dividido em camadas funcionais para garantir modularidade e leveza:

### 1. O Coletor (Shell Script)

O "olheiro" do sistema. Roda via `crontab` e exporta o estado atual do servidor em um arquivo JSON estruturado em `/tmp/sentinel_status.json`.

### 2. O Cérebro (Python 1)

Lê o JSON gerado, processa a lógica de negócio e:

* Verifica atualizações de segurança pendentes.
* Executa o **Auto-reparo** (`systemctl restart`).
* Salva os dados no banco **SQLite**.
* Dispara alertas via Telegram.

### 3. Analista de Dados (Python 2)

Focado em ciência de dados e relatórios. Utiliza a biblioteca **Pandas** para ler o SQLite e gerar:

* Relatórios semanais/mensais de uptime.
* Análise de tendências de consumo de recursos.
* Comparativos de performance mês a mês.

---

## Estrutura de Dados (JSON)

O coletor gera uma saída padronizada para facilitar a ingestão:

```json
{  
  "version": 1,
  "timestamp": 1760000000,  
  "cpu_percent": 12.4,  
  "ram_free_percent": 43.1,  
  "disk_percent": 61,  
  "apache": "running",  
  "mysql": "running",  
  "http_status": 200,  
  "response_time": 0.24  
}

```

---

## Roadmap de Desenvolvimento

* [ ] **Fase 1: Coração Linux** - Implementar script Shell e exportação JSON.
* [ ] **Fase 2: Inteligência** - Parser Python, integração SQLite e lógica de auto-reparo.
* [ ] **Fase 3: Comunicação** - Configuração da API do Telegram e disparos de alerta.
* [ ] **Fase 4: Automação** - Configuração de Crontab e Log Rotation para sustentabilidade do sistema.
* [ ] **Fase 5: Data Science** - Scripts de análise Ad Hoc com Pandas e visualização de dados.

---

## Exemplo de Análise de Dados

Utilizamos o **Pandas** para transformar dados brutos em insights de infraestrutura:

```python
import pandas as pd
import sqlite3

# Carregando dados para análise
conn = sqlite3.connect('sentinel_data.db')
df = pd.read_sql_query("SELECT * FROM saude_servidor", conn)

# Média mensal de uso de CPU
df['data'] = pd.to_datetime(df['data'])
media_mensal = df.groupby(df['data'].dt.to_period('M'))['cpu_uso'].mean()

```

---

**Contribuições:** Sinta-se à vontade para abrir Issues ou enviar Pull Requests para melhorar a inteligência de monitoramento!

