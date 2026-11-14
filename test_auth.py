from auth import verify_login

for attempt in range(5):
    print(attempt + 1, verify_login("admin", "wrong-password"))

# The correct password, after 5 failures.
print("correct password:", verify_login("admin", "demo-password-123"))