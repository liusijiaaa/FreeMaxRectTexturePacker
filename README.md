# FreeMaxRectTexturePacker

---

# 🧩 TexturePacker for Unity - 自动图集生成工具

> 一个轻量级、开源的 Python 工具，将多张图片打包成 Unity 可用的纹理图集（Texture Atlas），并生成 `.tpsheet` 元数据文件，支持自动对齐、命名去重和 EXIF 旋转修正。

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Unity](https://img.shields.io/badge/Unity-Compatible-brightgreen)

---

## 📌 简介

本工具使用 **MaxRects 算法** 高效打包图片资源，输出符合 [TexturePacker Importer](https://www.codeandweb.com/texturepacker/unity) 标准的 `.tpsheet` 文件，帮助 Unity 开发者：

- ✅ 减少 Draw Call
- ✅ 提高渲染性能
- ✅ 自动管理 UI/角色/特效 等 Sprite 资源
- ✅ 支持图集尺寸对齐到 4 的倍数（适配 ETC2/ASTC 压缩）

无需依赖外部软件，纯 Python 实现，开箱即用！

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pillow
```

### 2. 运行打包命令

```bash
python packer.py --input assets/ --output game_ui
```

### 3. 查看输出结果

```text
game_ui_0.png       # 打包后的图集图像
game_ui_0.tpsheet   # Unity 可识别的元数据
```

---

## 🛠️ 使用方法

### 基本语法

```bash
python packer.py --input <路径1> [路径2] ... --output <输出名称>
```

### 示例

```bash
# 打包整个文件夹
python packer.py --input icons/ --output ui_icons

# 打包多个文件夹和单个图片
python packer.py --input characters/ enemies/ boss.png --output atlas_characters

# 输出多个图集（自动分片）
# -> atlas_part_0.png, atlas_part_0.tpsheet
# -> atlas_part_1.png, atlas_part_1.tpsheet
```

---

## 🖼️ 输出说明

| 文件 | 说明 |
|------|------|
| `output_N.png` | 第 N 个图集图像（PNG 格式） |
| `output_N.tpsheet` | 对应的元数据文件，包含每张子图的位置、大小等信息 |

> 🔍 **提示**：`.tpsheet` 是 TexturePacker 标准格式，需配合 Unity 插件使用。

---

## 🎮 在 Unity 中使用

### 1. 安装插件

前往 Unity Asset Store 安装：
> [TexturePacker Importer](https://assetstore.unity.com/packages/tools/sprite-management/texturepacker-importer-84063)

### 2. 导入资源

将生成的 `.png` 和 `.tpsheet` 文件放入 Unity 的 `Assets/` 目录。

### 3. 查看切割效果

1. 选中 `.png` 文件
2. 点击 **Sprite Editor**
3. 点击右上角 **Import** → 选择 `.tpsheet`
4. 点击 **Apply**，即可自动切割出所有 Sprite

---

## ⚙️ 特性

| 功能 | 说明 |
|------|------|
| ✅ MaxRects 算法 | 高效利用空间，减少空白 |
| ✅ Y 轴翻转 | 适配 Unity 左下角坐标系 |
| ✅ 尺寸对齐 | 图集宽高自动对齐到 4 的倍数（利于 GPU 压缩） |
| ✅ 命名去重 | 多路径同名文件自动重命名（如 `folder_icon.png`） |
| ✅ EXIF 修正 | 自动旋转 JPG 图片方向 |
| ✅ 多图集支持 | 超出最大尺寸时自动创建新图集 |
| ✅ 批量处理 | 支持输入多个文件或文件夹 |

---

## 📂 项目结构

```
texture_packer/
├── packer.py           # 主脚本：打包逻辑与命令行入口
├── maxrects.py         # 空间管理模块：MaxRects 算法实现
└── assets/             # 示例资源目录（可选）
```

---

## 🔧 高级配置

### 修改最大图集尺寸

编辑 `packer.py` 中的调用：

```python
pack_sprites(inputs, output, max_size=1024)  # 默认 2048
```

### 更改对齐方式（可选）

默认对齐到 4 的倍数。如需对齐到 2 的幂（如 1024, 2048），可替换 `align_to_multiple` 函数。

---

## 🐛 常见问题

### ❓ 图片没被打包？

- 检查是否超过 `max_size`（默认 2048）
- 确认图片格式支持：`.png`, `.jpg`, `.bmp`, `.tga`, `.tif`, `.webp`
- 查看控制台日志是否有 `⚠️ Skipped`

### ❓ Unity 中切割错位？

- 确保 `.tpsheet` 和 `.png` 同名且在同一目录
- 确认已安装 **TexturePacker Importer**
- 检查 Unity 的 Texture Type 是否为 `Advanced`

---

## 📜 许可证

MIT License - 可自由用于商业或非商业项目。

---

## 💬 反馈与支持

欢迎提交 Issue 或联系作者：
- Email: [liusiiijia.@gmail.com]
