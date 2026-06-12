#!/usr/bin/env python3
"""海典运营平台套餐数据同步脚本
每月1号全量拉取套餐数据到 PostgreSQL 数据库。
用法: python3 sync_hydee_orders.py
"""

import json
import hashlib
import urllib.request
import urllib.error
import time
from datetime import datetime

import psycopg2
import psycopg2.extras

# ============ 配置 ============
API_BASE = "https://middle.hydee.cn/businesses-gateway/operate/1.0"
ACCOUNT = "zangbangyu"
PASSWORD = "18663561336"
PAGE_SIZE = 100

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "sop_4chan",
    "user": "sop_4chan_app",
    "password": "2f8a3dae032cf9580cdc6f41a32b1a0a56f2264b4f535255",
}

# 事业部 英文→中文
BEDEPT_MAP = {
    "east-china": "华东事业部",
    "central-south": "中南事业部",
    "north": "北方事业部",
    "southwest": "西南事业部",
    "northwest": "西北事业部",
    "GM": "GM",
    "ka": "KA",
}

# 订购状态映射
STATUS_MAP = {
    1: "开通",
    2: "暂停",
    3: "未知",
    4: "已取消",
}


def login():
    pwd_hash = hashlib.md5(PASSWORD.encode()).hexdigest().upper()
    data = json.dumps({"account": ACCOUNT, "pwd": pwd_hash}).encode()
    req = urllib.request.Request(
        f"{API_BASE}/acc/_login",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read())
    token = body.get("data", {}).get("token")
    if not token:
        raise Exception(f"登录失败: {body}")
    return token


def api_post(token, endpoint, data):
    url = f"{API_BASE}/{endpoint}"
    body = json.dumps(data).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": token,
                },
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except (urllib.error.HTTPError, Exception):
            if attempt < 2:
                time.sleep(3)
                continue
            raise


def fetch_all(token):
    all_records = []
    page = 1
    while True:
        result = api_post(
            token,
            "merchant/queryMerchantServiceList",
            {"currentPage": page, "pageSize": PAGE_SIZE},
        )
        data = result.get("data", {})
        svc_list = data.get("sysMerchantServiceInfoList", [])
        total = data.get("totalCount", 0)

        all_records.extend(svc_list)

        if page % 20 == 0:
            print(f"  已拉取 {len(all_records)}/{total} 条...", flush=True)

        if len(svc_list) < PAGE_SIZE:
            break
        page += 1

    return all_records


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def init_db(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hydee_orders (
            id SERIAL PRIMARY KEY,
            插入时间 TIMESTAMP NOT NULL,
            商户名称 VARCHAR(255),
            商户编码 VARCHAR(64),
            所属事业部 VARCHAR(64),
            订购套餐 VARCHAR(255),
            订购时长 INTEGER DEFAULT 0,
            订购状态 VARCHAR(32),
            过期时间 VARCHAR(64),
            订购时间 VARCHAR(64),
            订购人 VARCHAR(64)
        )
    """)
    # 索引（IF NOT EXISTS 方式）
    for idx_name, col in [
        ("idx_hydee_orders_过期时间", "过期时间"),
        ("idx_hydee_orders_商户编码", "商户编码"),
        ("idx_hydee_orders_事业部", "所属事业部"),
        ("idx_hydee_orders_插入时间", "插入时间"),
    ]:
        cur.execute(f"""
            CREATE INDEX IF NOT EXISTS {idx_name} ON hydee_orders ({col})
        """)
    conn.commit()


def sync_to_db(conn, records, sync_time):
    cur = conn.cursor()
    # 用 TRUNCATE 快速清空（隐式提交，需在事务外或先 commit）
    # 改用事务内 DELETE
    old_autocommit = conn.autocommit
    conn.autocommit = True
    cur.execute("TRUNCATE TABLE hydee_orders RESTART IDENTITY")
    conn.autocommit = old_autocommit

    insert_sql = """
        INSERT INTO hydee_orders
            (插入时间, 商户名称, 商户编码, 所属事业部, 订购套餐, 订购时长, 订购状态, 过期时间, 订购时间, 订购人)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    rows = []
    for r in records:
        bedept_raw = r.get("bedept") or ""
        rows.append((
            sync_time,
            r.get("merName") or "",
            r.get("merCode") or "",
            BEDEPT_MAP.get(bedept_raw, bedept_raw),
            r.get("serName") or "",
            r.get("monthsNum") or 0,
            STATUS_MAP.get(r.get("status"), str(r.get("status", ""))),
            r.get("endTime") or "",
            r.get("startTime") or "",
            r.get("createName") or "",
        ))

    psycopg2.extras.execute_batch(cur, insert_sql, rows, page_size=500)
    conn.commit()
    return len(rows)


def main():
    start = time.time()
    sync_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{sync_time}] 开始同步海典套餐数据...", flush=True)

    print("登录中...", flush=True)
    token = login()

    print("拉取全部套餐记录...", flush=True)
    records = fetch_all(token)
    print(f"拉取完成，共 {len(records)} 条", flush=True)

    print("写入 PostgreSQL...", flush=True)
    conn = get_conn()
    try:
        init_db(conn)
        count = sync_to_db(conn, records, sync_time)
    finally:
        conn.close()

    elapsed = time.time() - start
    print(f"同步完成! 写入 {count} 条，耗时 {elapsed:.0f} 秒", flush=True)


if __name__ == "__main__":
    main()
