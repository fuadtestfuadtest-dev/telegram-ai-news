#!/usr/bin/env python3
"""
Avtomatik planlayıcı — hər 30 dəqiqədən bir news_bot.py işlədir.
Müstəqil proses kimi işləyir (background).
"""
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

BAKU_TZ = timezone(timedelta(hours=4))
INTERVAL_SECONDS = 30 * 60  # 30 dəqiqə
SCRIPT_DIR = '/workspace/telegram-ai-news'

def log(msg):
    ts = datetime.now(BAKU_TZ).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts} Bakı] {msg}", flush=True)

def run_bot():
    log("🚀 news_bot.py başladılır...")
    try:
        result = subprocess.run(
            [f'{SCRIPT_DIR}/venv/bin/python', f'{SCRIPT_DIR}/news_bot.py'],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=SCRIPT_DIR
        )
        if result.returncode == 0:
            log("✅ news_bot.py uğurla bitdi")
            # Son 3 sətri göstər
            for line in result.stdout.strip().split('\n')[-3:]:
                log(f"   {line}")
        else:
            log(f"❌ news_bot.py xəta ilə bitdi (kod {result.returncode})")
            log(f"   stderr: {result.stderr[:500]}")
    except subprocess.TimeoutExpired:
        log("⏰ news_bot.py vaxtı keçdi (3 dəq)")
    except Exception as e:
        log(f"❌ Gözlənilməz xəta: {e}")

def main():
    log("=" * 50)
    log("🤖 AI News Scheduler işə düşdü")
    log(f"⏰ Hər {INTERVAL_SECONDS // 60} dəqiqədən bir işləyəcək")
    log("=" * 50)

    # İlk işləməni DƏRHAL et
    run_bot()

    # Sonra hər 30 dəqiqədən bir
    while True:
        now = datetime.now(BAKU_TZ)
        # Növbəti işləmə vaxtını hesabla (gələn yarım saatın başlanğıcı)
        next_minute = (now.minute // 30 + 1) * 30
        if next_minute >= 60:
            next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        else:
            next_run = now.replace(minute=next_minute, second=0, microsecond=0)

        wait_seconds = (next_run - now).total_seconds()
        log(f"😴 Növbəti post: {next_run.strftime('%H:%M:%S')} Bakı ({int(wait_seconds)} saniyə gözləyirəm)")

        time.sleep(wait_seconds)
        run_bot()

if __name__ == '__main__':
    main()