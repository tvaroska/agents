from typing import List, Optional
import feedparser
from datetime import datetime, timedelta
from time import mktime

from pydantic import BaseModel

class BaseXMLModel(BaseModel):
    def to_xml(self):
        """
        Export content of Pydantic model into XML
        
        Returns:
            str: XML representation of the model
        """
        def _escape_xml(value: str) -> str:
            """Helper function to escape special XML characters"""
            if not isinstance(value, str):
                return str(value)
            return value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
        
        def _to_xml_element(key: str, value) -> str:
            """Convert a key-value pair to XML element"""
            if value is None:
                return f"<{key}/>"
            elif isinstance(value, (list, tuple)):
                items = '\n'.join(f"<ITEM>{_escape_xml(item)}</ITEM>" for item in value)
                return f"<{key}>\n{items}\n</{key}>"
            elif isinstance(value, dict):
                nested = '\n'.join(_to_xml_element(k, v) for k, v in value.items())
                return f"<{key}>\n{nested}\n</{key}>"
            elif isinstance(value, BaseModel):
                return f"<{key}>\n{value.to_xml()}\n</{key}>"
            else:
                return f"<{key}>{_escape_xml(value)}</{key}>"

        # Get model's fields as dict and convert each field to XML element
        data = self.model_dump()
        elements = [_to_xml_element(key, value) for key, value in data.items()]
        # Get class name for root element
        root_tag = self.__class__.__name__
        # Combine all elements under root tag
        return f"<{root_tag}>\n{''.join(elements)}\n</{root_tag}>"


class RSSEntry(BaseXMLModel):
    title: str
    url: str
    media_type: Optional[str] = None
    summary: Optional[str]

# Default feeds that can be overridden
DEFAULT_FEEDS = [
    'https://huyenchip.com/feed.xml',  # Regular RSS
    'https://decodingml.substack.com/feed',  # Substack
    'https://www.youtube.com/feeds/videos.xml?channel_id=UCeMcDx6-rOq_RlKSPehk2tQ'  # Youtube
]

