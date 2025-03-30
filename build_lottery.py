import os
import sys
import shutil
from PyInstaller.__main__ import run

def build_app():
    """打包彩票分析程序"""
    try:
        # 检查必要文件是否存在
        required_files = ['main.py', 'data_validator.py', 'lottery_icon.ico']
        for file in required_files:
            if not os.path.exists(file):
                print(f"错误: 找不到必要文件 {file}")
                return False
        
        # 创建spec文件内容
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('lottery_icon.ico', '.'),
        ('zodiac_mapping.json', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='彩票号码分析器2.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='lottery_icon.ico',
    version='file_version_info.txt'
)
'''
        
        # 创建版本信息文件
        version_info = f'''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
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
          StringStruct(u'FileDescription', u'彩票号码分析工具'),
          StringStruct(u'FileVersion', u'2.0.0.0'),
          StringStruct(u'InternalName', u'lottery_analyzer'),
          StringStruct(u'LegalCopyright', u'Copyright (C) 2024'),
          StringStruct(u'OriginalFilename', u'彩票号码分析器2.0.exe'),
          StringStruct(u'ProductName', u'彩票号码分析器'),
          StringStruct(u'ProductVersion', u'2.0.0.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
  ]
)
'''
        
        # 写入spec文件
        with open('lottery_analyzer.spec', 'w', encoding='utf-8') as f:
            f.write(spec_content)
            
        # 写入版本信息文件
        with open('file_version_info.txt', 'w', encoding='utf-8') as f:
            f.write(version_info)
        
        print("正在打包程序，请稍候...")
        
        # 运行PyInstaller
        run([
            'lottery_analyzer.spec',
            '--clean',
            '--noconfirm'
        ])
        
        print("\n打包完成！")
        print("程序文件位于 dist 目录中")
        return True
        
    except Exception as e:
        print(f"打包过程中出错: {str(e)}")
        return False

if __name__ == '__main__':
    if build_app():
        print("\n打包成功完成！")
    else:
        print("\n打包过程中出现错误，请检查以上信息。") 