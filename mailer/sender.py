import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path
from typing import List
import logging

from config import EMAIL_CONFIG, REPORT_DIR
from scrapers.base_scraper import JobItem
from .template import generate_email_html

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, config=EMAIL_CONFIG):
        self.config = config

    def save_local_report(self, jobs: List[JobItem]) -> Path:
        """Saves an HTML report locally for web browser preview or archiving."""
        html_content = generate_email_html(jobs)
        today_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = REPORT_DIR / f"job_report_{today_str}.html"
        latest_file = REPORT_DIR / "latest_report.html"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        with open(latest_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Report saved locally: {report_file}")
        return latest_file

    def send_email(self, jobs: List[JobItem]) -> bool:
        """Sends the daily email report to the recipient."""
        local_report = self.save_local_report(jobs)

        smtp_user = self.config.get("smtp_user", "").strip()
        smtp_password = self.config.get("smtp_password", "").strip().replace(" ", "")
        recipient = self.config.get("recipient_email", "").strip()
        smtp_server = self.config.get("smtp_server", "smtp.gmail.com").strip()
        smtp_port = int(self.config.get("smtp_port", 587))

        if not smtp_user or not smtp_password or not recipient:
            logger.warning(
                "SMTP 설정(이메일 계정/비밀번호/수신자)이 아직 .env에 입력되지 않았습니다. "
                f"로컬 리포트 파일 생성 완료: {local_report}"
            )
            return False

        today_date = datetime.now().strftime("%m월 %d일")
        subject = f"[채용 알림] {today_date} 10년차 웹/앱 기획 PM 맞춤 신규 공고 {len(jobs)}건"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.config.get('sender_name', 'AI 커리어 비서')} <{smtp_user}>"
        msg["To"] = recipient

        html_body = generate_email_html(jobs)
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            context = ssl.create_default_context()
            if smtp_port == 465:
                # SSL
                with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                    server.login(smtp_user, smtp_password)
                    server.sendmail(smtp_user, recipient, msg.as_string())
            else:
                # STARTTLS (587)
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(smtp_user, smtp_password)
                    server.sendmail(smtp_user, recipient, msg.as_string())

            logger.info(f"Email sent successfully to {recipient} with {len(jobs)} jobs.")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
