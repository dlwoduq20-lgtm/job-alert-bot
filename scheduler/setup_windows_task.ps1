# ==============================================================================
# Windows 작업 스케줄러 등록 스크립트 (매일 아침 9시 자동 실행)
# ==============================================================================

$TaskName = "DailyJobAlertBot"
$BatPath = "C:\Users\dlwod\.gemini\antigravity\scratch\job_alert_system\scheduler\run_daily.bat"

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host " 🤖 10년 차 웹/앱 PM 채용 알림 봇 - 매일 9시 스케줄러 등록" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "실행 배치파일: $BatPath" -ForegroundColor Gray
Write-Host "실행 주기: 매일 오전 09:00:00" -ForegroundColor Gray
Write-Host ""

# schtasks 명령어로 등록
schtasks /create /tn $TaskName /tr $BatPath /sc daily /st 09:00 /f | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 작업 스케줄러 등록이 성공적으로 완료되었습니다!" -ForegroundColor Green
    Write-Host "매일 아침 9시에 자동으로 5대 채용사이트(잡코리아/사람인/원티드/리멤버/링크드인)를 탐색하여 이메일로 전송합니다." -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 수동으로 지금 즉시 테스트 실행해보려면:" -ForegroundColor Cyan
    Write-Host "   schtasks /run /tn `"$TaskName`"" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 등록 해제(삭제)하려면:" -ForegroundColor Cyan
    Write-Host "   schtasks /delete /tn `"$TaskName`" /f" -ForegroundColor White
} else {
    Write-Host "❌ 스케줄러 등록 중 오류가 발생했습니다." -ForegroundColor Red
}
