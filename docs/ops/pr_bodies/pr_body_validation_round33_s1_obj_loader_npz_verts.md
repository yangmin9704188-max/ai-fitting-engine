# PR: Round33 - S1 OBJ Loader Fallback + Verts NPZ Evidence

## 목적

Round32에서 skip_reasons.jsonl 불변식(records=200, has_mesh_path_true=5)을 달성했지만, proxy 5개 케이스가 여전히 load_failed로 처리되고 postprocess에서 NPZ_PATH_NOT_FOUND 또는 measurement-only npz로 SKIPPED가 발생했습니다.

이번 라운드는:
1. **proxy 5개 케이스가 반드시 Processed로 집계되도록** (Processed>=5)
2. **verts NPZ 증거를 생성하여** postprocess가 "measurement-only npz" 또는 "NPZ_PATH_NOT_FOUND"로만 끝나지 않도록 함

## 변경 사항

### 1. `verification/runners/run_geo_v0_s1_facts.py`

#### OBJ 로더 fallback 개선
- `load_obj_with_trimesh`: scale_warning 반환 추가
- `load_obj_with_fallback_parser`: MTL/재질 완전 무시, encoding='utf-8', errors='ignore' 안전 처리
- `load_verts_from_path_with_info`: 반환값에 scale_warning 추가 `(verts, loader_name, faces, scale_warning)`

#### 단위 canonicalization (mm -> m)
- max_abs > 10.0이면 mm로 추정하여 /1000 적용 (m로 canonicalize)
- `SCALE_ASSUMED_MM_TO_M` warning을 facts_summary/skip_reasons에 기록 (판정 금지, facts-only)

#### verts NPZ 생성
- proxy 5개 케이스의 로드 성공한 verts를 `{out_dir}/artifacts/verts_proxy.npz`로 저장
- NPZ 키: `verts` (float32), `case_id` (list), `meta_unit="m"`, `schema_version="s1_mesh_v0@1"`

#### facts_summary.json에 NPZ 경로 포함
- `meta_unit: "m"`
- `npz_has_verts: true`
- `npz_path`, `verts_npz_path`, `dataset_path`, `npz_path_abs` (다중 키로 postprocess 호환성 확보)

#### skip_reasons.jsonl 개선
- Type A: `manifest_path_is_null`
- Type B: `mesh_exists_false` (file_not_found)
- Type C: `npz_has_verts=False` (NPZ 관련, 이번 라운드에서는 미사용)
- Type D: `load_failed`

### 2. `tools/postprocess_round.py`

#### NPZ 경로 다중 키 지원
- 기존: `dataset_path` 또는 `npz_path_abs`만 검색
- 변경: `npz_path`, `verts_npz_path`, `dataset_path`, `npz_path_abs` 순서로 검색
- postprocess가 NPZ 경로를 찾을 수 있도록 보강

### 3. `docs/ops/INDEX.md`
- Round33 엔트리 추가

### 4. `reports/validation/INDEX.md`
- Round33 섹션 추가

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round33_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

## DoD Self-check (facts-only)

### 1. Processed >= 5 확인
```bash
# facts_summary.json에서 확인
cat verification/runs/facts/geo_v0_s1/round33_*/facts_summary.json | grep -o '"processed_cases":[0-9]*'
```

**예상 결과**: `"processed_cases":5` 이상

### 2. skip_reasons.jsonl에서 has_mesh_path_true == 5 확인
```bash
grep -c '"has_mesh_path":true' verification/runs/facts/geo_v0_s1/round33_*/artifacts/skip_reasons.jsonl
```

**예상 결과**: `5`

### 3. facts_summary.json: meta_unit == "m" 확인
```bash
cat verification/runs/facts/geo_v0_s1/round33_*/facts_summary.json | grep -o '"meta_unit":"m"'
```

**예상 결과**: `"meta_unit":"m"`

### 4. facts_summary.json: npz_has_verts == true 확인
```bash
cat verification/runs/facts/geo_v0_s1/round33_*/facts_summary.json | grep -o '"npz_has_verts":true'
```

**예상 결과**: `"npz_has_verts":true`

### 5. postprocess 출력에서 NPZ_PATH_NOT_FOUND 사라졌는지 확인
```bash
# postprocess 로그 또는 LINEAGE.md에서 확인
grep -i "NPZ_PATH_NOT_FOUND" verification/runs/facts/geo_v0_s1/round33_*/LINEAGE.md || echo "NPZ_PATH_NOT_FOUND not found (expected)"
```

**예상 결과**: NPZ_PATH_NOT_FOUND가 없거나, 최소한 proxy 케이스는 해당되지 않음

### 6. verts_proxy.npz 존재 확인
```bash
ls -la verification/runs/facts/geo_v0_s1/round33_*/artifacts/verts_proxy.npz
```

**예상 결과**: 파일 존재, 크기 > 0

### 7. visual proxy 실패 시에도 SKIPPED.txt에 구체 사유 확인
```bash
cat verification/runs/facts/geo_v0_s1/round33_*/artifacts/visual/SKIPPED.txt
```

**예상 결과**: 구체적인 사유가 기록됨 (best-effort)

### 8. skip_reasons.jsonl Type 구분 확인
```bash
# Type A/B/D 구분 확인
grep -o '"Type":"[^"]*"' verification/runs/facts/geo_v0_s1/round33_*/artifacts/skip_reasons.jsonl | sort | uniq -c
```

**예상 결과**: Type A (manifest_path_is_null), Type B (mesh_exists_false), Type D (load_failed) 구분됨

## 준수 사항

- ✅ PASS/FAIL 판정 금지 (facts-only)
- ✅ Semantic 재해석/단위 재논의 금지 (mm->m 변환은 관측 기반, warning만 기록)
- ✅ 측정 알고리즘 정답 튜닝 금지
- ✅ 대규모 리팩터링/폴더 이동/삭제(git rm) 금지
- ✅ verification/runs/** 커밋 금지
- ✅ 라운드 완료는 postprocess 마감까지
