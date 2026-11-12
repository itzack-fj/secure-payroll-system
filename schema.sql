CREATE TABLE pay_periods (
    pay_period_id INTEGER PRIMARY KEY,
    frequency     TEXT NOT NULL CHECK (frequency IN ('weekly', 'fortnightly', 'monthly')),
    start_date    TEXT NOT NULL,
    end_date      TEXT NOT NULL,
    payment_date  TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'open'
                  CHECK (status IN ('open', 'processing', 'approved', 'paid', 'closed')),
    CHECK (date(start_date) IS start_date),
    CHECK (date(end_date) IS end_date),
    CHECK (date(payment_date) IS payment_date),
    CHECK (end_date >= start_date),
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