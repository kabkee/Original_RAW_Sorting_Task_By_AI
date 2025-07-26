import os
import shutil
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

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

def move_files_to_root():
    # 원본 사진이 있는 디렉토리
    base_dir = 'origin_photos'
    
    # 모든 하위 디렉토리에서 파일을 찾아서 base_dir로 이동
    for root, dirs, files in os.walk(base_dir, topdown=False):
        if root == base_dir:
            continue  # 최상위 디렉토리는 건너뜁니다.
            
        for file in files:
            # 이미지 파일만 처리 (확장자 체크)
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.cr2', '.arw', '.nef')):
                src_path = os.path.join(root, file)
                dst_path = os.path.join(base_dir, file)
                
                # 파일명이 중복되는 경우 처리
                counter = 1
                while os.path.exists(dst_path):
                    name, ext = os.path.splitext(file)
                    new_filename = f"{name}_{counter}{ext}"
                    dst_path = os.path.join(base_dir, new_filename)
                    counter += 1
                
                # 파일 이동
                shutil.move(src_path, dst_path)
                print(f"Moved: {src_path} -> {dst_path}")
    
    # 빈 하위 디렉토리 삭제
    for root, dirs, files in os.walk(base_dir, topdown=False):
        if root == base_dir:
            continue  # 최상위 디렉토리는 건너뜁니다.
            
        try:
            # 디렉토리가 비어있는지 확인 후 삭제
            if not os.listdir(root):
                os.rmdir(root)
                print(f"Removed empty directory: {root}")
        except Exception as e:
            print(f"Error removing directory {root}: {e}")

def main():
    move_files_to_root()
    print("All files have been moved to the origin_photos directory and empty subdirectories have been removed.")

if __name__ == '__main__':
    main() 