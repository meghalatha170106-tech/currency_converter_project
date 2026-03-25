from models.db import get_db_connection

# Add history
def add_history(user, from_currency, to_currency, amount, result):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO history (user, from_currency, to_currency, amount, result)
        VALUES (?, ?, ?, ?, ?)
    """, (user, from_currency, to_currency, amount, result))

    conn.commit()
    conn.close()

# Get user history
def get_history(user):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM history WHERE user=?", (user,))
    data = cur.fetchall()
    conn.close()

    return data

# Dashboard data
def get_dashboard_data(user):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM history WHERE user=?", (user,))
    total = cur.fetchone()[0]

    cur.execute("""
        SELECT from_currency, COUNT(*) 
        FROM history 
        WHERE user=? 
        GROUP BY from_currency 
        ORDER BY COUNT(*) DESC LIMIT 1
    """, (user,))
    
    popular = cur.fetchone()

    conn.close()

    return total, popular