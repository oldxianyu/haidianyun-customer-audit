#!/usr/bin/env python3
"""海典云客户审核快速脚本：按 ID 或名称查询并审核通过。"""
import argparse
import json
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request

BASE = 'https://op.haidianyun.com/gateway/operation'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def post(path, payload, token=None, timeout=8):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['access-token'] = token
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        headers=headers,
    )
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def env_first(*names):
    for name in names:
        val = os.environ.get(name, '').strip()
        if val:
            return val
    return ''


def login():
    account = env_first('HAIDIANYUN_ACCOUNT', 'HAIDIANYUNUSERACCOUNT', 'HAIDIANYUN_USER_ACCOUNT')
    password = env_first('HAIDIANYUN_PASSWORD')
    if not account or not password:
        raise SystemExit('错误: 请设置 HAIDIANYUN_ACCOUNT/HAIDIANYUN_PASSWORD 环境变量')
    data = post('/auth/operation/auth', {'userAccount': account, 'password': password})
    token = (data.get('data') or {}).get('accessToken')
    if not token:
        raise SystemExit(f"登录失败: {data.get('msg') or data}")
    return token


def query_list(token, keyword='', page_size=50):
    body = {'currentPage': 1, 'pageSize': page_size, 'verifyStatus': 2}
    if keyword:
        body['customerName'] = keyword
    data = post('/orgmanager-v2/top/customerDraft/queryList', body, token=token)
    rows = data.get('data') or []
    if isinstance(rows, dict):
        rows = rows.get('records') or rows.get('list') or rows.get('rows') or rows.get('data') or []
    return rows


def detail(token, record_id):
    data = post('/orgmanager-v2/top/customerDraft/draftDetail', {'id': int(record_id)}, token=token)
    d = data.get('data')
    if not d:
        raise RuntimeError(f'获取详情失败 ID={record_id}: {data.get("msg") or data}')
    return d


def parse_area_codes(d):
    value = d.get('areaCode', d.get('areaCodes', []))
    if isinstance(value, str):
        try:
            return json.loads(value) if value else []
        except Exception:
            return []
    return value or []


def audit_pass(token, d):
    payload = {
        'id': d['id'],
        'verifyStatus': 3,
        'remark': '审核通过',
        'companyName': d.get('companyName') or d.get('customerName') or '',
        'customerName': d.get('customerName') or '',
        'customerShortName': d.get('customerShortName') or '',
        'socialCreditCode': d.get('socialCreditCode') or '',
        'contacts': d.get('contacts') or '',
        'phone': d.get('phone') or '',
        'address': d.get('address') or '',
        'areaCodes': parse_area_codes(d),
    }
    return post('/orgmanager-v2/top/customerDraft/audit', payload, token=token)


def norm(s):
    return re.sub(r'\s+', '', str(s or '')).lower()


def keywords(name):
    n = str(name).strip()
    parts = [n]
    for suffix in ['有限公司', '有限责任公司', '公司', '厂家', '系列']:
        if suffix in n:
            parts.append(n.split(suffix)[0])
    parts += re.split(r'[-—_\s()（）]+', n)
    out = []
    for p in parts:
        p = p.strip()
        if p and len(p) >= 2 and p not in out:
            out.append(p)
    return out[:5]


def resolve_ids(token, targets, all_matches=False):
    ids = []
    unresolved = []
    for t in targets:
        t = str(t).strip()
        if re.fullmatch(r'\d+', t):
            ids.append(int(t))
            continue
        matches = []
        for kw in keywords(t):
            rows = query_list(token, kw)
            tn = norm(t)
            for r in rows:
                name = r.get('customerName') or r.get('companyName') or ''
                rn = norm(name)
                if not tn or tn in rn or rn in tn or norm(kw) in rn:
                    if r.get('id') and r not in matches:
                        matches.append(r)
            if matches:
                break
        if not matches:
            unresolved.append(t)
        elif len(matches) == 1 or all_matches:
            ids.extend(int(r['id']) for r in matches)
        else:
            print(f'匹配到多条，请指定 ID：{t}')
            for r in matches[:10]:
                print(f"  ID={r.get('id')} 名称={r.get('customerName') or r.get('companyName')}")
            unresolved.append(t)
    # 去重保序
    seen, unique = set(), []
    for i in ids:
        if i not in seen:
            unique.append(i); seen.add(i)
    return unique, unresolved


def main():
    ap = argparse.ArgumentParser(description='海典云客户审核：按 ID 或名称审核通过')
    ap.add_argument('targets', nargs='*', help='记录 ID 或厂家名称；多个用空格分隔')
    ap.add_argument('--all', action='store_true', help='名称匹配多条时全部审核（仅在用户明确要求全部通过时使用）')
    ap.add_argument('--list', action='store_true', help='列出待审核记录，不执行审核')
    ap.add_argument('--json', action='store_true', help='输出 JSON')
    args = ap.parse_args()

    token = login()
    if args.list:
        rows = query_list(token, '', 50)
        if args.json:
            print(json.dumps({'success': True, 'records': rows}, ensure_ascii=False))
        else:
            print(f'待审核 {len(rows)} 条：')
            for r in rows:
                print(f"ID={r.get('id')} 名称={r.get('customerName') or r.get('companyName')}")
        return

    if not args.targets:
        raise SystemExit('用法: python3 /root/scripts/haidianyun_audit.py <record_id|厂家名称> [更多ID/名称]')

    ids, unresolved = resolve_ids(token, args.targets, all_matches=args.all)
    results = []
    for rid in ids:
        try:
            d = detail(token, rid)
            res = audit_pass(token, d)
            ok = res.get('code') == '00103' or '成功' in str(res.get('msg', ''))
            results.append({'id': rid, 'name': d.get('customerName'), 'success': ok, 'msg': res.get('msg')})
        except Exception as e:
            results.append({'id': rid, 'success': False, 'msg': str(e)})

    success = all(r.get('success') for r in results) and not unresolved
    if args.json:
        print(json.dumps({'success': success, 'results': results, 'unresolved': unresolved}, ensure_ascii=False))
    else:
        for r in results:
            mark = '✅' if r.get('success') else '❌'
            print(f"{mark} ID={r.get('id')} {r.get('name') or ''}: {r.get('msg') or ('审核通过' if r.get('success') else '失败')}")
        for u in unresolved:
            print(f'❌ 未找到或需指定 ID: {u}')
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
