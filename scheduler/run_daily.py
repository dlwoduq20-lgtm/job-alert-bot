"""
매일 아침 9시 실행을 위한 데일리 러너 스크립트.
Windows 작업 스케줄러(Task Scheduler) 또는 cron 등에 의해 매일 09:00에 실행됩니다.
"""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
from main import run_job_pipeline

logging.basicConfig(
    filename=PROJECT_ROOT / "daily_scheduler.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

if __name__ == "__main__":
    logging.info("==========================================")
    logging.info("매일 아침 9시 정기 채용정보 수집 작업 시작")
    logging.info("==========================================")
    try:
        jobs = run_job_pipeline(force_all=False, preview=False)
        logging.info(f"정기 작업 완료: {len(jobs)}건의 맞춤 공고 처리 및 발송 완료.")
    except Exception as e:
        logging.error(f"정기 작업 실행 중 오류 발생: {e}", exc_info=True)
