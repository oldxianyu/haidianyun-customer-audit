#!/usr/bin/env python3
"""环境检查脚本 - 验证海典运营平台审核技能的运行环境"""
import sys
import os
import shutil

def check_python():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print(f"✗ Python 版本过低: {version.major}.{version.minor} (需要 3.6+)")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_modules():
    """检查必需的 Python 模块"""
    modules = ['urllib.request', 'json', 'ssl']
    all_ok = True
    for mod in modules:
        try:
            __import__(mod)
            print(f"✓ 模块 {mod}")
        except ImportError:
            print(f"✗ 模块 {mod} 缺失")
            all_ok = False
    return all_ok

def check_network():
    """检查网络连接"""
    import urllib.request
    import ssl
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request('https://op.haidianyun.com', method='HEAD')
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        print(f"✓ 网络连接 op.haidianyun.com (状态码: {resp.status})")
        return True
    except Exception as e:
        print(f"✗ 网络连接失败: {e}")
        return False

def check_env_vars():
    """检查环境变量"""
    account = os.environ.get('HAIDIANYUN_USER_ACCOUNT')
    password = os.environ.get('HAIDIANYUN_PASSWORD')
    
    if account:
        print(f"✓ HAIDIANYUN_USER_ACCOUNT 已设置")
    else:
        print(f"✗ HAIDIANYUN_USER_ACCOUNT 未设置")
    
    if password:
        print(f"✓ HAIDIANYUN_PASSWORD 已设置")
    else:
        print(f"✗ HAIDIANYUN_PASSWORD 未设置")
    
    return bool(account and password)

def check_hermes():
    """检查 Hermes Agent"""
    hermes_path = shutil.which('hermes')
    if hermes_path:
        print(f"✓ Hermes Agent 已安装: {hermes_path}")
        return True
    else:
        print(f"✗ Hermes Agent 未安装")
        return False

def main():
    print("=" * 50)
    print("海典运营平台审核技能 - 环境检查")
    print("=" * 50)
    print()
    
    checks = [
        ("Python 版本", check_python),
        ("Python 模块", check_modules),
        ("网络连接", check_network),
        ("环境变量", check_env_vars),
        ("Hermes Agent", check_hermes),
    ]
    
    results = []
    for name, check_fn in checks:
        print(f"\n[{name}]")
        try:
            results.append(check_fn())
        except Exception as e:
            print(f"✗ 检查失败: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ 所有检查通过！可以使用审核技能。")
        sys.exit(0)
    else:
        print("✗ 部分检查未通过，请修复后重试。")
        sys.exit(1)

if __name__ == '__main__':
    main()
