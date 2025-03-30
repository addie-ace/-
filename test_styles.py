#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QWidget, QLabel, QComboBox, QHBoxLayout, QTabWidget, 
                           QTextEdit, QCheckBox, QRadioButton, QGroupBox, 
                           QProgressBar, QSlider, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class StyleDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('样式表测试器')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('lottery_icon.ico'))
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 样式选择器
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("选择样式:"))
        
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Win11风格", "拟物化设计", "macOS风格"])
        self.style_combo.currentIndexChanged.connect(self.change_style)
        style_layout.addWidget(self.style_combo)
        style_layout.addStretch()
        
        main_layout.addLayout(style_layout)
        
        # 创建标签页
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 基本控件标签页
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        tab_widget.addTab(basic_tab, "基本控件")
        
        # 按钮控件
        button_group = QGroupBox("按钮控件")
        button_layout = QVBoxLayout(button_group)
        
        normal_btn = QPushButton("普通按钮")
        hover_btn = QPushButton("悬停按钮 (将鼠标放在这里)")
        disabled_btn = QPushButton("禁用按钮")
        disabled_btn.setEnabled(False)
        
        button_layout.addWidget(normal_btn)
        button_layout.addWidget(hover_btn)
        button_layout.addWidget(disabled_btn)
        
        basic_layout.addWidget(button_group)
        
        # 文本输入控件
        input_group = QGroupBox("文本输入")
        input_layout = QVBoxLayout(input_group)
        
        input_layout.addWidget(QLabel("单行文本输入:"))
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("请输入文本...")
        input_layout.addWidget(line_edit)
        
        input_layout.addWidget(QLabel("多行文本输入:"))
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("这是一个可以输入多行文本的区域...")
        input_layout.addWidget(text_edit)
        
        basic_layout.addWidget(input_group)
        
        # 选择控件标签页
        selection_tab = QWidget()
        selection_layout = QVBoxLayout(selection_tab)
        tab_widget.addTab(selection_tab, "选择控件")
        
        # 下拉框
        combo_group = QGroupBox("下拉框")
        combo_layout = QVBoxLayout(combo_group)
        
        combo = QComboBox()
        combo.addItems(["选项1", "选项2", "选项3", "选项4", "选项5"])
        combo_layout.addWidget(combo)
        
        selection_layout.addWidget(combo_group)
        
        # 复选框
        check_group = QGroupBox("复选框")
        check_layout = QVBoxLayout(check_group)
        
        check1 = QCheckBox("选项A")
        check2 = QCheckBox("选项B")
        check3 = QCheckBox("选项C (已选)")
        check3.setChecked(True)
        check4 = QCheckBox("禁用选项")
        check4.setEnabled(False)
        
        check_layout.addWidget(check1)
        check_layout.addWidget(check2)
        check_layout.addWidget(check3)
        check_layout.addWidget(check4)
        
        selection_layout.addWidget(check_group)
        
        # 单选框
        radio_group = QGroupBox("单选框")
        radio_layout = QVBoxLayout(radio_group)
        
        radio1 = QRadioButton("选项一")
        radio2 = QRadioButton("选项二")
        radio3 = QRadioButton("选项三 (已选)")
        radio3.setChecked(True)
        radio4 = QRadioButton("禁用选项")
        radio4.setEnabled(False)
        
        radio_layout.addWidget(radio1)
        radio_layout.addWidget(radio2)
        radio_layout.addWidget(radio3)
        radio_layout.addWidget(radio4)
        
        selection_layout.addWidget(radio_group)
        
        # 滑块和进度条标签页
        progress_tab = QWidget()
        progress_layout = QVBoxLayout(progress_tab)
        tab_widget.addTab(progress_tab, "进度控件")
        
        # 滑块
        slider_group = QGroupBox("滑块")
        slider_layout = QVBoxLayout(slider_group)
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        
        slider_layout.addWidget(slider)
        progress_layout.addWidget(slider_group)
        
        # 进度条
        progress_group = QGroupBox("进度条")
        progress_group_layout = QVBoxLayout(progress_group)
        
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(75)
        
        progress_group_layout.addWidget(progress)
        progress_layout.addWidget(progress_group)
        
        # 初始应用默认样式
        self.change_style(0)
        
    def change_style(self, index):
        """更改样式表"""
        style_file = ""
        
        if index == 0:  # Win11风格
            style_file = "styles/win11.qss"
        elif index == 1:  # 拟物化设计
            style_file = "styles/neumorphism.qss"
        elif index == 2:  # macOS风格
            style_file = "styles/macos.qss"
        
        try:
            # 检查样式文件是否存在
            if os.path.exists(style_file):
                with open(style_file, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
                self.statusBar().showMessage(f"已应用{self.style_combo.currentText()}", 2000)
            else:
                self.statusBar().showMessage(f"样式文件{style_file}不存在", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"应用样式出错: {str(e)}", 2000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 设置默认字体
    default_font = QFont("Microsoft YaHei", 9)
    app.setFont(default_font)
    
    window = StyleDemo()
    window.show()
    
    sys.exit(app.exec_())