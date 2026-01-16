# step0_make_dummy.py
# 이 코드는 검증 코드를 테스트하기 위한 "가짜(Dummy) 데이터"를 생성합니다.
# 실제 SMPL-X 데이터가 없을 때, 코드가 잘 돌아가는지 확인하는 용도입니다.

import numpy as np
import os

def make_dummy_data(filename="dummy_data.npz"):
    print(f"Creating dummy data: {filename} ...")
    
    # 1. 설정 (SMPL-X 대략적인 스펙)
    n_frames = 5   # 5개의 프레임(동작)
    n_verts = 10475 # SMPL-X 기본 정점 수
    n_joints = 55   # SMPL-X 관절 수
    
    # 2. 가짜 데이터 생성 (랜덤 값)
    # verts: 사람 크기 비슷하게 (미터 단위)
    verts = np.random.randn(n_frames, n_verts, 3).astype(np.float32) * 0.5 
    
    # joints: 관절 위치
    joints = np.random.randn(n_frames, n_joints, 3).astype(np.float32) * 0.5
    
    # weights: LBS 웨이트 (0~1 사이)
    weights = np.random.rand(n_verts, n_joints).astype(np.float32)
    # 웨이트 합이 1이 되도록 정규화
    weights /= weights.sum(axis=1, keepdims=True)

    # 3. 저장
    np.savez(filename, 
             verts=verts, 
             joints_xyz=joints, 
             lbs_weights=weights)
    
    print("Done! File saved.")
    print(f"Path: {os.path.abspath(filename)}")

if __name__ == "__main__":
    make_dummy_data()