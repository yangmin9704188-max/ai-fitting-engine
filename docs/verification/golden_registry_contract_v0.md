# Golden Registry Contract v0

## Purpose

Golden Registry는 NPZ 파일의 족보를 추적하기 위한 facts-only 기록입니다.
**기록은 하되 판정하지 않습니다.**

## File Location

- `docs/verification/golden_registry.json`

## Schema

```json
{
  "schema_version": "golden_registry@1",
  "updated_at": "ISO timestamp",
  "entries": [
    {
      "npz_path": "relative path",
      "npz_path_abs": "absolute path",
      "npz_sha256": "hash (optional, small files only)",
      "npz_mtime": "timestamp",
      "npz_size_bytes": "size",
      "schema_version": "from NPZ meta",
      "meta_unit": "from NPZ meta",
      "source_path_abs": "source file path",
      "generator_script": "script path",
      "generator_commit": "git commit hash",
      "notes": ""
    }
  ]
}
```

## Upsert 규칙

- **중복 방지 키**: `npz_path` 또는 `npz_path_abs`
- 같은 `npz_path`가 있으면 갱신(upsert), 없으면 append
- Atomic write (임시파일 -> rename)

## SHA256 계산 규칙

- 기본 OFF 또는 작은 파일만 계산 (예: <= 50MB)
- 큰 파일은 `npz_sha256: null`로 기록
- 성능을 위해 선택적으로만 계산

## Baseline 연결 (선택)

- round_registry의 baseline.run_dir에서 참조한 npz가 있으면
- notes에 "used_as_baseline_by: <lane>" 정도 기록 가능
- **판정 금지**: 단순 사실 기록만

## Notes

- 모든 파일 write는 atomic하게 구현
- 실패 시 예외로 죽지 말고 warnings 출력 후 계속
- git이 없는 환경에서는 generator_commit을 null로 처리
