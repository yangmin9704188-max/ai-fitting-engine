# SizeKorea Measurement Methods v0 (Evidence)

본 문서는 SizeKorea 측정 방법 정의를 요약한 Evidence 문서입니다.

---

## 0. 기본 입력값 (Input/Meta)

### HEIGHT_M
측정 정의: 바닥면에서 머리마루점까지의 수직거리

측정 방법: 피측정자의 옆에서 수직자를 뒤에 놓고 가로자의 끝이 머리 마루점에 닿게 한 후, 바닥면에서 이 점까지의 수직거리를 측정한다. 이때 피측정자의 머리카락을 누르면서 측정한다.

- Pose Constraints: standing; vertical alignment
- Allowed DoF: vertical_distance=required; auto_pose_correction=forbidden; pose_violation=warn_only

### WEIGHT_KG
측정 정의: 몸의 무게

측정 방법: 저울 위에서 양발에 몸무게를 나누어 싣고 선 후 눈금을 읽는다.

- Pose Constraints: standing; weight evenly distributed
- Allowed DoF: (N/A - weight measurement)

---

## 1. 핵심 둘레 (Circumference)

### NECK_CIRC_M
측정 정의: 방패연골아래점을 지나는 둘레

기준점(랜드마크): 방패연골아래점

측정 방법: 피측정자의 앞에서 줄자로 방패연골아래점에서 목의 축에 직각으로 지나는 둘레를 측정한다.

- Pose Constraints: standing; tape horizontal; breath_state=neutral_mid
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; breath_state=neutral_mid; pose_violation=warn_only; substitution=forbidden

### BUST_CIRC_M
측정 정의: 젖꼭지점을 지나는 수평둘레

기준점(랜드마크): 젖꼭지점

측정 방법: 피측정자의 앞에서 줄자로 젖꼭지점을 지나는 둘레를 측정한다. 이때 줄자는 수평을 유지하도록 주의하여야 한다. 자연스러운 숨쉬기의 중간 호흡일 때 눈금을 읽는다.

- Pose Constraints: standing; tape horizontal; breath_state=neutral_mid
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; breath_state=neutral_mid; pose_violation=warn_only; substitution=forbidden

### UNDERBUST_CIRC_M
측정 정의: 젖가슴아래점을 지나는 수평둘레

기준점(랜드마크): 젖가슴아래점

측정 방법: 피측정자의 앞에서 줄자로 젖가슴아래점 높이 수준에서의 둘레를 측정한다. 이때 줄자는 수평을 유지하여야 하고 특히 등 쪽에서 줄자의 수평을 확인한다. 자연스러운 숨쉬기의 중간 호흡일 때 눈금을 읽는다.

- Pose Constraints: standing; tape horizontal; breath_state=neutral_mid
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; breath_state=neutral_mid; pose_violation=warn_only; substitution=forbidden

### WAIST_CIRC_M
측정 정의: 허리옆점을 지나는 수평둘레

기준점(랜드마크): 허리옆점

측정 방법: 피측정자의 앞에서 줄자로 허리옆점을 지나는 둘레를 측정한다. 자연스러운 숨쉬기의 중간 호흡일 때 눈금을 읽는다.

- Pose Constraints: standing; tape horizontal; breath_state=neutral_mid
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; breath_state=neutral_mid; pose_violation=warn_only; substitution=forbidden

### NAVEL_WAIST_CIRC_M
측정 정의: 배꼽점을 지나는 수평둘레

기준점(랜드마크): 배꼽점

측정 방법: 피측정자의 앞에서 줄자로 배꼽점을 지나는 둘레를 측정한다. 자연스러운 숨쉬기의 중간 호흡일 때 눈금을 읽는다.

- Pose Constraints: standing; tape horizontal; breath_state=neutral_mid
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; breath_state=neutral_mid; pose_violation=warn_only; substitution=forbidden

