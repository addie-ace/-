"""
彩票号码分析器2.0打包脚本
用于将Python程序打包成Windows可执行文件(.exe)
"""

import os
import sys
import shutil
from PIL import Image
import PyInstaller.__main__

# 程序名称
APP_NAME = "彩票号码分析器2.0（吴京为）"

# 原始图标文件路径
ORIGINAL_ICON_PATH = os.path.abspath("彩票图标.png")

# 转换后的ICO图标路径
ICON_PATH = os.path.abspath("lottery_icon.ico")

# 转换PNG图标为ICO格式
def convert_png_to_ico(png_path, ico_path):
    try:
        # 尝试安装Pillow库(如果尚未安装)
        import pip
        try:
            from PIL import Image
        except ImportError:
            print("正在安装Pillow库...")
            pip.main(['install', 'Pillow'])
            from PIL import Image
            
        # 转换图片
        img = Image.open(png_path)
        
        # 调整大小为标准尺寸（如256x256）
        img = img.resize((256, 256))
        
        # 保存为ICO
        img.save(ico_path, format='ICO')
        
        return True
    except Exception as e:
        print(f"图标转换失败: {e}")
        return False

# 确保原始图标文件存在
if not os.path.exists(ORIGINAL_ICON_PATH):
    print(f"错误: 图标文件未找到: {ORIGINAL_ICON_PATH}")
    sys.exit(1)

# 转换图标
print(f"正在将PNG图标转换为ICO格式...")
if not convert_png_to_ico(ORIGINAL_ICON_PATH, ICON_PATH):
    print("无法转换图标，将使用PyInstaller默认图标")
    ICON_PATH = None
else:
    print(f"图标已转换: {ICON_PATH}")

# 需要包含的数据文件
data_files = [
    ('zodiac_mapping.json', '.'),  # 将生肖映射文件复制到根目录
    ('README.md', '.'),  # 包含说明文档
    ('UPDATE_LOG.md', '.'),  # 包含更新日志
    ('DEVELOPER.md', '.'),  # 包含开发者文档
]

# 创建zodiac_archives目录（如果不存在）
if not os.path.exists('zodiac_archives'):
    os.makedirs('zodiac_archives')

# 构建PyInstaller命令参数
pyinstaller_args = [
    '--name=%s' % APP_NAME,
    '--windowed',  # 创建无控制台窗口的GUI应用
    '--onefile',   # 创建单个可执行文件
    '--noconfirm', # 不询问确认
    '--add-data=%s' % ';'.join(['zodiac_archives', 'zodiac_archives']),  # 添加生肖存档目录
]

# 添加图标参数(如果转换成功)
if ICON_PATH and os.path.exists(ICON_PATH):
    pyinstaller_args.append('--icon=%s' % ICON_PATH)

# 添加数据文件
for src, dst in data_files:
    if os.path.exists(src):
        pyinstaller_args.append('--add-data=%s' % ';'.join([src, dst]))
    else:
        print(f"警告: 文件未找到: {src}")

# 添加主程序文件
pyinstaller_args.append('main.py')

# 打印打包信息
print("=" * 50)
print(f"开始打包程序: {APP_NAME}")
if ICON_PATH and os.path.exists(ICON_PATH):
    print(f"使用图标: {ICON_PATH}")
else:
    print("使用默认图标")
print("包含以下数据文件:")
for src, dst in data_files:
    if os.path.exists(src):
        print(f" - {src} -> {dst}")
print("=" * 50)

# 执行PyInstaller打包
try:
    PyInstaller.__main__.run(pyinstaller_args)
    print("\n打包完成！")
    print(f"可执行文件位于: dist/{APP_NAME}.exe")
except Exception as e:
    print(f"打包过程中出错: {e}")
    print("尝试使用命令行方式打包...")
    
    # 构建命令行命令
    cmd_args = ["pyinstaller"]
    for arg in pyinstaller_args:
        cmd_args.append(arg)
    
    cmd = " ".join(cmd_args)
    print(f"执行命令: {cmd}")
    os.system(cmd)

print("=" * 50) 