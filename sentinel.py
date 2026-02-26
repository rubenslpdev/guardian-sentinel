import json
import sqlite3
import os
import subprocess
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
DB_PATH = "database/sentinel.db"
JSON_PATH = "/tmp/sentinel_status.json"
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensagem):
    """Envia notificações formatadas para o Bot do Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": f"🛡️ *Guardian Sentinel*\n\n{mensagem}", 
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")

def inicializar_db():
    """Cria o banco e as tabelas se não existirem."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela Performance (1 registro por dia - Chave Primária é a DATA)
    cursor.execute('''CREATE TABLE IF NOT EXISTS status_diario (
        data TEXT PRIMARY KEY, cpu REAL, ram_free REAL, disco REAL, resp_time REAL)''')
    
    # Tabela Logs de Erros (Sempre que algo falhar)
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs_erros (
        id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, componente TEXT, mensagem TEXT)''')
    
    conn.commit()
    return conn

def modulo_seguranca():
    """Verifica e aplica atualizações de sistema."""
    try:
        # Verifica se há pacotes
        subprocess.run(["sudo", "apt-get", "update"], check=True, capture_output=True)
        resultado = subprocess.check_output(["apt", "list", "--upgradable"], stderr=subprocess.STDOUT).decode()
        
        # Filtra linhas que indicam pacotes reais
        pacotes = [l for l in resultado.split('\n') if '/' in l]
        
        if pacotes:
            qtd = len(pacotes)
            enviar_telegram(f"📦 *Segurança:* {qtd} atualizações encontradas. Instalando...")
            subprocess.run(["sudo", "apt-get", "upgrade", "-y"], check=True, capture_output=True)
            enviar_telegram(f"✅ *Segurança:* Sistema atualizado com sucesso.")
    except Exception as e:
        print(f"Erro no módulo de segurança: {e}")

def auto_reparo(servico, comando_systemd):
    """Tenta reiniciar um serviço e avisa o resultado."""
    try:
        subprocess.run(["sudo", "systemctl", "restart", comando_systemd], check=True)
        enviar_telegram(f"🛠️ *Auto-reparo:* O serviço `{servico}` estava caído. Reiniciado com sucesso!")
        return True
    except:
        enviar_telegram(f"🚨 *CRÍTICO:* Falha ao tentar reiniciar `{servico}`.")
        return False

def analisar_sistema():
    conn = inicializar_db()
    cursor = conn.cursor()
    
    if not os.path.exists(JSON_PATH):
        print("Arquivo JSON não encontrado.")
        return

    with open(JSON_PATH, 'r') as f:
        d = json.load(f)

    agora = datetime.now()
    alertas = []

    # --- ANÁLISE DE MÉTRICAS ---
    if d['cpu_percent'] > 80:
        alertas.append(f"CPU alta: {d['cpu_percent']}%")
    
    if d['ram_free_percent'] < 10:
        alertas.append(f"RAM crítica: {d['ram_free_percent']}% livre")
    
    if d['disk_percent'] > 85:
        alertas.append(f"Disco quase cheio: {d['disk_percent']}%")
    
    if d['swap_percent'] > 80:
        alertas.append(f"Swap elevado: {d['swap_percent']}%")

    # --- SERVIÇOS E AUTO-REPARO ---
    if d['apache'] != "running":
        auto_reparo("Apache", "apache2")
    
    if d['mysql'] != "running":
        auto_reparo("MariaDB", "mariadb")

    # --- APLICAÇÃO ---
    if d['http_status'] != 200:
        alertas.append(f"App Down: HTTP {d['http_status']}")
    
    if d['response_time'] > 3:
        alertas.append(f"Lentidão: {d['response_time']}s de resposta")

    # --- PERSISTÊNCIA ---
    # 1. Salva Erros (se houver)
    for msg in alertas:
        cursor.execute("INSERT INTO logs_erros (timestamp, componente, mensagem) VALUES (?, 'Monitor', ?)", 
               (agora.isoformat(), msg)) # .isoformat() transforma em string
        enviar_telegram(msg)

    # 2. Salva Status Diário (O 'INSERT OR IGNORE' garante que só salve 1x por dia)
    data_hoje = agora.strftime("%Y-%m-%d")
    cursor.execute('''INSERT OR IGNORE INTO status_diario VALUES (?, ?, ?, ?, ?)''', 
                   (data_hoje, d['cpu_percent'], d['ram_free_percent'], d['disk_percent'], d['response_time']))

    # 3. Limpeza Quinzenal (Remove erros com mais de 15 dias)
    limite_data = (agora - timedelta(days=15)).isoformat()
    cursor.execute("DELETE FROM logs_erros WHERE timestamp < ?", (limite_data,))
   
    conn.commit()
    conn.close()

if __name__ == "__main__":
    analisar_sistema()
