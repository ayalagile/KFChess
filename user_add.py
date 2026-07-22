import sqlite3

# התחברות לקובץ מסד הנתונים (נתיב לקובץ ה-db שלך)
conn = sqlite3.connect("database.db")  # ודאי ששם הקובץ תואם לשם ה-db בפרויקט שלך
cursor = conn.cursor()

try:
    cursor.execute(
        "INSERT INTO users (username, password, rating) VALUES (?, ?, 1200)",
        ("player2", "mypassword123")
    )
    conn.commit()
    print("User 'player2' added successfully!")
except sqlite3.IntegrityError:
    print("User 'player2' already exists.")
finally:
    conn.close()