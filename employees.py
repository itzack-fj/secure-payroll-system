import sqlite3

from payroll import fnpf_employee_cents


def connect():
    conn = sqlite3.connect("payroll.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def list_employees():
    conn = connect()
    rows = conn.execute("SELECT employee_id, first_name, last_name FROM employees").fetchall()

    for row in rows:
        print(row[0], row[1], row[2])

    conn.close()


def find_employee_by_tin(tin):
    conn = connect()

    row = conn.execute(
        "SELECT employee_id, first_name, last_name FROM employees WHERE tin = ?",
        (tin,)
    ).fetchone()

    conn.close()
    return row


def create_payslip(employee_id, pay_period_id, gross_cents, paye_cents):
    # PAYE is passed in for now. The real formula comes later, after we check FRCS's rules.
    fnpf_cents = fnpf_employee_cents(gross_cents)
    net_cents = gross_cents - fnpf_cents - paye_cents

    conn = connect()
    try:
        conn.execute(
            "INSERT INTO payslips "
            "(employee_id, pay_period_id, gross_pay_cents, fnpf_employee_cents, paye_cents, net_pay_cents) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (employee_id, pay_period_id, gross_cents, fnpf_cents, paye_cents, net_cents),
        )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    list_employees()
    print(find_employee_by_tin("000000001"))

    attempts = [
        ("valid payslip", (1, 1, 200000, 20000)),
        ("duplicate payslip", (1, 1, 200000, 20000)),
        ("employee that doesn't exist", (999, 1, 200000, 20000)),
    ]
    for label, args in attempts:
        try:
            create_payslip(*args)
            print(label, "-> created")
        except sqlite3.IntegrityError as error:
            print(label, "-> rejected:", error)