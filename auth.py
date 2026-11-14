import hashlib
import hmac
import os
import sqlite3

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
        conn.execute(
            "INSERT INTO users (username, password_hash, salt, role, employee_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (username, digest.hex(), salt.hex(), role, employee_id),
        )
        conn.commit()
    finally:
        conn.close()


def verify_login(username, password):
    # Returns (user_id, role) on success, or None. The caller never learns WHY it failed.
    conn = connect()
    try:
        row = conn.execute(
            "SELECT user_id, password_hash, salt, role, is_locked "
            "FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if row is None:
            # Do the same slow work for unknown users so timing doesn't reveal which usernames exist.
            hash_password(password, b"\x00" * 16)
            return None

        user_id, stored_hash, stored_salt, role, is_locked = row

        if is_locked:
            return None

        digest = hash_password(password, bytes.fromhex(stored_salt))

        if hmac.compare_digest(digest, bytes.fromhex(stored_hash)):
            conn.execute("UPDATE users SET failed_attempts = 0 WHERE user_id = ?", (user_id,))
            conn.commit()
            return (user_id, role)

        conn.execute(
            "UPDATE users SET failed_attempts = failed_attempts + 1, "
            "is_locked = CASE WHEN failed_attempts + 1 >= ? THEN 1 ELSE is_locked END "
            "WHERE user_id = ?",
            (MAX_FAILED_ATTEMPTS, user_id),
        )
        conn.commit()
        return None
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