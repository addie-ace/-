import sys
import json
import os
import itertools
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QWidget, QFileDialog, QTextEdit, QLabel, QMessageBox,
                           QTabWidget, QHBoxLayout, QGridLayout, QComboBox,
                           QDialog, QLineEdit, QInputDialog, QListWidget,
                           QAction, QMenu, QMenuBar)
from PyQt5.QtCore import Qt, QSettings
from data_validator import LotteryDataAnalyzer
from license_validator import LicenseValidator
from PyQt5.QtGui import QFont, QIcon

class ZodiacMappingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置生肖映射")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # 添加存档管理部分
        archive_layout = QHBoxLayout()
        archive_label = QLabel("生肖存档:")
        self.archive_combo = QComboBox()
        self.refresh_archives_button = QPushButton("刷新")
        self.refresh_archives_button.clicked.connect(self.refresh_archives)
        
        archive_layout.addWidget(archive_label)
        archive_layout.addWidget(self.archive_combo, 1)  # 设置伸展因子为1
        archive_layout.addWidget(self.refresh_archives_button)
        
        layout.addLayout(archive_layout)
        
        # 创建网格布局用于显示号码和生肖选择
        grid = QGridLayout()
        self.combo_boxes = {}
        
        # 创建49个下拉框
        for i in range(49):
            row = i // 7
            col = i % 7
            number = i + 1
            
            label = QLabel(f"{number}号:")
            combo = QComboBox()
            combo.addItems(['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪'])
            self.combo_boxes[number] = combo
            
            grid.addWidget(label, row, col * 2)
            grid.addWidget(combo, row, col * 2 + 1)
        
        layout.addLayout(grid)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 确定按钮
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # 加载已保存按钮
        load_button = QPushButton("加载选中存档")
        load_button.clicked.connect(self.load_selected_archive)
        button_layout.addWidget(load_button)
        
        # 保存设置按钮
        save_button = QPushButton("保存为新存档")
        save_button.clicked.connect(self.save_as_new_archive)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # 初始化时刷新存档列表
        self.refresh_archives()
    
    def refresh_archives(self):
        """刷新生肖存档列表"""
        self.archive_combo.clear()
        
        # 创建zodiac_archives目录（如果不存在）
        if not os.path.exists("zodiac_archives"):
            os.makedirs("zodiac_archives")
            
        # 扫描存档目录中的JSON文件
        archive_files = [f for f in os.listdir("zodiac_archives") if f.endswith(".json")]
        
        # 添加默认存档
        if os.path.exists("zodiac_mapping.json"):
            self.archive_combo.addItem("默认存档 (zodiac_mapping.json)")
            
        # 添加其他存档
        for archive in archive_files:
            self.archive_combo.addItem(archive)
            
        if self.archive_combo.count() == 0:
            self.archive_combo.addItem("无可用存档")
    
    def load_selected_archive(self, silent=False):
        """加载选中的存档
        
        Args:
            silent: 是否静默加载（不显示消息框）
        """
        try:
            selected = self.archive_combo.currentText()
            
            # 检查是否有选中的存档
            if selected == "无可用存档":
                if not silent:
                    QMessageBox.warning(self, "提示", "没有可用的存档")
                return
                
            # 确定文件路径
            if selected == "默认存档 (zodiac_mapping.json)":
                file_path = "zodiac_mapping.json"
            else:
                file_path = os.path.join("zodiac_archives", selected)
                
            # 加载文件
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    mapping = json.load(f)
                    # 将字符串键转换为整数键
                    mapping = {int(num): zodiac for num, zodiac in mapping.items()}
                    for number, zodiac in mapping.items():
                        if number in self.combo_boxes:
                            index = self.combo_boxes[number].findText(zodiac)
                            if index >= 0:
                                self.combo_boxes[number].setCurrentIndex(index)
                if not silent:
                    QMessageBox.information(self, "成功", f"已加载存档: {selected}")
            else:
                if not silent:
                    QMessageBox.warning(self, "提示", f"未找到存档文件: {file_path}")
        except Exception as e:
            if not silent:
                QMessageBox.critical(self, "错误", f"加载生肖映射时出错：{str(e)}")
    
    def save_as_new_archive(self):
        """将当前映射保存为新存档"""
        try:
            # 获取存档名称
            archive_name, ok = QInputDialog.getText(self, "保存存档", "请输入存档名称:")
            if not ok or not archive_name:
                return
                
            # 添加.json扩展名（如果没有）
            if not archive_name.endswith(".json"):
                archive_name += ".json"
                
            # 创建zodiac_archives目录（如果不存在）
            if not os.path.exists("zodiac_archives"):
                os.makedirs("zodiac_archives")
                
            # 保存到文件
            file_path = os.path.join("zodiac_archives", archive_name)
            mapping = {number: combo.currentText() for number, combo in self.combo_boxes.items()}
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)
                
            # 同时保存为默认映射
            with open("zodiac_mapping.json", 'w', encoding='utf-8') as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)
                
            QMessageBox.information(self, "成功", f"生肖映射已保存为存档: {archive_name}")
            
            # 刷新存档列表
            self.refresh_archives()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存生肖映射时出错：{str(e)}")
    
    def get_mapping(self):
        """获取当前的生肖映射"""
        return {number: combo.currentText() for number, combo in self.combo_boxes.items()}

class SmartCombinationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("聪明组合工具")
        self.setModal(True)
        self.resize(800, 600)
        self.valid_combinations = []  # 保存有效组合结果
        
        layout = QVBoxLayout()
        
        # 输入区域
        input_layout = QHBoxLayout()
        input_label = QLabel("输入号码(空格分隔):")
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("例如: 1 8 12 23 31 36 42")
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_field, 1)
        
        # 组合按钮
        self.combine_button = QPushButton("生成组合")
        self.combine_button.clicked.connect(self.generate_combinations)
        input_layout.addWidget(self.combine_button)
        
        layout.addLayout(input_layout)
        
        # 结果显示区域
        result_label = QLabel("组合结果:")
        layout.addWidget(result_label)
        
        self.result_list = QListWidget()
        layout.addWidget(self.result_list)
        
        # 统计信息
        self.stats_label = QLabel("统计信息: ")
        layout.addWidget(self.stats_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 导出按钮
        self.export_button = QPushButton("导出结果")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)  # 初始时禁用
        button_layout.addWidget(self.export_button)
        
        # 关闭按钮
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def generate_combinations(self):
        """生成号码组合并应用霍华德理论过滤"""
        try:
            # 获取输入号码
            input_text = self.input_field.text().strip()
            if not input_text:
                QMessageBox.warning(self, "警告", "请输入号码")
                return
                
            # 解析号码
            try:
                numbers = [int(num) for num in input_text.split()]
                # 验证号码范围
                if any(num < 1 or num > 49 for num in numbers):
                    QMessageBox.warning(self, "警告", "号码必须在1-49之间")
                    return
                    
                # 去重
                numbers = list(set(numbers))
                numbers.sort()
                
                if len(numbers) < 7:
                    QMessageBox.warning(self, "警告", "至少需要7个不同的号码")
                    return
            except ValueError:
                QMessageBox.warning(self, "警告", "输入格式不正确，请使用空格分隔的数字")
                return
                
            # 清空结果列表
            self.result_list.clear()
            self.valid_combinations = []
            
            # 生成6个号码的组合
            all_combinations = list(itertools.combinations(numbers, 6))
            self.valid_combinations = []
            
            # 应用霍华德理论过滤
            for combo in all_combinations:
                if self.howard_filter(combo):
                    self.valid_combinations.append(combo)
                    self.result_list.addItem(" ".join(f"{num:02d}" for num in combo))
            
            # 更新统计信息
            total = len(all_combinations)
            valid = len(self.valid_combinations)
            self.stats_label.setText(f"统计信息: 共生成 {total} 种组合，其中 {valid} 种满足霍华德理论 ({valid/total*100:.1f}%)")
            
            # 如果有有效组合则启用导出按钮
            self.export_button.setEnabled(valid > 0)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成组合时出错: {str(e)}")
    
    def export_results(self):
        """导出组合结果到TXT文件"""
        if not self.valid_combinations:
            QMessageBox.warning(self, "警告", "没有可导出的结果")
            return
            
        try:
            # 获取保存文件路径
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "导出组合结果", 
                "聪明组合结果.txt", 
                "文本文件 (*.txt)"
            )
            
            if not file_path:
                return  # 用户取消了保存
                
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                # 写入标题和说明
                f.write("聪明组合结果 - 符合霍华德理论的组合\n")
                f.write("="*50 + "\n\n")
                
                # 写入输入号码
                f.write(f"输入号码: {self.input_field.text()}\n\n")
                
                # 写入统计信息
                f.write(f"{self.stats_label.text()}\n\n")
                
                # 写入组合结果
                f.write("组合列表:\n")
                for i, combo in enumerate(self.valid_combinations, 1):
                    f.write(f"{i}. {' '.join(f'{num:02d}' for num in combo)}\n")
            
            QMessageBox.information(self, "成功", f"组合结果已成功导出到:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出结果时出错: {str(e)}")
    
    def howard_filter(self, numbers):
        """应用霍华德理论过滤组合
        
        霍华德理论规则:
        1. 奇偶比例不应该是6:0或0:6
        2. 大小比例不应该是6:0或0:6
        3. 连续数字不超过3个
        4. 号码和应在某个合理范围内
        5. 同尾数不超过3个
        """
        # 奇偶比例检查
        odd_count = sum(1 for num in numbers if num % 2 == 1)
        even_count = 6 - odd_count
        if odd_count == 0 or even_count == 0:
            return False
        
        # 大小比例检查(小:1-24, 大:25-49)
        small_count = sum(1 for num in numbers if num <= 24)
        big_count = 6 - small_count
        if small_count == 0 or big_count == 0:
            return False
        
        # 连续数字检查
        sorted_nums = sorted(numbers)
        for i in range(len(sorted_nums) - 3 + 1):
            if sorted_nums[i+2] - sorted_nums[i] == 2:  # 三个连续数字
                return False
        
        # 号码和检查
        total_sum = sum(numbers)
        if total_sum < 90 or total_sum > 220:  # 号码和应在合理范围内
            return False
        
        # 同尾数检查
        tails = [num % 10 for num in numbers]
        tail_counts = {}
        for tail in tails:
            tail_counts[tail] = tail_counts.get(tail, 0) + 1
            if tail_counts[tail] > 3:  # 同尾数不超过3个
                return False
        
        return True

