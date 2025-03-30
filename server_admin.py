import requests
import json
from datetime import datetime, timedelta
import base64
import hashlib

class LicenseServerAdmin:
    def __init__(self):
        self.server_url = "https://a814003570.pythonanywhere.com"
        self.admin_key = "LOTTERY_ANALYZER_ADMIN_KEY_2024"
        self.secret_key = "LOTTERY_ANALYZER_SECRET_KEY_2024"

    def _generate_signature(self, data):
        """生成签名"""
        sorted_keys = sorted(data.keys())
        sign_str = "".join(f"{k}{data[k]}" for k in sorted_keys)
        sign_str = f"{sign_str}{self.secret_key}"
        return hashlib.sha256(sign_str.encode()).hexdigest()

    def list_licenses(self):
        """列出所有序列号"""
        try:
            response = requests.post(
                f"{self.server_url}/api/admin/list",
                json={'admin_key': self.admin_key}
            )
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print("\n序列号列表：")
                    print("-" * 60)
                    for license_info in result['licenses']:
                        print(f"序列号ID: {license_info['license_id']}")
                        print(f"机器码: {license_info.get('machine_code', '未绑定')}")
                        print(f"激活状态: {'已激活' if license_info.get('is_active') else '未激活'}")
                        print(f"到期时间: {license_info.get('expiry_date', '未知')}")
                        print("-" * 60)
                else:
                    print(f"获取列表失败：{result['message']}")
            else:
                print(f"服务器响应错误：{response.status_code}")
        except Exception as e:
            print(f"操作失败：{str(e)}")

    def unbind_license(self, license_id):
        """解绑序列号"""
        try:
            response = requests.post(
                f"{self.server_url}/api/admin/unbind",
                json={
                    'admin_key': self.admin_key,
                    'license_id': license_id
                }
            )
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"序列号 {license_id} 解绑成功")
                    if 'details' in result:
                        print(f"原绑定机器码：{result['details'].get('machine_code', '无')}")
                else:
                    print(f"解绑失败：{result['message']}")
            else:
                print(f"服务器响应错误：{response.status_code}")
        except Exception as e:
            print(f"操作失败：{str(e)}")

    def view_logs(self):
        """查看操作日志"""
        try:
            response = requests.post(
                f"{self.server_url}/api/admin/logs",
                json={'admin_key': self.admin_key}
            )
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print("\n操作日志：")
                    print("-" * 60)
                    for log in result['logs']:
                        print(f"时间：{log['timestamp']}")
                        print(f"操作：{log['action']}")
                        print(f"详情：{json.dumps(log['details'], ensure_ascii=False)}")
                        print("-" * 60)
                else:
                    print(f"获取日志失败：{result['message']}")
            else:
                print(f"服务器响应错误：{response.status_code}")
        except Exception as e:
            print(f"操作失败：{str(e)}")

def main():
    admin = LicenseServerAdmin()
    while True:
        print("\n序列号管理系统")
        print("1. 查看所有序列号")
        print("2. 解绑序列号")
        print("3. 查看操作日志")
        print("0. 退出")
        
        choice = input("\n请选择操作 (0-3): ")
        
        if choice == "1":
            admin.list_licenses()
        elif choice == "2":
            license_id = input("请输入要解绑的序列号ID: ")
            admin.unbind_license(license_id)
        elif choice == "3":
            admin.view_logs()
        elif choice == "0":
            print("感谢使用！")
            break
        else:
            print("无效的选择，请重试")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main() 