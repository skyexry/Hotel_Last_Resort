import pandas as pd
import numpy as np
import sqlite3
from datetime import date, timedelta
import os
import random

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


# --- 2.5 真实化：随机生成 Cancelled 状态 ---
cancel_indices = data[(data['status'] == 'Booked')].sample(frac=0.10, random_state=42).index

for idx in cancel_indices:
    row = data.loc[idx]
    start = row["startDate"]
    cancel_date = start - timedelta(days=random.randint(1, 7))
    data.at[idx, "status"] = "Cancelled"
    data.at[idx, "endDate"] = cancel_date   # 对 cancelled，endDate 改为 cancel date


# --- 3. 只给 CheckedIn / CheckedOut 分配房间 ---
conn = sqlite3.connect(DB_FILE)
room_ids = pd.read_sql("SELECT roomId FROM room;", conn)['roomId'].tolist()
conn.close()

def assign_room(status):
    return np.random.choice(room_ids) if status not in ['Booked', 'Cancelled'] else None

data['roomId'] = data['status'].apply(assign_room)

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

    # --- (A) ROOM charge：仅入住/已退房客户 ---
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

    # --- (B) FOOD / SPA / MISC 消费 ---
    charge_rows = []
    for _, row in final_df.iterrows():
        if row["status"] in ["Booked", "Cancelled"]:
            continue

        partyId = row["partyId"]
        start = row["startDate"]
        end = row["endDate"]
        stay_len = (end - start).days

        num_charges = random.randint(1, 3)

        for _ in range(num_charges):
            incur_date = start + timedelta(days=random.randint(0, max(0, stay_len - 1)))

            service = random.choice(["FOOD", "SPA", "MISC"])

            if service == "FOOD":
                amount = random.randint(40, 200)
            elif service == "SPA":
                amount = random.randint(80, 400)
            else:
                amount = random.randint(20, 120)

            charge_rows.append((partyId, service, amount, incur_date))

    # 插入消费记录
    cur.executemany("""
        INSERT INTO charge (accountId, serviceCode, amount, dateIncurred)
        VALUES (?, ?, ?, ?)
    """, charge_rows)

    conn.commit()
    print("🎉 已成功生成 reservation + ROOM + FOOD + SPA + MISC + Cancelled 数据！")

except Exception as e:
    print(f"⚠️ 数据库写入错误: {e}")

finally:
    conn.close()
