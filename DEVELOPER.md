# 彩票号码分析器 - 开发者文档

## 项目架构

彩票号码分析器项目主要由以下组件构成：

1. **主程序界面** (`main.py`): 定义用户界面和交互逻辑
2. **数据分析模块** (`data_validator.py`): 处理数据验证、分析和预测逻辑
3. **序列号验证模块** (`license_validator.py`): 负责序列号验证和激活
4. **生肖映射系统**: 管理号码与生肖的对应关系，包括存档功能
5. **聪明组合工具**: 基于霍华德理论的组合生成与筛选功能
6. **界面风格系统**: 提供多种界面风格切换功能，支持用户个性化设置

## 主要类及其功能

### 1. LotteryAnalyzer (main.py)

主窗口类，负责管理整个应用程序的用户界面和交互逻辑。

**主要方法**:

- `__init__()`: 初始化UI组件，设置信号和槽连接，加载默认生肖映射，初始化序列号验证
- `import_data()`: 导入彩票数据文件，支持Excel和文本格式
- `analyze_range_data()`: 分析指定范围内的数据
- `analyze_all_data()`: 分析全部数据
- `analyze_specific_period()`: 分析特定年份和期数的数据
- `_display_analysis_results()`: 显示分析结果
- `generate_prediction()`: 生成并显示预测结果
- `set_zodiac_mapping()`: 显示生肖映射设置对话框
- `open_smart_combo_tool()`: 打开聪明组合工具对话框
- `manage_license()`: 打开序列号管理对话框
- `check_license()`: 检查序列号状态
- `createMenus()`: 创建程序菜单栏和子菜单
- `loadSettings()`: 加载用户设置，包括界面风格选择
- `applyStyle()`: 应用指定风格的样式表
- `refresh_license_status()`: 刷新序列号状态

### 2. ZodiacMappingDialog (main.py)

生肖映射设置对话框，用于管理号码与生肖的映射关系。

**主要方法**:

- `__init__()`: 初始化对话框UI，创建49个号码对应的生肖下拉选择框
- `refresh_archives()`: 刷新生肖存档列表
- `load_selected_archive()`: 加载选中的存档数据
- `save_as_new_archive()`: 将当前映射保存为新存档
- `get_mapping()`: 获取当前设置的映射关系

### 3. SmartCombinationDialog (main.py)

聪明组合工具对话框，用于基于霍华德理论筛选号码组合。

**主要方法**:

- `__init__()`: 初始化对话框UI，设置输入和显示区域
- `generate_combinations()`: 生成并筛选号码组合
- `export_results()`: 导出筛选后的组合结果
- `howard_filter()`: 基于霍华德理论规则过滤组合

### 4. LicenseDialog (main.py)

序列号管理对话框，用于验证和激活序列号。

**主要方法**:

- `__init__()`: 初始化对话框UI，设置序列号验证器
- `setup_ui()`: 设置对话框UI组件
- `refresh_status()`: 刷新服务器状态和序列号状态
- `activate_license()`: 激活序列号
- `check_current_license()`: 检查当前序列号状态

### 5. LotteryDataAnalyzer (data_validator.py)

数据分析类，负责数据加载、验证、分析和预测。

**主要方法**:

- `load_data()`: 加载彩票数据文件
- `validate_data()`: 验证数据格式和完整性
- `analyze_data()`: 分析数据，从多个维度提取信息
- `get_prediction()`: 基于分析结果生成预测号码
- `set_zodiac_mapping()`: 设置生肖映射关系
- `get_number_zodiac()`: 获取指定号码对应的生肖
- `find_period_index()`: 查找特定年份和期数在数据中的索引位置

### 6. LicenseValidator (license_validator.py)

序列号验证类，负责序列号的验证、激活和状态检查。

**主要方法**:

