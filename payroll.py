def fnpf_employee_cents(gross_cents):
    if gross_cents < 0:
        raise ValueError("gross pay cannot be negative")
    # Round down to avoid deducting a fraction of a cent.
    return (gross_cents * 8) // 100


def format_fjd(cents):
    if cents < 0:
        raise ValueError("amount cannot be negative")
    dollars = cents // 100
    leftover_cents = cents % 100
    return f"FJD {dollars:,}.{leftover_cents:02d}"


if __name__ == "__main__":
    # FNPF tests
    assert fnpf_employee_cents(200000) == 16000
    assert fnpf_employee_cents(0) == 0
    assert fnpf_employee_cents(12345) == 987   # 987.6 -> 987
    assert fnpf_employee_cents(99) == 7        # 7.92  -> 7

    try:
        fnpf_employee_cents(-1)
        assert False, "expected ValueError"
    except ValueError:
        pass

    # Formatting tests
    assert format_fjd(200000) == "FJD 2,000.00"
    assert format_fjd(5) == "FJD 0.05"
    assert format_fjd(0) == "FJD 0.00"
    assert format_fjd(123456) == "FJD 1,234.56"

    try:
        format_fjd(-5)
        assert False, "expected ValueError"
    except ValueError:
        pass

    print("All tests passed")
    