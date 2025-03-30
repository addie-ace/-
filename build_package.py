"""
彩票号码分析器打包脚本 - 简化版
用于将项目打包为独立的exe文件
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_project():
    """清理项目冗余文件"""
    print("清理项目临时文件...")
    
    # 临时打包文件
    temp_dirs = ["__pycache__", "build"]
    temp_files = ["*.spec", "version_info.txt"]
    
    # 删除临时目录
    for dir_name in temp_dirs:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"已删除目录: {dir_name}")
            except Exception as e:
                print(f"无法删除目录 {dir_name}: {e}")
    
    # 删除临时文件
    for pattern in temp_files:
        for file in Path('.').glob(pattern):
            try:
                file.unlink()
                print(f"已删除文件: {file}")
            except Exception as e:
                print(f"无法删除文件 {file}: {e}")
    
    return True

def create_version_info():
    """创建版本信息文件"""
    print("创建版本信息文件...")
    
    version_info = """# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(3, 0, 0, 0),
    prodvers=(3, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'080404b0',
          [StringStruct(u'CompanyName', u'彩票号码分析器'),
          StringStruct(u'FileDescription', u'彩票号码分析器 - 专业的彩票数据分析工具'),
          StringStruct(u'FileVersion', u'3.0.0.0'),
          StringStruct(u'InternalName', u'lottery_analyzer'),
          StringStruct(u'LegalCopyright', u'Copyright (C) 2024'),
          StringStruct(u'OriginalFilename', u'彩票号码分析器3.0.exe'),
          StringStruct(u'ProductName', u'彩票号码分析器'),
          StringStruct(u'ProductVersion', u'3.0.0.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
  ]
)
"""
    with open("version_info.txt", "w", encoding="utf-8") as f:
        f.write(version_info)
    
    print("版本信息文件已创建")
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("彩票号码分析器打包工具 - 简化版")
    print("=" * 60)
    
    # 检查文件
    print("\n检查必要文件...")
    required_files = ["main.py", "data_validator.py", "license_validator.py", "lottery_icon.ico"]
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("缺少以下必要文件:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    print("文件检查通过")
    
    # 清理临时文件
    clean_project()
    
    # 创建版本信息
    create_version_info()
    
    # 运行打包命令
    print("\n开始打包程序，请稍候...")
    cmd = [
        "pyinstaller",
        "--name=彩票号码分析器3.0",
        "--windowed",
        "--onefile",
        "--clean",
        "--icon=lottery_icon.ico",
        "--version-file=version_info.txt",
        "--add-data=lottery_icon.ico;.",
        "--add-data=zodiac_mapping.json;.",
        "main.py"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("打包过程中出错:")
        print(result.stderr)
        return False
    
    print("\n打包完成！")
    
    # 检查打包结果
    exe_path = os.path.join("dist", "彩票号码分析器3.0.exe")
    if os.path.exists(exe_path):
        print(f"程序已保存到: {os.path.abspath(exe_path)}")
    else:
        print("警告: 未找到打包后的程序文件，请检查错误信息")
    
    print("\n" + "=" * 60)
    print("打包过程已完成")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n打包过程中出现错误，请解决以上问题后重试。")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n打包过程被用户中断。")
        sys.exit(1)
    except Exception as e:
        print(f"\n打包过程中出现意外错误: {e}")
        sys.exit(1) 