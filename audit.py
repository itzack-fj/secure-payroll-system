def log_action(conn, user_id, action, table_name=None, row_id=None, details=None):
    # Does NOT commit. The caller commits, so the audit row and the change
    # it describes are saved together or not at all.
    conn.execute(
        "INSERT INTO audit_log (user_id, action, table_name, row_id, details) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, action, table_name, row_id, details),
    )
    