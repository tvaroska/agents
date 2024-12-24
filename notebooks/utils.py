from typing import List, Optional
import feedparser
from datetime import datetime, timedelta
from time import mktime

from pydantic import BaseModel

class RSSEntry(BaseModel):
    title: str
    url: str
    media_type: Optional[str] = None
    summary: Optional[str]

FEEDS = [
    'https://huyenchip.com/feed.xml', # Regular RSS
    'https://decodingml.substack.com/feed', # Substact
    'https://www.youtube.com/feeds/videos.xml?channel_id=UCeMcDx6-rOq_RlKSPehk2tQ' # Youtube
]

def new_articles(feeds: List[str], starting_point: datetime) -> List[RSSEntry]:
    """
    Function will check RSS feeds in feeds and return all entries which are new from starting_point

    Args:
        feeds: List of RSS feed URLs to check
        starting_point: datetime object representing the cutoff point for new articles

    Returns:
        List of RSSEntry objects that were published after the starting_point
    """
    new_entries = []
    
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        
        # Determine media type based on feed URL
        media_type = None
        if 'youtube.com' in feed_url:
            media_type = 'video'
        
        for entry in feed.entries:
            # Get published date from the entry
            if hasattr(entry, 'published_parsed'):
                pub_date = datetime.fromtimestamp(mktime(entry.published_parsed))
            elif hasattr(entry, 'updated_parsed'):
                pub_date = datetime.fromtimestamp(mktime(entry.updated_parsed))
            else:
                continue  # Skip if no date available
                
            # Check if article is newer than starting_point
            if pub_date > starting_point:
                if hasattr(entry, 'link'):
                    # Extract summary, handling potential missing field
                    summary = None
                    if hasattr(entry, 'summary'):
                        summary = entry.summary
                    
                    # Create RSSEntry object
                    rss_entry = RSSEntry(
                        title=entry.title,
                        url=entry.link,
                        media_type=media_type,
                        summary=summary
                    )
                    new_entries.append(rss_entry)
    
    return new_entries

starting_point = datetime(year=1900, month=1, day=1)
urls = new_articles(FEEDS, starting_point)

pass
