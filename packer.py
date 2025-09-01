# packer.py
from PIL import Image, ExifTags
import os
import sys
import hashlib
from maxrects import MaxRectsPacker, align_to_multiple

# 支持的图片格式
SUPPORTED_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.tga', '.tif', '.tiff', '.webp'}

def auto_rotate_image(img):
    """根据 EXIF 信息自动旋转图像"""
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img._getexif()
        if exif is not None:
            orientation = exif[orientation]
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    except:
        pass
    return img

def load_images_from_folder_or_list(paths):
    """接受文件夹或文件列表，返回所有图片 (name, image, w, h)"""
    images = []
    seen_names = set()

    for path in paths:
        if os.path.isdir(path):
            print(f"Loading images from folder: {path}")
            for root, _, files in os.walk(path):
                for file in files:
                    filepath = os.path.join(root, file)
                    if is_image_file(filepath):
                        try:
                            img = Image.open(filepath).convert("RGBA")
                            img = auto_rotate_image(img)
                            name = get_unique_name(filepath, seen_names)
                            images.append((name, img, img.size[0], img.size[1]))
                        except Exception as e:
                            print(f"Failed to load {filepath}: {e}")
        elif os.path.isfile(path):
            if is_image_file(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    img = auto_rotate_image(img)
                    name = get_unique_name(os.path.basename(path), seen_names)
                    images.append((name, img, img.size[0], img.size[1]))
                except Exception as e:
                    print(f"Failed to load {path}: {e}")
        else:
            print(f"Path not found: {path}")

    # 按面积降序排列（MaxRects 推荐）
    images.sort(key=lambda x: -x[2] * x[3])
    return images

def is_image_file(filepath):
    """判断是否为支持的图片格式"""
    return os.path.splitext(filepath.lower())[1] in SUPPORTED_EXTS

def get_unique_name(filepath, seen_names):
    """生成唯一名称，避免重名（如多个 folder1/icon.png）"""
    rel_path = os.path.relpath(filepath).replace("\\", "/")
    name = os.path.splitext(rel_path.replace("/", "_"))[0]
    counter = 1
    original = name
    while name in seen_names:
        name = f"{original}_{counter}"
        counter += 1
    seen_names.add(name)
    return name

def pack_sprites(input_paths, output_name="atlas", max_size=2048):
    images = load_images_from_folder_or_list(input_paths)
    if not images:
        print("❌ No images loaded.")
        return

    print(f"📦 Found {len(images)} images to pack.")

    current_atlas_index = 0
    placements = []  # (name, x, y, w, h, image)

    def save_current_atlas(index, placements, used_width, used_height):
        atlas_output_name = f"{output_name}_{index}"
        padded_width = align_to_multiple(used_width, 4)
        padded_height = align_to_multiple(used_height, 4)

        atlas = Image.new("RGBA", (padded_width, padded_height), (0, 0, 0, 0))
        for name, x, y, w, h, img in placements:
            atlas.paste(img, (x, y))

        atlas.save(f"{atlas_output_name}.png", "PNG")
        print(f"✅ Atlas saved: {atlas_output_name}.png ({padded_width}x{padded_height})")

        write_tpsheet(atlas_output_name, placements, padded_width, padded_height)
        print(f"✅ Metadata saved: {atlas_output_name}.tpsheet")

    # 初始化 MaxRectsPacker
    packer = MaxRectsPacker(max_size, max_size)

    for name, img, w, h in images:
        if w > max_size or h > max_size:
            print(f"⚠️ Image {name} ({w}x{h}) exceeds the maximum size and will be skipped.")
            continue

        pos = packer.insert(w, h)
        while pos is None:
            # 当前图集中无法放入该图片，则保存当前图集并开始新的一个
            if placements:
                used_width = max(x + w for _, x, y, w, h, _ in placements)
                used_height = max(y + h for _, x, y, w, h, _ in placements)
                save_current_atlas(current_atlas_index, placements, used_width, used_height)
                current_atlas_index += 1
                placements = []
                packer = MaxRectsPacker(max_size, max_size)
            else:
                print(f"❌ Cannot fit even in empty atlas: {name} ({w}x{h})")
                break

            pos = packer.insert(w, h)

        if pos is not None:
            x, y = pos
            placements.append((name, x, y, w, h, img))
            print(f"✅ Placed: {name} -> ({x},{y}) {w}x{h}")
        else:
            print(f"❌ Failed to place: {name}")

    # Save any remaining sprites in the last atlas
    if placements:
        used_width = max(x + w for _, x, y, w, h, _ in placements)
        used_height = max(y + h for _, x, y, w, h, _ in placements)
        save_current_atlas(current_atlas_index, placements, used_width, used_height)

def write_tpsheet(output_name, placements, width, height):
    tpsheet_path = f"{output_name}.tpsheet"
    smart_hash = hashlib.md5(f"{output_name}{width}x{height}".encode()).hexdigest()[:32]

    with open(tpsheet_path, "w", encoding="utf-8") as f:
        f.write("# Sprite sheet data for Unity.\n")
        f.write("# To import these sprites into your Unity project, download \"TexturePackerImporter\":\n")
        f.write("# https://www.codeandweb.com/texturepacker/unity\n\n")
        f.write(f"# $TexturePacker:SmartUpdate:{smart_hash}:0:0$\n")
        f.write(":format=40300\n")
        f.write(f":texture={output_name}.png\n")
        f.write(f":size={width}x{height}\n")
        f.write(":pivotpoints=enabled\n")
        f.write(":borders=disabled\n")
        f.write(":alphahandling=ClearTransparentPixels\n\n")

        for name, x, y, w, h, _ in placements:
            # ✅ 关键：y 要从底部算起（Unity 原点在左下）
            y_unity = height - y - h  # 翻转 y 坐标
            vertices = f"4;{w};0;0;0;0;{h};{w};{h}"
            triangles = "2;1;2;3;0;1;3"
            # ✅ 输出格式：name;x;y;w;h;...
            f.write(f"{name};{x};{y_unity};{w};{h}; 0.5;0.5; 0;0;0;0; {vertices}; {triangles}\n")

# ======================
# 命令行入口
# ======================
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python packer.py --input folder1/ folder2/ img1.png ... --output atlas_name")
        sys.exit(1)

    inputs = []
    output = "atlas"
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--input":
            i += 1
            while i < len(sys.argv) and not sys.argv[i].startswith("--"):
                inputs.append(sys.argv[i])
                i += 1
            continue
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output = sys.argv[i + 1]
            i += 1
        i += 1

    pack_sprites(inputs, output)
    # Run Like This:
    # python packer.py --input assets/ --output game_ui