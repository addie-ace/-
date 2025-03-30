from flask import Flask, request, jsonify
import json
import os
from datetime import datetime, timedelta
import hashlib
import base64

app = Flask(__name__)

# 服务器密钥
SERVER_SECRET_KEY = "LOTTERY_ANALYZER_SECRET_KEY_2024"

# 管理员密钥
ADMIN_KEY = "LOTTERY_ANALYZER_ADMIN_KEY_2024"

# 序列号数据库文件
LICENSE_DB_FILE = "license_database.json"

def init_database():
    """初始化序列号数据库"""
    if not os.path.exists(LICENSE_DB_FILE):
        # 初始化数据库结构
        db = {
            'licenses': {},
            'admin_logs': []
        }
        
        # 生成100个序列号
        for i in range(100):
            license_data = {
                'license_id': f"LICENSE_{i+1:03d}",
                'machine_code': None,  # 未绑定的机器码
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'expiry_date': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
                'is_active': False,
                'last_check': None
            }
            db['licenses'][license_data['license_id']] = license_data
            
        # 保存到文件
        with open(LICENSE_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)

def load_database():
    """加载序列号数据库"""
    if os.path.exists(LICENSE_DB_FILE):
        with open(LICENSE_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_database(licenses):
    """保存序列号数据库"""
    with open(LICENSE_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(licenses, f, indent=2, ensure_ascii=False)

def verify_signature(data, signature):
    """验证签名"""
    sorted_keys = sorted(data.keys())
    sign_str = "".join(f"{k}{data[k]}" for k in sorted_keys)
    sign_str = f"{sign_str}{SERVER_SECRET_KEY}"
    expected_signature = hashlib.sha256(sign_str.encode()).hexdigest()
    return signature == expected_signature

def log_admin_action(db, action, details):
    """记录管理员操作"""
    if 'admin_logs' not in db:
        db['admin_logs'] = []
        
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'action': action,
        'details': details
    }
    db['admin_logs'].append(log_entry)
    save_database(db)

def verify_admin_key(admin_key):
    """验证管理员密钥"""
    return admin_key == ADMIN_KEY

@app.route('/')
def home():
    """主页"""
    return "序列号验证服务器正在运行"

@app.route('/api/verify', methods=['POST'])
def verify_license():
    """验证序列号"""
    try:
        data = request.get_json()
        license_str = data.get('license')
        machine_code = data.get('machine_code')
        
        if not license_str or not machine_code:
            return jsonify({'success': False, 'message': '缺少必要参数'})
            
        # 解码序列号
        decoded = base64.b64decode(license_str).decode()
        license_data = json.loads(decoded)
        
        # 验证签名
        signature = license_data.pop('signature', None)
        if not signature or not verify_signature(license_data, signature):
            return jsonify({'success': False, 'message': '序列号无效'})
            
        # 加载数据库
        db = load_database()
        
        # 查找序列号
        license_id = license_data.get('license_id')
        if 'licenses' not in db or license_id not in db['licenses']:
            return jsonify({'success': False, 'message': '序列号不存在'})
            
        db_license = db['licenses'][license_id]
        
        # 检查是否已绑定其他机器
        if db_license['machine_code'] and db_license['machine_code'] != machine_code:
            return jsonify({'success': False, 'message': '序列号已被其他机器使用'})
            
        # 检查是否过期
        expiry_date = datetime.strptime(db_license['expiry_date'], '%Y-%m-%d')
        if expiry_date < datetime.now():
            return jsonify({'success': False, 'message': '序列号已过期'})
            
        # 更新数据库
        db_license['machine_code'] = machine_code
        db_license['is_active'] = True
        db_license['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_database(db)
        
        return jsonify({'success': True, 'message': '序列号验证通过'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证失败：{str(e)}'})

@app.route('/api/check', methods=['POST'])
def check_license():
    """检查序列号状态"""
    try:
        data = request.get_json()
        license_str = data.get('license')
        machine_code = data.get('machine_code')
        
        if not license_str or not machine_code:
            return jsonify({'success': False, 'message': '缺少必要参数'})
            
        # 解码序列号
        decoded = base64.b64decode(license_str).decode()
        license_data = json.loads(decoded)
        
        # 验证签名
        signature = license_data.pop('signature', None)
        if not signature or not verify_signature(license_data, signature):
            return jsonify({'success': False, 'message': '序列号无效'})
            
        # 加载数据库
        db = load_database()
        
        # 查找序列号
        license_id = license_data.get('license_id')
        if 'licenses' not in db or license_id not in db['licenses']:
            return jsonify({'success': False, 'message': '序列号不存在'})
            
        db_license = db['licenses'][license_id]
        
        # 检查是否绑定到当前机器
        if db_license['machine_code'] != machine_code:
            return jsonify({'success': False, 'message': '序列号与当前机器不匹配'})
            
        # 检查是否过期
        expiry_date = datetime.strptime(db_license['expiry_date'], '%Y-%m-%d')
        if expiry_date < datetime.now():
            return jsonify({'success': False, 'message': '序列号已过期'})
            
        # 更新最后检查时间
        db_license['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_database(db)
        
        return jsonify({'success': True, 'message': '序列号验证通过'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'检查失败：{str(e)}'})

@app.route('/api/admin/unbind', methods=['POST'])
def admin_unbind_license():
    """管理员解绑序列号"""
    try:
        data = request.get_json()
        if not data or 'admin_key' not in data or 'license_id' not in data:
            return jsonify({'success': False, 'message': '缺少必要参数'})
            
        admin_key = data['admin_key']
        license_id = data['license_id']
        
        # 验证管理员密钥
        if not verify_admin_key(admin_key):
            return jsonify({'success': False, 'message': '管理员密钥无效'})
            
        # 加载数据库
        db = load_database()
        
        # 检查序列号是否存在
        if license_id not in db['licenses']:
            return jsonify({'success': False, 'message': '序列号不存在'})
            
        # 获取序列号信息用于日志
        license_info = db['licenses'][license_id]
        machine_code = license_info.get('machine_code')
        
        # 清除绑定信息
        license_info['machine_code'] = None
        license_info['is_active'] = False
        license_info['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 保存更新后的数据库
        save_database(db)
        
        # 记录操作日志
        log_details = {
            'license_id': license_id,
            'machine_code': machine_code,
            'unbind_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        log_admin_action(db, 'unbind_license', log_details)
        
        return jsonify({
            'success': True,
            'message': '序列号解绑成功',
            'details': {
                'license_id': license_id,
                'machine_code': machine_code
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'解绑失败：{str(e)}'})

@app.route('/api/admin/list', methods=['POST'])
def admin_list_licenses():
    """管理员查看所有序列号状态"""
    try:
        data = request.get_json()
        if not data or 'admin_key' not in data:
            return jsonify({'success': False, 'message': '缺少管理员密钥'})
            
        admin_key = data['admin_key']
        
        # 验证管理员密钥
        if not verify_admin_key(admin_key):
            return jsonify({'success': False, 'message': '管理员密钥无效'})
            
        # 加载数据库
        db = load_database()
        
        # 整理序列号信息
        licenses = []
        for license_id, license_info in db['licenses'].items():
            machine_code = license_info.get('machine_code')
            licenses.append({
                'license_id': license_id,
                'machine_code': machine_code,
                'activated_date': license_info.get('activated_date')
            })
            
        return jsonify({
            'success': True,
            'licenses': licenses
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取列表失败：{str(e)}'})

@app.route('/api/admin/logs', methods=['POST'])
def admin_get_logs():
    """管理员查看操作日志"""
    try:
        data = request.get_json()
        if not data or 'admin_key' not in data:
            return jsonify({'success': False, 'message': '缺少管理员密钥'})
            
        admin_key = data['admin_key']
        
        # 验证管理员密钥
        if not verify_admin_key(admin_key):
            return jsonify({'success': False, 'message': '管理员密钥无效'})
            
        # 加载数据库
        db = load_database()
        
        return jsonify({
            'success': True,
            'logs': db['admin_logs']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取日志失败：{str(e)}'})

if __name__ == '__main__':
    print("正在初始化序列号数据库...")
    init_database()
    print("序列号数据库初始化完成")
    print("正在启动验证服务器...")
    
    # 配置HTTPS（生产环境必须使用）
    ssl_context = None
    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        ssl_context = ('cert.pem', 'key.pem')
        print("已启用HTTPS加密")
    else:
        print("警告：未找到SSL证书，将使用HTTP模式（不建议在生产环境中使用）")
    
    # 获取环境变量中的主机和端口配置
    host = os.environ.get('LICENSE_SERVER_HOST', '0.0.0.0')
    port = int(os.environ.get('LICENSE_SERVER_PORT', 5000))
    
    print(f"服务器将在 {host}:{port} 上运行")
    app.run(
        host=host,
        port=port,
        ssl_context=ssl_context,
        debug=False  # 生产环境禁用调试模式
    ) 