class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.validator = LicenseValidator()
        self.setup_ui()
        self.refresh_status()
        self.activation_success = False  # 添加激活成功标志

    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("序列号管理")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        # 服务器状态
        status_layout = QHBoxLayout()
        self.status_label = QLabel("服务器状态：")
        self.status_value = QLabel()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_value)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # 序列号输入
        input_layout = QHBoxLayout()
        self.license_label = QLabel("序列号：")
        self.license_input = QLineEdit()
        input_layout.addWidget(self.license_label)
        input_layout.addWidget(self.license_input)
        layout.addLayout(input_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        self.activate_button = QPushButton("激活")
        self.activate_button.clicked.connect(self.activate_license)
        button_layout.addWidget(self.activate_button)
        
        self.minimize_button = QPushButton("最小化")
        self.minimize_button.clicked.connect(self.showMinimized)
        button_layout.addWidget(self.minimize_button)
        
        layout.addLayout(button_layout)
        
        # 状态消息
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)
        
        self.setLayout(layout)
        
        # 加载当前序列号
        current_license = self.validator.get_current_license()
        if current_license:
            self.license_input.setText(current_license)
            
    def refresh_status(self):
        """刷新服务器状态和序列号状态"""
        # 检查服务器状态
        if self.validator.check_server_status():
            self.status_value.setText("正常")
            self.status_value.setStyleSheet("color: green")
        else:
            self.status_value.setText("离线")
            self.status_value.setStyleSheet("color: red")
            
        # 检查序列号状态
        success, message = self.validator.check_license()
        if success:
            self.message_label.setText("序列号状态：" + message)
            self.message_label.setStyleSheet("color: green")
        else:
            self.message_label.setText("序列号状态：" + message)
            self.message_label.setStyleSheet("color: red")
            
    def activate_license(self):
        """激活序列号"""
        license_str = self.license_input.text().strip()
        if not license_str:
            QMessageBox.warning(self, "错误", "请输入序列号")
            return
            
        success, message = self.validator.activate_license(license_str)
        if success:
            QMessageBox.information(self, "成功", message)
            self.refresh_status()
            self.activation_success = True  # 标记激活成功
            self.accept()  # 关闭对话框并返回Accepted
        else:
            QMessageBox.warning(self, "错误", message)
            
    def closeEvent(self, event):
        """关闭窗口时最小化到托盘"""
        event.ignore()
        self.hide()
        
    def check_current_license(self):
        """检查当前序列号状态"""
        success, message = self.validator.check_license()
        return success

