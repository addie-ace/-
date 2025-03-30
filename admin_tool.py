import requests
import json
from datetime import datetime
import os
import base64
import hashlib

class LicenseAdmin:
    def __init__(self, server_url=None, admin_key="LOTTERY_ANALYZER_ADMIN_KEY_2024"):
        self.server_url = "https://a814003570.pythonanywhere.com" if server_url is None else server_url
        self.admin_key = admin_key
        self.secret_key = "LOTTERY_ANALYZER_SECRET_KEY_2024"
        
    def _generate_signature(self, data):
        """生成签名"""
        sorted_keys = sorted(data.keys())
        sign_str = "".join(f"{k}{data[k]}" for k in sorted_keys)
        sign_str = f"{sign_str}{self.secret_key}"
        return hashlib.sha256(sign_str.encode()).hexdigest()
        
    def list_licenses(self):
        """查看所有序列号状态"""
        try:
            response = requests.post(
                f"{self.server_url}/api/admin/list",
                json={'admin_key': self.admin_key}
            )
            print(f"请求URL: {self.server_url}/api/admin/list")
            print(f"请求数据: {{'admin_key': '{self.admin_key}'}}")
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print("\n序列号列表：")
                    print("-" * 80)
                    for license_info in result['licenses']:
                        print(f"序列号ID: {license_info['license_id']}")
                        print(f"机器码: {license_info.get('machine_code', '未绑定')}")
                        print(f"激活状态: {'已激活' if license_info.get('is_active') else '未激活'}")
                        print(f"到期时间: {license_info.get('expiry_date', '未知')}")
                        print("-" * 80)
                else:
                    print(f"获取列表失败：{result['message']}")
            else:
                print(f"服务器响应错误：{response.text}")
        except Exception as e:
            print(f"操作失败：{str(e)}")
            print(f"异常类型：{type(e).__name__}")
            import traceback
            print(f"异常详情：{traceback.format_exc()}")
            
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
                print(f"服务器响应错误：{response.text}")
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
                    print("-" * 80)
                    for log in result['logs']:
                        print(f"时间：{log['timestamp']}")
                        print(f"操作：{log['action']}")
                        print(f"详情：{json.dumps(log['details'], ensure_ascii=False)}")
                        print("-" * 80)
                else:
                    print(f"获取日志失败：{result['message']}")
            else:
                print(f"服务器响应错误：{response.text}")
        except Exception as e:
            print(f"操作失败：{str(e)}")

    def check_server_status(self):
        """检查服务器状态"""
        try:
            response = requests.get(f"{self.server_url}/")
            if response.status_code == 200:
                print("服务器状态：正常")
                return True
            else:
                print("服务器状态：异常")
                return False
        except Exception as e:
            print(f"服务器状态：离线 ({str(e)})")
            return False

def main():
    admin = LicenseAdmin()
    
    while True:
        print("\n序列号管理系统")
        print("=" * 30)
        print("1. 查看服务器状态")
        print("2. 查看所有序列号")
        print("3. 解绑序列号")
        print("4. 查看操作日志")
        print("0. 退出")
        print("=" * 30)
        
        choice = input("\n请选择操作 (0-4): ").strip()
        
        if choice == "1":
            admin.check_server_status()
        elif choice == "2":
            admin.list_licenses()
        elif choice == "3":
            license_id = input("请输入要解绑的序列号ID: ").strip()
            if license_id:
                admin.unbind_license(license_id)
            else:
                print("序列号ID不能为空")
        elif choice == "4":
            admin.view_logs()
        elif choice == "0":
            print("感谢使用！")
            break
        else:
            print("无效的选择，请重试")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main() 