import yaml
import sys
import argparse
import json
from pathlib import Path

def validate(require_manifest=False):
    obs_path = Path("logs/observation.md")
    if not obs_path.exists():
        print("[FAIL] logs/observation.md 파일이 없습니다.")
        sys.exit(1)

    content = obs_path.read_text(encoding="utf-8")
    
    # YAML 블록 추출 (```yaml ... ``` 사이의 내용)
    try:
        if "```yaml" not in content:
            raise ValueError("YAML 블록(```yaml)을 찾을 수 없습니다.")
        
        yaml_part = content.split("```yaml")[1].split("```")[0]
        data = yaml.safe_load(yaml_part)
        
        # 필수 필드 체크
        required_fields = ["policy_name", "run_id", "state_intent"]
        for field in required_fields:
            if not data.get(field):
                print(f"[FAIL] 필수 항목이 비어있습니다: {field}")
                sys.exit(1)
        
        # manifest.json 체크 (--require-manifest 옵션)
        if require_manifest:
            artifacts = data.get("artifacts", {})
            run_dir = artifacts.get("run_dir", "")
            if not run_dir:
                print("[FAIL] artifacts.run_dir이 비어있습니다.")
                sys.exit(1)
            
            manifest_path = Path(run_dir) / "manifest.json"
            if not manifest_path.exists():
                print(f"[FAIL] manifest.json 파일이 없습니다: {manifest_path}")
                sys.exit(1)
            
            # manifest.json 내용 검증
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                
                if "run_id" not in manifest:
                    print("[FAIL] manifest.json에 run_id 필드가 없습니다.")
                    sys.exit(1)
                
                manifest_run_id = manifest.get("run_id", "")
                yaml_run_id = data.get("run_id", "")
                
                if manifest_run_id != yaml_run_id:
                    print(f"[FAIL] observation.md의 run_id({yaml_run_id})와 manifest.json의 run_id({manifest_run_id})가 일치하지 않습니다.")
                    sys.exit(1)
                
                if "artifacts" not in manifest:
                    print("[FAIL] manifest.json에 artifacts 필드가 없습니다.")
                    sys.exit(1)
                
                print(f"[PASS] manifest.json 검증 통과: {manifest_path}")
            except json.JSONDecodeError as e:
                print(f"[FAIL] manifest.json 파싱 오류: {e}")
                sys.exit(1)
                
        print("[PASS] observation.md 형식이 올바릅니다!")
        
    except Exception as e:
        print(f"[FAIL] 검증 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate observation.md format")
    parser.add_argument("--require-manifest", action="store_true", 
                        help="Also validate that manifest.json exists and matches")
    args = parser.parse_args()
    validate(require_manifest=args.require_manifest)