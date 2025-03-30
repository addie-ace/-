import hashlib
import uuid
import base64
import json
import requests
from datetime import datetime
import os
import wmi
import socket

class LicenseValidator:
    def __init__(self):
        self.secret_key = "LOTTERY_ANALYZER_SECRET_KEY_2024"  # 开发团队密钥
        self.server_url = "https://a814003570.pythonanywhere.com"  # 生产环境服务器
        self.local_server_url = "http://127.0.0.1:5001"  # 本地测试服务器
        self.license_file = "license.dat"  # 序列号存储文件
        self.local_mode = False  # 禁用本地模式，使用线上服务器
        
    def get_server_url(self):
        """获取当前使用的服务器地址"""
        return self.local_server_url if self.local_mode else self.server_url
        
    def is_network_available(self):
        """检查网络连接是否可用"""
        try:
            # 尝试连接到验证服务器
            response = requests.get(self.get_server_url())
            return response.status_code == 200
        except:
            return False
        
    def get_machine_code(self):
        """获取机器码"""
        try:
            c = wmi.WMI()
            # 获取CPU ID
            cpu_id = c.Win32_Processor()[0].ProcessorId.strip()
            # 获取硬盘序列号
            disk_id = c.Win32_DiskDrive()[0].SerialNumber.strip()
            # 组合并哈希
            machine_code = f"{cpu_id}_{disk_id}"
            return hashlib.sha256(machine_code.encode()).hexdigest()[:32]
        except:
            # 如果WMI获取失败，使用UUID
            return str(uuid.uuid4()).replace('-', '')[:32]
    
    def get_current_license(self):
        """获取当前绑定的序列号"""
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r') as f:
                    license_data = json.load(f)
                    return license_data.get('license')
            return None
        except:
            return None
    
    def _generate_signature(self, data):
        """生成签名"""
        sorted_keys = sorted(data.keys())
        sign_str = "".join(f"{k}{data[k]}" for k in sorted_keys)
        sign_str = f"{sign_str}{self.secret_key}"
        return hashlib.sha256(sign_str.encode()).hexdigest()
    
    def verify_license(self, license_str, machine_code):
        """验证序列号"""
        try:
            # 检查网络连接
            if not self.is_network_available():
                return False, "无法连接到验证服务器，请检查网络连接"
            
            # 验证序列号格式
            try:
                # 解码序列号
                decoded = base64.b64decode(license_str).decode('ascii')
                license_data = json.loads(decoded)
                
                # 验证必要字段
                required_fields = ['license_id', 'created_date', 'expiry_date', 'signature']
                if not all(field in license_data for field in required_fields):
                    return False, "序列号格式无效"
                    
                # 验证日期格式
                try:
                    created_date = datetime.strptime(license_data['created_date'], '%Y-%m-%d')
                    expiry_date = datetime.strptime(license_data['expiry_date'], '%Y-%m-%d')
                    
                    # 检查是否过期
                    if datetime.now() > expiry_date:
                        return False, "序列号已过期"
                        
                except ValueError:
                    return False, "序列号日期格式无效"
                
                # 验证签名
                data_to_sign = {
                    'license_id': license_data['license_id'],
                    'created_date': license_data['created_date'],
                    'expiry_date': license_data['expiry_date']
                }
                expected_signature = self._generate_signature(data_to_sign)
                if expected_signature != license_data['signature']:
                    return False, "序列号签名无效"
                
            except Exception as e:
                return False, f"序列号格式错误：{str(e)}"
                
            # 发送验证请求到服务器
            response = requests.post(
                f"{self.get_server_url()}/api/verify",
                json={
                    'license': license_str,
                    'machine_code': machine_code
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['success'], result['message']
            else:
                return False, f"服务器响应错误：{response.text}"
                
        except Exception as e:
            return False, f"序列号验证失败：{str(e)}"
            
    def activate_license(self, license_str):
        """激活序列号"""
        try:
            # 检查网络连接
            if not self.is_network_available():
                return False, "无法连接到验证服务器，请检查网络连接"
                
            machine_code = self.get_machine_code()
            success, message = self.verify_license(license_str, machine_code)
            
            if success:
                # 保存序列号和机器码到本地文件
                license_data = {
                    'license': license_str,
                    'machine_code': machine_code,
                    'activated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                with open(self.license_file, 'w') as f:
                    json.dump(license_data, f)
                return True, "序列号激活成功"
            else:
                return False, message
        except Exception as e:
            return False, f"序列号激活失败：{str(e)}"
            
    def check_license(self):
        """检查序列号状态"""
        try:
            # 检查是否有本地序列号文件
            if not os.path.exists(self.license_file):
                return False, "未找到序列号文件"
                
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
                
            # 获取当前机器码
            current_machine_code = self.get_machine_code()
            
            # 验证机器码是否匹配
            if license_data.get('machine_code') != current_machine_code:
                return False, "序列号与当前机器不匹配"
                
            # 检查网络连接
            if not self.is_network_available():
                return False, "无法连接到验证服务器，请检查网络连接"
                
            # 发送验证请求到服务器
            response = requests.post(
                f"{self.get_server_url()}/api/check",
                json={
                    'license': license_data['license'],
                    'machine_code': current_machine_code
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['success'], result['message']
            else:
                return False, f"服务器响应错误：{response.text}"
                
        except Exception as e:
            return False, f"序列号检查失败：{str(e)}"

    def check_server_status(self):
        """检查验证服务器状态
        
        Returns:
            bool: 服务器是否在线
        """
        try:
            # 先尝试使用GET请求检查根路径
            response = requests.get(self.get_server_url(), timeout=3)
            if response.status_code == 200:
                return True
                
            # 如果GET请求失败，尝试使用POST请求检查API
            response = requests.post(
                f"{self.get_server_url()}/api/check", 
                json={}, 
                timeout=3
            )
            return response.status_code == 200
        except Exception as e:
            print(f"检查服务器状态失败: {str(e)}")
            return False 