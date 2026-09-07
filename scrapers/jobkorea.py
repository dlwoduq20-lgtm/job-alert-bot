import re
import urllib.parse
from typing import List
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper, JobItem, logger

class JobKoreaScraper(BaseScraper):
    PLATFORM_NAME = "잡코리아"
    BASE_URL = "https://www.jobkorea.co.kr"
    SEARCH_URL = "https://www.jobkorea.co.kr/Search/"

    def search(self, keywords: List[str], limit_per_keyword: int = 15) -> List[JobItem]:
        results: List[JobItem] = []
        seen_ids = set()

        for kw in keywords:
            try:
                params = {
                    "stext": kw,
                    "careerType": "2",  # 경력
                }
                resp = self.session.get(self.SEARCH_URL, params=params, timeout=self.timeout)
                if resp.status_code != 200:
                    logger.warning(f"[{self.PLATFORM_NAME}] HTTP error {resp.status_code} for query: {kw}")
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Find job title links with GI_Read
                title_links = soup.select('a[data-sentry-component="Title"]')
                if not title_links:
                    # Fallback to any GI_Read link that has text
                    title_links = [
                        a for a in soup.find_all("a", href=re.compile(r"/Recruit/GI_Read/(\d+)"))
                        if a.get_text(strip=True) and not a.find("img")
                    ]

                count = 0
                for a in title_links:
                    if count >= limit_per_keyword:
                        break

                    href = a.get("href", "")
                    m = re.search(r"/Recruit/GI_Read/(\d+)", href)
                    if not m:
                        continue
                    jid = m.group(1)
                    if jid in seen_ids:
                        continue
                    seen_ids.add(jid)

                    title = a.get_text(strip=True)
                    clean_url = f"{self.BASE_URL}/Recruit/GI_Read/{jid}"

                    # Locate parent container
                    card = a.find_parent(lambda tag: tag.name in ["div", "li"] and ("p-7" in tag.get("class", []) or "w-full" in tag.get("class", [])))
                    company = "미공개 기업"
                    exp = "경력"
                    loc = "서울"
                    tags = []
                    summary = ""

                    if card:
                        # Extract company name
                        comp_span = card.select_one("span.text-gray700, span.text-typo-b2-16")
                        if comp_span:
                            company = comp_span.get_text(strip=True)

                        # Extract chips / conditions
                        chips = [c.get_text(strip=True) for c in card.select('[data-sentry-component="GrayChip"], .chip')]
                        if chips:
                            summary = " | ".join(chips)
                            for chip in chips:
                                if "년" in chip or "경력" in chip:
                                    exp = chip
                                elif any(city in chip for city in ["서울", "경기", "인천", "판교", "강남", "재택", "원격"]):
                                    loc = chip
                                else:
                                    tags.append(chip)
                        else:
                            summary = card.get_text(" | ", strip=True)[:100]

                    results.append(
                        JobItem(
                            id=f"jobkorea_{jid}",
                            platform=self.PLATFORM_NAME,
                            title=title,
                            company=company,
                            experience=exp,
                            location=loc,
                            url=clean_url,
                            summary=summary,
                            tags=tags[:5] if tags else [kw],
                        )
                    )
                    count += 1
            except Exception as e:
                logger.error(f"[{self.PLATFORM_NAME}] Error searching keyword '{kw}': {e}")

        logger.info(f"[{self.PLATFORM_NAME}] Found {len(results)} jobs.")
        return results
