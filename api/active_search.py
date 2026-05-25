import os
import json
import sys
from pathlib import Path

# Añadir el directorio raíz al path para permitir importaciones de 'api'
root_dir = Path(__file__).parent.parent.absolute()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from api.job_radar import JobRadar
from api.config import settings

def update_radar():
    print("Iniciando escaneo activo de vacantes (CareerBoosterAI Swarm)...")
    
    # Inicializar Radar
    radar = JobRadar(settings)
    
    # Realizar búsqueda (usamos Fintech y Mexico como defaults estratégicos)
    print("Buscando nuevas oportunidades en Remotive, JobLeads y Google...")
    new_hits = radar.search_jobs(query="Fintech", location="Mexico")
    
    # Guardar resultados y enviar alerta
    try:
        radar.save_results(new_hits)
        print(f"[OK] Escaneo completado. Se encontraron {len(new_hits)} oportunidades.")
        
        # Enviar alerta de Telegram
        import requests
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN") or settings.telegram_bot_token
        chat_id = os.environ.get("TELEGRAM_CHAT_ID") or settings.telegram_chat_id
        
        if bot_token and chat_id and new_hits:
            # Filtrar solo vacantes recomendadas (score alto)
            top_jobs = sorted(new_hits, key=lambda x: x.get('score', 0), reverse=True)[:5]
            
            message = "🎯 *Radar Fintech - Nuevas Vacantes*\n\n"
            for job in top_jobs:
                score = job.get('score', 'N/A')
                company = job.get('company', 'Unknown')
                title = job.get('title', 'Unknown')
                url = job.get('url', '#')
                message += f"⭐ {score} - *{company}*: {title}\n[Ver Oferta]({url})\n\n"
            
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            res = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=payload)
            if res.status_code == 200:
                print("[OK] Alerta enviada por Telegram exitosamente.")
            else:
                print(f"[WARN] Error al enviar Telegram: {res.text}")
                
    except Exception as e:
        print(f"[ERROR] Error al procesar los resultados: {e}")

if __name__ == "__main__":
    update_radar()
