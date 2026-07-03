# 🤖 AI AZƏRBAYCAN — Telegram Xəbər Botu

Bu bot Bloomberg-in texnologiya, bazar və iqtisadiyyat RSS lentlərini izləyir, **süni intellekt və robotika** ilə bağlı xəbərləri süzgəcdən keçirir, **Azərbaycan dilinə tərcümə edir** və avtomatik olaraq Telegram kanalınızda paylaşır.

## ✨ Xüsusiyyətlər

- ⏰ **Hər 30 dəqiqədən bir** avtomatik dərc (GitHub Actions ilə)
- 🎯 **AI aşkarlama**: 30+ açar söz (OpenAI, Anthropic, Nvidia, robot, LLM və s.)
- 🌐 **Tərcümə**: Google Translate API ilə EN → AZ
- 🚫 **Təkrar yoxdur**: URL hash ilə unikal xəbər izləmə
- 😃 **Emoji ilə formatlama**: mövzuya uyğun (🧠 AI, 🔧 çip, 💰 investisiya, 🦾 robot)
- 📊 **Ağıllı kəsmə**: cümlə sonunda bitir
- 🛡️ **Səhvlərə davamlı**: tərcümə uğursuz olarsa, növbəti xəbərə keçir

## 📂 Struktura

```
telegram-ai-news/
├── .github/workflows/
│   └── news-bot.yml       # GitHub Actions — hər 30 dəq
├── news_bot.py            # Əsas skript
├── requirements.txt       # Python asılılıqları
├── posted_news.json       # Paylaşılmış xəbərlər (auto-gen)
├── .gitignore
└── README.md              # Bu fayl
```

## 🚀 Quraşdırma (5 dəqiqə)

