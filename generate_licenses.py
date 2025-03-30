import base64
import json
from datetime import datetime, timedelta
import hashlib

def generate_license(license_id):
    """生成单个序列号"""
    # 创建序列号数据
    data = {
        'license_id': license_id,
        'created_date': datetime.now().strftime('%Y-%m-%d'),
        'expiry_date': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    }
    
    # 生成签名
    secret_key = "LOTTERY_ANALYZER_SECRET_KEY_2024"
    sorted_keys = sorted(data.keys())
    sign_str = "".join(f"{k}{data[k]}" for k in sorted_keys)
    sign_str = f"{sign_str}{secret_key}"
    signature = hashlib.sha256(sign_str.encode()).hexdigest()
    
    # 添加签名到数据中
    data['signature'] = signature
    
    # 编码序列号
    license_str = base64.b64encode(json.dumps(data).encode()).decode()
    return license_str

def main():
    print("开始生成序列号...")
    
    # 创建序列号列表
    licenses = []
    
    # 生成100个序列号
    for i in range(100):
        license_id = f"LICENSE_{i+1:03d}"
        license_str = generate_license(license_id)
        licenses.append({
            'id': license_id,
            'license': license_str
        })
        
    # 保存序列号到文件
    with open('generated_licenses.txt', 'w', encoding='utf-8') as f:
        f.write("彩票号码分析器序列号列表\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"序列号数量：{len(licenses)}\n\n")
        f.write("序列号列表：\n")
        f.write("-" * 50 + "\n")
        for i, lic in enumerate(licenses, 1):
            f.write(f"{i}. 序列号ID: {lic['id']}\n")
            f.write(f"   序列号: {lic['license']}\n")
            f.write("-" * 50 + "\n")
            
    print(f"已生成 {len(licenses)} 个序列号")
    print("序列号已保存到 generated_licenses.txt")

if __name__ == "__main__":
    main() 