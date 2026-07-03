#!/usr/bin/env python3
"""
Telegram AI News Bot — AI və Robotexnika xəbərləri
- Bloomberg RSS mənbələrini oxuyur
- AI/robotika xəbərlərini süzgəcdən keçirir
- Azərbaycan dilinə tərcümə edir
- @AIAZE01 kanalına hər 30 dəqiqədən bir paylaşır
- Təkrar paylaşmanın qarşısını alır
"""

import feedparser
import json
import os
import re
import hashlib
import time
import requests
from datetime import datetime, timezone, timedelta
from deep_translator import GoogleTranslator

# ─── KONFİQURASİYA ─────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get(
    'TELEGRAM_BOT_TOKEN',
    '8865540268:AAEtF6QeVir9RIgtxU30lUNYCfcHDuWWgc8'  # yalnız lokal test üçün
)
TELEGRAM_CHANNEL = os.environ.get('TELEGRAM_CHANNEL', '@AIAZE01')

RSS_FEEDS = [
    'https://feeds.bloomberg.com/technology/news.rss',
    'https://feeds.bloomberg.com/markets/news.rss',
    'https://feeds.bloomberg.com/economics/news.rss',
    'https://www.nytimes.com/svc/collections/v1/publish/https:/www.nytimes.com/section/technology/rss.xml',
]

STATE_FILE = 'posted_news.json'
MAX_TITLE_LEN = 200
MAX_SUMMARY_LEN = 500
BAKU_TZ = timezone(timedelta(hours=4))

# ─── AI AŞKAR ETMƏ AÇAR SÖZLƏRİ ──────────────────────────────────────
# Sərt açar sözlər (tam söz/ifadə kimi axtarır — yalançı müsbət azdır)
AI_KEYWORDS_STRICT = [
    # Əsas AI anlayışları
    'artificial intelligence', 'machine learning', 'deep learning',
    'generative ai', 'gen ai', 'genai',
    'large language model', 'foundation model',
    'neural network', 'computer vision',
    # Məşhur AI şirkətləri / məhsulları
    'openai', 'chatgpt', 'anthropic', 'claude ai', 'mistral ai',
    'nvidia ai', 'google ai', 'meta ai', 'microsoft ai',
    'deepmind', 'xai', 'inflection ai', 'cohere', 'hugging face',
    # Məhsullar
    'chatgpt', 'gpt-4', 'gpt-5', 'gpt4', 'gpt5', 'sora', 'dall-e',
    'gemini ai', 'copilot ai', 'github copilot', 'midjourney',
    # Robotika
    'humanoid robot', 'humanoid robotics', 'industrial robot',
    'boston dynamics', 'figure ai', '1x technologies', 'agility robotics',
    # Texniki
    'ai chip', 'ai accelerator', 'ai infrastructure', 'ai model',
    'ai training', 'gpu cluster', 'tpu chip',
    # Bazar
    'ai funding', 'ai investment', 'ai deal', 'ai startup',
    'ai boom', 'ai bubble', 'ai bubble', 'ai race',
    'ai capex', 'ai compute',
]

# Boş açar sözlər (yalnız başlıqda, söz sərhədi ilə)
AI_KEYWORDS_TITLE = [
    r'\bai\b', r'\bai\b', r'\bllm\b', r'\bllms\b',
    r'\brobot\b', r'\brobotics\b', r'\bhumanoid\b',
    r'\bopenai\b', r'\banthropic\b', r'\bnvidia\b',
    r'\bchatgpt\b', r'\bclaude\b', r'\bgemini\b',
    r'\bgpt-?\d', r'\bgpt-?5', r'\bgpt-?4',
    r'\bdeepmind\b', r'\bxai\b', r'\bmistral\b',
    r'\bdeep learning\b', r'\bmachine learning\b',
    r'\bcopilot\b', r'\bsora\b',
]


