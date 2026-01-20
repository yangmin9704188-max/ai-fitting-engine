Run 기록 가이드 (경량 운영용)

1\. Run이란 무엇인가



Run은 “한 번의 실제 실행 기록”이다.



Run의 목적은 다음 한 가지뿐이다.



언제, 어떤 조건으로 실행했는지



그 결과 무엇이 생성되었는지



를 남기는 것.



Run은 하지 않는 것



PASS / FAIL / HOLD 판단 ❌



정책 변경 제안 ❌



Gate 통과 여부 서술 ❌



실험 해석 ❌



판단과 해석은 Report의 역할이다.



2\. Run의 위치와 구조

기본 디렉토리 구조

runs/

└─ <policy\_key>/

&nbsp;  └─ <date>\_run\_<seq>/

&nbsp;     └─ run.md





예시:



runs/

└─ apose\_normalization/

&nbsp;  └─ 2026-01-16\_run\_001/

&nbsp;     └─ run.md



운영 규칙



Run 1개 = 디렉토리 1개



Run 디렉토리는 생성 후 수정하지 않는다



새로운 실행은 항상 새 Run 디렉토리를 만든다



3\. 필수 파일 (최소 단위)

run.md (필수)



모든 Run에는 반드시 run.md가 존재해야 한다.

다른 파일은 없어도 된다.



run.md 최소 템플릿

---

run\_id: "<policy\_key>-<YYYY-MM-DD>-run-XXX"

policy\_name: "<Policy Name>"

policy\_version: "vX.Y"

execution\_date: "YYYY-MM-DD"

status: "completed | failed | aborted"

artifacts\_path: "<outputs or result path>"

---



\# Run: <Policy Name> <Policy Version> — <run\_id>



\## 실행 목적

\- (이 실행을 왜 했는지 한 줄)



\## 입력 요약

\- (입력 데이터/조건 요약 한 줄)



\## 결과 요약

\- (무슨 결과물이 생성되었는지 한 줄)



\## 비고

\- (특이사항이 있을 때만)



4\. 선택 파일 (권장, 하지만 필수 아님)



아래 파일들은 초기에는 없어도 된다.

필요해질 때만 추가한다.



config.json (선택)



실행 시 사용한 주요 설정 스냅샷



dtype, device, 주요 플래그 정도면 충분



inputs.json (선택)



입력 데이터 유형



샘플 수



데이터 출처 요약



logs.txt (선택)



콘솔 출력 덤프



에러/경고 추적용



⚠️ 자동 생성은 강제하지 않는다.

Run이 5~10개 이상 쌓여 작성 비용이 부담될 때만 자동화를 고려한다.



5\. Run과 다른 문서의 관계

Run ↔ Report



Run은 사실 기록



Report는 판단



Report는 여러 Run을 참조할 수 있다



Report에서 Run을 참조할 때 예시:



본 리포트는 다음 Run 결과를 근거로 작성되었다.

\- runs/apose\_normalization/2026-01-16\_run\_001



Run ↔ Spec



Spec은 “어떻게 구현되어야 하는가”



Run은 “그 구현이 실제로 실행된 기록”



6\. Run 작성 판단 체크리스트



아래 질문에 답할 수 있으면 충분하다.



이 실행은 무엇을 했는가?



그 결과 무슨 파일이 생성되었는가?



나중에 봐도 혼동될 여지가 없는가?



3개 모두 YES면 Run으로 합격이다.



7\. 지금 단계에서의 운영 원칙 (중요)



Run은 미래 기록이다

→ 과거 실행을 억지로 복구하지 않는다



Run을 DB에 넣지 않는다

→ Git이 정본



완벽하게 쓰려 하지 않는다

→ “존재하는 기록”이 “없는 완벽함”보다 낫다



8\. 요약



Run의 최소 단위는 run.md 하나



판단은 Report에서만 한다



자동화는 나중에



단순함을 유지한다

