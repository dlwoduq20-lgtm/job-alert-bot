from .base_scraper import JobItem, BaseScraper
from .wanted import WantedScraper
from .saramin import SaraminScraper
from .jobkorea import JobKoreaScraper
from .remember import RememberScraper
from .linkedin import LinkedInScraper

ALL_SCRAPERS = [
    WantedScraper,
    SaraminScraper,
    JobKoreaScraper,
    RememberScraper,
    LinkedInScraper,
]

__all__ = [
    "JobItem",
    "BaseScraper",
    "WantedScraper",
    "SaraminScraper",
    "JobKoreaScraper",
    "RememberScraper",
    "LinkedInScraper",
    "ALL_SCRAPERS",
]
