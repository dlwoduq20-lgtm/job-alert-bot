import re
import logging
from typing import List, Tuple
from config import (
    SCORING_CRITERIA,
    USER_PROFILE,
    EXCLUDE_AGENCY_KEYWORDS,
    ALLOWED_LOCATIONS,
    DISALLOWED_LOCATIONS,
)
from scrapers.base_scraper import JobItem

logger = logging.getLogger(__name__)

class JobScorer:
    def __init__(self):
        self.ai_kw = SCORING_CRITERIA["ai_keywords"]
        self.analytics_kw = SCORING_CRITERIA["analytics_keywords"]
        self.lifecycle_kw = SCORING_CRITERIA["lifecycle_keywords"]
        self.webapp_kw = SCORING_CRITERIA["webapp_keywords"]
        self.agency_kw = EXCLUDE_AGENCY_KEYWORDS
        self.allowed_locations = ALLOWED_LOCATIONS
        self.disallowed_locations = DISALLOWED_LOCATIONS
        self.last_stats = {
            "agency_excluded": 0,
            "location_excluded": 0,
            "qualified": 0
        }

    def is_agency(self, job: JobItem) -> Tuple[bool, str]:
        """Checks if the job is from an agency, SI, outsourcing, or dispatch company."""
        target_text = f"{job.company} {job.title} {job.summary} {' '.join(job.tags)}".lower()

        for kw in self.agency_kw:
            kw_clean = kw.lower().strip()
            # For short words like 'si' or 'sm', match whole words to avoid false positives
            if len(kw_clean) <= 3 and kw_clean.isalpha():
                if re.search(r"(?:\b|_|\s)" + re.escape(kw_clean) + r"(?:\b|_|\s|\/)", target_text):
                    return True, f"에이전시/SI 키워드 감지 ('{kw}')"
            else:
                if kw_clean in target_text:
                    return True, f"에이전시/외주 키워드 감지 ('{kw}')"

        return False, ""

    def is_valid_location(self, job: JobItem) -> Tuple[bool, str]:
        """Checks if the job is in Seoul, Gyeonggi, Incheon (Metropolitan Area) or Remote."""
        loc = (job.location or "").lower().strip()
        summary = (job.summary or "").lower()
        full_text = f"{loc} {summary}"

        # 1. Check if any disallowed region is explicitly in location
        for dis in self.disallowed_locations:
            if dis in loc:
                return False, f"비수도권/지방 근무지 제외 ({dis})"

        # 2. Check if allowed metropolitan area keyword is in location or summary
        for allowed in self.allowed_locations:
            if allowed in full_text:
                return True, f"수도권 근무지 ({allowed})"

        # 3. Check if disallowed region is in summary
        for dis in self.disallowed_locations:
            if dis in summary:
                return False, f"비수도권/지방 근무지 제외 ({dis})"

        # 4. If generic location like "대한민국" or empty, treat as Seoul metropolitan by default
        if not loc or any(g in loc for g in ["대한민국", "korea", "전국"]):
            return True, "기본 수도권 간주"

        return False, f"수도권 외 지역 ({loc})"

    def score_job(self, job: JobItem) -> JobItem:
        score = 0
        matched_tags: List[str] = []
        reasons: List[str] = []

        # Combines all text for searching
        text_corp = f"{job.title} {job.experience} {job.summary} {' '.join(job.tags)}".lower()

        # --------------------------------------------------
        # 1. 경력 적합도 (10년차 기준: 최대 30점)
        # --------------------------------------------------
        exp_score = self._evaluate_experience(job.experience, text_corp)
        score += exp_score
        if exp_score >= 25:
            matched_tags.append("10년차 매칭")

        # --------------------------------------------------
        # 2. 직무 기본 적합도 (PM, 서비스/웹/앱 기획: 최대 25점)
        # --------------------------------------------------
        role_score = self._evaluate_role(job.title, text_corp)
        score += role_score
        if role_score >= 20:
            matched_tags.append("웹/앱 PM")

        # --------------------------------------------------
        # 3. AI 활용 역량 매칭 (최대 20점 가산)
        # --------------------------------------------------
        ai_matches = [kw for kw in self.ai_kw if re.search(r'\b' + re.escape(kw) + r'\b', text_corp) or kw in text_corp]
        if ai_matches:
            score += 20
            matched_tags.append("AI 활용 우대")
            reasons.append(f"AI 역량({', '.join(ai_matches[:2])})")

        # --------------------------------------------------
        # 4. 구글애널리틱스 (GA4) 및 데이터 분석 역량 (최대 15점 가산)
        # --------------------------------------------------
        data_matches = [kw for kw in self.analytics_kw if kw in text_corp]
        if data_matches:
            score += 15
            matched_tags.append("GA4/데이터분석")
            reasons.append(f"데이터 분석({', '.join(data_matches[:2])})")

        # --------------------------------------------------
        # 5. 신규 구축, 리뉴얼, 운영 유지보수 전주기 경험 (최대 15점 가산)
        # --------------------------------------------------
        cycle_matches = [kw for kw in self.lifecycle_kw if kw in text_corp]
        if cycle_matches:
            score += 15
            matched_tags.append("구축/리뉴얼/운영")
            reasons.append(f"전주기 PM({', '.join(cycle_matches[:2])})")

        # Cap score between 0 and 100
        final_score = min(max(score, 0), 100)
        job.score = final_score
        job.matched_keywords = matched_tags

        # Compose recommendation summary
        if reasons:
            job.match_reason = " | ".join(reasons)
        else:
            job.match_reason = "10년 차 웹/앱 기획 PM 적합 포지션 (인하우스/서비스 기업)"

        return job

    def _evaluate_experience(self, exp_str: str, full_text: str) -> int:
        exp_lower = f"{exp_str} {full_text}".lower()

        is_senior_lead = any(w in exp_lower for w in ["senior", "lead", "리드", "팀장", "파트장", "수석", "책임", "이사"])

        nums = [int(n) for n in re.findall(r"(\d+)\s*년", exp_str)]
        if nums:
            min_y = min(nums)
            max_y = max(nums)
            if (min_y <= 10 <= max_y) or (7 <= min_y <= 12):
                return 30
            if 5 <= min_y <= 15:
                return 25
            if max_y < 4 and not is_senior_lead:
                return -20

        if is_senior_lead:
            return 28
        if "경력무관" in exp_str or "경력" in exp_str:
            return 20
        return 15

    def _evaluate_role(self, title: str, full_text: str) -> int:
        t_lower = title.lower()
        high_value = ["pm", "po", "product manager", "서비스기획", "웹기획", "앱기획", "프로덕트매니저", "프로덕트 오너"]
        if any(w in t_lower for w in high_value):
            return 25
        
        if any(w in t_lower for w in ["기획", "매니저", "플래너", "planner"]):
            return 18

        if any(w in full_text for w in high_value):
            return 15
        return 5

    def filter_and_rank(self, jobs: List[JobItem], min_score: int = 35) -> List[JobItem]:
        filtered: List[JobItem] = []
        agency_count = 0
        location_count = 0

        for j in jobs:
            # 1. 에이전시 / SI / 외주 필터링
            is_ag, ag_reason = self.is_agency(j)
            if is_ag:
                agency_count += 1
                logger.debug(f"[필터 제외] 에이전시 제외: {j.company} - {j.title} ({ag_reason})")
                continue

            # 2. 서울 / 경기권 지역 필터링
            is_loc, loc_reason = self.is_valid_location(j)
            if not is_loc:
                location_count += 1
                logger.debug(f"[필터 제외] 비수도권 제외: {j.company} - {j.title} ({loc_reason})")
                continue

            # 3. 채점 및 점수 필터링
            scored = self.score_job(j)
            if scored.score >= min_score:
                filtered.append(scored)

        filtered.sort(key=lambda x: x.score, reverse=True)

        self.last_stats["agency_excluded"] = agency_count
        self.last_stats["location_excluded"] = location_count
        self.last_stats["qualified"] = len(filtered)

        logger.info(
            f"필터링 결과: 에이전시 제외 {agency_count}건, "
            f"수도권 외 지역 제외 {location_count}건, "
            f"최종 통과 공고 {len(filtered)}건"
        )
        return filtered
