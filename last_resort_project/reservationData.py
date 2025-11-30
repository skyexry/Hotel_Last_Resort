import pandas as pd
import numpy as np
import sqlite3
from datetime import date, timedelta
import os

# --- 1. 参数配置 ---
NUM_ROWS = 200
START_DATE_RANGE = date(2025, 9, 1)
END_DATE_RANGE = date(2026, 1, 1)
OBSERVATION_DATE = date(2025, 11, 25)
MIN_STAY = 2
MAX_STAY = 10

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "hotel1.db")


# --- 2. 生成 reservation 数据 ---
max_offset_days = (END_DATE_RANGE - START_DATE_RANGE).days

data = pd.DataFrame({
    'partyId': np.random.randint(1, 101, size=NUM_ROWS),
    'day_offset': np.random.randint(0, max_offset_days, size=NUM_ROWS),
    'stay_days': np.random.randint(MIN_STAY, MAX_STAY + 1, size=NUM_ROWS)
})

# 日期必须保证是 Python date 类型，不是 Timestamp
data['startDate'] = [
    START_DATE_RANGE + timedelta(days=o) for o in data['day_offset']
]

data['endDate'] = [
    s + timedelta(days=d) for s, d in zip(data['startDate'], data['stay_days'])
]

def get_status(row):
    if OBSERVATION_DATE < row['startDate']:
        return 'Booked'
    if row['startDate'] <= OBSERVATION_DATE < row['endDate']:
        return 'CheckedIn'
    return 'CheckedOut'

data['status'] = data.apply(get_status, axis=1)


# --- 3. 分配 roomId（仅给 CheckedIn / CheckedOut） ---
conn = sqlite3.connect(DB_FILE)
room_ids = pd.read_sql("SELECT roomId FROM room;", conn)['roomId'].tolist()
conn.close()

def assign_room(status):
    return np.random.choice(room_ids) if status != 'Booked' else None

data['roomId'] = data['status'].apply(assign_room)

# 最终数据列
final_df = data[['partyId', 'startDate', 'endDate', 'status', 'roomId']]


# --- 4. 写入 reservation 并生成 charge ---
try:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # 清空旧数据
    cur.execute("DELETE FROM reservation;")
    cur.execute("DELETE FROM charge;")

    # 插入 reservation
    insert_sql = """
        INSERT INTO reservation (partyId, startDate, endDate, status, roomId)
        VALUES (?, ?, ?, ?, ?)
    """
    cur.executemany(insert_sql, final_df.values.tolist())

    # --- ★ 新增：生成 room charge（关键） ---
    cur.execute("""
        INSERT INTO charge (accountId, serviceCode, amount, dateIncurred)
        SELECT
            b.accountId,
            'ROOM',
            rm.baseRate * (julianday(r.endDate) - julianday(r.startDate)),
            r.startDate
        FROM reservation r
        JOIN billing_account b ON b.partyId = r.partyId
        JOIN room rm ON rm.roomId = r.roomId
        WHERE r.roomId IS NOT NULL;
    """)

    conn.commit()

    print("🎉 成功写入 reservation 并生成 ROOM charge！")

    print("\n--- Reservation 示例 ---")
    print(pd.read_sql("SELECT * FROM reservation LIMIT 5", conn))

    print("\n--- Charge 示例 ---")
    print(pd.read_sql("SELECT * FROM charge LIMIT 5", conn))

except Exception as e:
    print(f"⚠️ 数据库写入错误: {e}")

finally:
    conn.close()
