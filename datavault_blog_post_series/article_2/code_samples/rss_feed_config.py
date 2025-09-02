# rss_feed_config.py
# DataVault's RSS feed configuration
# As implemented by David Kim in Article 2

rss_feeds = [
    {
        "name": "MarketWatch Markets",
        "url": "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain",
        "category": "market_analysis"
    },
    {
        "name": "Reuters Business News",
        "url": "https://feeds.feedburner.com/reuters/businessNews", 
        "category": "market_news"
    },
    {
        "name": "Bloomberg Markets",
        "url": "https://feeds.bloomberg.com/markets/news.rss",
        "category": "market_news"
    }
]

# Configuration for Nuclia RSS feed integration
def configure_rss_feeds(nuclia_client, kb_id):
    """
    Configure RSS feeds for automatic ingestion into Nuclia
    
    Args:
        nuclia_client: Authenticated Nuclia client
        kb_id: Knowledge Box ID to add feeds to
    
    Returns:
        List of configured feed IDs
    """
    configured_feeds = []
    
    for feed in rss_feeds:
        # Configure each RSS feed with Nuclia
        feed_config = {
            "name": feed["name"],
            "url": feed["url"],
            "sync_interval": 900,  # 15 minutes in seconds
            "category": feed["category"],
            "auto_index": True
        }
        
        # This would be the actual API call to configure the feed
        # feed_id = nuclia_client.add_rss_feed(kb_id, feed_config)
        # configured_feeds.append(feed_id)
        
        print(f"Configured RSS feed: {feed['name']}")
        print(f"  URL: {feed['url']}")
        print(f"  Category: {feed['category']}")
        print(f"  Sync: Every 15 minutes")
        print()
    
    return configured_feeds

if __name__ == "__main__":
    print("DataVault Financial Services - RSS Feed Configuration")
    print("=" * 50)
    print(f"Total feeds to configure: {len(rss_feeds)}")
    print()
    
    for i, feed in enumerate(rss_feeds, 1):
        print(f"{i}. {feed['name']}")
        print(f"   URL: {feed['url']}")
        print(f"   Category: {feed['category']}")
        print()