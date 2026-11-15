import sqlite3

from employees import connect, create_payslip

conn = connect()
conn.execute(
    "INSERT OR IGNORE INTO pay_periods (frequency, start_date, end_date, payment_date) "
    "VALUES ('monthly', '2026-12-01', '2026-12-31', '2027-01-05')"
)
conn.commit()

# Predict first: what happens on the first run? On the second run?
try:
    create_payslip(1, 2, 200000, 20000, acting_user_id=1)
    print("payslip created")
except sqlite3.IntegrityError as error:
    print("rejected:", error)

for row in conn.execute(
    "SELECT audit_id, user_id, action, table_name, row_id, details, created_at FROM audit_log"
):
    print(row)

# The log must refuse edits and deletes.
for sql in ("UPDATE audit_log SET action = 'x'", "DELETE FROM audit_log"):
    try:
        conn.execute(sql)
        conn.commit()
        print("DANGER: allowed ->", sql)
    except sqlite3.IntegrityError as error:
        conn.rollback()
        print("blocked:", error)

conn.close()