- `__init__()`: 初始化验证器，设置服务器地址和密钥
- `get_machine_code()`: 获取当前机器的唯一标识码
- `verify_license()`: 验证序列号有效性
- `activate_license()`: 激活序列号并绑定到当前机器
- `check_license()`: 检查当前序列号的状态
- `check_server_status()`: 检查验证服务器的连接状态
- `get_current_license()`: 获取当前已绑定的序列号

### 7. StyleDemo (test_styles.py)

样式表测试窗口，用于测试和预览不同的样式效果。

**主要方法**:

- `__init__()`: 初始化测试窗口
- `initUI()`: 创建测试UI，包含各种控件
- `change_style()`: 切换不同的界面风格

## 数据流

1. **序列号验证流程**:
   ```
   程序启动 → check_license() → 验证序列号 → 如果无效则显示激活对话框 → 用户输入序列号 → activate_license() → 保存到本地
   ```

2. **数据导入流程**:
   ```
   用户选择文件 → load_data() → 数据验证 → 加载到内存 → 启用分析按钮
   ```

3. **数据分析流程**:
   ```
   用户点击分析按钮 → 分析方法调用 → analyze_data() → _display_analysis_results() → 显示结果
   ```

4. **预测生成流程**:
   ```
   用户点击预测按钮 → generate_prediction() → get_prediction() → 处理预测结果 → 显示预测结果
   ```

5. **生肖映射流程**:
   ```
   用户点击生肖映射按钮 → ZodiacMappingDialog → 用户设置映射 → set_zodiac_mapping() → 保存到JSON文件
   ```

6. **存档管理流程**:
   ```
   存档保存: 设置映射 → save_as_new_archive() → 存储到zodiac_archives目录
   存档加载: 选择存档 → load_selected_archive() → 应用到界面
   ```

7. **样式设置流程**:
   ```
   用户选择样式 → applyStyle() → 读取样式文件 → 应用样式表 → 保存样式设置 → 下次启动时自动应用
   ```

## 文件结构

```
Project/
├── main.py                 # 主程序文件
├── data_validator.py       # 数据分析模块
├── license_validator.py    # 序列号验证模块
├── zodiac_mapping.json     # 默认生肖映射文件
├── license.dat             # 序列号存储文件
├── lottery_icon.ico        # 程序图标
├── test_styles.py          # 样式测试程序
├── styles/                 # 样式表目录
│   ├── win11.qss          # Windows 11风格样式表
│   ├── neumorphism.qss    # 拟物化设计样式表
│   ├── macos.qss          # macOS风格样式表
│   └── dropdown.png       # 下拉菜单图标
├── zodiac_archives/        # 生肖映射存档目录
│   ├── archive1.json       # 生肖映射存档1
│   └── archive2.json       # 生肖映射存档2
├── README.md               # 用户说明文档
├── UPDATE_LOG.md           # 更新日志
└── DEVELOPER.md            # 开发者文档
```

## 技术实现细节

### 1. 序列号验证系统

序列号验证系统使用客户端-服务器架构，确保激活和验证的安全性：

1. **序列号格式**: 使用Base64编码的JSON数据，包含以下信息:
   - license_id: 唯一标识符
   - created_date: 创建日期
   - expiry_date: 过期日期
   - signature: 使用密钥生成的签名

2. **机器码生成**: 
   - 使用WMI获取CPU ID和硬盘序列号
   - 组合并哈希生成唯一机器码
   - 如果WMI失败，使用UUID作为备选方案

3. **服务器验证**:
   - 序列号格式本地验证
   - 发送序列号和机器码到服务器验证
   - 服务器检查序列号是否有效且未被其他机器绑定
   - 服务器记录绑定信息并返回验证结果

4. **本地存储**:
   - 验证成功后，序列号信息保存到本地文件
   - 包含序列号、机器码和激活日期
   - 程序启动时自动检查本地序列号状态

### 2. 生肖映射系统

生肖映射使用JSON文件存储，格式如下:

