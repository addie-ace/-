import pandas as pd
import numpy as np
from typing import Tuple, List, Dict
import json
from datetime import datetime
import os
import re

class LotteryDataAnalyzer:
    def __init__(self):
        self.valid_range = range(1, 50)
        self.data = None
        self.analysis_results = {}
        self.zodiac_mapping = {}  # 存储生肖映射
        # 自动加载默认生肖映射文件
        if os.path.exists("zodiac_mapping.json"):
            try:
                with open("zodiac_mapping.json", 'r', encoding='utf-8') as f:
                    self.zodiac_mapping = json.load(f)
            except Exception as e:
                print(f"加载默认生肖映射文件时出错：{str(e)}")

        
    def load_data(self, file_path: str) -> Tuple[bool, str]:
        """加载数据文件（支持Excel、TXT和特定格式文本）"""
        try:
            # 保存最后加载的文件路径
            self.last_loaded_file = file_path
            
            if file_path.lower().endswith('.xlsx'):
                # 读取Excel文件
                self.data = pd.read_excel(file_path, engine='openpyxl')
                print(f"从Excel加载了 {len(self.data)} 行数据")
            elif file_path.lower().endswith('.txt'):
                # 以二进制方式读取，避免编码问题
                parsed_data = []
                
                # 支持的编码列表，增加ANSI编码（实际是Windows-1252或cp1252）
                encodings = ['utf-8', 'gbk', 'gb2312', 'cp1252', 'windows-1252', 'latin1', 'ISO-8859-1']
                lines = None
                encoding_used = None
                
                # 尝试所有可能的编码
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            lines = f.readlines()
                            encoding_used = encoding
                            print(f"使用 {encoding} 成功读取了 {len(lines)} 行原始数据")
                            break
                    except UnicodeDecodeError:
                        continue
                
                # 如果所有编码都失败，尝试二进制读取
                if lines is None:
                    try:
                        with open(file_path, 'rb') as f:
                            binary_content = f.read()
                        
                        # 尝试使用错误忽略模式
                        content = binary_content.decode('latin1', errors='ignore')
                        lines = content.splitlines()
                        encoding_used = 'latin1 (忽略错误)'
                        print(f"使用 {encoding_used} 读取了 {len(lines)} 行原始数据")
                    except Exception as e:
                        return False, f"无法读取文件: {str(e)}"
                
                # 解析每一行数据
                for line in lines:
                    line = line.strip()
                    if not line or len(line) < 10:  # 跳过空行和太短的行
                        continue
                    
                    try:
                        # 识别这一行是否包含预期的数据
                        if ':' in line:
                            # 按照冒号分割
                            parts = line.split(':')
                            if len(parts) >= 3:  # 期数:日期:号码
                                numbers_part = parts[-1]
                            elif len(parts) == 2:  # 期数:号码
                                numbers_part = parts[1]
                            else:
                                numbers_part = line
                        else:
                            numbers_part = line
                        
                        # 查找分隔普通号码和特别号码的标记
                        special_mark = None
                        for mark in ['特', '+', '/', '|', '\\']:
                            if mark in numbers_part:
                                special_mark = mark
                                break
                        
                        # 提取数字
                        all_numbers = []
                        if special_mark:
                            # 分割普通号码和特别号码
                            try:
                                normal_str, special_str = numbers_part.split(special_mark)
                                # 提取普通号码
                                normal_numbers = [int(n) for n in re.findall(r'\d+', normal_str)]
                                # 提取特别号码
                                special_number = int(re.findall(r'\d+', special_str)[0])
                                # 组合所有号码
                                all_numbers = normal_numbers + [special_number]
                            except:
                                # 如果失败，尝试直接提取所有数字
                                all_numbers = [int(n) for n in re.findall(r'\d+', numbers_part)]
                        else:
                            # 直接提取所有数字
                            all_numbers = [int(n) for n in re.findall(r'\d+', numbers_part)]
                        
                        # 过滤有效的号码（1-49之间）
                        valid_numbers = [n for n in all_numbers if 1 <= n <= 49]
                        
                        # 我们期望有7个有效数字
                        if len(valid_numbers) >= 7:
                            row_data = valid_numbers[:7]
                            parsed_data.append(row_data)
                    except Exception as e:
                        print(f"解析行时出错: {line}, 错误: {str(e)}")
                        continue
                
                print(f"成功解析了 {len(parsed_data)} 行数据")
                
                # 创建DataFrame
                if parsed_data:
                    self.data = pd.DataFrame(parsed_data)
                    # 重命名列
                    self.data.columns = range(len(self.data.columns))
                else:
                    return False, f"未能从文件中解析出有效数据 (尝试使用编码: {encoding_used})"
            else:
                return False, "不支持的文件格式，请使用.xlsx或.txt文件"
            
            # 验证数据是否成功加载
            if self.data is None or len(self.data) == 0:
                return False, "未能加载数据或数据为空"
                
            print(f"数据加载完成，共 {len(self.data)} 行")
            return True, f"数据加载成功，共 {len(self.data)} 行"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"数据加载失败：{str(e)}"
    
    def validate_data(self) -> Tuple[bool, List[str]]:
        """验证数据格式"""
        errors = []
        if self.data is None:
            errors.append("未加载数据")
            return False, errors
            
        try:
            # 检查列数
            if len(self.data.columns) != 7:
                errors.append(f"列数不正确：期望7列，实际{len(self.data.columns)}列")
            
            # 检查数据类型
            for col in self.data.columns:
                if not pd.api.types.is_numeric_dtype(self.data[col]):
                    errors.append(f"第{col+1}列包含非数字数据")
            
            # 检查数值范围
            for col in self.data.columns:
                invalid_numbers = self.data[~self.data[col].between(1, 49)]
                if not invalid_numbers.empty:
                    errors.append(f"第{col+1}列包含超出范围(1-49)的数值")
            
            # 检查每行是否有重复值
            for idx, row in self.data.iterrows():
                row_numbers = row.values
                if len(set(row_numbers)) != 7:
                    errors.append(f"第{idx+1}行包含重复的号码")
            
            # 检查是否为空
            if self.data.empty:
                errors.append("数据为空")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"验证过程出错：{str(e)}")
            return False, errors
    
    def set_zodiac_mapping(self, mapping: Dict[int, str]) -> bool:
        """设置生肖映射"""
        try:
            # 验证映射是否完整
            if len(mapping) != 49:
                return False
            # 验证所有号码是否在有效范围内
            if not all(1 <= num <= 49 for num in mapping.keys()):
                return False
            # 验证生肖是否有效
            valid_zodiacs = {'鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪'}
            if not all(zodiac in valid_zodiacs for zodiac in mapping.values()):
                return False
            
            # 保存映射
            self.zodiac_mapping = mapping
            try:
                with open("zodiac_mapping.json", 'w', encoding='utf-8') as f:
                    json.dump(mapping, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"保存生肖映射时出错：{str(e)}")
                return False
        except Exception:
            return False
    
    def get_number_zodiac(self, number: int) -> str:
        """获取号码对应的生肖"""
        return self.zodiac_mapping.get(number, "未知")
    
    def analyze_data(self, num_periods: int = None, start_period: int = None, end_period: int = None) -> Dict:
        """分析数据模式
        
        Args:
            num_periods: 要分析的期数，如果为None则分析所有数据
            start_period: 起始期数，如果为None则从头开始分析
            end_period: 结束期数，如果为None则分析到最后
        """
        if self.data is None:
            return {"错误": "未加载数据"}
        
        # 创建数据副本，避免修改原始数据
        data_to_analyze = self.data.copy()
            
        # 如果指定了期数范围，按范围分析数据
        if start_period is not None and end_period is not None:
            if start_period > end_period:
                start_period, end_period = end_period, start_period
            if start_period < 0:
                start_period = 0
            if end_period > len(data_to_analyze):
                end_period = len(data_to_analyze)
            data_to_analyze = data_to_analyze.iloc[start_period:end_period].copy()
        # 如果指定了期数，只分析最近的n期数据
        elif num_periods is not None and num_periods > 0:
            if num_periods > len(data_to_analyze):
                num_periods = len(data_to_analyze)
            data_to_analyze = data_to_analyze.iloc[-num_periods:].copy()
            
        try:
            analysis = {
                "基本信息": {
                    "总行数": int(len(data_to_analyze)),
                    "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "号码统计": {},
                "列分析": {},
                "模式分析": {"特别号码": {}},
                "生肖分析": {}
            }
            
            # 只有在数据非空时添加数据范围信息
            if not data_to_analyze.empty and len(data_to_analyze.index) > 0:
                try:
                    analysis["基本信息"]["数据范围"] = f"0 - {len(data_to_analyze) - 1}"
                except:
                    pass
            
            # 号码频率分析
            try:
                # 分析每个号码的出现频率
                all_numbers = data_to_analyze.values.flatten()
                number_freq = {}
                for num in all_numbers:
                    if not pd.isna(num):
                        try:
                            num_int = int(num)
                            number_freq[num_int] = number_freq.get(num_int, 0) + 1
                        except:
                            pass
                
                analysis["号码统计"]["频率"] = number_freq
            except Exception as e:
                analysis["号码统计"]["频率"] = {"错误": f"统计号码频率时出错: {str(e)}"}
            
            # 生肖频率分析
            try:
                zodiac_freq = {}
                for num, freq in number_freq.items():
                    if isinstance(num, int) and 1 <= num <= 49:
                        zodiac = self.get_number_zodiac(num)
                        zodiac_freq[zodiac] = zodiac_freq.get(zodiac, 0) + freq
                analysis["生肖分析"]["频率"] = zodiac_freq
            except Exception as e:
                analysis["生肖分析"]["频率"] = {"错误": f"统计生肖频率时出错: {str(e)}"}
            
            # 列分析
            try:
                self._analyze_columns(data_to_analyze, analysis)
            except Exception as e:
                analysis["列分析"] = {"错误": f"列分析时出错: {str(e)}"}
            
            # 特别号码分析
            try:
                self._analyze_special_numbers(data_to_analyze, analysis)
            except Exception as e:
                analysis["模式分析"]["特别号码"] = {"错误": f"特别号码分析时出错: {str(e)}"}
            
            # 组合模式分析
            try:
                self._analyze_combinations_for_data(data_to_analyze, analysis)
            except Exception as e:
                analysis["模式分析"]["组合模式"] = {"错误": f"组合模式分析时出错: {str(e)}"}
            
            self.analysis_results = analysis
            return analysis
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"错误": f"分析过程中出错：{str(e)}"}
    
    def _analyze_consecutive_patterns(self, series: pd.Series) -> Dict:
        """分析连续出现模式"""
        try:
            # 检查输入
            if series is None or len(series) == 0:
                return {"错误": "没有数据可分析"}
                
            # 确保没有NaN值
            series = series.dropna()
            if len(series) == 0:
                return {"错误": "数据全为NaN"}
                
            if len(series) == 1:
                # 只有一条数据
                return {
                    "连续出现次数": {int(series.iloc[0]): 1},
                    "最长连续": 1
                }
                
            patterns = {
                "连续出现次数": {},
                "最长连续": 1
            }
            
            # 获取第一个有效值
            try:
                current_number = int(series.iloc[0])
            except (ValueError, TypeError):
                return {"错误": "无法获取有效的起始值"}
                
            consecutive_count = 1
            max_consecutive = 1
            
            # 分析连续出现
            for num in series.iloc[1:]:
                try:
                    # 尝试将数据转换为整数
                    num_int = int(num)
                    
                    if num_int == current_number:
                        consecutive_count += 1
                        max_consecutive = max(max_consecutive, consecutive_count)
                        patterns["连续出现次数"][current_number] = max(
                            patterns["连续出现次数"].get(current_number, 0),
                            consecutive_count
                        )
                    else:
                        current_number = num_int
                        consecutive_count = 1
                except (ValueError, TypeError):
                    # 跳过非整数值
                    consecutive_count = 1
                    continue
            
            patterns["最长连续"] = max_consecutive
            return patterns
            
        except Exception as e:
            # 出错时返回错误信息
            return {"错误": f"分析连续模式时出错: {str(e)}"}
            
    def _analyze_intervals(self, series: pd.Series) -> Dict:
        """分析号码间隔"""
        try:
            if series is None or len(series) <= 1:
                return {"说明": "数据不足，无法分析间隔"}
                
            # 确保没有NaN值
            series = series.dropna()
            if len(series) <= 1:
                return {"说明": "有效数据不足，无法分析间隔"}
                
            intervals = {}
            for num in range(1, 50):
                try:
                    # 找出该号码出现的位置
                    positions = series[series == num].index
                    
                    if len(positions) > 1:
                        # 计算间隔
                        gaps = [int(positions[i+1] - positions[i]) for i in range(len(positions)-1)]
                        
                        # 统计间隔信息
                        intervals[num] = {
                            "平均间隔": float(round(np.mean(gaps), 2)),
                            "最大间隔": int(max(gaps)),
                            "最小间隔": int(min(gaps)),
                            "间隔标准差": float(round(np.std(gaps), 2)) if len(gaps) > 1 else 0.0
                        }
                except Exception as e:
                    # 忽略单个号码的错误
                    continue
                    
            return intervals
            
        except Exception as e:
            # 出错时返回错误信息
            return {"错误": f"分析间隔时出错: {str(e)}"}
    
    def _analyze_columns(self, data, analysis):
        """分析每列的统计信息"""
        if data is None or data.empty:
            analysis["列分析"] = {"信息": "没有数据可分析"}
            return
            
        try:
            for col in data.columns:
                try:
                    # 检查是否有NaN值
                    col_data = data[col].dropna()
                    if len(col_data) == 0:
                        continue
                    
                    col_stats = {
                        "平均值": float(round(col_data.mean(), 2)),
                        "标准差": float(round(col_data.std(), 2)) if len(col_data) > 1 else 0.0,
                        "最小值": int(col_data.min()) if not pd.isna(col_data.min()) else 0,
                        "最大值": int(col_data.max()) if not pd.isna(col_data.max()) else 0,
                        "中位数": int(col_data.median()) if not pd.isna(col_data.median()) else 0
                    }
                    
                    # 安全地添加众数
                    try:
                        if not col_data.mode().empty:
                            col_stats["众数"] = int(col_data.mode().iloc[0])
                        else:
                            col_stats["众数"] = 0
                    except:
                        col_stats["众数"] = 0
                    
                    analysis["列分析"][f"第{col+1}列"] = col_stats
                except Exception as e:
                    # 出错时添加简化的统计信息
                    analysis["列分析"][f"第{col+1}列"] = {
                        "错误": f"分析此列时出错: {str(e)}",
                        "数据范围": "0-0"
                    }
        except Exception as e:
            analysis["列分析"] = {"错误": f"列分析总体出错: {str(e)}"}
    
    def _analyze_special_numbers(self, data, analysis):
        """分析特别号码（第7列）的模式"""
        if data is None or data.empty:
            analysis["模式分析"]["特别号码"] = {"信息": "没有数据可分析"}
            return
            
        try:
            special_col = 6  # 第7列索引为6
            
            # 检查列是否存在
            if special_col not in data.columns:
                analysis["模式分析"]["特别号码"] = {"信息": "数据中缺少特别号码列"}
                return
                
            # 获取特别号码列，并处理可能的NaN值
            special_numbers = data[special_col].dropna()
            
            if len(special_numbers) == 0:
                analysis["模式分析"]["特别号码"] = {"信息": "特别号码列中没有有效数据"}
                return
                
            special_analysis = {}
            
            # 计算频率
            freq_counts = {}
            for num in special_numbers:
                try:
                    num_int = int(num)
                    freq_counts[num_int] = freq_counts.get(num_int, 0) + 1
                except:
                    continue
                    
            special_analysis["出现频率最高的号码"] = dict(
                sorted(freq_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            )
            
            # 计算连续模式
            consecutive_patterns = self._analyze_consecutive_patterns(special_numbers)
            if "错误" not in consecutive_patterns:
                special_analysis["连续模式"] = consecutive_patterns
                
            # 添加分析结果
            analysis["模式分析"]["特别号码"] = special_analysis
                
        except Exception as e:
            # 捕获错误但保留已有的分析结果
            if "模式分析" not in analysis or "特别号码" not in analysis["模式分析"]:
                analysis["模式分析"]["特别号码"] = {}
                
            analysis["模式分析"]["特别号码"]["错误"] = f"分析特别号码时出错: {str(e)}"
    
    def _analyze_combinations_for_data(self, data, analysis):
        """分析号码组合模式"""
        if data is None or data.empty:
            analysis["模式分析"]["组合模式"] = {"信息": "没有数据可分析"}
            return
            
        try:
            combinations = {
                "奇偶比例": {},
                "大小比例": {},
                "区间分布": {}
            }
            
            valid_rows = 0
            
            for idx, row in data.iterrows():
                # 跳过包含NaN的行
                if row.isna().any():
                    continue
                    
                try:
                    valid_rows += 1
                    row_vals = [int(x) for x in row if not pd.isna(x)]
                    
                    # 确保行有足够的数据
                    if len(row_vals) < 7:
                        continue
                    
                    # 分析奇偶比例
                    odd_count = sum(1 for x in row_vals if x % 2 == 1)
                    even_count = 7 - odd_count
                    ratio = f"{odd_count}:{even_count}"
                    combinations["奇偶比例"][ratio] = combinations["奇偶比例"].get(ratio, 0) + 1
                    
                    # 分析大小比例（以25为界）
                    big_count = sum(1 for x in row_vals if x > 25)
                    small_count = 7 - big_count
                    ratio = f"{big_count}:{small_count}"
                    combinations["大小比例"][ratio] = combinations["大小比例"].get(ratio, 0) + 1
                    
                    # 分析区间分布
                    zones = [0] * 5  # 1-10, 11-20, 21-30, 31-40, 41-49
                    for x in row_vals:
                        if 1 <= x <= 10: zones[0] += 1
                        elif 11 <= x <= 20: zones[1] += 1
                        elif 21 <= x <= 30: zones[2] += 1
                        elif 31 <= x <= 40: zones[3] += 1
                        else: zones[4] += 1
                    zone_pattern = "-".join(map(str, zones))
                    combinations["区间分布"][zone_pattern] = combinations["区间分布"].get(zone_pattern, 0) + 1
                except Exception:
                    # 忽略处理单行时的错误
                    valid_rows -= 1
                    continue
            
            # 转换为百分比
            if valid_rows > 0:
                for category in combinations:
                    combinations[category] = {
                        k: round(v/valid_rows * 100, 2) 
                        for k, v in combinations[category].items()
                    }
            
            analysis["模式分析"]["组合模式"] = combinations
            
        except Exception as e:
            # 出错时添加错误信息
            analysis["模式分析"]["组合模式"] = {"错误": f"分析组合模式时出错: {str(e)}"}
    
    def _analyze_combinations(self) -> Dict:
        """分析号码组合模式（兼容性方法）"""
        try:
            # 获取数据
            if self.data is None or self.data.empty:
                return {
                    "奇偶比例": {},
                    "大小比例": {},
                    "区间分布": {}
                }
                
            combinations = {
                "奇偶比例": {},
                "大小比例": {},
                "区间分布": {}
            }
            
            valid_rows = 0
            
            for idx, row in self.data.iterrows():
                # 跳过包含NaN的行
                if row.isna().any():
                    continue
                    
                try:
                    valid_rows += 1
                    
                    # 分析奇偶比例
                    odd_count = sum(1 for x in row if x % 2 == 1)
                    even_count = 7 - odd_count
                    ratio = f"{odd_count}:{even_count}"
                    combinations["奇偶比例"][ratio] = combinations["奇偶比例"].get(ratio, 0) + 1
                    
                    # 分析大小比例（以25为界）
                    big_count = sum(1 for x in row if x > 25)
                    small_count = 7 - big_count
                    ratio = f"{big_count}:{small_count}"
                    combinations["大小比例"][ratio] = combinations["大小比例"].get(ratio, 0) + 1
                    
                    # 分析区间分布
                    zones = [0] * 5  # 1-10, 11-20, 21-30, 31-40, 41-49
                    for x in row:
                        if 1 <= x <= 10: zones[0] += 1
                        elif 11 <= x <= 20: zones[1] += 1
                        elif 21 <= x <= 30: zones[2] += 1
                        elif 31 <= x <= 40: zones[3] += 1
                        else: zones[4] += 1
                    zone_pattern = "-".join(map(str, zones))
                    combinations["区间分布"][zone_pattern] = combinations["区间分布"].get(zone_pattern, 0) + 1
                except Exception:
                    # 忽略处理单行时的错误
                    valid_rows -= 1
                    continue
            
            # 转换为百分比
            if valid_rows > 0:
                for category in combinations:
                    combinations[category] = {
                        k: round(v/valid_rows * 100, 2) 
                        for k, v in combinations[category].items()
                    }
            
            return combinations
            
        except Exception as e:
            # 出错时返回空结果
            print(f"分析组合模式时出错: {str(e)}")
            return {
                "奇偶比例": {},
                "大小比例": {},
                "区间分布": {}
            }
    
    def get_prediction(self, num_predictions: int = 4) -> List[List[int]]:
        """基于分析结果生成预测号码"""
        if not self.analysis_results:
            return []
            
        predictions = []
        number_freq = self.analysis_results["号码统计"]["频率"]
        
        for _ in range(num_predictions):
            selected = []
            available = list(range(1, 50))
            
            # 选择前6个号码
            for _ in range(6):
                weights = [number_freq.get(n, 1) for n in available]
                weights = np.array(weights) / sum(weights)
                number = np.random.choice(available, p=weights)
                selected.append(number)
                available.remove(number)
            
            # 选择特别号码
            special_weights = [number_freq.get(n, 1) for n in available]
            special_weights = np.array(special_weights) / sum(special_weights)
            special = np.random.choice(available, p=special_weights)
            selected.append(special)
            
            predictions.append(selected)
        
        return predictions

    def find_period_index(self, year, period):
        """
        查找特定年份和期数对应的数据索引
        
        Args:
            year: 年份，如2025
            period: 期数，如34
            
        Returns:
            找到的索引，如果未找到则返回None
        """
        try:
            if self.data is None or len(self.data.index) == 0:
                print("没有加载数据或数据为空")
                return None
                
            # 格式化目标模式，支持不同的期数格式
            target_patterns = [
                f"{year}年{period:03d}期",  # 格式：2025年034期
                f"{year}年{period}期",      # 格式：2025年34期
                f"{year}/{period:03d}",     # 格式：2025/034
                f"{year}/{period}",         # 格式：2025/34
                f"{year}-{period:03d}",     # 格式：2025-034
                f"{year}-{period}"          # 格式：2025-34
            ]
            
            # 1. 首先，直接在已加载的数据中查找（最可靠的方法）
            try:
                # 如果数据已经成功加载，我们可以查看前两列是否包含期数或年份信息
                if hasattr(self, 'data') and self.data is not None and not self.data.empty:
                    # 先处理期数
                    # 如果期数在数据范围内，直接返回索引
                    if 0 <= period-1 < len(self.data):
                        print(f"在数据范围中找到期数 {period}，对应索引: {period-1}")
                        return period-1
                        
                    # 还可以尝试遍历数据，寻找特定模式
                    for idx, row in self.data.iterrows():
                        # 检查是否有任何列包含年份和期数
                        row_str = ','.join([str(val) for val in row.values])
                        if f"{year}" in row_str and f"{period:03d}" in row_str:
                            print(f"在数据行 {idx} 中找到匹配: {row_str}")
                            return idx
            except Exception as e:
                print(f"在已加载数据中查找时出错: {str(e)}")
            
            # 2. 如果数据是从TXT文件加载的，尝试从原始文件中查找
            try:
                if hasattr(self, 'last_loaded_file') and self.last_loaded_file.lower().endswith('.txt'):
                    # 尝试多种编码
                    encodings = ['utf-8', 'gbk', 'gb2312', 'cp1252', 'windows-1252', 'latin1']
                    for encoding in encodings:
                        try:
                            with open(self.last_loaded_file, 'r', encoding=encoding) as f:
                                lines = f.readlines()
                                
                                # 遍历所有行，寻找匹配的年份和期数
                                for idx, line in enumerate(lines):
                                    line = line.strip()
                                    if not line:
                                        continue
                                    
                                    # 检查是否包含目标年份和期数的任一格式
                                    for pattern in target_patterns:
                                        if pattern in line:
                                            print(f"在原始文件中使用 {encoding} 编码找到匹配行: {line}")
                                            return idx
                            # 如果没有抛出异常但也没有找到匹配，继续尝试下一个编码
                        except UnicodeDecodeError:
                            continue
                        except Exception as e:
                            print(f"使用 {encoding} 编码读取文件时出错: {str(e)}")
                            continue
                            
                    # 如果所有编码都尝试了但没有找到匹配，尝试二进制读取
                    try:
                        with open(self.last_loaded_file, 'rb') as f:
                            binary_content = f.read()
                        
                        # 使用latin1忽略错误模式
                        content = binary_content.decode('latin1', errors='ignore')
                        lines = content.splitlines()
                        
                        for idx, line in enumerate(lines):
                            line = line.strip()
                            if not line:
                                continue
                                
                            # 尝试查找年份和期数的组合
                            if str(year) in line and str(period).zfill(3) in line:
                                print(f"在二进制读取的文件中找到匹配行: {line}")
                                return idx
                    except Exception as e:
                        print(f"二进制读取文件时出错: {str(e)}")
            except Exception as e:
                print(f"从原始文件查找期数时出错: {str(e)}")
            
            # 3. 如果以上方法都失败，我们尝试使用期数作为索引（假设数据按期数排序）
            if 0 <= period-1 < len(self.data):
                print(f"使用期数作为索引: {period-1}")
                return period-1
            
            # 如果所有方法都失败，返回None
            print(f"未找到匹配项: 年份={year}, 期数={period}")
            return None
                
        except Exception as e:
            print(f"查找期数索引时出错: {str(e)}")
            return None