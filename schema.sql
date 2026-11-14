CREATE TABLE pay_periods (
    pay_period_id INTEGER PRIMARY KEY,
    frequency     TEXT NOT NULL CHECK (frequency IN ('weekly', 'fortnightly', 'monthly')),
    start_date    TEXT NOT NULL,
    end_date      TEXT NOT NULL,
    payment_date  TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'open'
                  CHECK (status IN ('open', 'processing', 'approved', 'paid', 'closed')),
    CHECK (end_date >= start_date),
    CHECK (date(start_date) IS start_date),
    CHECK (date(end_date) IS end_date),
    CHECK (date(payment_date) IS payment_date),
    UNIQUE (frequency, start_date, end_date)
);

CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,

    tin TEXT NOT NULL UNIQUE,
    fnpf_number TEXT NOT NULL UNIQUE,

    employment_type TEXT NOT NULL
        CHECK (employment_type IN ('full_time', 'part_time', 'casual')),

    pay_type TEXT NOT NULL
        CHECK (pay_type IN ('hourly', 'salary')),

    -- For salary: annual salary in cents.
    -- For hourly: hourly rate in cents.
    base_rate_cents INTEGER NOT NULL
        CHECK (base_rate_cents >= 0),

    tax_resident INTEGER NOT NULL
        CHECK (tax_resident IN (0, 1)),

    hire_date TEXT NOT NULL,
    termination_date TEXT,

    CHECK (date(hire_date) IS hire_date),
    CHECK (termination_date IS NULL OR date(termination_date) IS termination_date),
    CHECK (termination_date IS NULL OR termination_date >= hire_date)
);

CREATE TABLE payslips (
    payslip_id INTEGER PRIMARY KEY,

    employee_id INTEGER NOT NULL,
    pay_period_id INTEGER NOT NULL,

    gross_pay_cents INTEGER NOT NULL,
    fnpf_employee_cents INTEGER NOT NULL,
    paye_cents INTEGER NOT NULL,
    net_pay_cents INTEGER NOT NULL,

    FOREIGN KEY (employee_id)
        REFERENCES employees (employee_id),

    FOREIGN KEY (pay_period_id)
        REFERENCES pay_periods (pay_period_id),

    -- One payslip per employee per pay period.
    UNIQUE (employee_id, pay_period_id),

    CHECK (
        gross_pay_cents >= 0
        AND fnpf_employee_cents >= 0
        AND paye_cents >= 0
        AND net_pay_cents >= 0
    ),

    -- Net pay must equal gross minus deductions.
    CHECK (net_pay_cents = gross_pay_cents - fnpf_employee_cents - paye_cents)
);

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'accountant', 'employee')),
    failed_attempts INTEGER NOT NULL DEFAULT 0 CHECK (failed_attempts >= 0),
    is_locked INTEGER NOT NULL DEFAULT 0 CHECK (is_locked IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    employee_id INTEGER UNIQUE,

    FOREIGN KEY (employee_id) REFERENCES employees (employee_id),

    -- An 'employee' account must be linked to a real employee.
    CHECK (role <> 'employee' OR employee_id IS NOT NULL)
);

CREATE TABLE audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    action TEXT NOT NULL,

    table_name TEXT,
    row_id INTEGER,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    details TEXT,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
);