def fnpf_employee_cents(gross_cents):
    if gross_cents < 0:
        raise ValueError("gross pay cannot be negative")
    # Round down to avoid deducting a fraction of a cent.
    return (gross_cents * 8) // 100


if __name__ == "__main__":
    assert fnpf_employee_cents(200000) == 16000
    assert fnpf_employee_cents(0) == 0
    assert fnpf_employee_cents(12345) == 987   # 987.6 -> 987
    assert fnpf_employee_cents(99) == 7        # 7.92  -> 7

    try:
        fnpf_employee_cents(-1)
        assert False, "expected ValueError"
    except ValueError:
        pass

    print("All tests passed")