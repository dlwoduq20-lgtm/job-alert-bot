# 🎯 10년 차 웹/앱 기획 PM 맞춤 채용 알림 봇 (Daily Job Alert Bot)

> **잡코리아, 사람인, 원티드, 리멤버, 링크드인** 5대 취업포털에서 매일 최신 채용정보를 자동 수집·분석하여, **매일 아침 9시 이메일**로 맞춤 리포트를 발송하는 자동화 시스템입니다.

---

## 📌 주요 특징

1. **5대 채용 플랫폼 실시간 자동 탐색**
   - **원티드 (Wanted)**: IT/스타트업 중심 포지션 및 리워드 채용
   - **사람인 (Saramin)**: 국내 대표 대기업·중견·IT 채용
   - **잡코리아 (JobKorea)**: 대규모 기업 및 전문 플랫폼 공고
   - **리멤버 (Remember)**: 경력직/시니어/리드 스카우트 포지션
   - **링크드인 (LinkedIn)**: 글로벌 테크 및 시니어 Product Manager 포지션

2. **사용자 맞춤형 정밀 스코어링 (0~100점 채점)**
   - **경력 10년차 적합도**: 7~15년차, 시니어/팀장/리드 PM 포지션 가산점 (주니어/신입 제외)
   - **AI 활용 역량**: 생성형 AI, LLM, 프롬프트 엔지니어링, 에이전트, 업무 자동화 우대 공고 가산점
   - **구글 애널리틱스 (GA4) & 데이터 역량**: GA4 지표 설계, 이벤트 트래킹, 퍼널 분석, Amplitude, SQL 등 데이터 드리븐 기획 요건 매칭
   - **전주기 PM 역량**: 신규 구축(0 to 1), 대규모 리뉴얼, 운영 및 유지보수, 백로그/스프린트 관리 요건 매칭

3. **스마트 중복 필터링 (SQLite DB)**
   - 이미 수신한 공고는 SQLite 데이터베이스(`database/job_history.db`)에 자동 기록되어, **매일 아침 새로 올라온 신규 공고만 엄선**하여 발송합니다.

4. **모바일 반응형 이메일 템플릿 & 로컬 리포트**
   - 메일함에서 한눈에 보기 편한 카드형 디자인
   - 플랫폼 뱃지, 적합도 점수(Badge), 매칭 태그(#AI활용, #GA4/데이터분석 등), 원문 바로가기 버튼 제공

---

## 📁 프로젝트 구조

```
job_alert_system/
├── config.py                 # 검색 키워드, 가중치, 이메일 설정
├── scrapers/                 # 5대 플랫폼별 크롤러 모듈
│   ├── wanted.py             # 원티드
│   ├── saramin.py            # 사람인
│   ├── jobkorea.py           # 잡코리아
│   ├── remember.py           # 리멤버
│   └── linkedin.py           # 링크드인
├── analyzer/
│   └── scorer.py             # 10년차 PM 맞춤형 점수 산출 및 필터링 엔진
├── database/
│   └── db.py                 # SQLite 중복 방지 및 이력 관리
├── mailer/
│   ├── template.py           # 고화질 모던 HTML 이메일 템플릿
│   └── sender.py             # SMTP 이메일 발송 및 로컬 리포트 저장기
├── scheduler/
│   ├── run_daily.py          # 매일 아침 9시 실행용 러너
│   └── setup_windows_task.ps1# 윈도우 작업 스케줄러 자동 등록 스크립트
├── reports/                  # 생성된 HTML 리포트 보관함
├── main.py                   # 메인 실행 CLI 컨트롤러
├── .env                      # 이메일 계정 환경변수 설정
└── README.md                 # 안내 문서
```

---

## 🚀 빠른 시작 가이드

### 1. 이메일 전송 설정 (`.env`)
프로젝트 폴더 내 `.env` 파일을 메모장이나 에디터로 열어 본인의 메일 정보를 입력합니다.

#### 네이버 메일 사용 시 (추천):
1. 네이버 메일 웹 접속 → 좌측 하단 [환경설정(톱니바퀴)] → [POP3/IMAP 설정]
2. **IMAP/SMTP 설정** 탭에서 **'사용함'**으로 변경 후 저장
3. `.env` 파일에 아래와 같이 입력:
```ini
SMTP_SERVER=smtp.naver.com
SMTP_PORT=587
SMTP_USER=본인아이디@naver.com
SMTP_PASSWORD=본인네이버비밀번호
RECIPIENT_EMAIL=결과를받을이메일주소@naver.com
```

#### 구글 Gmail 사용 시:
1. 구글 계정 관리 → [보안] → **'2단계 인증'** 활성화
2. [보안] → [2단계 인증] 최하단의 **'앱 비밀번호'** 생성 (16자리 생성됨)
3. `.env` 파일에 아래와 같이 입력:
```ini
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=본인구글계정@gmail.com
SMTP_PASSWORD=생성된16자리앱비밀번호
RECIPIENT_EMAIL=결과를받을이메일주소
```

---

### 2. 수집 결과 미리보기 (브라우저 확인)
이메일 계정을 설정하기 전이라도, 지금 당장 브라우저에서 크롤링 결과와 이메일 디자인을 직접 확인할 수 있습니다:

```bash
python main.py --preview --force
```
*실행 즉시 5개 사이트를 탐색하고 최신 리포트 웹페이지가 기본 브라우저에 바로 열립니다.*

---

### 3. 매일 아침 9시 자동 실행 등록 (Windows)

Windows 내장 **작업 스케줄러(Task Scheduler)**를 통해 PC가 켜져 있을 때 매일 오전 09:00에 자동으로 실행되도록 등록할 수 있습니다.

PowerShell을 열고 프로젝트 폴더에서 아래 명령어를 실행하세요:

```powershell
powershell -ExecutionPolicy Bypass -File .\scheduler\setup_windows_task.ps1
```

- 등록이 완료되면 매일 아침 9시마다 자동으로 5대 포털을 크롤링하여 이메일이 발송됩니다.
- 등록된 스케줄을 확인하거나 즉시 테스트해보고 싶다면:
  ```powershell
  Start-ScheduledTask -TaskName "DailyJobAlertBot"
  ```
- 스케줄러 등록을 삭제하려면:
  ```powershell
  Unregister-ScheduledTask -TaskName "DailyJobAlertBot" -Confirm:$false
  ```

---

### 4. CLI 주요 명령어

- **일반 실행 (신규 공고만 탐색 및 발송)**:
  ```bash
  python main.py
  ```
- **전체 공고 강제 리포트 (중복 필터 무시)**:
  ```bash
  python main.py --force
  ```
- **수집 및 발송 통계 확인**:
  ```bash
  python main.py --stats
  ```
- **최소 적합도 점수 조정 (예: 50점 이상만)**:
  ```bash
  python main.py --score 50
  ```
