from datetime import datetime
from typing import List
from scrapers.base_scraper import JobItem

PLATFORM_COLORS = {
    "원티드": "#258BF7",
    "사람인": "#FF6B00",
    "잡코리아": "#0056B3",
    "리멤버": "#5E4BE2",
    "링크드인": "#0A66C2",
}

def generate_email_html(jobs: List[JobItem], total_scanned: int = 0) -> str:
    now_str = datetime.now().strftime("%Y년 %m월 %d일 (%a)")
    
    # Platform counts
    platform_counts = {}
    for j in jobs:
        platform_counts[j.platform] = platform_counts.get(j.platform, 0) + 1

    stats_badges = "".join([
        f'<span style="display:inline-block; margin-right:8px; margin-bottom:6px; padding:4px 10px; border-radius:12px; font-size:12px; font-weight:600; background-color:{PLATFORM_COLORS.get(p, "#4b5563")}15; color:{PLATFORM_COLORS.get(p, "#1f2937")}; border:1px solid {PLATFORM_COLORS.get(p, "#9ca3af")}40;">{p} {c}건</span>'
        for p, c in platform_counts.items()
    ])

    job_cards = ""
    for idx, job in enumerate(jobs, 1):
        p_color = PLATFORM_COLORS.get(job.platform, "#2563eb")
        
        # Score color
        if job.score >= 85:
            score_bg = "#dcfce7"
            score_text = "#15803d"
        elif job.score >= 60:
            score_bg = "#e0f2fe"
            score_text = "#0369a1"
        else:
            score_bg = "#f3f4f6"
            score_text = "#4b5563"

        # Keywords tags
        tags_html = ""
        for tag in job.matched_keywords:
            tags_html += f'<span style="display:inline-block; margin-right:6px; margin-bottom:4px; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:600; background-color:#f1f5f9; color:#334155;">#{tag}</span>'

        job_cards += f"""
        <div style="background:#ffffff; border-radius:12px; border:1px solid #e2e8f0; padding:20px; margin-bottom:16px; box-shadow:0 2px 4px rgba(0,0,0,0.02);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
                <div>
                    <span style="display:inline-block; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:bold; color:#ffffff; background-color:{p_color}; margin-right:8px;">
                        {job.platform}
                    </span>
                    <span style="font-size:14px; font-weight:bold; color:#475569;">
                        {job.company}
                    </span>
                </div>
                <div style="text-align:right;">
                    <span style="display:inline-block; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:bold; background-color:{score_bg}; color:{score_text};">
                        적합도 {job.score}점
                    </span>
                </div>
            </div>

            <h3 style="margin:4px 0 10px 0; font-size:17px; font-weight:700; line-height:1.4;">
                <a href="{job.url}" target="_blank" style="color:#0f172a; text-decoration:none;">
                    {job.title}
                </a>
            </h3>

            <div style="margin-bottom:12px; font-size:13px; color:#64748b; line-height:1.5;">
                <span style="margin-right:12px;">📍 <strong>위치:</strong> {job.location}</span>
                <span style="margin-right:12px;">💼 <strong>요건:</strong> {job.experience}</span>
            </div>

            {f'<div style="margin-bottom:10px;">{tags_html}</div>' if tags_html else ''}

            {f'<div style="font-size:12px; color:#475569; background:#f8fafc; padding:8px 12px; border-radius:6px; margin-bottom:12px; border-left:3px solid {p_color};">{job.match_reason}</div>' if job.match_reason else ''}

            <div style="text-align:right; margin-top:10px;">
                <a href="{job.url}" target="_blank" style="display:inline-block; padding:8px 16px; background-color:#0f172a; color:#ffffff; font-size:13px; font-weight:600; text-decoration:none; border-radius:6px;">
                    채용 공고 바로보기 &rarr;
                </a>
            </div>
        </div>
        """

    if not jobs:
        job_cards = """
        <div style="background:#ffffff; border-radius:12px; border:1px solid #e2e8f0; padding:30px; text-align:center; color:#64748b;">
            <p style="font-size:16px; font-weight:bold;">새로운 맞춤 공고가 없습니다.</p>
            <p style="font-size:13px;">오늘 신규 등록된 공고 중 10년차 웹/앱 PM 조건에 부합하는 새로운 공고가 없습니다. 내일 아침 다시 탐색합니다.</p>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>오늘의 맞춤 채용 브리핑</title>
</head>
<body style="margin:0; padding:0; background-color:#f1f5f9; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#0f172a;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#f1f5f9; padding:24px 0;">
        <tr>
            <td align="center">
                <table width="640" border="0" cellspacing="0" cellpadding="0" style="max-width:640px; width:100%; margin:0 auto;">
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding:24px 20px; background:linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius:16px 16px 0 0; color:#ffffff;">
                            <div style="font-size:12px; font-weight:700; letter-spacing:1px; color:#38bdf8; text-transform:uppercase; margin-bottom:4px;">
                                DAILY PM RECRUIT REPORT
                            </div>
                            <h1 style="margin:0 0 8px 0; font-size:22px; font-weight:800; line-height:1.3;">
                                🎯 10년 차 웹/앱 기획 PM 맞춤 채용 브리핑
                            </h1>
                            <p style="margin:0; font-size:13px; color:#94a3b8;">
                                {now_str} 기준 • <strong>서울·경기권 인하우스 포지션</strong> (에이전시/SI 제외)
                            </p>
                        </td>
                    </tr>

                    <!-- Summary Box -->
                    <tr>
                        <td style="background-color:#ffffff; padding:18px 20px; border-bottom:1px solid #e2e8f0;">
                            <div style="font-size:13px; color:#334155; margin-bottom:10px; line-height:1.5;">
                                💡 <strong>5대 채용 플랫폼</strong>에서 <strong>에이전시/SI 및 비수도권을 제외</strong>하고, 총 <strong>{len(jobs)}건</strong>의 서울·경기권 인하우스 맞춤 신규 공고를 엄선했습니다.
                            </div>
                            <div>{stats_badges}</div>
                        </td>
                    </tr>

                    <!-- Job List -->
                    <tr>
                        <td style="background-color:#f8fafc; padding:20px; border-left:1px solid #e2e8f0; border-right:1px solid #e2e8f0;">
                            {job_cards}
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding:20px; text-align:center; font-size:12px; color:#94a3b8; background-color:#ffffff; border-radius:0 0 16px 16px; border:1px solid #e2e8f0; border-top:none;">
                            <p style="margin:0 0 6px 0;">본 메일은 설정된 검색 키워드 및 10년차 PM 프로필(서울/경기, 인하우스) 적합도 분석을 통해 매일 아침 9시에 자동 발송됩니다.</p>
                            <p style="margin:0; color:#cbd5e1;">Target: 10년차 웹/앱 PM (서울·경기 인하우스) | AI 활용 | GA4 데이터분석 | 신규구축 & 운영</p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return html
