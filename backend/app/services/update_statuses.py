from sqlalchemy import text
from app.database import SessionLocal

db = SessionLocal()
# Update in correct order to avoid unique constraint conflicts
db.execute(text("UPDATE ticket_statuses SET label = 'En v\u00e9rification', name = 'under_review' WHERE id = 4"))
db.execute(text("UPDATE ticket_statuses SET label = 'En attente', name = 'pending' WHERE id = 3"))
db.execute(text("UPDATE ticket_statuses SET label = 'En cours', name = 'in_progress' WHERE id = 2"))
db.execute(text("UPDATE ticket_statuses SET sort_order = 5 WHERE id = 5"))
db.commit()
rows = db.execute(text("SELECT id, label, name, sort_order FROM ticket_statuses ORDER BY id")).fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]} ({r[2]}) order={r[3]}")
db.close()
print("Statuses updated OK")
