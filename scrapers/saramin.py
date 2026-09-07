import re
import urllib.parse
from typing import List
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper, JobItem, logger

class SaraminScraper(BaseScraper):
    PLATFORM_NAME = "사람인"
    BASE_URL = "https://www.saramin.co.kr"
    SEARCH_URL = "https://www.saramin.co.kr/zf_user/search/recruit"

    def search(self, keywords: List[str], limit_per_keyword: int = 15) -> List[JobItem]:
        results: List[JobItem] = []
        seen_ids = set()

        for kw in keywords:
            try:
                params = {
                    "searchword": kw,
                    "exp_cd": "2",      # 경력
                    "sort": "rc",        # 최신 등록순 (or 정확도순)
                }
                resp = self.session.get(self.SEARCH_URL, params=params, timeout=self.timeout)
                if resp.status_code != 200:
                    logger.warning(f"[{self.PLATFORM_NAME}] HTTP error {resp.status_code} for query: {kw}")
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                items = soup.select(".item_recruit")

                count = 0
                for el in items:
                    if count >= limit_per_keyword:
                        break

                    title_elem = el.select_one(".job_tit a")
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    rel_url = title_elem.get("href", "")
                    full_url = rel_url if rel_url.startswith("http") else f"{self.BASE_URL}{rel_url}"

                    # Extract rec_idx from URL or element attribute
                    m = re.search(r"rec_idx=(\d+)", full_url)
                    jid = m.group(1) if m else str(hash(full_url))

                    if jid in seen_ids:
                        continue
                    seen_ids.add(jid)

                    corp_elem = el.select_one(".corp_name a")
                    company = corp_elem.get_text(strip=True) if corp_elem else "미공개 기업"

                    conditions = [s.get_text(strip=True) for s in el.select(".job_condition span")]
                    # conditions typically: ['서울 강남구', '경력 7년↑', '학력무관', '정규직']
                    loc = conditions[0] if len(conditions) > 0 else "서울"
                    exp = conditions[1] if len(conditions) > 1 else "경력"

                    sectors = [s.get_text(strip=True) for s in el.select(".job_sector a, .job_sector span")]

                    results.append(
                        JobItem(
                            id=f"saramin_{jid}",
                            platform=self.PLATFORM_NAME,
                            title=title,
                            company=company,
                            experience=exp,
                            location=loc,
                            url=full_url,
                            summary=" | ".join(conditions),
                            tags=sectors[:5],
                        )
                    )
                    count += 1
            except Exception as e:
                logger.error(f"[{self.PLATFORM_NAME}] Error searching keyword '{kw}': {e}")

        logger.info(f"[{self.PLATFORM_NAME}] Found {len(results)} jobs.")
        return results
