import argparse
import sys
import webbrowser
import logging
from typing import List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import SEARCH_KEYWORDS, CRAWLER_CONFIG
from scrapers import ALL_SCRAPERS, JobItem
from analyzer import JobScorer
from database import JobDatabase
from mailer import EmailSender

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("JobAlertSystem")

def run_job_pipeline(force_all: bool = False, preview: bool = False, min_score: int = None) -> List[JobItem]:
    if min_score is None:
        min_score = CRAWLER_CONFIG["min_score_threshold"]

    db = JobDatabase()
    scorer = JobScorer()
    mailer = EmailSender()

    logger.info("=" * 60)
    logger.info("🚀 10년 차 웹/앱 기획 PM 맞춤 채용정보 탐색을 시작합니다.")
    logger.info(f"검색 키워드: {', '.join(SEARCH_KEYWORDS)}")
    logger.info("=" * 60)

    raw_jobs: List[JobItem] = []

    # 1. 5개 플랫폼 크롤링 실행
    for ScraperClass in ALL_SCRAPERS:
        scraper = ScraperClass()
        try:
            logger.info(f"[{scraper.PLATFORM_NAME}] 채용 공고 수집 시작...")
            jobs = scraper.search(SEARCH_KEYWORDS, limit_per_keyword=5)
            raw_jobs.extend(jobs)
            logger.info(f"[{scraper.PLATFORM_NAME}] {len(jobs)}건 수집 완료.")
        except Exception as e:
            logger.error(f"[{scraper.PLATFORM_NAME}] 수집 중 예외 발생: {e}")

    logger.info(f"총 {len(raw_jobs)}건의 원시 채용 공고를 수집했습니다.")

    # 2. 중복 방지 필터링 (DB 기준)
    if force_all:
        logger.info("(--force 옵션 적용: DB 중복 필터를 건너뜁니다.)")
        unseen_jobs = raw_jobs
    else:
        unseen_jobs = db.filter_new_jobs(raw_jobs)
        logger.info(f"이전 발송 이력 제외 후 신규 공고: {len(unseen_jobs)}건")

    # 3. 10년차 PM 프로필 맞춤형 적합도 채점 및 랭킹
    ranked_jobs = scorer.filter_and_rank(unseen_jobs, min_score=min_score)
    logger.info(f"적합도 {min_score}점 이상 추천 대상 공고: {len(ranked_jobs)}건")

    # 상위 25건으로 제한 (이메일 가독성 최적화)
    top_jobs = ranked_jobs[:25]

    # 4. 이메일 발송 및 로컬 리포트 저장
    latest_report_path = mailer.save_local_report(top_jobs)

    if not preview:
        sent = mailer.send_email(top_jobs)
        if sent and not force_all:
            db.record_and_mark_emailed(top_jobs)
            logger.info(f"발송된 {len(top_jobs)}건 공고를 DB에 기록 완료했습니다.")
    else:
        logger.info(f"미리보기 모드: 웹 브라우저에서 리포트를 확인합니다: {latest_report_path}")
        webbrowser.open(latest_report_path.as_uri())

    logger.info("=" * 60)
    logger.info("🎉 채용정보 수집 및 분석 작업이 완료되었습니다.")
    logger.info("=" * 60)

    return top_jobs

def main():
    parser = argparse.ArgumentParser(description="10년차 웹/앱 기획 PM 맞춤 채용 알림 봇")
    parser.add_argument("--force", action="store_true", help="DB 중복 체크 무시하고 전체 결과 리포트 생성")
    parser.add_argument("--preview", action="store_true", help="이메일 발송 대신 결과 HTML 리포트를 브라우저로 미리보기")
    parser.add_argument("--score", type=int, default=30, help="최소 적합도 점수 필터 (기본 30점)")
    parser.add_argument("--stats", action="store_true", help="DB에 저장된 공고 통계 확인")
    parser.add_argument("--test-email", action="store_true", help="설정된 Gmail SMTP로 테스트 이메일 발송 확인")

    args = parser.parse_args()

    if args.test_email:
        print("📧 Gmail SMTP 연결 및 테스트 메일 발송을 시도합니다...")
        from scrapers.base_scraper import JobItem
        sample_job = JobItem(
            id="test_001",
            platform="원티드",
            title="[테스트] 시니어 프로덕트 매니저 (웹/앱 기획 PM 10년차)",
            company="테스트 테크놀로지",
            experience="경력 7~12년",
            location="서울 강남구 테헤란로",
            url="https://www.wanted.co.kr",
            summary="AI 활용 및 GA4 데이터 분석 기반 신규 서비스 구축 및 리뉴얼 총괄 PM",
            tags=["AI 활용 우대", "GA4/데이터분석", "신규구축/리뉴얼"],
            score=95,
            matched_keywords=["AI 활용 우대", "GA4/데이터분석", "신규구축/리뉴얼", "10년차 매칭"],
            match_reason="테스트 발송 메일입니다. 설정이 성공적으로 완료되었습니다!"
        )
        mailer = EmailSender()
        success = mailer.send_email([sample_job])
        if success:
            print("✅ 테스트 이메일이 성공적으로 전송되었습니다! 받은편지함을 확인해주세요.")
        else:
            print("❌ 이메일 전송에 실패했습니다. .env의 Gmail 주소 및 앱 비밀번호를 다시 확인해주세요.")
        return

    if args.stats:
        db = JobDatabase()
        stats = db.get_stats()
        print(f"📊 수집 및 발송 이력 통계:")
        print(f" - 총 기록된 공고 수: {stats['total']}건")
        for plat, count in stats.get("by_platform", {}).items():
            print(f"   * {plat}: {count}건")
        return

    run_job_pipeline(force_all=args.force, preview=args.preview, min_score=args.score)

if __name__ == "__main__":
    main()
