from typing import List
from .base_scraper import BaseScraper, JobItem, logger

class RememberScraper(BaseScraper):
    PLATFORM_NAME = "리멤버"
    BASE_URL = "https://career.rememberapp.co.kr"
    API_URL = "https://career-api.rememberapp.co.kr/job_postings"

    def search(self, keywords: List[str], limit_per_keyword: int = 15) -> List[JobItem]:
        results: List[JobItem] = []
        seen_ids = set()

        for kw in keywords:
            try:
                params = {
                    "keyword": kw,
                    "order": "recent",
                    "page": 1,
                    "size": limit_per_keyword,
                }
                headers = {
                    "Referer": "https://career.rememberapp.co.kr/",
                    "Accept": "application/json",
                }
                resp = self.session.get(self.API_URL, params=params, headers=headers, timeout=self.timeout)
                if resp.status_code != 200:
                    logger.warning(f"[{self.PLATFORM_NAME}] API error {resp.status_code} for query: {kw}")
                    continue

                data = resp.json()
                items = data.get("data", [])

                for item in items:
                    jid = str(item.get("id"))
                    if jid in seen_ids:
                        continue
                    seen_ids.add(jid)

                    title = item.get("title", "").strip()
                    org = item.get("organization") or {}
                    company = org.get("name", "") if isinstance(org, dict) else ""
                    if not company:
                        company = "리멤버 추천 기업"

                    min_exp = item.get("min_experience")
                    max_exp = item.get("max_experience")
                    if min_exp is not None and max_exp is not None:
                        exp_str = f"경력 {min_exp}~{max_exp}년"
                    elif min_exp is not None:
                        exp_str = f"경력 {min_exp}년 이상"
                    else:
                        exp_str = "경력 협의"

                    addresses = item.get("addresses") or []
                    loc = "서울"
                    if addresses and isinstance(addresses, list):
                        addr = addresses[0]
                        if isinstance(addr, dict):
                            loc = addr.get("location", "서울")
                        elif isinstance(addr, str):
                            loc = addr

                    # Summary snippet from qualifications or description
                    qual = item.get("qualifications") or ""
                    pref = item.get("preferred_qualifications") or ""
                    summary = f"자격요건: {qual[:120]}... | 우대사항: {pref[:120]}..." if qual or pref else ""

                    chips_data = item.get("chips") or []
                    tags = [c.get("name") for c in chips_data if isinstance(c, dict) and c.get("name")]
                    if not tags:
                        tags = [kw]

                    url = f"{self.BASE_URL}/job/posting/{jid}"

                    results.append(
                        JobItem(
                            id=f"remember_{jid}",
                            platform=self.PLATFORM_NAME,
                            title=title,
                            company=company,
                            experience=exp_str,
                            location=loc,
                            url=url,
                            summary=summary,
                            tags=tags[:5],
                        )
                    )
            except Exception as e:
                logger.error(f"[{self.PLATFORM_NAME}] Error searching keyword '{kw}': {e}")

        logger.info(f"[{self.PLATFORM_NAME}] Found {len(results)} jobs.")
        return results
