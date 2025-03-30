import hashlib
import uuid
import base64
import json
import requests
from datetime import datetime, timedelta
import os

class LicenseGenerator:
    def __init__(self):
        self.secret_key = "LOTTERY_ANALYZER_SECRET_KEY_2024"  # 开发团队密钥
        self.api_url = "http://your-license-server.com/api"  # 序列号验证服务器地址
        
    def get_machine_code(self):
        """获取机器唯一标识码"""
        # 获取CPU ID
        cpu_info = ""
        try:
            import wmi
            c = wmi.WMI()
            for item in c.Win32_Processor():
                cpu_info = item.ProcessorId.strip()
                break
        except:
            cpu_info = str(uuid.getnode())  # 使用MAC地址作为备选
            
        # 获取硬盘序列号
        disk_info = ""
        try:
            for item in c.Win32_DiskDrive():
                disk_info = item.SerialNumber.strip()
                break
        except:
            disk_info = str(uuid.uuid4())  # 使用UUID作为备选
            
        # 组合机器码
        machine_code = f"{cpu_info}_{disk_info}"
        return hashlib.sha256(machine_code.encode()).hexdigest()
    
    def generate_license(self, machine_code, days=365):
        """生成序列号
        
        Args:
            machine_code: 机器码
            days: 有效期天数
        """
        # 生成过期时间
        expire_date = datetime.now() + timedelta(days=days)
        
        # 构建许可证数据
        license_data = {
            "machine_code": machine_code,
            "expire_date": expire_date.strftime("%Y-%m-%d"),
            "create_date": datetime.now().strftime("%Y-%m-%d"),
            "version": "2.0"
        }
        
        # 添加签名
        signature = self._generate_signature(license_data)
        license_data["signature"] = signature
        
        # 编码序列号
        license_str = base64.b64encode(json.dumps(license_data).encode()).decode()
        return license_str
    
    def _generate_signature(self, data):
        """生成签名"""
        # 按字母顺序排序键
        sorted_keys = sorted(data.keys())
        # 构建签名字符串
        sign_str = "".join(f"{k}{data[k]}" for k in sorted_keys)
        # 添加密钥
        sign_str = f"{sign_str}{self.secret_key}"
        # 生成签名
        return hashlib.sha256(sign_str.encode()).hexdigest()
    
    def verify_license(self, license_str, machine_code):
        """验证序列号"""
        try:
            # 解码序列号
            license_data = json.loads(base64.b64decode(license_str.encode()).decode())
            
            # 验证机器码
            if license_data["machine_code"] != machine_code:
                return False, "序列号与当前机器不匹配"
            
            # 验证过期时间
            expire_date = datetime.strptime(license_data["expire_date"], "%Y-%m-%d")
            if expire_date < datetime.now():
                return False, "序列号已过期"
            
            # 验证签名
            signature = license_data.pop("signature", None)
            if not signature or signature != self._generate_signature(license_data):
                return False, "序列号无效"
            
            return True, "序列号验证通过"
            
        except Exception as e:
            return False, f"序列号验证失败: {str(e)}"
    
    def activate_license(self, license_str):
        """激活序列号（需要联网）"""
        try:
            # 获取当前机器码
            machine_code = self.get_machine_code()
            
            # 验证序列号
            is_valid, message = self.verify_license(license_str, machine_code)
            if not is_valid:
                return False, message
            
            # 发送激活请求到服务器
            response = requests.post(
                f"{self.api_url}/activate",
                json={
                    "license": license_str,
                    "machine_code": machine_code,
                    "activation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
            
            if response.status_code == 200:
                return True, "序列号激活成功"
            else:
                return False, f"序列号激活失败: {response.text}"
                
        except Exception as e:
            return False, f"序列号激活失败: {str(e)}"

def main():
    """主函数"""
    generator = LicenseGenerator()
    
    print("彩票号码分析器序列号生成工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作：")
        print("1. 生成序列号")
        print("2. 验证序列号")
        print("3. 激活序列号")
        print("4. 退出")
        
        choice = input("\n请输入选项（1-4）：")
        
        if choice == "1":
            # 获取机器码
            machine_code = generator.get_machine_code()
            print(f"\n当前机器码：{machine_code}")
            
            # 获取有效期
            try:
                days = int(input("请输入有效期天数（默认365天）：") or "365")
            except ValueError:
                days = 365
            
            # 生成序列号
            license_str = generator.generate_license(machine_code, days)
            print(f"\n生成的序列号：\n{license_str}")
            
            # 保存到文件
            with open("license.txt", "w", encoding="utf-8") as f:
                f.write(license_str)
            print("\n序列号已保存到 license.txt")
            
        elif choice == "2":
            # 获取机器码
            machine_code = generator.get_machine_code()
            print(f"\n当前机器码：{machine_code}")
            
            # 获取序列号
            license_str = input("\n请输入序列号：")
            
            # 验证序列号
            is_valid, message = generator.verify_license(license_str, machine_code)
            print(f"\n验证结果：{message}")
            
        elif choice == "3":
            # 获取序列号
            license_str = input("\n请输入序列号：")
            
            # 激活序列号
            success, message = generator.activate_license(license_str)
            print(f"\n激活结果：{message}")
            
        elif choice == "4":
            print("\n感谢使用！")
            break
            
        else:
            print("\n无效的选项，请重新选择")

if __name__ == "__main__":
    main() 