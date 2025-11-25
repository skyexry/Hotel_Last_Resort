# checked: Latest version with A-level queries, new guest logic, and mass data init
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
    # Helper to initialize DB if not exists
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            with open('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            with open('populate.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
            print("Database initialized with A-level data.")

# --- Routes ---

@app.route('/')
def dashboard():
    db = get_db()
    occupancy = db.execute("SELECT COUNT(*) FROM room WHERE currentStatus = 'Occupied'").fetchone()[0]
    total_rooms = db.execute("SELECT COUNT(*) FROM room").fetchone()[0]
    occupancy_rate = round((occupancy / total_rooms * 100), 1) if total_rooms > 0 else 0
    
    today_arrivals = db.execute("""
        SELECT r.resvId, COALESCE(p.firstName || ' ' || p.lastName, o.orgName) as guestName, 
               r.status, rm.roomNumber
        FROM reservation r
        JOIN party py ON r.partyId = py.partyId
        LEFT JOIN person p ON py.partyId = p.partyId
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
    query = """
        SELECT r.roomId, r.roomNumber, r.currentStatus, r.baseRate, 
               w.wingName, f.floorNo, rf.name as funcName
        FROM room r
        JOIN floor f ON r.floorId = f.floorId
        JOIN wing w ON f.wingId = w.wingId
        LEFT JOIN room_has_function rhf ON r.roomId = rhf.roomId
        LEFT JOIN room_function rf ON rhf.functionCode = rf.functionCode
    """
    if status_filter != 'All':
        query += f" WHERE r.currentStatus = '{status_filter}'"
    rooms_data = db.execute(query).fetchall()
    return render_template('rooms.html', rooms=rooms_data, active_page='rooms')

@app.route('/reservations')
def reservations():
    db = get_db()
    reservations = db.execute("""
        SELECT r.resvId, r.startDate, r.endDate, r.status,
               COALESCE(pe.firstName || ' ' || pe.lastName, org.orgName) as displayName,
               CASE WHEN pe.partyId IS NOT NULL THEN 'Person' ELSE 'Org' END as partyType
        FROM reservation r
        JOIN party p ON r.partyId = p.partyId
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization org ON p.partyId = org.partyId
        ORDER BY r.startDate DESC
    """).fetchall()
    return render_template('reservations.html', reservations=reservations, active_page='reservations')

@app.route('/reservations/new', methods=['GET', 'POST'])
def new_reservation():
    db = get_db()
    if request.method == 'POST':
        guest_mode = request.form.get('guest_mode')
        party_id = None
        
        # Handle New Guest Creation Logic
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
        
    # GET: Fetch parties for dropdown
    parties = db.execute("""
        SELECT p.partyId, COALESCE(pe.firstName || ' ' || pe.lastName, org.orgName) as name
        FROM party p
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization org ON p.partyId = org.partyId
    """).fetchall()
    return render_template('reservation_new.html', parties=parties, active_page='reservations')

@app.route('/checkin/<int:resv_id>')
def checkin(resv_id):
    db = get_db()
    resv = db.execute("""
        SELECT r.resvId, r.startDate, r.endDate,
               COALESCE(pe.firstName || ' ' || pe.lastName, org.orgName) as guestName
        FROM reservation r
        LEFT JOIN person pe ON r.partyId = pe.partyId
        LEFT JOIN organization org ON r.partyId = org.partyId
        WHERE r.resvId = ?
    """, (resv_id,)).fetchone()
    available_rooms = db.execute("SELECT * FROM room WHERE currentStatus = 'Clean'").fetchall()
    return render_template('checkin.html', resv=resv, rooms=available_rooms, active_page='reservations')

@app.route('/parties')
def parties():
    db = get_db()
    parties_list = db.execute("""
        SELECT p.partyId, p.email, p.phone,
               pe.firstName, pe.lastName, org.orgName, org.contactName,
               CASE WHEN pe.partyId IS NOT NULL THEN 'Person' ELSE 'Organization' END as type
        FROM party p
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization org ON p.partyId = org.partyId
    """).fetchall()
    return render_template('parties.html', parties=parties_list, active_page='parties')

@app.route('/events')
def events():
    db = get_db()
    events_list = db.execute("""
        SELECT e.name, e.startDate, e.endDate, r.roomNumber, org.orgName
        FROM event e
        LEFT JOIN room r ON e.roomId = r.roomId
        LEFT JOIN organization org ON e.partyId = org.partyId
    """).fetchall()
    return render_template('events.html', events=events_list, active_page='events')

@app.route('/billing')
def billing():
    db = get_db()
    accounts = db.execute("""
        SELECT b.accountId, b.status, 
               COALESCE(pe.firstName || ' ' || pe.lastName, org.orgName) as responsibleParty,
               (SELECT SUM(amount) FROM charge c WHERE c.accountId = b.accountId) as total_balance
        FROM billing_account b
        LEFT JOIN party p ON b.partyId = p.partyId
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization org ON p.partyId = org.partyId
    """).fetchall()
    return render_template('billing.html', accounts=accounts, active_page='billing')

# --- 核心更新：报表路由 (A-Level Queries) ---
@app.route('/reports')
def reports():
    db = get_db()
    
    # 1. Top Revenue (Multi-table join, aggregation, sorting)
    report_revenue = db.execute("""
        SELECT COALESCE(pe.firstName || ' ' || pe.lastName, org.orgName) as partyName,
               SUM(c.amount) as totalSpent,
               COUNT(DISTINCT c.stayId) as stays
        FROM billing_account b
        JOIN charge c ON b.accountId = c.accountId
        JOIN party p ON b.partyId = p.partyId
        LEFT JOIN person pe ON p.partyId = pe.partyId
        LEFT JOIN organization org ON p.partyId = org.partyId
        GROUP BY partyName
        ORDER BY totalSpent DESC
        LIMIT 10
    """).fetchall()

    # 2. Room Utilization (Aggregation by Category)
    report_util = db.execute("""
        SELECT rf.name, COUNT(r.roomId) as total_rooms,
               SUM(CASE WHEN r.currentStatus = 'Occupied' THEN 1 ELSE 0 END) as occupied_count,
               ROUND(CAST(SUM(CASE WHEN r.currentStatus = 'Occupied' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(r.roomId) * 100, 1) as util_rate
        FROM room r
        JOIN room_has_function rhf ON r.roomId = rhf.roomId
        JOIN room_function rf ON rhf.functionCode = rf.functionCode
        GROUP BY rf.name
    """).fetchall()
    
    # 3. Monthly Revenue Trend (Date manipulation, Grouping)
    report_monthly = db.execute("""
        SELECT strftime('%Y-%m', dateIncurred) as month, 
               SUM(amount) as revenue
        FROM charge
        GROUP BY month
        ORDER BY month DESC
    """).fetchall()
    
    # 4. Service Type Popularity (Group By Service Code)
    report_service = db.execute("""
        SELECT st.description, COUNT(c.chargeId) as usage_count, SUM(c.amount) as total_revenue
        FROM charge c
        JOIN service_type st ON c.serviceCode = st.serviceCode
        GROUP BY st.description
        ORDER BY total_revenue DESC
    """).fetchall()

    # 5. Cancellation Rate by Month (CASE Statements, Date grouping)
    report_cancel = db.execute("""
        SELECT strftime('%Y-%m', startDate) as month,
               COUNT(*) as total_resv,
               SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled_count
        FROM reservation
        GROUP BY month
        ORDER BY month DESC
    """).fetchall()
    
    # 6. Guest Type Analysis (Person vs Organization Avg Spend)
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

    return render_template('reports.html', 
                           report_revenue=report_revenue, 
                           report_util=report_util,
                           report_monthly=report_monthly,
                           report_service=report_service,
                           report_cancel=report_cancel,
                           report_demographics=report_demographics,
                           active_page='reports')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results_guests = []
    results_resv = []
    
    if query:
        db = get_db()
        search_term = f"%{query}%"

        results_guests = db.execute("""
            SELECT p.partyId, 
                   CASE 
                       WHEN pe.partyId IS NOT NULL THEN 'Person' 
                       WHEN o.partyId IS NOT NULL THEN 'Organization' 
                       ELSE 'Unknown' 
                   END as type,
                   p.email, p.phone,
                   pe.firstName, pe.lastName, 
                   o.orgName
            FROM party p
            LEFT JOIN person pe ON p.partyId = pe.partyId
            LEFT JOIN organization o ON p.partyId = o.partyId
            WHERE pe.firstName LIKE ? 
               OR pe.lastName LIKE ? 
               OR o.orgName LIKE ? 
               OR p.email LIKE ?
        """, (search_term, search_term, search_term, search_term)).fetchall()

        if query.isdigit():
            results_resv = db.execute("""
                SELECT r.resvId, r.startDate, r.endDate, r.status,
                       pe.firstName, pe.lastName, o.orgName
                FROM reservation r
                JOIN party p ON r.partyId = p.partyId
                LEFT JOIN person pe ON p.partyId = pe.partyId
                LEFT JOIN organization o ON p.partyId = o.partyId
                WHERE r.resvId = ?
            """, (query,)).fetchall()
        
    return render_template('search.html', 
                           active_page='search', 
                           query=query, 
                           guests=results_guests, 
                           reservations=results_resv)

if __name__ == '__main__':
    # Init DB only if file doesn't exist to avoid overwriting every time
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True, port=5000)
