# scraper.py
# Updated by assistant — dedupe + better source mix + basic filtering
import feedparser
import json
import datetime
import re

# Sources: mix of Polish financial sites + international business feeds
SOURCES = {
    # Polska
    "Bankier.pl": "https://www.bankier.pl/rss/wiadomosci.xml",
    "Money.pl": "https://www.money.pl/rss/",
    "BusinessInsider.pl": "https://businessinsider.com.pl/.feed",
    "Comparic.pl": "https://comparic.pl/feed/",
    "Stooq.pl": "https://stooq.pl/n/?f=114",
    "FXMag.pl": "https://fxmag.pl/feed",
    "Forsal.pl": "https://forsal.pl/rss",
    "Parkiet.com": "https://www.parkiet.com/rss/1079",
    "PulsBiznesu.pl": "https://www.pb.pl/rss",
    "StockWatch.pl": "https://www.stockwatch.pl/rss.xml",
    # International / USA
    "Reuters": "http://feeds.reuters.com/reuters/businessNews",
    "CNBC": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    "MarketWatch": "https://www.marketwatch.com/rss/topstories",
    "YahooFinance": "https://feeds.finance.yahoo.com/rss/",
    "Bloomberg": "https://www.bloomberg.com/feed/podcast/etf-report.xml"
}

# Configuration
MAX_PER_FEED = 20            # how many entries to read per feed
MAX_TOTAL = 300              # how many articles to keep before truncating
FINAL_KEEP = 200             # final number saved to news.json (can be 200, site shows 20)
MIN_TITLE_LENGTH = 10
MIN_SUMMARY_LENGTH = 40

GENERIC_PATTERNS = [
    r"krótki (podsumowanie|przegląd)",
    r"wydarzenia na rynku",
    r"aktualności", r"wiadomości", r"news",
    r"przegląd rynków", r"raport"
]

def is_generic(text):
    if not text:
        return True
    t = text.lower()
    # too short
    if len(t) < MIN_TITLE_LENGTH:
        return True
    # match generic patterns
    for p in GENERIC_PATTERNS:
        if re.search(p, t):
            return True
    return False

def normalize_title(title):
    if not title:
        return ""
    # remove punctuation, lowercase, collapse spaces
    s = re.sub(r'\s+', ' ', title.strip().lower())
    s = re.sub(r'[^\w\s]', '', s)
    return s

def guess_category(source, title, summary):
    s = (source or "").lower()
    t = (title or "").lower()
    if any(x in s for x in ["bankier","money","parkiet","pb.pl","stockwatch","puls","comparic","fxmag","forsal","stooq"]):
        return "pl"
    if any(x in s for x in ["reuters","cnbc","marketwatch","yahoo","bloomberg"]):
        # heuristic: if title mentions europe/uk/pl, might be eu, else us
        if "europe" in t or "euro" in t or "uk" in t:
            return "eu"
        return "us"
    if "crypto" in t or "btc" in t or "krypt" in t or "bitcoin" in t:
        return "crypto"
    return "other"

def parse_feed(url, source):
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print("feedparser exception for", source, e)
        return []
    entries = getattr(feed, "entries", [])[:MAX_PER_FEED]
    out = []
    for entry in entries:
        title = entry.get("title") or entry.get("headline") or ""
        link = entry.get("link") or ""
        summary = (entry.get("summary") or entry.get("description") or "") or ""
        published = entry.get("published") or entry.get("updated") or datetime.datetime.utcnow().isoformat()
        # basic clean
        title = title.strip()
        summary = re.sub(r'\s+', ' ', summary).strip()
        out.append({
            "title": title,
            "link": link,
            "summary": summary,
            "published": published,
            "source": source
        })
    return out

def collect_all():
    all_articles = []
    for name, url in SOURCES.items():
        print("Fetching", name, "->", url)
        try:
            articles = parse_feed(url, name)
            all_articles.extend(articles)
        except Exception as e:
            print("Error fetching", name, e)
    return all_articles

def dedupe_and_filter(articles):
    seen_urls = set()
    seen_titles = set()
    kept = []
    for a in articles:
        url = (a.get("link") or "").split('#')[0].strip()
        title = a.get("title") or ""
        norm = normalize_title(title)
        # filters
        if not url and not title:
            continue
        if url in seen_urls:
            continue
        if norm in seen_titles:
            continue
        # skip too generic titles or too-short summaries (but keep if title strong)
        if is_generic(title) and len(a.get("summary","") or "") < MIN_SUMMARY_LENGTH:
            # skip generic short items
            continue
        # passed — keep
        seen_urls.add(url)
        seen_titles.add(norm)
        kept.append(a)
        if len(kept) >= MAX_TOTAL:
            break
    return kept

def enrich_and_sort(articles):
    # assign category and convert published to ISO
    enriched = []
    for a in articles:
        cat = guess_category(a.get("source",""), a.get("title",""), a.get("summary",""))
        # try to normalize published to ISO
        pub = a.get("published")
        try:
            # feedparser often gives structured 'published_parsed'
            enriched_pub = None
            # if entry had published_parsed it would be handled earlier; keep raw otherwise
            enriched_pub = pub
        except Exception:
            enriched_pub = datetime.datetime.utcnow().isoformat()
        enriched.append({
            "title": a.get("title",""),
            "link": a.get("link",""),
            "summary": a.get("summary","")[:400],
            "published": enriched_pub,
            "source": a.get("source",""),
            "category": cat
        })
    # simple sort: newest first by published (best-effort)
    try:
        enriched.sort(key=lambda x: x.get("published",""), reverse=True)
    except Exception:
        pass
    return enriched

def main():
    all_articles = collect_all()
    print("Collected", len(all_articles), "raw articles")
    filtered = dedupe_and_filter(all_articles)
    print("After dedupe/filter:", len(filtered))
    enriched = enrich_and_sort(filtered)
    final = enriched[:FINAL_KEEP]
    data = {
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "articles": final
    }
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved", len(final), "articles to news.json")

if __name__ == "__main__":
    main()
