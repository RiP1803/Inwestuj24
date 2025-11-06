import feedparser, json, datetime

SOURCES = {
    "Bankier.pl": "https://www.bankier.pl/rss/wiadomosci.xml",
    "Money.pl": "https://www.money.pl/rss/",
    "BusinessInsider.pl": "https://businessinsider.com.pl/.feed",
    "Comparic.pl": "https://comparic.pl/feed/",
    "Stooq.pl": "https://stooq.pl/n/?f=114",
    "FXMag.pl": "https://fxmag.pl/feed",
    "Forsal.pl": "https://forsal.pl/rss",
    "Parkiet.com": "https://www.parkiet.com/rss/1079",
    "PulsBiznesu.pl": "https://www.pb.pl/rss",
    "Interia Biznes": "https://biznes.interia.pl/rss",
    "Reuters USA": "https://feeds.reuters.com/reuters/businessNews",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Bloomberg": "https://www.bloomberg.com/feed/podcast/etf-report.xml"
}

def parse_feed(url, source):
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:10]:
            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "")[:250],
                "published": entry.get("published", str(datetime.datetime.utcnow())),
                "source": source
            })
        return articles
    except Exception as e:
        print(f"Error parsing {source}: {e}")
        return []

def main():
    all_articles = []
    for name, url in SOURCES.items():
        print(f"Fetching {name}...")
        all_articles.extend(parse_feed(url, name))
    data = {
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "articles": all_articles
    }
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_articles)} articles to news.json")

if __name__ == "__main__":
    main()
