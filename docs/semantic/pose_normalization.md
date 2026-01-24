# Pose Normalization (Semantic v0)

## 1. Baseline Pose (Default)
- Standing, upright, neutral spine
- Feet: 편안한 간격(과도한 벌림/모음 금지), 체중 균등
- Arms: 자연스럽게 내림(상체 측정 방해 최소)
- Head/Neck: 중립
- Breathing: 자연 호흡(과흡기/과호기 금지)
- Shoulder/Scapula Neutrality: 견갑 중립(과도한 말림/후인 금지) 상태가 SHOULDER_WIDTH 등 폭 계열의 의미 보존 전제, 위반 시 warning. 자동 보정 금지, warning만 허용.

## 2. Prohibited Conditions (Semantic-level)
- 두꺼운 의복/보정속옷/강한 압박
- 팔을 들거나 크게 벌린 자세로 상체 둘레/폭 측정
- 무릎 굴곡 상태에서 KNEE_HEIGHT/둘레 측정(명시적 목적 없으면 금지)

## 3. Notes
- 본 문서는 “어떤 자세가 동일 의미를 보장하는가”만 정의한다.
- Geometry는 본 자세 원칙을 만족시키는지 여부를 warning으로 기록할 수 있으나, 자동 보정은 금지한다. 
