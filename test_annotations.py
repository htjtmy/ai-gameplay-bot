import pandas as pd
from pathlib import Path

annotations_path = Path('data/raw/gameplay_videos/勘察/委托_妮弗尔夫人/annotations_20260131_125634.csv')
frames_dir = Path('data/processed/frames/勘察/委托_妮弗尔夫人/20260131_125634')

# 读取标注
annotations = pd.read_csv(annotations_path)
print(f'列名: {annotations.columns.tolist()}')
print(f'形状: {annotations.shape}')
print(f'前5行:\n{annotations.head()}')

# 测试iterrows
print('\n测试iterrows:')
count = 0
for idx, row in annotations.iterrows():
    if count < 3:
        print(f"Row {idx}: frame={row['frame']}, action_id={row['action_id']}")
        count += 1
    else:
        break

# 测试帧匹配
print(f'\n帧目录: {frames_dir}')
print(f'帧目录存在: {frames_dir.exists()}')

if frames_dir.exists():
    frames = list(frames_dir.glob('frame_*.jpg'))
    print(f'找到 {len(frames)} 个帧文件')
    if frames:
        print(f'示例: {frames[0].name}')
