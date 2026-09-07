from dataclasses import dataclass, field
from typing import List, Optional
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

@dataclass
class JobItem:
    id: str
    platform: str
    title: str
    company: str
    experience: str = ""
    location: str = ""
    url: str = ""
    summary: str = ""
    tags: List[str] = field(default_factory=list)
    date: str = ""
    score: int = 0
    matched_keywords: List[str] = field(default_factory=list)
    match_reason: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "title": self.title,
            "company": self.company,
            "experience": self.experience,
            "location": self.location,
            "url": self.url,
            "summary": self.summary,
            "tags": self.tags,
            "date": self.date,
            "score": self.score,
            "matched_keywords": self.matched_keywords,
            "match_reason": self.match_reason,
        }

class BaseScraper:
    def __init__(self, timeout: int = 12):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        })

    def search(self, keywords: List[str]) -> List[JobItem]:
        raise NotImplementedError
