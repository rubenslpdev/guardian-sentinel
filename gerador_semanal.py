import sqlite3
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configurações
load_dotenv()
DB_PATH = "database/sentinel.db"
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": mensagem, 
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar relatório: {e}")

def gerar_relatorio():
    if not os.path.exists(DB_PATH):
        print("Banco de dados não encontrado.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Define o período (últimos 7 dias)
    hoje = datetime.now()
    uma_semana_atras = (hoje - timedelta(days=7)).strftime("%Y-%m-%d")
    uma_semana_atras_iso = (hoje - timedelta(days=7)).isoformat()

    # 1. MÉTRICAS DE PERFORMANCE (Média da última semana)
    cursor.execute('''
        SELECT 
            AVG(cpu), AVG(ram_free), AVG(disco), AVG(resp_time)
        FROM status_diario 
        WHERE data >= ?
    ''', (uma_semana_atras,))
    
    perf = cursor.fetchone()
    # Se não houver dados ainda, perf virá com Nones
    avg_cpu = perf[0] if perf[0] else 0
    avg_ram = perf[1] if perf[1] else 0
    avg_disk = perf[2] if perf[2] else 0
    avg_resp = perf[3] if perf[3] else 0

    # 2. CONTAGEM DE ERROS
    cursor.execute('''
        SELECT COUNT(*) FROM logs_erros 
        WHERE timestamp >= ?
    ''', (uma_semana_atras_iso,))
    total_erros = cursor.fetchone()[0]

    # 3. IDENTIFICAÇÃO DE INSTABILIDADES (Componentes mais problemáticos)
    cursor.execute('''
        SELECT componente, COUNT(*) as total 
        FROM logs_erros 
        WHERE timestamp >= ?
        GROUP BY componente
        ORDER BY total DESC LIMIT 3
    ''', (uma_semana_atras_iso,))
    problemas = cursor.fetchall()
    
    lista_problemas = ""
    if problemas:
        for p in problemas:
            lista_problemas += f"• {p[0]}: {p[1]} ocorrências\n"
    else:
        lista_problemas = "• Nenhum incidente registrado ✅"

    conn.close()

    # MONTAGEM DA MENSAGEM
    relatorio = (
        f"📊 *RELATÓRIO SEMANAL SENTINEL*\n"
        f"_{uma_semana_atras} até {hoje.strftime('%Y-%m-%d')}_\n\n"
        f"*Métricas Médias:*\n"
        f"💻 CPU: {avg_cpu:.1f}%\n"
        f"🧠 RAM Livre: {avg_ram:.1f}%\n"
        f"💽 Disco: {avg_disk:.1f}%\n"
        f"⏱️ Resp. Time: {avg_resp:.2f}s\n\n"
        f"*Saúde do Sistema:*\n"
        f"🚨 Total de Alertas: {total_erros}\n"
        f"{lista_problemas}\n\n"
        f"Status Final: {'⚠️ Requer Atenção' if total_erros > 5 else '🟢 Estável'}"
    )

    enviar_telegram(relatorio)

if __name__ == "__main__":
    gerar_relatorio()
