import os
import json
import sys
import subprocess
from datetime import datetime
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADER_DIR = os.path.join(BASE_DIR, '_uploader')
IMAGES_DIR = os.path.join(UPLOADER_DIR, 'images')
INFO_JSON = os.path.join(UPLOADER_DIR, 'info_P.json')
PUBLIC_GALLERY_DIR = os.path.join(BASE_DIR, 'public', 'gallery')

def process_image_file(source_path, target_dir, yy_mm, folder_name, new_filename):
    os.makedirs(target_dir, exist_ok=True)
    
    webp_filename = f"{new_filename}.webp"
    target_path = os.path.join(target_dir, webp_filename)
    
    try:
        with Image.open(source_path) as img:
            if img.mode in ("RGBA", "P", "CMYK"):
                img = img.convert("RGB")
            
            target_max = 4096
            disp_ratio = min(target_max / img.width, target_max / img.height)
            if disp_ratio < 1:
                disp_size = (int(img.width * disp_ratio), int(img.height * disp_ratio))
                disp_img = img.resize(disp_size, Image.Resampling.LANCZOS)
            else:
                disp_img = img
            disp_img.save(target_path, 'WEBP', quality=85)
            
            os.remove(source_path)
            
            rel_path = f"public/gallery/portrait/{yy_mm}/{folder_name}/{webp_filename}"
            return rel_path, rel_path
    except Exception as e:
        print(f"处理出错 {source_path}: {e}")
        return None, None

def main():
    print("开始执行 [写真组图 P] 自动化处理脚本...")
    if not os.path.exists(INFO_JSON):
        print("未找到 info_P.json，请先填写配置！")
        return
        
    with open(INFO_JSON, 'r', encoding='utf-8') as f:
        try: info = json.load(f)
        except Exception as e:
            print("解析 info_P.json 失败:", e)
            return

    date_str = info.get('date', '2026-01-01')
    location = info.get('location', '未命名地点')
    title = info.get('title', '')
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        yy_mm = dt.strftime('%y-%m')
    except:
        yy_mm = "26-01"
        
    folder_name = f"{date_str} {location}"
    target_dir = os.path.join(PUBLIC_GALLERY_DIR, "portrait", yy_mm, folder_name)

    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

    layout = info.get('layout', {})
    required_keys = ['cover', 'grid_1', 'grid_2', 'grid_3', 'grid_4', 'grid_5']
    missing_files = []
    
    layout_files = []
    for key in required_keys:
        fname = layout.get(key)
        if not fname:
            missing_files.append(f"[{key}未填写]")
        else:
            source_path = os.path.join(IMAGES_DIR, fname)
            if not os.path.exists(source_path):
                missing_files.append(fname)
            else:
                layout_files.append(fname)
                
    if missing_files:
        print(f"严重错误: 缺失必要的1+5布局图片: {', '.join(missing_files)}")
        sys.exit(1)

    valid_exts = ('.jpg', '.jpeg', '.png', '.webp', '.tiff')
    all_files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(valid_exts)]
    other_files = [f for f in all_files if f not in layout_files]

    processed_count = 0
    processed_layout = {}
    
    for i, key in enumerate(required_keys):
        fname = layout[key]
        new_fname = "cover" if key == "cover" else str(i)
        print(f"  -> [布局图] 重命名: {fname} -> {new_fname}.webp")
        source_path = os.path.join(IMAGES_DIR, fname)
        thumb, disp = process_image_file(source_path, target_dir, yy_mm, folder_name, new_fname)
        processed_layout[key] = {"thumbnail": thumb, "display": disp}
        processed_count += 1
        
    processed_others = []
    for j, fname in enumerate(other_files, start=6):
        new_fname = str(j)
        print(f"  -> [其他图自动挂载] 重命名: {fname} -> {new_fname}.webp")
        source_path = os.path.join(IMAGES_DIR, fname)
        thumb, disp = process_image_file(source_path, target_dir, yy_mm, folder_name, new_fname)
        if thumb and disp:
            processed_others.append({"thumbnail": thumb, "display": disp})
            processed_count += 1

    entry_id = f"port-{date_str}-{location}"
    new_entry = {
        "id": entry_id,
        "type": "gallery",
        "date": date_str,
        "title": title,
        "location": location,
        "category": "P",
        "layout": processed_layout,
        "others": processed_others
    }
    
    meta_path = os.path.join(target_dir, "meta.json")
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(new_entry, f, ensure_ascii=False, indent=2)
        
    print(f"成功写入底层物理记录: {meta_path}")
    
    # 触发 Manager 自动构建
    manager_script = os.path.join(BASE_DIR, 'data', 'manager.py')
    subprocess.run(['python', manager_script, 'build'])

    print(f"\n完美收工！成功处理了 {processed_count} 张写真照片。")

if __name__ == "__main__":
    main()