### ABDOMEN_CIRC_M
측정 정의: 배돌출점 높이에서의 몸통의 수평둘레

기준점(랜드마크): 배돌출점

측정 방법: 피측정자의 앞에서 줄자로 배돌출점을 지나는 수평둘레를 측정한다. 자연스러운 숨쉬기의 중간 호흡일 때 눈금을 읽는다.

- Pose Constraints: standing; tape horizontal; breath_state=neutral_mid
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; breath_state=neutral_mid; pose_violation=warn_only; substitution=forbidden

### HIP_CIRC_M
측정 정의: 엉덩이돌출점을 지나는 수평둘레

기준점(랜드마크): 엉덩이돌출점

측정 방법: 피측정자의 오른쪽앞옆에서 엉덩이돌출점수준에서 둘레를 측정한다.

- Pose Constraints: standing; tape horizontal
- Allowed DoF: fixed_height=required; band_scan=forbidden; min/max_search=forbidden; pose_violation=warn_only; substitution=forbidden

### THIGH_CIRC_M
측정 정의: 볼기고랑점을 지나는 수평둘레

기준점(랜드마크): 볼기고랑점

측정 방법: 피측정자의 옆에서 줄자로 볼기고랑점을 지나는 오른쪽다리의 수평둘레를 측정한다.

- Pose Constraints: standing; right-side measurement
- Allowed DoF: canonical_side=right; symmetry_avg=forbidden; fixed_height=required; band_scan=forbidden; pose_violation=warn_only

### MIN_CALF_CIRC_M
측정 정의: 종아리아래점을 지나는 수평둘레

기준점(랜드마크): 종아리아래점

측정 방법: 피측정자의 오른쪽 앞에서 줄자로 종아리아래점을 지나는 수평둘레를 측정한다.

- Pose Constraints: standing; right-side measurement
- Allowed DoF: canonical_side=right; symmetry_avg=forbidden; fixed_height=required; band_scan=forbidden; pose_violation=warn_only

---

## 2. 핵심 너비 (Width)

### CHEST_WIDTH_M
측정 정의: 겨드랑점수준에서의 몸통 좌우 수평거리

기준점(랜드마크): 겨드랑점수준

측정 방법: 피측정자의 앞에서 양쪽 겨드랑점 수준에 가로자를 몸통의 양 옆면에 깊이 넣은 후 팔을 자연스럽게 내리게 하여 수평 거리를 측정한다. 자연스러운 숨쉬기의 중간 호흡일 때 눈금을 읽는다.

- Pose Constraints: breath_state=neutral_mid; arms_down_required
- Allowed DoF: fixed_cross_section=required; linear_distance=required; plane_clamp=proxy_only(with_provenance); scan=forbidden; pose_violation=warn_only

### WAIST_WIDTH_M
측정 정의: 허리옆점수준에서의 몸통좌우 수평거리

기준점(랜드마크): 허리옆점수준

측정 방법: 피측정자의 앞에서 허리옆점수준에 가로자를 몸통의 양 옆 면에 깊이 넣은 후 수평거리를 측정한다. 자연스러운 숨쉬기의 중간 호흡일 때 눈금을 읽는다.

- Pose Constraints: breath_state=neutral_mid
- Allowed DoF: fixed_cross_section=required; linear_distance=required; plane_clamp=proxy_only(with_provenance); scan=forbidden; pose_violation=warn_only

### HIP_WIDTH_M
측정 정의: 양쪽 엉덩이돌출점수준에서의 몸통 좌우 수평거리

기준점(랜드마크): 엉덩이돌출점수준

측정 방법: 피측정자의 뒤에서 큰수평자로 피측정자의 엉덩이돌출점수준에서의 좌우 수평거리를 측정한다.

- Pose Constraints: standing
- Allowed DoF: fixed_cross_section=required; linear_distance=required; plane_clamp=proxy_only(with_provenance); scan=forbidden; pose_violation=warn_only

---

## 3. 핵심 두께 (Depth)

