import json
from groq import Groq
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.models.ticket import Ticket
from app.models.problem_category import ProblemCategory
from app.models.problem_subcategory import ProblemSubcategory

GROQ_API_KEY = getattr(settings, "GROQ_API_KEY", "")


def _get_groq_client() -> Groq | None:
    if not GROQ_API_KEY:
        return None
    return Groq(api_key=GROQ_API_KEY)


def _build_technician_context(db: Session) -> list[dict]:
    techs = db.query(User).filter(User.role_id == 2, User.is_active == True).all()
    result = []
    for t in techs:
        open_count = db.query(Ticket).filter(
            Ticket.assigned_to == t.id,
            Ticket.status_id.in_([2, 3, 4]),
        ).count()
        result.append({
            "id": t.id,
            "name": f"{t.first_name} {t.last_name}".strip(),
            "open_tickets": open_count,
        })
    return result


def ai_assign_technician(db: Session, category_id: int, subcategory_id: int, description: str, priority: str) -> int | None:
    client = _get_groq_client()
    if not client:
        return None

    techs = _build_technician_context(db)
    if not techs:
        return None

    cat = db.query(ProblemCategory).filter(ProblemCategory.id == category_id).first()
    sub = db.query(ProblemSubcategory).filter(ProblemSubcategory.id == subcategory_id).first()
    cat_name = cat.name if cat else "Inconnue"
    sub_name = sub.name if sub else "Inconnue"

    prompt = f"""Tu es un assistant d'assignation de tickets pour un centre informatique universitaire.

Ticket à assigner :
- Catégorie : {cat_name}
- Sous-catégorie : {sub_name}
- Description : {description[:300]}
- Priorité : {priority}

Techniciens disponibles (avec leur charge actuelle de tickets ouverts) :
{json.dumps(techs, indent=2, ensure_ascii=False)}

Choisis le technicien le plus adapté en fonction de :
1. L'équilibrage de charge (priorité au moins chargé)
2. La pertinence par rapport à la catégorie du ticket

Réponds UNIQUEMENT par un JSON valide : {{"technician_id": <id>}}
Ne mets aucun autre texte."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100,
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        tech_id = result.get("technician_id")
        if tech_id and any(t["id"] == tech_id for t in techs):
            return tech_id
    except Exception:
        pass

    return None
