import os
import shutil
import sys
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

# 사진이 들어있는 폴더명 (현재 디렉토리 기준)
PHOTO_DIR = 'origin_photos'
DEFAULT_GROUP_TIME_SEC = 180  # 기본값: 3분(180초) 이내

def get_datetime_original(path):
    try:
        img = Image.open(path)
        exif_data = img._getexif()
        if not exif_data:
            return None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'DateTimeOriginal':
                return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Error reading {path}: {e}")
    return None

def main():
    # 명령줄 인자 처리
    if len(sys.argv) > 1:
        try:
            group_time_sec = int(sys.argv[1])
            if group_time_sec <= 0:
                print("오류: 그룹화 시간은 1초 이상이어야 합니다.")
                return
        except ValueError:
            print("오류: 유효한 숫자(초)를 입력해주세요. 예: python group_photos_by_time.py 120")
            return
    else:
        group_time_sec = DEFAULT_GROUP_TIME_SEC
        print(f"그룹화 시간을 지정하지 않아 기본값({group_time_sec}초)을 사용합니다.")
    
    print(f"사진을 {group_time_sec}초 간격으로 그룹화합니다.")
    
    files = [f for f in os.listdir(PHOTO_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.cr2', '.arw', '.nef'))]
    file_times = []
    for f in files:
        path = os.path.join(PHOTO_DIR, f)
        dt = get_datetime_original(path)
        if dt:
            file_times.append((f, dt))
        else:
            print(f"No DateTimeOriginal for {f}, skipping.")
    # 촬영 시간순 정렬
    file_times.sort(key=lambda x: x[1])

    groups = []
    current_group = []
    last_time = None
    for fname, dt in file_times:
        if not last_time or (dt - last_time).total_seconds() > group_time_sec:
            if current_group:
                groups.append(current_group)
            current_group = [fname]
        else:
            current_group.append(fname)
        last_time = dt
    if current_group:
        groups.append(current_group)

    # 그룹별 폴더 생성 및 파일 이동
    for idx, group in enumerate(groups, 1):
        group_dir = os.path.join(PHOTO_DIR, str(idx))
        os.makedirs(group_dir, exist_ok=True)
        for fname in group:
            src = os.path.join(PHOTO_DIR, fname)
            dst = os.path.join(group_dir, fname)
            shutil.move(src, dst)
        print(f"Group {idx}: {len(group)} files moved.")

if __name__ == '__main__':
    main() 