### CHEST_DEPTH_M
측정 정의: 겨드랑점수준에서의 몸통 앞뒤 최대 수평거리

기준점(랜드마크): 겨드랑점수준

측정 방법: 피측정자의 오른쪽 옆에서 큰수평자로 겨드랑점수준에서 가슴의 앞뒤 수평거리를 측정한다. 자연스러운 숨쉬기의 중간 호흡일 때 눈금을 읽는다.

- Pose Constraints: breath_state=neutral_mid
- Allowed DoF: fixed_cross_section=required; linear_distance=required; plane_clamp=proxy_only(with_provenance); scan=forbidden; pose_violation=warn_only

### WAIST_DEPTH_M
측정 정의: 허리점수준에서의 몸통 앞뒤 최대 수평거리

기준점(랜드마크): 허리점수준

측정 방법: 피측정자의 오른쪽 옆에서 큰수평자로 허리점수준에서의 앞뒤 최대 돌출위치의 수평거리를 측정한다. 자연스러운 숨쉬기의 중간 호흡일 때 눈금을 읽는다.

- Pose Constraints: breath_state=neutral_mid
- Allowed DoF: fixed_cross_section=required; linear_distance=required; plane_clamp=proxy_only(with_provenance); scan=forbidden; pose_violation=warn_only

### HIP_DEPTH_M
측정 정의: 엉덩이돌출점수준에서의 몸통 좌우 수평거리

기준점(랜드마크): 엉덩이돌출점수준

측정 방법: 얇은 아크릴판을 피측정자의 배돌출 부위에 대고, 피측정자의 옆에서 엉덩이돌출점수준의 좌우 수평거리를 측정한다.

- Pose Constraints: standing
- Allowed DoF: fixed_cross_section=required; linear_distance=required; plane_clamp=proxy_only(with_provenance); scan=forbidden; pose_violation=warn_only

---

## 4. 길이 및 높이 (Length & Height)

### CROTCH_HEIGHT_M
측정 정의: 바닥면에서 샅점까지의 수직거리

기준점(랜드마크): 샅점, 바닥면

측정 방법: 피측정자의 뒤에서 수직자를 뒤에 놓은 다음 가로자의 끝이 아크릴판의 위가장자리에 닿게 한 후 바닥면에서 이 점까지의 수직거리를 측정한다. 남자의 경우 생식기의 오른쪽으로 아크릴판을 끼운다. 아크릴판이 수평이 되도록 유의한다.

- Pose Constraints: strict_standing; knee_flexion=forbidden; board_level=required(아크릴판 수평)
- Allowed DoF: vertical_distance=required; auto_pose_correction=forbidden; pose_violation=warn_only

### KNEE_HEIGHT_M
측정 정의: 바닥면에서 무릎뼈가운데점까지의 수직거리

기준점(랜드마크): 무릎뼈가운데점, 바닥면

측정 방법: 피측정자의 오른쪽 앞에 수직자를 놓은 다음, 가로자의 끝이 오른다리 무릎뼈가운데점에 닿게 한 후, 바닥면에서 무릎뼈가운데점까지의 수직거리를 측정한다.

- Pose Constraints: strict_standing; knee_flexion=forbidden; right-side measurement
- Allowed DoF: vertical_distance=required; auto_pose_correction=forbidden; canonical_side=right; pose_violation=warn_only

### ARM_LEN_M
측정 정의: 어깨점에서 노뼈위점을 지나 손목안쪽점까지의 길이

기준점(랜드마크): 어깨점, 노뼈위점, 손목안쪽점

측정 방법: 피측정자의 오른쪽 옆에서 줄자로 어깨점에서 노뼈위점까지 잰 후, 손목안쪽점까지의 체표길이를 측정한다.

- Pose Constraints: right-side measurement
- Allowed DoF: path_type=surface_path(체표길이); canonical_side=right; symmetry_avg=forbidden; pose_violation=warn_only
