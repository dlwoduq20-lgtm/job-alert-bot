import re
import urllib.parse
from typing import List
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper, JobItem, logger

class LinkedInScraper(BaseScraper):
    PLATFORM_NAME = "링크드인"
    BASE_URL = "https://www.linkedin.com"
    API_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    def search(self, keywords: List[str], limit_per_keyword: int = 15) -> List[JobItem]:
        results: List[JobItem] = []
        seen_ids = set()

        for kw in keywords:
            try:
                params = {
                    "keywords": kw,
                    "location": "South Korea",
                    "start": 0,
                }
                resp = self.session.get(self.API_URL, params=params, timeout=self.timeout)
                if resp.status_code != 200:
                    logger.warning(f"[{self.PLATFORM_NAME}] HTTP error {resp.status_code} for query: {kw}")
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("li")

                count = 0
                for card in cards:
                    if count >= limit_per_keyword:
                        break

                    title_elem = card.select_one(".base-search-card__title")
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)

                    link_elem = card.select_one("a.base-card__full-link, a.base-search-card--link")
                    if not link_elem:
                        continue
                    raw_url = link_elem.get("href", "")
                    clean_url = raw_url.split("?")[0] if "?" in raw_url else raw_url

                    m = re.search(r"-(\d+)(?:\?|$)", raw_url)
                    jid = m.group(1) if m else str(hash(clean_url))

                    if jid in seen_ids:
                        continue
                    seen_ids.add(jid)

                    comp_elem = card.select_one(".base-search-card__subtitle a, .base-search-card__subtitle")
                    company = comp_elem.get_text(strip=True) if comp_elem else "글로벌/국내 기업"

                    loc_elem = card.select_one(".job-search-card__location")
                    loc = loc_elem.get_text(strip=True) if loc_elem else "대한민국"

                    time_elem = card.select_one("time")
                    post_date = time_elem.get_text(strip=True) if time_elem else ""

                    results.append(
                        JobItem(
                            id=f"linkedin_{jid}",
                            platform=self.PLATFORM_NAME,
                            title=title,
                            company=company,
                            experience="시니어 / 경력직",
                            location=loc,
                            url=clean_url,
                            summary=f"게시일: {post_date}" if post_date else "LinkedIn 채용 공고",
                            tags=[kw],
                            date=post_date,
                        )
                    )
                    count += 1
            except Exception as e:
                logger.error(f"[{self.PLATFORM_NAME}] Error searching keyword '{kw}': {e}")

        logger.info(f"[{self.PLATFORM_NAME}] Found {len(results)} jobs.")
        return results