class LotteryAnalyzer(QMainWindow):
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 确保程序完全退出
        reply = QMessageBox.question(self, '确认退出', '确定要退出程序吗？',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 保存当前样式设置
            settings = QSettings("CaipiaofenxiApp", "LotteryAnalyzer")
            settings.setValue("style", self.current_style)
            
            QApplication.quit()
            event.accept()
        else:
            event.ignore()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('彩票号码分析器')
        self.setGeometry(100, 100, 1000, 800)
        
        # 设置应用图标
        self.setWindowIcon(QIcon('lottery_icon.ico'))
        
        # 初始化样式设置
        self.current_style = "win11"  # 默认风格
        self.loadSettings()  # 加载用户设置
        self.applyStyle(self.current_style)  # 应用样式
        
        # 初始化状态栏
        self.statusBar().showMessage("正在检查序列号...", 2000)
        
        # 初始化序列号验证器
        self.license_validator = LicenseValidator()
        
        # 检查序列号
        self.check_license()
        
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建菜单栏
        self.createMenus()
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        self.import_btn = QPushButton('导入数据文件')
        self.analyze_range_btn = QPushButton('期数范围分析')
        self.analyze_all_btn = QPushButton('全部期数分析')
        self.predict_btn = QPushButton('生成预测')
        self.zodiac_btn = QPushButton('设置生肖映射')
        self.smart_combo_btn = QPushButton('聪明组合工具')
        self.analyze_specific_btn = QPushButton('指定年份期数分析')
        self.license_btn = QPushButton('序列号管理')  # 新增序列号管理按钮
        
        self.analyze_range_btn.setEnabled(False)
        self.analyze_all_btn.setEnabled(False)
        self.predict_btn.setEnabled(False)
        self.analyze_specific_btn.setEnabled(False)
        
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.analyze_range_btn)
        button_layout.addWidget(self.analyze_all_btn)
        button_layout.addWidget(self.analyze_specific_btn)
        button_layout.addWidget(self.predict_btn)
        button_layout.addWidget(self.zodiac_btn)
        button_layout.addWidget(self.smart_combo_btn)
        button_layout.addWidget(self.license_btn)  # 添加序列号管理按钮
        main_layout.addLayout(button_layout)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.analysis_tab = QWidget()
        self.prediction_tab = QWidget()
        self.tab_widget.addTab(self.analysis_tab, "数据分析")
        self.tab_widget.addTab(self.prediction_tab, "预测结果")
        
        # 设置分析标签页
        analysis_layout = QVBoxLayout(self.analysis_tab)
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        analysis_layout.addWidget(self.analysis_text)
        
        # 设置预测标签页
        prediction_layout = QVBoxLayout(self.prediction_tab)
        self.prediction_text = QTextEdit()
        self.prediction_text.setReadOnly(True)
        prediction_layout.addWidget(self.prediction_text)
        
        # 连接信号
        self.import_btn.clicked.connect(self.import_data)
        self.analyze_range_btn.clicked.connect(self.analyze_range_data)
        self.analyze_all_btn.clicked.connect(self.analyze_all_data)
        self.predict_btn.clicked.connect(self.generate_prediction)
        self.zodiac_btn.clicked.connect(self.set_zodiac_mapping)
        self.smart_combo_btn.clicked.connect(self.open_smart_combo_tool)
        self.analyze_specific_btn.clicked.connect(self.analyze_specific_period)
        self.license_btn.clicked.connect(self.manage_license)  # 新增序列号管理按钮信号
        
        # 初始化分析器
        self.analyzer = LotteryDataAnalyzer()
        # 自动加载默认生肖映射文件（静默加载，不显示消息框）
        dialog = ZodiacMappingDialog(self)
        dialog.load_selected_archive(silent=True)
        mapping = dialog.get_mapping()
        self.analyzer.set_zodiac_mapping(mapping)
    
    def createMenus(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        fileMenu = menubar.addMenu('文件')
        
        importAction = QAction('导入数据', self)
        importAction.triggered.connect(self.import_data)
        fileMenu.addAction(importAction)
        
        fileMenu.addSeparator()
        
        exitAction = QAction('退出', self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)
        
        # 分析菜单
        analysisMenu = menubar.addMenu('分析')
        
        allAction = QAction('全部期数分析', self)
        allAction.triggered.connect(self.analyze_all_data)
        analysisMenu.addAction(allAction)
        
        rangeAction = QAction('期数范围分析', self)
        rangeAction.triggered.connect(self.analyze_range_data)
        analysisMenu.addAction(rangeAction)
        
        specificAction = QAction('指定年份期数分析', self)
        specificAction.triggered.connect(self.analyze_specific_period)
        analysisMenu.addAction(specificAction)
        
        analysisMenu.addSeparator()
        
        predictAction = QAction('生成预测', self)
        predictAction.triggered.connect(self.generate_prediction)
        analysisMenu.addAction(predictAction)
        
        # 工具菜单
        toolsMenu = menubar.addMenu('工具')
        
        zodiacAction = QAction('设置生肖映射', self)
        zodiacAction.triggered.connect(self.set_zodiac_mapping)
        toolsMenu.addAction(zodiacAction)
        
        comboAction = QAction('聪明组合工具', self)
        comboAction.triggered.connect(self.open_smart_combo_tool)
        toolsMenu.addAction(comboAction)
        
        toolsMenu.addSeparator()
        
        licenseAction = QAction('序列号管理', self)
        licenseAction.triggered.connect(self.manage_license)
        toolsMenu.addAction(licenseAction)
        
        # 样式菜单
        styleMenu = menubar.addMenu('界面风格')
        
        win11Action = QAction('Win11风格', self)
        win11Action.triggered.connect(lambda: self.applyStyle("win11"))
        styleMenu.addAction(win11Action)
        
        neumorphismAction = QAction('拟物化设计', self)
        neumorphismAction.triggered.connect(lambda: self.applyStyle("neumorphism"))
        styleMenu.addAction(neumorphismAction)
        
        macosAction = QAction('macOS风格', self)
        macosAction.triggered.connect(lambda: self.applyStyle("macos"))
        styleMenu.addAction(macosAction)
        
        # 帮助菜单
        helpMenu = menubar.addMenu('帮助')
        
        aboutAction = QAction('关于', self)
        aboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(aboutAction)

    def loadSettings(self):
        """加载用户设置"""
        try:
            settings = QSettings("CaipiaofenxiApp", "LotteryAnalyzer")
            style = settings.value("style", "win11")
            self.current_style = style
        except Exception:
            # 如果出错，使用默认值
            self.current_style = "win11"
    
    def applyStyle(self, style_name):
        """应用样式表"""
        style_file = ""
        
        if style_name == "win11":
            style_file = "styles/win11.qss"
        elif style_name == "neumorphism":
            style_file = "styles/neumorphism.qss"
        elif style_name == "macos":
            style_file = "styles/macos.qss"
        
        try:
            # 检查样式文件是否存在
            if os.path.exists(style_file):
                with open(style_file, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
                self.current_style = style_name
                self.statusBar().showMessage(f"已应用{style_name}风格", 2000)
            else:
                self.statusBar().showMessage(f"样式文件{style_file}不存在", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"应用样式出错: {str(e)}", 2000)
    
    def showAbout(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于彩票号码分析器",
            "<h3>彩票号码分析器 v3.0</h3>"
            "<p>一款专业的彩票数据分析和预测工具。</p>"
            "<p>联系方式：814003570@qq.com</p>"
            "<p>版权所有 © 2025 吴京为</p>")
    
    def set_zodiac_mapping(self):
        """设置生肖映射"""
        dialog = ZodiacMappingDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            mapping = dialog.get_mapping()
            if self.analyzer.set_zodiac_mapping(mapping):
                QMessageBox.information(self, '成功', '生肖映射设置成功！')
            else:
                QMessageBox.critical(self, '错误', '生肖映射设置失败，请检查输入！')
    
    def import_data(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            '选择数据文件', 
            '', 
            '数据文件 (*.xlsx *.txt);;Excel文件 (*.xlsx);;文本文件 (*.txt)'
        )
        if file_name:
            try:
                success, message = self.analyzer.load_data(file_name)
                if success:
                    self.analyze_range_btn.setEnabled(True)
                    self.analyze_all_btn.setEnabled(True)
                    self.analyze_specific_btn.setEnabled(True)
                    QMessageBox.information(self, '成功', message)
                else:
                    QMessageBox.critical(self, '错误', message)
            except Exception as e:
                QMessageBox.critical(self, '错误', f'导入数据时出错：{str(e)}')
    
    def analyze_range_data(self):
        """分析指定期数范围的数据"""
        try:
            # 验证数据
            is_valid, errors = self.analyzer.validate_data()
            if not is_valid:
                QMessageBox.warning(self, '警告', '数据验证失败：\n' + '\n'.join(errors))
                return
            
            # 让用户选择分析范围
            start_period, ok = QInputDialog.getInt(
                self, '选择起始期数',
                '请输入起始期数（从0开始）：',
                value=0, min=0, max=10000
            )
            if not ok:
                return
                
            end_period, ok = QInputDialog.getInt(
                self, '选择结束期数',
                '请输入结束期数：',
                value=start_period + 50, min=start_period, max=10000
            )
            if not ok:
                return
            
            self._display_analysis_results(start_period, end_period)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'分析过程中出错：{str(e)}')
    
    def analyze_all_data(self):
        """分析全部期数的数据"""
        try:
            # 验证数据
            is_valid, errors = self.analyzer.validate_data()
            if not is_valid:
                QMessageBox.warning(self, '警告', '数据验证失败：\n' + '\n'.join(errors))
                return
            
            self._display_analysis_results()
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'分析过程中出错：{str(e)}')
    
    def _display_analysis_results(self, start_period=None, end_period=None):
        """显示分析结果"""
        try:
            # 清除之前的结果
            self.analysis_text.clear()
            
            # 分析数据
            results = self.analyzer.analyze_data(start_period=start_period, end_period=end_period)
            
            # 检查是否有错误
            if "错误" in results:
                self.analysis_text.append(f"分析出错：{results['错误']}")
                return
                
            # 显示基本信息
            if "基本信息" in results:
                self.analysis_text.append("<h3>基本信息</h3>")
                for key, value in results["基本信息"].items():
                    self.analysis_text.append(f"{key}: {value}")
                self.analysis_text.append("")
            
            # 显示号码频率（仅显示前10个）
            try:
                if "号码统计" in results and "频率" in results["号码统计"]:
                    if isinstance(results["号码统计"]["频率"], dict) and results["号码统计"]["频率"]:
                        self.analysis_text.append("<h3>号码频率（前10名）</h3>")
                        # 排序并获取前10个
                        sorted_freq = sorted(results["号码统计"]["频率"].items(), key=lambda x: x[1], reverse=True)[:10]
                        
                        for num, freq in sorted_freq:
                            try:
                                if isinstance(num, int) and isinstance(freq, (int, float)):
                                    zodiac = self.analyzer.get_number_zodiac(num)
                                    self.analysis_text.append(f"号码 {num:02d} ({zodiac}): {freq}次")
                            except:
                                continue
                                
                        self.analysis_text.append("")
                    elif isinstance(results["号码统计"]["频率"], dict) and "错误" in results["号码统计"]["频率"]:
                        self.analysis_text.append("<h3>号码频率</h3>")
                        self.analysis_text.append(f"统计出错：{results['号码统计']['频率']['错误']}")
                        self.analysis_text.append("")
            except Exception as e:
                self.analysis_text.append("<h3>号码频率</h3>")
                self.analysis_text.append(f"显示出错：{str(e)}")
                self.analysis_text.append("")
            
            # 显示生肖频率
            try:
                if "生肖分析" in results and "频率" in results["生肖分析"]:
                    if isinstance(results["生肖分析"]["频率"], dict) and results["生肖分析"]["频率"]:
                        self.analysis_text.append("<h3>生肖频率</h3>")
                        for zodiac, freq in sorted(results["生肖分析"]["频率"].items(), key=lambda x: x[1], reverse=True):
                            try:
                                if isinstance(zodiac, str) and isinstance(freq, (int, float)):
                                    self.analysis_text.append(f"{zodiac}: {freq}次")
                            except:
                                continue
                                
                        self.analysis_text.append("")
                    elif isinstance(results["生肖分析"]["频率"], dict) and "错误" in results["生肖分析"]["频率"]:
                        self.analysis_text.append("<h3>生肖频率</h3>")
                        self.analysis_text.append(f"统计出错：{results['生肖分析']['频率']['错误']}")
                        self.analysis_text.append("")
            except Exception as e:
                self.analysis_text.append("<h3>生肖频率</h3>")
                self.analysis_text.append(f"显示出错：{str(e)}")
                self.analysis_text.append("")
            
            # 其他分析结果（如果可用）
            try:
                # 列分析
                if "列分析" in results and isinstance(results["列分析"], dict):
                    if "信息" in results["列分析"]:
                        self.analysis_text.append("<h3>列分析</h3>")
                        self.analysis_text.append(results["列分析"]["信息"])
                        self.analysis_text.append("")
                    else:
                        self.analysis_text.append("<h3>列分析</h3>")
                        # 仅显示第7列（特别号码）
                        if "第7列" in results["列分析"]:
                            for key, value in results["列分析"]["第7列"].items():
                                self.analysis_text.append(f"特别号码 - {key}: {value}")
                        self.analysis_text.append("")
                
                # 组合模式
                if "模式分析" in results and "组合模式" in results["模式分析"]:
                    if "信息" in results["模式分析"]["组合模式"]:
                        self.analysis_text.append("<h3>组合模式分析</h3>")
                        self.analysis_text.append(results["模式分析"]["组合模式"]["信息"])
                        self.analysis_text.append("")
                    else:
                        self.analysis_text.append("<h3>组合模式分析</h3>")
                        # 奇偶比例
                        if "奇偶比例" in results["模式分析"]["组合模式"]:
                            self.analysis_text.append("<b>奇偶比例</b>")
                            for ratio, percentage in sorted(results["模式分析"]["组合模式"]["奇偶比例"].items(), key=lambda x: x[1], reverse=True)[:3]:
                                self.analysis_text.append(f"{ratio}: {percentage}%")
                            self.analysis_text.append("")
                            
                        # 大小比例
                        if "大小比例" in results["模式分析"]["组合模式"]:
                            self.analysis_text.append("<b>大小比例</b>")
                            for ratio, percentage in sorted(results["模式分析"]["组合模式"]["大小比例"].items(), key=lambda x: x[1], reverse=True)[:3]:
                                self.analysis_text.append(f"{ratio}: {percentage}%")
                            self.analysis_text.append("")
                
                # 特别号码
                if "模式分析" in results and "特别号码" in results["模式分析"]:
                    if "信息" in results["模式分析"]["特别号码"]:
                        self.analysis_text.append("<h3>特别号码分析</h3>")
                        self.analysis_text.append(results["模式分析"]["特别号码"]["信息"])
                        self.analysis_text.append("")
                    elif "出现频率最高的号码" in results["模式分析"]["特别号码"]:
                        self.analysis_text.append("<h3>特别号码分析</h3>")
                        self.analysis_text.append("<b>出现频率最高的号码</b>")
                        for num, freq in results["模式分析"]["特别号码"]["出现频率最高的号码"].items():
                            try:
                                if isinstance(num, int):
                                    zodiac = self.analyzer.get_number_zodiac(num)
                                    self.analysis_text.append(f"{num:02d} ({zodiac}): {freq}次")
                            except:
                                # 如果不是整数键，直接显示
                                self.analysis_text.append(f"{num}: {freq}")
                        self.analysis_text.append("")
            except Exception as e:
                self.analysis_text.append("<h3>其他分析结果</h3>")
                self.analysis_text.append(f"显示出错：{str(e)}")
                self.analysis_text.append("")
            
            # 启用预测按钮
            self.predict_btn.setEnabled(True)
            # 显示在分析标签页
            self.tab_widget.setCurrentIndex(0)
            
        except Exception as e:
            # 处理任何其他异常
            self.analysis_text.clear()
            self.analysis_text.append(f"显示分析结果时出错：{str(e)}")
            import traceback
            traceback.print_exc()
            return
    
    def generate_prediction(self):
        try:
            # 检查是否有分析结果
            if not hasattr(self.analyzer, 'analysis_results') or not self.analyzer.analysis_results:
                QMessageBox.warning(self, '警告', '请先进行数据分析（期数范围分析/全部期数分析/指定年份期数分析）')
                return
                
            predictions = self.analyzer.get_prediction()
            
            # 显示预测结果
            self.prediction_text.clear()
            
            # 添加数据来源信息
            self.prediction_text.append("<h3>预测数据来源</h3>")
            
            # 显示分析数据的文件名
            if hasattr(self.analyzer, 'last_loaded_file'):
                file_name = os.path.basename(self.analyzer.last_loaded_file)
                self.prediction_text.append(f"数据文件: {file_name}")
            
            # 显示分析数据范围（从基本信息中获取）
            if "基本信息" in self.analyzer.analysis_results:
                basic_info = self.analyzer.analysis_results["基本信息"]
                
                # 显示总行数和分析时间
                if "总行数" in basic_info:
                    self.prediction_text.append(f"分析数据总量: {basic_info['总行数']}期")
                    
                if "分析时间" in basic_info:
                    self.prediction_text.append(f"分析时间: {basic_info['分析时间']}")
                    
                # 显示数据范围（如果有）
                if "数据范围" in basic_info:
                    self.prediction_text.append(f"数据索引范围: {basic_info['数据范围']}")
            
            # 从分析文本中提取区间信息
            analysis_text = self.analysis_text.toPlainText()
            for line in analysis_text.split('\n'):
                if line.startswith("分析区间:"):
                    self.prediction_text.append(line)
                    break
            
            self.prediction_text.append("\n")
            
            # 显示号码概率排序（横向排列）
            self.prediction_text.append("<h3>号码出现概率排序（从高到低）</h3>")
            number_freq = self.analyzer.analysis_results["号码统计"]["频率"]
            sorted_numbers = sorted(number_freq.items(), key=lambda x: x[1], reverse=True)
            
            # 每行显示7个号码
            for i in range(0, len(sorted_numbers), 7):
                line = ""
                for num, freq in sorted_numbers[i:i+7]:
                    zodiac = self.analyzer.get_number_zodiac(num)
                    line += f"{num:02d}({zodiac})({freq}) "
                self.prediction_text.append(line.strip())
            
            self.prediction_text.append("\n" + "="*50 + "\n")
            
            # 显示预测号码
            self.prediction_text.append("<h3>预测号码组合</h3>")
            for i, pred in enumerate(predictions, 1):
                self.prediction_text.append(f'第{i}组预测号码：')
                normal_zodiacs = [self.analyzer.get_number_zodiac(n) for n in pred[:6]]
                special_zodiac = self.analyzer.get_number_zodiac(pred[6])
                self.prediction_text.append(f'普通号码：{[f"{n:02d}({z})" for n, z in zip(pred[:6], normal_zodiacs)]}')
                self.prediction_text.append(f'特别号码：{pred[6]:02d}({special_zodiac})')
                self.prediction_text.append('-' * 30)
            
            # 切换到预测标签页
            self.tab_widget.setCurrentWidget(self.prediction_tab)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'生成预测时出错：{str(e)}')

    def open_smart_combo_tool(self):
        """打开聪明组合工具"""
        dialog = SmartCombinationDialog(self)
        dialog.exec_()

    def analyze_specific_period(self):
        """分析特定年份和期数的数据"""
        try:
            # 验证是否已加载数据
            if self.analyzer.data is None:
                QMessageBox.warning(self, '警告', '请先导入数据文件！')
                return
                
            # 验证数据
            is_valid, errors = self.analyzer.validate_data()
            if not is_valid:
                QMessageBox.warning(self, '警告', '数据验证失败：\n' + '\n'.join(errors))
                return
            
            # 创建一个对话框获取年份和期数
            dialog = QDialog(self)
            dialog.setWindowTitle("指定年份期数")
            dialog.setModal(True)
            
            layout = QVBoxLayout()
            
            # 显示已加载的文件信息
            if hasattr(self.analyzer, 'last_loaded_file'):
                file_info = QLabel(f"当前加载文件: {os.path.basename(self.analyzer.last_loaded_file)}")
                file_info.setStyleSheet("color: blue;")
                layout.addWidget(file_info)
                
                # 显示数据行数信息
                if self.analyzer.data is not None:
                    rows_info = QLabel(f"数据行数: {len(self.analyzer.data)}")
                    rows_info.setStyleSheet("color: blue;")
                    layout.addWidget(rows_info)
            
            # 年份输入
            year_layout = QHBoxLayout()
            year_label = QLabel("年份:")
            year_input = QLineEdit()
            year_input.setPlaceholderText("例如: 2015（不需要前导零）")
            year_layout.addWidget(year_label)
            year_layout.addWidget(year_input)
            layout.addLayout(year_layout)
            
            # 期数输入
            period_layout = QHBoxLayout()
            period_label = QLabel("期数:")
            period_input = QLineEdit()
            period_input.setPlaceholderText("例如: 34（不需要前导零）")
            period_layout.addWidget(period_label)
            period_layout.addWidget(period_input)
            layout.addLayout(period_layout)
            
            # 分析区间设置
            range_layout = QHBoxLayout()
            range_label = QLabel("分析区间:")
            layout.addWidget(QLabel("请设置分析区间:"))
            
            # 向前分析期数
            backward_layout = QHBoxLayout()
            backward_label = QLabel("向前分析期数:")
            backward_input = QLineEdit()
            backward_input.setPlaceholderText("例如: 9（默认）")
            backward_input.setText("9")  # 默认值
            backward_layout.addWidget(backward_label)
            backward_layout.addWidget(backward_input)
            layout.addLayout(backward_layout)
            
            # 向后分析期数
            forward_layout = QHBoxLayout()
            forward_label = QLabel("向后分析期数:")
            forward_input = QLineEdit()
            forward_input.setPlaceholderText("例如: 0（默认）")
            forward_input.setText("0")  # 默认值
            forward_layout.addWidget(forward_label)
            forward_layout.addWidget(forward_input)
            layout.addLayout(forward_layout)
            
            # 说明文字
            info_label = QLabel("将分析指定期数及区间内的数据\n数据格式例如：2015年034期:03月27日:10-49-47-19-44-35特15")
            layout.addWidget(info_label)
            
            # 按钮
            button_layout = QHBoxLayout()
            ok_button = QPushButton("确定")
            ok_button.clicked.connect(dialog.accept)
            cancel_button = QPushButton("取消")
            cancel_button.clicked.connect(dialog.reject)
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            # 显示对话框
            if dialog.exec_() == QDialog.Accepted:
                # 获取输入的年份和期数
                try:
                    # 验证输入
                    year_text = year_input.text().strip()
                    period_text = period_input.text().strip()
                    backward_text = backward_input.text().strip()
                    forward_text = forward_input.text().strip()
                    
                    if not year_text or not period_text:
                        QMessageBox.warning(self, '警告', '请输入年份和期数')
                        return
                        
                    year = int(year_text)
                    period = int(period_text)
                    
                    # 解析分析区间
                    backward = 9  # 默认向前9期
                    forward = 0   # 默认向后0期
                    
                    if backward_text:
                        try:
                            backward = int(backward_text)
                            if backward < 0:
                                QMessageBox.warning(self, '警告', '向前分析期数不能为负数')
                                return
                        except ValueError:
                            QMessageBox.warning(self, '警告', '请输入有效的向前分析期数')
                            return
                    
                    if forward_text:
                        try:
                            forward = int(forward_text)
                            if forward < 0:
                                QMessageBox.warning(self, '警告', '向后分析期数不能为负数')
                                return
                        except ValueError:
                            QMessageBox.warning(self, '警告', '请输入有效的向后分析期数')
                            return
                    
                    if year < 1900 or year > 2100:
                        QMessageBox.warning(self, '警告', '请输入有效的年份 (1900-2100)')
                        return
                        
                    if period < 1 or period > 999:
                        QMessageBox.warning(self, '警告', '请输入有效的期数 (1-999)')
                        return
                    
                    # 显示正在分析的提示
                    self.analysis_text.clear()
                    self.analysis_text.append(f"正在查找{year}年第{period:03d}期数据...")
                    QApplication.processEvents()  # 确保UI更新
                    
                    # 查找数据中对应的期数
                    period_index = self.analyzer.find_period_index(year, period)
                    
                    if period_index is None:
                        # 如果找不到期数，不再尝试使用期数作为索引，而是直接提示未找到
                        QMessageBox.warning(self, '警告', f'导入数据未找到对应内容: {year}年 第{period:03d}期')
                        self.analysis_text.append(f"导入数据中未找到 {year}年 第{period:03d}期 的数据")
                        self.analysis_text.append("请检查导入的数据文件是否包含所需期数，或使用其他分析功能。")
                        return
                    
                    # 计算起始和结束期数索引
                    start_index = max(0, period_index - backward)  # 确保不小于0
                    end_index = min(len(self.analyzer.data), period_index + forward + 1)  # 确保不超过数据范围
                    
                    # 显示正在分析的提示
                    self.analysis_text.append(f"找到期数索引: {period_index}")
                    self.analysis_text.append(f"分析范围: 索引 {start_index} 到 {end_index-1} (共{end_index-start_index}期)")
                    QApplication.processEvents()  # 确保UI更新
                    
                    # 显示分析结果
                    try:
                        self._display_analysis_results(start_index, end_index)
                        
                        # 显示分析区间信息
                        starting_period = max(1, period - backward)
                        ending_period = period + forward
                        
                        if backward > 0 and forward > 0:
                            self.analysis_text.append(f"分析区间: 从第 {starting_period:03d}期 到第 {ending_period:03d}期，共{backward+forward+1}期数据")
                        elif backward > 0:
                            self.analysis_text.append(f"分析区间: 从第 {starting_period:03d}期 到第 {period:03d}期，共{backward+1}期数据")
                        elif forward > 0:
                            self.analysis_text.append(f"分析区间: 从第 {period:03d}期 到第 {ending_period:03d}期，共{forward+1}期数据")
                        else:
                            self.analysis_text.append(f"分析区间: 仅第 {period:03d}期")
                    except Exception as e:
                        # 如果显示结果时出错，给出友好的提示
                        self.analysis_text.clear()
                        self.analysis_text.append(f"分析过程中出错：{str(e)}")
                        self.analysis_text.append("\n请尝试使用'全部期数分析'功能，或联系技术支持。")
                    
                except ValueError:
                    QMessageBox.warning(self, '警告', '请输入有效的数字')
                    return
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'分析特定期数时出错：{str(e)}')

    def manage_license(self):
        """管理序列号"""
        dialog = LicenseDialog(self)
        result = dialog.exec_()
        
        # 如果激活成功，显示成功消息
        if result == QDialog.Accepted and dialog.activation_success:
            self.statusBar().showMessage("序列号已成功激活", 5000)
        
        # 检查序列号状态
        success, message = self.license_validator.check_license()
        if not success:
            reply = QMessageBox.question(
                self,
                "序列号无效",
                "序列号无效或已过期，您想现在激活一个有效的序列号吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # 再次打开序列号对话框
                self.manage_license()
            else:
                # 用户选择不激活，提醒功能限制
                QMessageBox.warning(
                    self,
                    "功能限制",
                    "没有有效的序列号，部分功能将被限制使用"
                )

    def check_license(self):
        """检查序列号状态"""
        success, message = self.license_validator.check_license()
        if not success:
            # 检查是否有本地序列号文件
            if os.path.exists(self.license_validator.license_file):
                try:
                    # 如果有本地序列号文件，尝试重新激活
                    with open(self.license_validator.license_file, 'r') as f:
                        license_data = json.load(f)
                        license_str = license_data.get('license')
                    if license_str:
                        success, message = self.license_validator.activate_license(license_str)
                        if success:
                            return
                except Exception as e:
                    print(f"读取序列号文件失败: {str(e)}")
                    
            # 如果验证失败或没有本地序列号，显示验证对话框
            dialog = LicenseDialog(self)
            result = dialog.exec_()
            if result == QDialog.Accepted and dialog.activation_success:
                # 如果用户成功激活了序列号，继续程序
                return
            elif result == QDialog.Rejected:
                # 如果用户点击关闭或取消，退出程序
                sys.exit()
                
            # 再次检查许可证状态
            success, message = self.license_validator.check_license()
            if not success:
                QMessageBox.critical(self, "错误", "序列号验证失败，程序将退出")
                sys.exit()
        else:
            # 如果验证成功，显示成功消息，但不弹窗干扰用户
            self.statusBar().showMessage(f"序列号状态: {message}", 5000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 设置默认字体
    default_font = QFont("Microsoft YaHei", 9)  # 使用微软雅黑作为默认字体
    app.setFont(default_font)
    
    # 创建并显示主窗口
    window = LotteryAnalyzer()
    window.show()
    
    sys.exit(app.exec_())