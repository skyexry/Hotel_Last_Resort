import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = 'hotel.db'

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
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            with open('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            with open('populate.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
            print("Database initialized.")

@app.route('/')
def dashboard():
    db = get_db()
    occupancy = db.execute("SELECT COUNT(*) FROM room WHERE currentStatus = 'Occupied'").fetchone()[0]
    total_rooms = db.execute("SELECT COUNT(*) FROM room").fetchone()[0]
    occupancy_rate = round((occupancy / total_rooms * 100), 1) if total_rooms > 0 else 0
    
    today_arrivals = db.execute("""
        SELECT r.resvId, 
               COALESCE(pe.firstName || ' ' || pe.lastName, o.orgName) as guestName, 
               r.status, rm.roomNumber
        FROM reservation r
        JOIN party py ON r.partyId = py.partyId
        LEFT JOIN person pe ON py.partyId = pe.partyId
        LEFT JOIN organization o ON py.partyId = o.partyId
        LEFT JOIN room_assignment ra ON r.resvId = ra.resvId
        LEFT JOIN room rm ON ra.roomId = rm.roomId
        WHERE r.startDate <= date('now') AND r.status = 'Booked'
    """).fetchall()

    revenue = db.execute("SELECT SUM(amount) FROM charge WHERE dateIncurred = date('now')").fetchone()[0] or 0.00

    kpi = {
        "occupancy": occupancy_rate,
        "arrivals": len(today_arrivals),
        "departures": 0,
        "revenue": revenue
    }
    return render_template('dashboard.html', kpi=kpi, arrivals=today_arrivals, active_page='dashboard')

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
    sql = """
        SELECT r.resvId, r.startDate, r.endDate, r.status,
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
        sql += " AND (pe.firstName LIKE ? OR pe.lastName LIKE ? OR o.orgName LIKE ?)"
        s = f'%{search_query}%'
        params.extend([s, s, s])
    sql += " ORDER BY r.startDate DESC"
    reservations = db.execute(sql, params).fetchall()
    return render_template('reservations.html', reservations=reservations, active_page='reservations')

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
    search_query = request.args.get('search', '')
    sql = """
        SELECT p.partyId, p.email, p.phone,
               COALESCE(pe.firstName || ' ' || pe.lastName, o.orgName) as displayName,
               CASE WHEN pe.partyId IS NOT NULL THEN 'Person' ELSE 'Organization' END as type
        FROM party p
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization o ON p.partyId = o.partyId
        WHERE 1=1
    """
    params = []
    if search_query:
        sql += " AND (pe.firstName LIKE ? OR pe.lastName LIKE ? OR o.orgName LIKE ?)"
        s = f'%{search_query}%'
        params.extend([s, s, s])
    parties_list = db.execute(sql, params).fetchall()
    return render_template('parties.html', parties=parties_list, active_page='parties')

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
    report_revenue = db.execute("""
        SELECT COALESCE(pe.firstName || ' ' || pe.lastName, o.orgName) as partyName,
               SUM(c.amount) as totalSpent,
               COUNT(DISTINCT c.stayId) as stays
        FROM billing_account b
        JOIN charge c ON b.accountId = c.accountId
        JOIN party p ON b.partyId = p.partyId
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization o ON p.partyId = o.partyId
        GROUP BY partyName ORDER BY totalSpent DESC LIMIT 10
    """).fetchall()
    
    report_util = db.execute("""
        SELECT rf.name, COUNT(r.roomId) as total_rooms,
               SUM(CASE WHEN r.currentStatus = 'Occupied' THEN 1 ELSE 0 END) as occupied_count,
               ROUND(CAST(SUM(CASE WHEN r.currentStatus = 'Occupied' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(r.roomId) * 100, 1) as util_rate
        FROM room r JOIN room_has_function rhf ON r.roomId = rhf.roomId JOIN room_function rf ON rhf.functionCode = rf.functionCode GROUP BY rf.name
    """).fetchall()
    
    report_monthly = db.execute("""SELECT strftime('%Y-%m', dateIncurred) as month, SUM(amount) as revenue FROM charge GROUP BY month ORDER BY month DESC""").fetchall()
    report_service = db.execute("""SELECT st.description, COUNT(c.chargeId) as usage_count, SUM(c.amount) as total_revenue FROM charge c JOIN service_type st ON c.serviceCode = st.serviceCode GROUP BY st.description ORDER BY total_revenue DESC""").fetchall()
    report_cancel = db.execute("""SELECT strftime('%Y-%m', startDate) as month, COUNT(*) as total_resv, SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled_count FROM reservation GROUP BY month ORDER BY month DESC""").fetchall()
    report_demographics = db.execute("""SELECT CASE WHEN pe.partyId IS NOT NULL THEN 'Individual' ELSE 'Organization' END as party_type, COUNT(DISTINCT b.accountId) as active_accounts, ROUND(AVG(total_amt), 2) as avg_spend FROM billing_account b JOIN party p ON b.partyId = p.partyId LEFT JOIN person pe ON p.partyId = pe.partyId JOIN (SELECT accountId, SUM(amount) as total_amt FROM charge GROUP BY accountId) c ON b.accountId = c.accountId GROUP BY party_type""").fetchall()

    return render_template('reports.html', report_revenue=report_revenue, report_util=report_util, 
                           report_monthly=report_monthly, report_service=report_service,
                           report_cancel=report_cancel, report_demographics=report_demographics,
                           active_page='reports')

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True, port=5000)