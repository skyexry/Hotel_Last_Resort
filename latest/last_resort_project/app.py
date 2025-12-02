import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, g
import subprocess
from datetime import date, timedelta

app = Flask(__name__)
DATABASE = os.path.join(app.root_path, 'hotel1.db')
SYSTEM_DATE = date(2025, 11, 25)

# last_resort_
def init_reservation_data():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # 检查 reservation 表是否为空
    cur.execute("SELECT COUNT(*) FROM reservation;")
    count = cur.fetchone()[0]

    conn.close()

    if count == 0:
        print("⚠️ reservation is empty run the dataGeneration file")
        subprocess.run(["python3", "reservationData.py"])
        print("🎉 reservation data generated")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    with app.app_context():
        db = get_db()
        with open('schema.sql', mode='r') as f:
            db.executescript(f.read())
        with open('populate.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()
        print("Database initialized.")
        print("Using DB:", DATABASE)
        init_reservation_data()

@app.route('/')
def dashboard():
    db = get_db()
    today_str = SYSTEM_DATE.strftime('%Y-%m-%d')
    
    occupancy_count = db.execute("""
        SELECT COUNT(*) 
        FROM reservation 
        WHERE status IN ('CheckedIn', 'Booked')
        AND startDate <= ? AND endDate > ?
    """, (today_str, today_str)).fetchone()[0]

    total_rooms = db.execute("SELECT COUNT(*) FROM room").fetchone()[0]
    occupancy_rate = round((occupancy_count / total_rooms * 100), 1) if total_rooms > 0 else 0
    arrivals_count = db.execute("SELECT COUNT(*) FROM reservation WHERE startDate = ?", (today_str,)).fetchone()[0]
    departures_count = db.execute("SELECT COUNT(*) FROM reservation WHERE endDate = ?", (today_str,)).fetchone()[0]
    revenue_today = db.execute("""
        SELECT SUM(rm.baseRate)
        FROM reservation r
        JOIN room rm ON r.roomId = rm.roomId
        WHERE r.status IN ('CheckedIn', 'Booked')
        AND r.startDate <= ? AND r.endDate > ?
    """, (today_str, today_str)).fetchone()[0]
    revenue_today = round(revenue_today, 2) if revenue_today else 0
    arrivals_data = db.execute("""
        SELECT r.resvId, 
               CASE 
                   WHEN pe.partyId IS NOT NULL THEN pe.firstName || ' ' || pe.lastName 
                   ELSE o.orgName 
               END as guestName,
               r.status, 
               rm.roomNumber
        FROM reservation r
        JOIN party p ON r.partyId = p.partyId
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization o ON p.partyId = o.partyId
        LEFT JOIN room rm ON r.roomId = rm.roomId
        WHERE r.startDate = ?
        ORDER BY r.status DESC
        LIMIT 5
    """, (today_str,)).fetchall()

    kpi_data = {
        'occupancy': occupancy_rate,
        'arrivals': arrivals_count,
        'departures': departures_count,
        'revenue': revenue_today
    }

    return render_template('dashboard.html', 
                           kpi=kpi_data, 
                           arrivals=arrivals_data, 
                           active_page='dashboard')

@app.route('/rooms')
def rooms():
    db = get_db()
    status_filter = request.args.get('status', 'All')
    search_query = request.args.get('search', '')

    sql = """
        SELECT r.roomId, r.roomNumber, r.currentStatus, r.baseRate, 
               w.wingName, f.floorNo, rf.name as funcName
        FROM room r
        JOIN floor f ON r.floorId = f.floorId
        JOIN wing w ON f.wingId = w.wingId
        LEFT JOIN room_has_function rhf ON r.roomId = rhf.roomId
        LEFT JOIN room_function rf ON rhf.functionCode = rf.functionCode
        WHERE 1=1
    """
    params = []
    if status_filter != 'All':
        sql += " AND r.currentStatus = ?"
        params.append(status_filter)
    if search_query:
        sql += " AND (r.roomNumber LIKE ? OR w.wingName LIKE ?)"
        params.append(f'%{search_query}%')
        params.append(f'%{search_query}%')

    rooms_data = db.execute(sql, params).fetchall()
    return render_template('rooms.html', rooms=rooms_data, active_page='rooms')

@app.route('/room/<int:room_id>')
def room_detail(room_id):
    db = get_db()
    room = db.execute("""
        SELECT r.*, f.floorNo, w.wingName, rf.name as funcName
        FROM room r
        JOIN floor f ON r.floorId = f.floorId
        JOIN wing w ON f.wingId = w.wingId
        LEFT JOIN room_has_function rhf ON r.roomId = rhf.roomId
        LEFT JOIN room_function rf ON rhf.functionCode = rf.functionCode
        WHERE r.roomId = ?
    """, (room_id,)).fetchone()

    beds = db.execute("""
        SELECT bt.name, bt.capacity, rhb.count
        FROM room_has_bed rhb
        JOIN bed_type bt ON rhb.bedTypeId = bt.bedTypeId
        WHERE rhb.roomId = ?
    """, (room_id,)).fetchall()

    fixtures = db.execute("""
        SELECT rfix.name 
        FROM room_has_fixture rhf
        JOIN room_fixture rfix ON rhf.fixtureId = rfix.fixtureId
        WHERE rhf.roomId = ?
    """, (room_id,)).fetchall()

    adjacencies = db.execute("""
        SELECT r.roomId, r.roomNumber, ra.connectionType
        FROM room_adjacency ra
        JOIN room r ON (ra.roomId1 = r.roomId OR ra.roomId2 = r.roomId)
        WHERE (ra.roomId1 = ? OR ra.roomId2 = ?) AND r.roomId != ?
    """, (room_id, room_id, room_id)).fetchall()

    maintenance = db.execute("""
        SELECT ticketId, issueDescription, status, dateCreated, dateResolved
        FROM maintenance_ticket
        WHERE roomId = ?
        ORDER BY dateCreated DESC
    """, (room_id,)).fetchall()

    history = db.execute("""
        SELECT s.checkInTime, s.checkOutTime, 
               COALESCE(pe.firstName || ' ' || pe.lastName, o.orgName) as guestName
        FROM stay s
        JOIN room_assignment ra ON s.resvId = ra.resvId
        JOIN reservation r ON s.resvId = r.resvId
        JOIN party p ON r.partyId = p.partyId
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization o ON p.partyId = o.partyId
        WHERE ra.roomId = ?
        ORDER BY s.checkInTime DESC
    """, (room_id,)).fetchall()

    return render_template('room_detail.html', room=room, beds=beds, fixtures=fixtures, 
                           adjacencies=adjacencies, maintenance=maintenance, history=history,
                           active_page='rooms')

@app.route('/reservations')
def reservations():
    db = get_db()
    search_query = request.args.get('search', '')
    sort = request.args.get('sort', 'startDate')
    direction = request.args.get('direction', request.args.get('order', 'desc')).lower()

    allowed_sort_cols = {
        "resvId": "r.resvId",
        "startDate": "r.startDate",
        "endDate": "r.endDate",
        "status": "r.status",
        "displayName": "displayName"
    }
    sort_col = allowed_sort_cols.get(sort, "r.startDate")
    direction = "ASC" if direction == "asc" else "DESC"

    sql = f"""
        SELECT 
            r.resvId, r.startDate, r.endDate, r.status,
            COALESCE(pe.firstName || ' ' || pe.lastName, o.orgName) as displayName,
            CASE WHEN pe.partyId IS NOT NULL THEN 'Person' ELSE 'Org' END as partyType
        FROM reservation r
        JOIN party p ON r.partyId = p.partyId
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization o ON p.partyId = o.partyId
        WHERE 1=1
    """

    params = []
    if search_query:
        sql += """ 
           AND (
            pe.firstName LIKE ? 
            OR pe.lastName LIKE ? 
            OR (pe.firstName || ' ' || pe.lastName) LIKE ?
            OR o.orgName LIKE ?
        )
        """
        s = f'%{search_query}%'
        params.extend([s, s, s, s])
    sql += f" ORDER BY {sort_col} {direction}"

    reservations = db.execute(sql, params).fetchall()

    return render_template(
        'reservations.html',
        reservations=reservations,
        active_page='reservations'
    )

@app.route('/reservations/new', methods=['GET', 'POST'])
def new_reservation():
    db = get_db()
    if request.method == 'POST':
        guest_mode = request.form.get('guest_mode')
        party_id = None
        if guest_mode == 'new':
            email = request.form.get('email')
            phone = request.form.get('phone')
            cursor = db.cursor()
            cursor.execute("INSERT INTO party (email, phone) VALUES (?, ?)", (email, phone))
            party_id = cursor.lastrowid
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            cursor.execute("INSERT INTO person (partyId, firstName, lastName) VALUES (?, ?, ?)", 
                           (party_id, first_name, last_name))
            db.commit()
        else:
            party_id = request.form.get('party_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        db.execute("INSERT INTO reservation (partyId, startDate, endDate, status) VALUES (?, ?, ?, 'Booked')",
                   (party_id, start_date, end_date))
        db.commit()
        return redirect(url_for('reservations'))
    
    parties = db.execute("""
        SELECT p.partyId, 
        COALESCE(pe.firstName || ' ' || pe.lastName, o.orgName) as name
        FROM party p
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization o ON p.partyId = o.partyId
    """).fetchall()
    return render_template('reservation_new.html', parties=parties, active_page='reservations')

@app.route('/checkin/<int:resv_id>')
def checkin(resv_id):
    db = get_db()
    resv = db.execute("""
        SELECT r.resvId, r.startDate, r.endDate,
               COALESCE(pe.firstName || ' ' || pe.lastName, o.orgName) as guestName
        FROM reservation r
        LEFT JOIN person pe ON r.partyId = pe.partyId
        LEFT JOIN organization o ON r.partyId = o.partyId
        WHERE r.resvId = ?
    """, (resv_id,)).fetchone()
    available_rooms = db.execute("SELECT * FROM room WHERE currentStatus = 'Clean'").fetchall()
    return render_template('checkin.html', resv=resv, rooms=available_rooms, active_page='reservations')

@app.route('/parties')
def parties():
    db = get_db()

    # --- 1) 获取 search, sort, order 参数 ---
    search_query = request.args.get('search', '')
    sort_col = request.args.get('sort', 'partyId')   # 默认按 ID
    order = request.args.get('order', 'asc').lower() # asc / desc

    # --- 2) 限制可排序字段（防止 SQL 注入）---
    allowed_sort_cols = {
        'partyId': 'p.partyId',
        'displayName': 'displayName',
        'type': 'type',
        'email': 'p.email',
        'phone': 'p.phone'
    }
    sort_sql = allowed_sort_cols.get(sort_col, 'p.partyId')

    # --- 3) 限制 order ---
    if order not in ['asc', 'desc']:
        order = 'asc'

    # --- 4) 主 SQL ---
    sql = f"""
        SELECT p.partyId, p.email, p.phone,
               COALESCE(pe.firstName || ' ' || pe.lastName, o.orgName) AS displayName,
               CASE WHEN pe.partyId IS NOT NULL THEN 'Person' ELSE 'Organization' END AS type
        FROM party p
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization o ON p.partyId = o.partyId
        WHERE 1=1
    """

    # --- 5) search 部分 ---
    params = []
    if search_query:
        sql += """ 
           AND (
            pe.firstName LIKE ? 
            OR pe.lastName LIKE ? 
            OR (pe.firstName || ' ' || pe.lastName) LIKE ?
            OR o.orgName LIKE ?
        )
        """
        s = f'%{search_query}%'
        params.extend([s, s, s, s])

    # --- 6) 排序部分 ---
    sql += f" ORDER BY {sort_sql} {order}"

    # --- 7) 执行查询 ---
    parties_list = db.execute(sql, params).fetchall()

    return render_template(
        'parties.html',
        parties=parties_list,
        active_page='parties'
    )


@app.route('/events')
def events():
    db = get_db()
    events_list = db.execute("""
        SELECT e.name, e.description, e.startDate, e.endDate, r.roomNumber, o.orgName
        FROM event e
        LEFT JOIN room r ON e.roomId = r.roomId
        LEFT JOIN organization o ON e.partyId = o.partyId
    """).fetchall()
    return render_template('events.html', events=events_list, active_page='events')

@app.route('/billing')
def billing():
    db = get_db()
    # Changed alias 'org' to 'o' to avoid any potential keyword conflicts or typos
    accounts = db.execute("""
        SELECT b.accountId, b.status, 
               COALESCE(pe.firstName || ' ' || pe.lastName, o.orgName) as responsibleParty,
               (SELECT SUM(amount) FROM charge c WHERE c.accountId = b.accountId) as total_balance
        FROM billing_account b
        LEFT JOIN party p ON b.partyId = p.partyId
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization o ON p.partyId = o.partyId
    """).fetchall()
    return render_template('billing.html', accounts=accounts, active_page='billing')

@app.route('/reports')
def reports():
    db = get_db()
    # 1. Top 10 Clients
    report_revenuetop10 = db.execute("""
        SELECT p.partyId, 
               CASE WHEN pe.partyId IS NOT NULL THEN pe.firstName || ' ' || pe.lastName 
                    ELSE o.orgName END as partyName,
               COUNT(r.resvId) as stays,
               SUM(c.amount) as totalSpent
        FROM billing_account b
        JOIN party p ON b.partyId = p.partyId
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization o ON p.partyId = o.partyId
        JOIN charge c ON b.accountId = c.accountId
        JOIN reservation r ON b.partyId = r.partyId
        GROUP BY p.partyId
        ORDER BY totalSpent DESC
        LIMIT 10
    """).fetchall()

    # 2. Room Utilization
    report_util = db.execute("""
        SELECT rf.name as room_type,
               COUNT(r.roomId) as total_rooms,
               SUM(CASE WHEN r.currentStatus = 'Occupied' THEN 1 ELSE 0 END) as occupied_count
        FROM room r
        JOIN room_has_function rhf ON r.roomId = rhf.roomId
        JOIN room_function rf ON rhf.functionCode = rf.functionCode
        GROUP BY room_type
    """).fetchall()

    # 3. Monthly Revenue
    report_monthly = db.execute("""
        SELECT strftime('%Y-%m', dateIncurred) as month,
               SUM(amount) as total_rev
        FROM charge
        GROUP BY month
        ORDER BY month ASC
    """).fetchall()

    # 4. Service Breakdown
    report_service = db.execute("""
        SELECT serviceCode, SUM(amount) as total
        FROM charge
        WHERE serviceCode != 'ROOM'
        GROUP BY serviceCode
        ORDER BY total DESC
    """).fetchall()

    # 5. Cancellation Stats
    report_cancel = db.execute("""
        SELECT strftime('%Y-%m', startDate) as month,
               COUNT(*) as total_resv,
               SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled_count
        FROM reservation
        GROUP BY month
        ORDER BY month DESC
    """).fetchall()

    # 6. Demographics
    report_demographics = db.execute("""
        SELECT CASE WHEN pe.partyId IS NOT NULL THEN 'Individual' ELSE 'Organization' END as party_type,
               COUNT(DISTINCT b.accountId) as active_accounts,
               ROUND(AVG(total_amt), 2) as avg_spend
        FROM billing_account b
        JOIN party p ON b.partyId = p.partyId
        LEFT JOIN person pe ON p.partyId = pe.partyId
        JOIN (SELECT accountId, SUM(amount) as total_amt FROM charge GROUP BY accountId) c ON b.accountId = c.accountId
        GROUP BY party_type
    """).fetchall()
    
    # 7. Avg Stay Length
    report_average_stay = db.execute("""
        SELECT rf.name as room_type,
               ROUND(AVG(julianday(endDate) - julianday(startDate)), 1) as avg_stay
        FROM reservation r
        JOIN room rm ON r.roomId = rm.roomId
        JOIN room_has_function rhf ON rm.roomId = rhf.roomId
        JOIN room_function rf ON rhf.functionCode = rf.functionCode
        GROUP BY room_type
        ORDER BY avg_stay DESC
    """).fetchall()

    # 8. Peak Occupancy
    report_peak_occupancy = db.execute("""
        SELECT strftime('%w', startDate) AS weekday,
               COUNT(*) AS reservations
        FROM reservation
        WHERE status != 'Cancelled'
        GROUP BY weekday
        ORDER BY weekday
    """).fetchall()

    # Chart 1: Revenue Line Chart
    c1_labels = [row['month'] for row in report_monthly]
    c1_data = [row['total_rev'] for row in report_monthly]

    # Chart 2: 7-Day Occupancy
    observation_date = SYSTEM_DATE
    c2_labels = []
    c2_data = []
    for i in range(6, -1, -1):
        target_date = observation_date - timedelta(days=i)
        t_str = target_date.strftime('%Y-%m-%d')
        cnt = db.execute("""
            SELECT COUNT(*) FROM reservation 
            WHERE status IN ('CheckedIn', 'Booked') 
            AND startDate <= ? AND endDate > ?
        """, (t_str, t_str)).fetchone()[0]
        c2_labels.append(target_date.strftime('%m-%d'))
        c2_data.append(cnt)

    # Chart 3: Service Revenue
    c3_labels = [row['serviceCode'] for row in report_service]
    c3_data = [row['total'] for row in report_service]

    # Chart 4: Guest Demographics (Pie)
    c4_labels = [row['party_type'] for row in report_demographics]
    c4_data = [row['active_accounts'] for row in report_demographics]

    trend_direction = 'flat'
    if len(report_monthly) >= 2:
        last_month_rev = report_monthly[-1]['total_rev']  
        prev_month_rev = report_monthly[-2]['total_rev']
        
        if last_month_rev >= prev_month_rev:
            trend_direction = 'up'
        else:
            trend_direction = 'down'

    return render_template('reports.html', 
                           report_revenue=report_revenuetop10, 
                           report_util=report_util,
                           report_monthly=report_monthly,
                           report_service=report_service,
                           report_cancel=report_cancel,
                           report_demographics=report_demographics,
                           report_average_stay=report_average_stay,
                           report_peak_occupancy=report_peak_occupancy,
                           c1_labels=c1_labels, c1_data=c1_data,
                           c2_labels=c2_labels, c2_data=c2_data,
                           c3_labels=c3_labels, c3_data=c3_data,
                           c4_labels=c4_labels, c4_data=c4_data,
                           trend_direction=trend_direction, 
                           active_page='reports')

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True, port=5000)
