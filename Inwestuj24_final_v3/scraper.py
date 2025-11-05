import feedparser, json, datetime
SOURCES = {
    "Bankier.pl": "https://www.bankier.pl/rss/wiadomosci.xml",
    "Money.pl": "https://www.money.pl/rss/",
    "BusinessInsider.pl": "https://businessinsider.com.pl/.feed",
    "Comparic.pl": "https://comparic.pl/feed/",
    "Stooq.pl": "https://stooq.pl/n/?f=114",
    "FXMag.pl": "https://fxmag.pl/feed",
    "PulsBiznesu.pl": "https://www.pb.pl/rss",
    "Parkiet.com": "https://www.parkiet.com/rss/1079",
    "StockWatch.pl": "https://www.stockwatch.pl/rss.xml",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "Reuters": "http://feeds.reuters.com/reuters/businessNews",
    "MarketWatch": "https://www.marketwatch.com/rss/topstories",
    "YahooFinance": "https://finance.yahoo.com/news/rssindex"
}
def parse_feed(url, source):
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in getattr(feed,'entries',[])[:12]:
            articles.append({
                "title": entry.get("title",""),
                "link": entry.get("link",""),
                "summary": (entry.get("summary") or entry.get("description") or "")[:300],
                "published": entry.get("published", datetime.datetime.datetime.utcnow().isoformat()),
                "source": source
            })
        return articles
    except Exception as e:
        print("Error parsing", source, e)
        return []
def main():
    all_articles = []
    for name, url in SOURCES.items():
        print("Fetching", name)
        all_articles.extend(parse_feed(url, name))
    data = {"generated_at": datetime.datetime.datetime.utcnow().isoformat(), "articles": all_articles[:300]}
    with open("news.json","w",encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved", len(data["articles"]), "articles")
if __name__=='__main__':
    main()
