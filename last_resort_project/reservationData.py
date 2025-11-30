import pandas as pd
import numpy as np
import sqlite3
from datetime import date, timedelta

# --- 1. 定义参数 ---
NUM_ROWS = 200
START_DATE_RANGE = date(2025, 9, 1)
END_DATE_RANGE = date(2026, 1, 1)
OBSERVATION_DATE = date(2025, 11, 25)
MIN_STAY = 3
MAX_STAY = 10

# --- 2. 生成随机 reservation 数据 ---
max_offset_days = (END_DATE_RANGE - START_DATE_RANGE).days

data = pd.DataFrame({
    'partyId': np.random.randint(1, 101, size=NUM_ROWS),
    'day_offset': np.random.randint(0, max_offset_days, size=NUM_ROWS),
    'stay_days': np.random.randint(MIN_STAY, MAX_STAY + 1, size=NUM_ROWS)
})

data['startDate'] = (
    pd.to_datetime(START_DATE_RANGE)
    + data['day_offset'].apply(lambda x: timedelta(days=x))
).dt.date

data['endDate'] = (
    pd.to_datetime(data['startDate'])
    + data['stay_days'].apply(lambda x: timedelta(days=x))
).dt.date

def get_status(row):
    start = row['startDate']
    end = row['endDate']
    today = OBSERVATION_DATE
    if today < start:
        return 'Booked'
    if start <= today < end:
        return 'CheckedIn'
    return 'CheckedOut'

data['status'] = data.apply(get_status, axis=1)

# --- 3. 为 CheckedIn / CheckedOut 随机分配有效 roomId ---
# 读取数据库中的房间 ID
DB_FILE = "/Users/su/Desktop/Database/Hotel_Last_Resort/last_resort_project/hotel1.db"

conn = sqlite3.connect(DB_FILE)
room_ids = pd.read_sql("SELECT roomId FROM room;", conn)['roomId'].tolist()
conn.close()

def assign_room(status):
    if status == 'Booked':
        return None  # 未入住，不分配房
    return np.random.choice(room_ids)  # CheckedIn / CheckedOut 分配房间

data['roomId'] = data['status'].apply(assign_room)

# 最终数据列
final_df = data[['partyId', 'startDate', 'endDate', 'status', 'roomId']]

# --- 4. 写入 SQLite ---
try:
    conn = sqlite3.connect(DB_FILE)
    
    # 清空旧数据
    conn.execute("DELETE FROM reservation;")

    insert_sql = """
        INSERT INTO reservation (partyId, startDate, endDate, status, roomId)
        VALUES (?, ?, ?, ?, ?)
    """

    conn.executemany(insert_sql, final_df.values.tolist())
    conn.commit()

    print("🎉 成功将 200 条带 roomId 的 reservation 写入数据库！")

    sample = pd.read_sql("SELECT * FROM reservation LIMIT 5", conn)
    print("\n--- 写入验证 (前 5 行) ---")
    print(sample)

except Exception as e:
    print(f"⚠️ 写入数据库时发生错误: {e}")

finally:
    if 'conn' in locals():
        conn.close()
