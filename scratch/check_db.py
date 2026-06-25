import sqlite3

def check_and_update():
    try:
        conn = sqlite3.connect('backend/db.sqlite3')
        cursor = conn.cursor()
        
        # Verify table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patients_patient';")
        if not cursor.fetchone():
            print("Table patients_patient does not exist.")
            return

        # Check initial values
        cursor.execute("SELECT id, blood_group FROM patients_patient;")
        rows = cursor.fetchall()
        print("Before update, patient profiles:", rows)

        # Update empty blood groups
        cursor.execute("UPDATE patients_patient SET blood_group='O+' WHERE blood_group IS NULL OR blood_group='';")
        conn.commit()
        print("Updated rows count:", cursor.rowcount)

        # Check after values
        cursor.execute("SELECT id, blood_group FROM patients_patient;")
        rows_after = cursor.fetchall()
        print("After update, patient profiles:", rows_after)
        
        conn.close()
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    check_and_update()
