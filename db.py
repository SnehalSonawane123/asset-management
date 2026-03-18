import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="assetdb"
    )

def get_all_assets():
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM assets")
    rows = cur.fetchall()
    con.close()
    return rows

def add_asset(name, status, assigned_to):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO assets (name, status, assigned_to) VALUES (%s, %s, %s)",
                (name, status, assigned_to))
    con.commit()
    con.close()

def update_asset(asset_id, name, status, assigned_to):
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE assets SET name=%s, status=%s, assigned_to=%s WHERE id=%s",
                (name, status, assigned_to, asset_id))
    con.commit()
    con.close()

def delete_asset(asset_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM assets WHERE id=%s", (asset_id,))
    con.commit()
    con.close()

def get_asset_by_id(asset_id):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM assets WHERE id=%s", (asset_id,))
    row = cur.fetchone()
    con.close()
    return row
