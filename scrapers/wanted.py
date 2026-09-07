import urllib.parse
from typing import List
from .base_scraper import BaseScraper, JobItem, logger

class WantedScraper(BaseScraper):
    PLATFORM_NAME = "원티드"
    BASE_URL = "https://www.wanted.co.kr"
    API_URL = "https://www.wanted.co.kr/api/v4/jobs"

    def search(self, keywords: List[str], limit_per_keyword: int = 15) -> List[JobItem]:
        results: List[JobItem] = []
        seen_ids = set()

        for kw in keywords:
            try:
                params = {
                    "country": "kr",
                    "years": 10,
                    "query": kw,
                    "job_sort": "job.latest_order",
                    "limit": limit_per_keyword,
                }
                resp = self.session.get(self.API_URL, params=params, timeout=self.timeout)
                if resp.status_code != 200:
                    logger.warning(f"[{self.PLATFORM_NAME}] API error {resp.status_code} for query: {kw}")
                    continue

                data = resp.json()
                jobs = data.get("data", [])
                for item in jobs:
                    jid = str(item.get("id"))
                    if jid in seen_ids:
                        continue
                    seen_ids.add(jid)

                    title = item.get("position", "").strip()
                    company_data = item.get("company", {})
                    company = company_data.get("name", "").strip() if company_data else ""
                    
                    annual_from = item.get("annual_from")
                    annual_to = item.get("annual_to")
                    if annual_from is not None and annual_to is not None:
                        if annual_to >= 90:
                            exp_str = f"경력 {annual_from}년 이상"
                        else:
                            exp_str = f"경력 {annual_from}~{annual_to}년"
                    elif annual_from:
                        exp_str = f"경력 {annual_from}년 이상"
                    else:
                        exp_str = "경력무관 / 협의"

                    addr_data = item.get("address", {})
                    location = addr_data.get("full_location") or addr_data.get("district") or "서울"
                    url = f"{self.BASE_URL}/wd/{jid}"
                    
                    results.append(
                        JobItem(
                            id=f"wanted_{jid}",
                            platform=self.PLATFORM_NAME,
                            title=title,
                            company=company,
                            experience=exp_str,
                            location=location,
                            url=url,
                            summary=f"산업: {company_data.get('industry_name', 'IT')} | 리워드 채용",
                            tags=[kw],
                        )
                    )
            except Exception as e:
                logger.error(f"[{self.PLATFORM_NAME}] Error searching keyword '{kw}': {e}")

        logger.info(f"[{self.PLATFORM_NAME}] Found {len(results)} jobs.")
        return results