```json
{
  "1": "鼠",
  "2": "牛",
  "3": "虎",
  ...
  "49": "猪"
}
```

程序启动时会自动加载默认映射文件，如果存在的话。

### 3. 界面风格系统

界面风格系统通过QSS样式表实现，支持三种不同的设计风格：

1. **Windows 11风格**：`win11.qss`
   - 使用Windows 11设计语言
   - 扁平化设计，微妙的阴影效果
   - 现代化的控件样式

2. **拟物化设计**：`neumorphism.qss`
   - 使用新拟物化设计语言
   - 立体感和质感的表现
   - 内外浮雕效果的按钮和控件

3. **macOS风格**：`macos.qss`
   - 模拟macOS的界面风格
   - 半透明毛玻璃效果
   - 简约优雅的控件设计

**实现细节**：
- 使用`QSettings`保存用户的样式偏好
- 创建菜单栏提供样式切换选项
- 在程序启动时加载上次使用的样式
- 提供测试程序(`test_styles.py`)预览所有控件在不同样式下的效果

### 4. 预测数据来源

在v3.0版本中，预测功能增强显示了预测使用的数据来源信息，包括:
- 数据文件名
- 分析的数据总量(期数)
- 分析时间
- 数据索引范围
- 分析区间信息

这一功能通过在`generate_prediction()`方法中从`analysis_results`中提取信息实现。

### 5. 聪明组合工具

聪明组合工具基于霍华德理论筛选号码组合，筛选规则包括:
- 奇偶比例平衡(不能全奇或全偶)
- 大小比例平衡(不能全大或全小)
- 连续数字不超过3个
- 号码和在合理范围内(90-220)
- 同尾数不超过3个

### 6. 程序打包

程序使用PyInstaller打包为可执行文件，主要步骤:

1. **准备资源文件**:
   - 确保lottery_icon.ico图标文件存在
   - 生肖映射文件zodiac_mapping.json
   - 样式表文件目录styles/

2. **创建spec文件**:
   - 指定入口点为main.py
   - 添加资源文件
   - 设置程序图标和版本信息

3. **运行PyInstaller**:
   - 使用--clean参数清理临时文件
   - 使用--noconfirm参数无需确认
   - 使用--add-data添加样式表和资源文件
   - 打包完成后的程序位于dist目录

## 如何扩展功能

### 1. 添加新的分析维度

在`data_validator.py`的`analyze_data()`方法中添加新的分析逻辑:

```python
def analyze_data(self, start_period=None, end_period=None):
    # 现有分析代码
    
    # 添加新的分析维度
    results["新维度分析"] = self._analyze_new_dimension(data_to_analyze)
    
    return results

def _analyze_new_dimension(self, data):
    # 实现新维度的分析逻辑
    result = {}
    # ...分析代码...
    return result
```

然后在`_display_analysis_results()`方法中添加相应的显示代码。

### 2. 添加新的界面风格

要添加新的界面风格，需要以下步骤：

1. **创建新的样式表文件**:
   ```
   styles/new_style.qss
   ```

2. **在菜单中添加新的样式选项**:
   ```python
   # 在createMenus()方法中添加
   newStyleAction = QAction('新风格', self)
   newStyleAction.triggered.connect(lambda: self.applyStyle("new_style"))
   styleMenu.addAction(newStyleAction)
   ```

3. **修改applyStyle()方法**:
   ```python
   def applyStyle(self, style_name):
       """应用样式表"""
       style_file = ""
       
       if style_name == "win11":
           style_file = "styles/win11.qss"
       elif style_name == "neumorphism":
           style_file = "styles/neumorphism.qss"
       elif style_name == "macos":
           style_file = "styles/macos.qss"
       elif style_name == "new_style":  # 添加新风格
           style_file = "styles/new_style.qss"
       
       # 其余代码保持不变
   ```

4. **更新打包脚本**:
   确保新样式表文件被包含在打包中。