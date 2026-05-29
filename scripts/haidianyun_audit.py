#!/usr/bin/env python3
"""海淀云客户审核 - 快速模式
用法: python3 haidianyun_audit.py <record_id>
配置: 设置环境变量 HAIDIANYUN_USER_ACCOUNT 和 HAIDIANYUN_PASSWORD
"""
import urllib.request, json, ssl, sys, os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = 'https://op.haidianyun.com/gateway/operation'

def check_config():
    """检查配置是否完整"""
    user_account = os.environ.get('HAIDIANYUN_USER_ACCOUNT')
    password = os.environ.get('HAIDIANYUN_PASSWORD')
    if not user_account or not password:
        print("错误: 请配置环境变量")
        print("  export HAIDIANYUN_USER_ACCOUNT=your_account")
        print("  export HAIDIANYUN_PASSWORD=your_password")
        print("或在 ~/.hermes/.env 中添加:")
        print("  HAIDIANYUN_USER_ACCOUNT=your_account")
        print("  HAIDIANYUN_PASSWORD=your_password")
        sys.exit(1)
    return user_account, password

def login(user_account, password):
    req = urllib.request.Request(BASE + '/auth/operation/auth',
        data=json.dumps({'userAccount': user_account, 'password': password}).encode(),
        headers={'Content-Type':'application/json'})
    resp = urllib.request.urlopen(req, context=ctx, timeout=5)
    return json.loads(resp.read())['data']['accessToken']

def get_detail(token, record_id):
    req = urllib.request.Request(BASE + '/orgmanager-v2/top/customerDraft/draftDetail',
        data=json.dumps({'id': record_id}).encode(),
        headers={'Content-Type':'application/json','access-token':token})
    r = urllib.request.urlopen(req, context=ctx, timeout=10)
    return json.loads(r.read()).get('data', {})

def audit_approve(token, record_id, detail):
    payload = {
        'id': record_id,
        'verifyStatus': 3,
        'remark': '审核通过',
        'companyName': detail.get('customerName', ''),
        'customerName': detail.get('customerName', ''),
        'customerShortName': detail.get('customerShortName', ''),
        'socialCreditCode': detail.get('socialCreditCode', ''),
        'contacts': detail.get('contacts', ''),
        'phone': detail.get('phone', ''),
        'address': detail.get('address', ''),
        'areaCodes': detail.get('areaCodes', []),
    }
    req = urllib.request.Request(BASE + '/orgmanager-v2/top/customerDraft/audit',
        data=json.dumps(payload).encode(),
        headers={'Content-Type':'application/json','access-token':token})
    r = urllib.request.urlopen(req, context=ctx, timeout=10)
    return json.loads(r.read())

def main():
    if len(sys.argv) < 2:
        print("用法: python3 haidianyun_audit.py <record_id>")
        print("示例: python3 haidianyun_audit.py 21322")
        sys.exit(1)
    
    record_id = int(sys.argv[1])
    
    # 检查配置
    user_account, password = check_config()
    
    # 登录
    token = login(user_account, password)
    
    # 获取详情
    detail = get_detail(token, record_id)
    if not detail:
        print(f"错误: 未找到记录 ID {record_id}")
        sys.exit(1)
    
    status_map = {1:'审核不通过', 2:'待审核', 3:'审核通过', 4:'已撤回'}
    current_status = status_map.get(detail.get('verifyStatus'), '未知')
    print(f"找到: ID={record_id} | {detail.get('customerName')} | 状态={current_status}")
    
    if detail.get('verifyStatus') != 2:
        print(f"跳过: 该记录状态为「{current_status}」，不是待审核")
        sys.exit(0)
    
    # 审核通过
    result = audit_approve(token, record_id, detail)
    if result.get('code') == '00103':
        print(f"✓ 审核通过成功")
    else:
        print(f"✗ 审核失败: {result.get('msg', '未知错误')}")

if __name__ == '__main__':
    main()
