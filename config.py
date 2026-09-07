import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# -------------------------------------------------------------
# 사용자 프로필 및 매칭 키워드 설정 (웹/앱 기획 PM 10년차)
# -------------------------------------------------------------
USER_PROFILE = {
    "role": "웹, 앱 기획 PM (Product Manager / PO / Service Planner)",
    "target_experience_years": 10,
    "min_experience_acceptable": 5,   # 최소 5년차 이상 공고 (주니어/신입 제외)
    "max_experience_acceptable": 16,  # 15년차 내외까지 허용
}

# 채용 사이트별 검색어 목록
SEARCH_KEYWORDS = [
    "서비스기획",
    "웹기획",
    "앱기획",
    "PM",
    "PO",
    "프로덕트매니저",
    "Product Manager"
]

# 적합도 가산점 키워드 그룹
SCORING_CRITERIA = {
    # 1. AI 활용 역량 (생성형 AI, 프롬프트, LLM, 자동화 등)
    "ai_keywords": [
        "ai", "인공지능", "생성형", "llm", "프롬프트", "prompt", "chatgpt", 
        "gpt", "claude", "에이전트", "agent", "머신러닝", "자동화"
    ],
    # 2. 구글애널리틱스 (GA4) 및 데이터 분석/지표 도출 역량
    "analytics_keywords": [
        "ga", "ga4", "구글애널리틱스", "google analytics", "애널리틱스", 
        "데이터", "데이터분석", "amplitude", "앰플리튜드", "퍼널", "지표", 
        "대시보드", "sql", "a/b", "ab테스트", "cohort", "코호트"
    ],
    # 3. 신규 구축, 리뉴얼, 운영/유지보수 PM 전주기 경험
    "lifecycle_keywords": [
        "신규구축", "리뉴얼", "신규 구축", "0 to 1", "유지보수", "운영", 
        "고도화", "prd", "요구사항", "백로그", "스프린트", "애자일", "agile",
        "wbs", "화면설계", "와이어프레임", "기능정의서", "프로젝트 관리"
    ],
    # 4. 웹/앱/모바일 도메인
    "webapp_keywords": [
        "웹", "앱", "모바일", "web", "app", "ios", "android", "플랫폼", 
        "서비스기획", "프로덕트"
    ]
}

# -------------------------------------------------------------
# 필터링 조건: 에이전시 배제 및 근무지(서울/경기) 제한
# -------------------------------------------------------------
# 1. 에이전시/SI/파견 배제 키워드
EXCLUDE_AGENCY_KEYWORDS = [
    "에이전시", "agency", "웹에이전시", "디지털에이전시",
    "si", "sm", "si/sm", "파견", "외주", "도급", "용역",
    "구축대행", "구축 대행", "고객사 상주", "상주", "고객사 프로젝트",
    "si 프로젝트", "si 사업", "인력파견", "파견직"
]

# 2. 허용 근무 지역 (서울, 경기, 인천 수도권 및 재택/원격)
ALLOWED_LOCATIONS = [
    "서울", "경기", "인천", "판교", "분당", "성남", "수원", "안양", 
    "부천", "고양", "일산", "용인", "과천", "하남", "광명", "화성", 
    "동탄", "평택", "송도", "수도권", "재택", "원격", "remote", "korea", "대한민국"
]

# 3. 비수도권/해외 배제 지역
DISALLOWED_LOCATIONS = [
    "부산", "대구", "대전", "광주", "울산", "세종", "강원", 
    "충북", "충남", "충청", "전북", "전남", "전라", "경북", "경남", "경상", 
    "제주", "해외", "미국", "일본", "싱가포르", "베트남"
]

# -------------------------------------------------------------
# 이메일 전송 설정 (SMTP)
# -------------------------------------------------------------
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "smtp_user": os.getenv("SMTP_USER", ""),          # 발신자 이메일
    "smtp_password": os.getenv("SMTP_PASSWORD", ""),  # 발신자 비밀번호 / 앱비밀번호
    "recipient_email": os.getenv("RECIPIENT_EMAIL", ""),  # 수신자 이메일
    "sender_name": "AI 커리어 비서 (Job Alert Bot)",
}

# -------------------------------------------------------------
# 크롤러 설정
# -------------------------------------------------------------
CRAWLER_CONFIG = {
    "request_timeout": 12,
    "max_results_per_platform": 15,
    "min_score_threshold": 35,  # 100점 만점 중 35점 이상만 최종 리포트에 포함
}

# -------------------------------------------------------------
# 파일 경로
# -------------------------------------------------------------
DB_PATH = BASE_DIR / "database" / "job_history.db"
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