### 1. GitHub-da yeni repo yarat
- [github.com/new](https://github.com/new) ünvanına gedin
- **Repository name**: `telegram-ai-news` (və ya istədiyin ad)
- **Visibility**: Public (Actions üçün limitsiz) və ya Private (2000 dəq pulsuz)
- ✅ "Add a README file" işarələ
- **Create repository**

### 2. Faylları repo-ya yüklə
Variant A — Browser ilə (asan):
- Repo səhifəsində **"uploading an existing file"** linkinə kliklə
- Bu qovluqdakı bütün faylları sürükləyib burax
- Commit et

Variant B — Git əmri ilə:
```bash
cd telegram-ai-news
git init
git remote add origin https://github.com/SƏNIN-İSTİFADƏÇİ-ADIN/telegram-ai-news.git
git add .
git commit -m "initial commit"
git branch -M main
git push -u origin main
```

### 3. Bot token-i Secret kimi əlavə et
- Repo səhifəsində **Settings** → **Secrets and variables** → **Actions**
- **"New repository secret"** kliklə
- Ad: `TELEGRAM_BOT_TOKEN`
- Dəyər: `8865540268:AAEtF6QeVir9RIgtxU30lUNYCfcHDuWWgc8`
- **Add secret**

### 4. (İstəyə bağlı) Branch qorumasını düzəlt
`posted_news.json` avtomatik commit olunur. Heç bir problem olmamalıdır, amma default branch-i qoruya bilərsən.

### 5. Test et
- Repo-da **Actions** tabına gedin
- Sol panel: **AI News Bot**
- **"Run workflow"** → yaşıl düymə
- Run bitdikdən sonra log-lara baxın:
  - ✅ "Uğurla dərc edildi" — Telegram-a mesaj getdi
  - ❌ Xəta varsa — log-da göstəriləcək

## ⏰ Cədvəl

Hər 30 dəqiqədən bir (UTC):
```
00:00, 00:30, 01:00, ... 23:30
```

**Bakı vaxtı ilə** (UTC+4):
```
04:00, 04:30, 05:00, ... 03:30 (növbəti gün)
```

> 💡 Cron ifadəsini dəyişmək istəyirsən? `.github/workflows/news-bot.yml` faylındakı `cron:` sətirini redaktə et.

## 🧪 Lokal test

```bash
# Repo-nu klonla
git clone https://github.com/SƏNİN-İSTİFADƏÇİ-ADIN/telegram-ai-news.git
cd telegram-ai-news

# Virtual mühit yarat (tövsiyə olunur)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Asılılıqları yüklə
pip install -r requirements.txt

# Bot token-i export et
export TELEGRAM_BOT_TOKEN='8865540268:AAEtF6QeVir9RIgtxU30lUNYCfcHDuWWgc8'

# Skripti işə sal
python news_bot.py
```

## 🎨 Xəbər formatı

Hər post bu formata uyğundur:

```
🤖 <b>Başlıq burada</b>

Qısa xülasə Azərbaycan dilində, 1-3 cümlə...

🔗 Mənbə: <a href="...">Bloomberg</a>
```

Emoji mövzuya görə avtomatik seçilir:

| Emoji | Mövzu |
|-------|-------|
| 🤖 | Ümumi AI |
| 🧠 | OpenAI, Anthropic, ChatGPT, LLM |
| 🔧 | Nvidia, çip, yarımkeçirici |
| 🦾 | Robot, humanoid |
| 💰 | İnvestisiya, fond |
| 🏢 | Google, Meta, böyük texnologiya |
| 👥 | İş, məşğulluq |

## ⚙️ Fərdiləşdirmə

### Daha çox/az mənbə əlavə et
`news_bot.py` faylındakı `RSS_FEEDS` siyahısını redaktə et:

```python
RSS_FEEDS = [
    'https://feeds.bloomberg.com/technology/news.rss',
    'https://feeds.bloomberg.com/markets/news.rss',
    'https://feeds.bloomberg.com/economics/news.rss',
    'https://www.nytimes.com/svc/collections/v1/publish/https:/www.nytimes.com/section/technology/rss.xml',
    # əlavə mənbələr:
    # 'https://techcrunch.com/category/artificial-intelligence/feed/',
    # 'https://www.theverge.com/rss/ai-artificial-intelligence/index.xml',
    # 'https://spectrum.ieee.org/feeds/topic/robotics.rss',
    # 'https://www.ft.com/companies?format=rss',
    # 'https://www.reutersagency.com/feed/?best-topics=tech&post_type=best',
]
```

**Cari mənbələr:**
- ✅ Bloomberg — Texnologiya / Bazar / İqtisadiyyat
- ✅ The New York Times — Texnologiya
- ⏳ Əlavə etmək istədiklərin üçün yuxarıdakı kimi yaz, skript özü formatlayacaq

### Cədvəli dəyiş
`.github/workflows/news-bot.yml` faylındakı cron:
```yaml
schedule:
  - cron: '0 */1 * * *'   # Hər saat
  - cron: '*/15 * * * *'  # Hər 15 dəqiqə
  - cron: '0 9-18 * * *'  # İş saatlarında hər saat
```

### AI süzgəc açarsözləri
`AI_KEYWORDS` siyahısına yeni sözlər əlavə et (ingilis dilində).

## 🐛 Problem həlli

| Problem | Həll |
|---------|------|
| Bot mesaj göndərmir | Token düzgündür? Bot kanalda admin-dir? |
| Tərcümə uğursuz | Google Translate rate limit — bir neçə dəqiqə gözlə |
| Eyni xəbər təkrarlanır | `posted_news.json` sil, sıfırdan başlayacaq |
| Cron işləmir | GitHub Actions səhifəsində aktiv olduğunu yoxla |

## 📊 Xərclər

- **GitHub Actions**: Pulsuz public repo üçün limitsiz; private üçün 2000 dəq/ay (bu iş ~1500 dəq/ay istifadə edəcək — sərhəddədir)
- **Google Translate**: `deep-translator` pulsuz tier kifayətdir
- **Telegram Bot API**: Tamamilə pulsuz

## 📝 Lisenziya

Bu layihə şəxsi istifadə üçündür. İstədiyin kimi dəyişdirə bilərsən.

---

🤖 Mavis tərəfindən hazırlanıb • 2026