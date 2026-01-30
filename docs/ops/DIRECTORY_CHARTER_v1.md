Final Round Plan v1 (피드백 반영)
Round 0 — SSoT Pack v1 Freeze + “근거 단일화 선언” (즉시)

해결할 문제

과도기 혼란(옛 문서/새 문서 동시 참조) 방지

“판단 근거가 어디냐”를 단번에 고정

작업

SSoT Pack v1(5문서) 목록 확정 + 링크 고정(문서 1개에 선언)

선언문(한 줄): “이제부터 모든 판단 근거는 SSoT Pack v1에 있다.” 를

루트 README 또는 ops 상위 문서(에이전트가 제일 먼저 보는 문서)에 최상단에 배치

(가능하면) .cursorrules 같은 에이전트 가이드에도 동일 문구 1줄 삽입

왜 먼저?

Round 1~4 동안 파일이 이동/스탬프/스텁 처리되며 혼란이 생길 수 있으니,
“근거 단일화”를 정리 시작 전에 강제해야 함.

산출물

docs/ssot/SSOT_PACK_v1.md (또는 동급의 선언 문서 1개)

README/가이드 상단 1줄 선언(근거 단일화)

Round 1 — Directory Charter v1 + “Sanctuary(성역) 금지 구역” 잠금

해결할 문제

폴더 중복/무규칙 생성으로 인한 구조 오염

에이전트가 실수로 핵심 계약/코어를 오염시키는 문제

작업

Directory Charter v1 문서에 다음을 “규칙”으로 명시:

허용 top-level 디렉토리 목록

각 디렉토리 목적(contracts/docs/modules/tools/exports/verification 등)

새 폴더 생성 금지(예외는 Charter 개정만)

Sanctuary(에이전트 전용 금지 구역) 명시
예: contracts/, core/(존재 시), docs/ssot/(SSoT Pack) 등

원칙: “에이전트는 Sanctuary에 신규 파일 생성/대량 편집/이동 금지”

예외: 인간이 명시적으로 ‘Sanctuary 변경 작업’을 지시한 경우만

왜 여기서?

레거시 이동을 시작하기 전에 “이제부터 폴더는 이렇게만 쓴다”를 박아야
opus가 멋대로 새 폴더를 만들지 못함.

산출물

docs/ops/DIRECTORY_CHARTER_v1.md (단일 정본)

Round 2 — Reference Inventory(참조 인벤토리) + 분류표 생성

해결할 문제

옮겼더니 링크 깨짐/암묵적 참조 깨짐

작업

파일을 facts-only로 3분류:

KEEP: SSoT/운영 필수

SAFE-MOVE: inbound reference 0

NEEDS-STUB: 참조 있음(호환 레이어 필요)

“어디에서 참조되는지” 근거를 간단히 기록(파일명/라인 수준까지는 선택)

왜 이 순서?

이동은 되돌리기 비용이 큼 → 먼저 ‘사실’을 확보해야 함.

산출물

docs/ops/legacy/REFERENCE_INVENTORY_v1.md (또는 csv/md 표)

Round 3 — Legacy Move v1 (SAFE-MOVE만 git mv) + LEGACY_INDEX “계보(Lineage)” 포함

해결할 문제

레거시 문서가 흩어져 에이전트가 잘못 근거로 삼는 문제

작업

SAFE-MOVE만 git mv로 docs/legacy/...로 이동

문서 상단 STATUS: LEGACY 스탬프(헤더 최상단, 크게)

docs/legacy/LEGACY_INDEX.md 생성 및 1줄 매핑 추가(피드백 #2 반영)

LEGACY_INDEX 1줄 포맷(예시)

old_path → new_ssot_doc (replaced_by: <SSoT doc id/section>) | reason: <짧게>

핵심은 “이 문서가 무엇으로 대체되었는지”를 한 줄로만 남기는 것

왜 SAFE부터?

참조 0만 옮기면 깨짐 리스크가 거의 없음.

산출물

docs/legacy/LEGACY_INDEX.md (계보 매핑 포함)

Round 4 — Stub & Redirect(NEEDS-STUB 처리)로 과도기 안정화

해결할 문제

참조가 남아있는 문서 이동 시 링크/경로 깨짐

과도기 혼란 방지(옛 경로를 열었을 때 새 근거로 유도)

작업

NEEDS-STUB 파일은:

원위치에 stub만 남김(STATUS: LEGACY + “대체 문서 링크/경로”)

본문은 legacy로 이동하거나(원칙), 남길 경우에도 상단에 강한 스탬프+대체 링크

stub는 10~20줄 내로 제한(추론 여지 제거)

왜 이 단계에서?

SAFE 이동이 끝난 뒤에 참조 있는 것만 처리해야 범위가 통제됨.

Round 5 — Ops/Dashboard Rebind (SSoT Pack v1 기반 재결선)

해결할 문제

ops/대시보드/계약 문서가 예전 문서를 근거로 잡는 문제

작업

대시보드/ops 문서에서 “근거 링크”를 전부 SSoT Pack v1로 재결선

중복 서술 제거: ops는 “링크 + step/DoD/evidence + unlock facts”만 유지

(선택) Charter 위반 탐지 규칙을 guard/체크리스트에 추가해 재발 방지

왜 마지막?

경로 이동/스텁 처리가 끝나야 참조 경로가 안정화됨.