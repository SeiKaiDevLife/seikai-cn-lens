import os
import glob
from PIL import Image

def resize_image(path, max_size, quality=85):
    try:
        with Image.open(path) as img:
            ratio = min(max_size / img.width, max_size / img.height)
            if ratio < 1:
                new_size = (int(img.width * ratio), int(img.height * ratio))
                # retain RGBA if PNG, otherwise RGB
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGBA")
                    res_img = img.resize(new_size, Image.Resampling.LANCZOS)
                    res_img.save(path, format=img.format, quality=quality)
                else:
                    img = img.convert("RGB")
                    res_img = img.resize(new_size, Image.Resampling.LANCZOS)
                    res_img.save(path, format=img.format, quality=quality)
                print(f"Resized {path} to {new_size}")
            else:
                pass
    except Exception as e:
        print(f"Failed {path}: {e}")

# Thumbnails
for f in glob.glob("public/gallery/**/thumbnails/*.webp", recursive=True):
    resize_image(f, 512, quality=80)

# Display
for f in glob.glob("public/gallery/**/display/*.webp", recursive=True):
    resize_image(f, 1080, quality=85)

# Avatars & QR
resize_image("public/avatar.webp", 320, quality=85)
resize_image("public/qrcode.webp", 320, quality=85)
resize_image("public/hero-bg.webp", 1080, quality=85)

# New QR
try:
    with Image.open("_uploader/images/7d7181cb79ecc6aef93d12c7694c7e85.jpg") as img:
        img = img.convert("RGB")
        ratio = min(320 / img.width, 320 / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio)) if ratio < 1 else (img.width, img.height)
        res_img = img.resize(new_size, Image.Resampling.LANCZOS)
        res_img.save("public/xiaohongshu-qrcode.webp", "WEBP", quality=85)
        print("Created public/xiaohongshu-qrcode.webp")
    os.remove("_uploader/images/7d7181cb79ecc6aef93d12c7694c7e85.jpg")
except Exception as e:
    print(f"Failed new QR: {e}")

# Logo
try:
    with Image.open("_uploader/images/LOGO_White.png") as img:
        img = img.convert("RGBA")
        ratio = min(512 / img.width, 512 / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio)) if ratio < 1 else (img.width, img.height)
        res_img = img.resize(new_size, Image.Resampling.LANCZOS)
        res_img.save("public/logo.png", "PNG")
        print("Created public/logo.png")
    os.remove("_uploader/images/LOGO_White.png")
except Exception as e:
    print(f"Failed new logo: {e}")