# ─── KÖMƏKÇİ FUNKSİYALAR ─────────────────────────────────────────────
def is_ai_news(title, description):
    """Başlıq və təsvirə əsasən AI/robotika xəbəri olub-olmadığını yoxla"""
    title_lower = (title or '').lower()
    desc_lower = (description or '').lower()
    full_text = f"{title_lower} {desc_lower}"

    # 1) Sərt açar sözlər — istənilən yerdə (təsvirdə daha çox tolerant)
    for kw in AI_KEYWORDS_STRICT:
        if kw in full_text:
            return True

    # 2) Başlıqda söz sərhədli açar sözlər (yalançı müsbət azdır)
    for pattern in AI_KEYWORDS_TITLE:
        if re.search(pattern, title_lower):
            return True

    return False


def get_url_hash(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def load_posted():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_posted(posted):
    """Dövlət faylını saxla, həddindən artıq böyüməsin"""
    MAX_KEEP = 500
    if len(posted) > MAX_KEEP:
        # Ən son 500-ü saxla
        sorted_items = sorted(
            posted.items(),
            key=lambda x: x[1].get('posted_at', ''),
            reverse=True
        )
        posted = dict(sorted_items[:MAX_KEEP])
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(posted, f, ensure_ascii=False, indent=2)


def translate_with_retry(text, max_retries=3):
    """Google Translate ilə tərcümə et, xəta olarsa təkrar cəhd et"""
    if not text or not text.strip():
        return text
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source='en', target='az')
            if len(text) <= 4500:
                return translator.translate(text)
            # Uzun mətnləri hissələrə böl
            chunks, result = [], []
            for i in range(0, len(text), 4500):
                chunks.append(text[i:i + 4500])
            for chunk in chunks:
                result.append(translator.translate(chunk))
                time.sleep(0.3)
            return ' '.join(result)
        except Exception as e:
            print(f"  Tərcümə cəhdi {attempt+1}/{max_retries} uğursuz: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s gözlə
    return text  # Son çarə olaraq originalı qaytar


def clean_html(text):
    if not text:
        return ''
    cleaned = re.sub(r'<[^>]+>', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def truncate_smart(text, max_len):
    """Cümlə sonunda kəs"""
    if not text or len(text) <= max_len:
        return text
    truncated = text[:max_len]
    # Son cümlə sonluğunu tap
    for sep in ['. ', '! ', '? ', '; ']:
        idx = truncated.rfind(sep)
        if idx > max_len * 0.5:
            return truncated[:idx + 1]
    return truncated.rstrip() + '...'


def pick_emoji(title, summary):
    """Xəbərin mövzusuna görə emoji seç"""
    text = f"{title} {summary}".lower()
    if any(kw in text for kw in ['nvidia', 'chip', 'semiconductor', 'gpu', 'tpu']):
        return '🔧'
    if any(kw in text for kw in ['openai', 'anthropic', 'chatgpt', 'claude', 'gpt', 'llm', 'language model']):
        return '🧠'
    if any(kw in text for kw in ['robot', 'humanoid', 'boston dynamics']):
        return '🦾'
    if any(kw in text for kw in ['fund', 'invest', 'billion', 'raise', 'valuation', 'stake']):
        return '💰'
    if any(kw in text for kw in ['google', 'meta', 'microsoft', 'apple']):
        return '🏢'
    if any(kw in text for kw in ['job', 'worker', 'layoff', 'hire', 'employment']):
        return '👥'
    return '🤖'


def format_post(title_az, summary_az, url, source='Bloomberg'):
    """Telegram üçün formatla"""
    emoji = pick_emoji(title_az, summary_az)
    safe_title = title_az.replace('<', '&lt;').replace('>', '&gt;')[:MAX_TITLE_LEN]
    safe_summary = summary_az.replace('<', '&lt;').replace('>', '&gt;')
    return (
        f"{emoji} <b>{safe_title}</b>\n\n"
        f"{safe_summary}\n\n"
        f"🔗 Mənbə: <a href=\"{url}\">{source}</a>"
    )


def detect_source(url):
    """URL-dən mənbə adını avtomatik təyin et"""
    url_lower = (url or '').lower()
    if 'bloomberg.com' in url_lower:
        return 'Bloomberg'
    if 'nytimes.com' in url_lower:
        return 'The New York Times'
    if 'reuters.com' in url_lower:
        return 'Reuters'
    if 'ft.com' in url_lower:
        return 'Financial Times'
    if 'techcrunch.com' in url_lower:
        return 'TechCrunch'
    if 'theverge.com' in url_lower:
        return 'The Verge'
    if 'wired.com' in url_lower:
        return 'Wired'
    if 'cnbc.com' in url_lower:
        return 'CNBC'
    return 'Xəbər mənbəyi'


def send_to_telegram(text):
    """Telegram kanalına göndər"""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHANNEL,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False,
    }
    try:
        resp = requests.post(url, json=data, timeout=20)
        result = resp.json()
        if result.get('ok'):
            msg = result.get('result', {})
            print(f"  ✅ Telegram: message_id={msg.get('message_id')}")
            return True
        else:
            print(f"  ❌ Telegram xətası: {result.get('description')}")
            return False
    except Exception as e:
        print(f"  ❌ Telegram bağlantı xətası: {e}")
        return False


# ─── ƏSAS FUNKSİYA ────────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    print(f"🕐 Başladı: {datetime.now(BAKU_TZ).strftime('%Y-%m-%d %H:%M:%S')} (Bakı)")
    print(f"{'='*60}")

    posted = load_posted()
    print(f"📚 Verilənlər bazasında {len(posted)} köhnə xəbər var")

    found_ai_news = []

    # Bütün mənbələri yoxla
    for feed_url in RSS_FEEDS:
        print(f"\n📡 Yüklənir: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)
            if not feed.entries:
                print(f"  ⚠️ Boş feed")
                continue
            print(f"  📰 {len(feed.entries)} xəbər tapıldı")
        except Exception as e:
            print(f"  ❌ Feed xətası: {e}")
            continue

        for entry in feed.entries[:10]:  # Hər feed-dən ən son 10 (sürət üçün)
            link = entry.get('link', '')
            if not link:
                continue

            url_hash = get_url_hash(link)
            if url_hash in posted:
                continue  # Artıq paylaşılıb

            title_en = clean_html(entry.get('title', ''))
            desc_en = clean_html(
                entry.get('description', '') or entry.get('summary', '')
            )

            if not is_ai_news(title_en, desc_en):
                continue

            print(f"\n  🎯 AI xəbər tapıldı:")
            print(f"     EN: {title_en[:90]}")

            # Tərcümə — paralel etmək olmaz (Google rate limit), amma tez
            print(f"     🌐 Tərcümə edilir...")
            try:
                title_az = translate_with_retry(title_en, max_retries=2)
                if title_az == title_en:
                    print(f"     ⚠️ Tərcümə uğursuz, keçilir")
                    continue
                desc_az = translate_with_retry(desc_en, max_retries=2)
                desc_az = truncate_smart(desc_az, MAX_SUMMARY_LEN)
            except Exception as e:
                print(f"     ❌ Tərcümə xətası: {e}")
                continue

            found_ai_news.append({
                'title_az': title_az,
                'summary_az': desc_az,
                'url': link,
                'title_en': title_en,
            })

    # Yalnız ən yeni / ən uyğun birini göndər (hər 30 dəq-də bir)
    if not found_ai_news:
        print("\n💤 Bu dövrdə yeni AI xəbəri yoxdur.")
        return

    print(f"\n📤 Tapılan {len(found_ai_news)} yeni AI xəbəri var.")
    chosen = found_ai_news[0]
    print(f"🎯 Seçildi: {chosen['title_az'][:90]}")

    post_text = format_post(
        chosen['title_az'],
        chosen['summary_az'],
        chosen['url'],
        source=detect_source(chosen['url']),
    )

    if send_to_telegram(post_text):
        posted[get_url_hash(chosen['url'])] = {
            'title': chosen['title_en'],
            'url': chosen['url'],
            'posted_at': datetime.now(BAKU_TZ).isoformat(),
        }
        save_posted(posted)
        print(f"\n✅ Uğurla dərc edildi və qeydə alındı")
    else:
        print(f"\n❌ Dərc uğursuz oldu")

    print(f"\n{'='*60}")
    print(f"🏁 Bitdi: {datetime.now(BAKU_TZ).strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()