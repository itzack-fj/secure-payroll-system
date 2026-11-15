import hashlib
import hmac
import os
import sqlite3

from audit import log_action
from employees import connect

MAX_FAILED_ATTEMPTS = 5


def hash_password(password, salt):
    # scrypt is deliberately slow and memory-hungry, which makes guessing expensive.
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)


def register_user(username, password, role, employee_id=None):
    if len(password) < 12:
        raise ValueError("password must be at least 12 characters")

    salt = os.urandom(16)
    digest = hash_password(password, salt)

    conn = connect()
    try:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, salt, role, employee_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (username, digest.hex(), salt.hex(), role, employee_id),
        )
        # The role is safe to record. The username and password are not logged.
        log_action(conn, None, "user_registered", "users", cursor.lastrowid, f"role={role}")
        conn.commit()          # user + audit row saved together
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_login(username, password):
    # Returns (user_id, role) on success, or None. The caller never learns WHY it failed.
    # Every path below writes an audit row, committed together with any state change.
    # The attempted username is never logged: someone may have typed a password into that box.
    conn = connect()
    try:
        row = conn.execute(
            "SELECT user_id, password_hash, salt, role, is_locked "
            "FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        # PATH 1: unknown user
        if row is None:
            # Do the same slow work so timing doesn't reveal which usernames exist.
            hash_password(password, b"\x00" * 16)
            log_action(conn, None, "login_failed", "users", None, "reason=unknown_user")
            conn.commit()
            return None

        user_id, stored_hash, stored_salt, role, is_locked = row

        # PATH 2: locked account
        if is_locked:
            log_action(conn, user_id, "login_blocked", "users", user_id, "reason=account_locked")
            conn.commit()
            return None

        digest = hash_password(password, bytes.fromhex(stored_salt))

        # PATH 3: wrong password
        if not hmac.compare_digest(digest, bytes.fromhex(stored_hash)):
            conn.execute(
                "UPDATE users SET failed_attempts = failed_attempts + 1, "
                "is_locked = CASE WHEN failed_attempts + 1 >= ? THEN 1 ELSE is_locked END "
                "WHERE user_id = ?",
                (MAX_FAILED_ATTEMPTS, user_id),
            )
            attempts, locked = conn.execute(
                "SELECT failed_attempts, is_locked FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            log_action(
                conn, user_id, "login_failed", "users", user_id,
                f"failed_attempts={attempts}, locked={locked}",
            )
            conn.commit()      # counter update + audit row saved together
            return None

        # PATH 4: success
        conn.execute("UPDATE users SET failed_attempts = 0 WHERE user_id = ?", (user_id,))
        log_action(conn, user_id, "login_success", "users", user_id)
        conn.commit()          # reset + audit row saved together
        return (user_id, role)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Fake demo password only. Never put a real password in code.
    try:
        register_user("admin", "demo-password-123", "admin")
        print("registered")
    except sqlite3.IntegrityError as error:
        print("register rejected:", error)

    print(verify_login("admin", "demo-password-123"))   # predict first
    print(verify_login("admin", "wrong-password"))      # predict first
    print(verify_login("nobody", "whatever"))           # predict first