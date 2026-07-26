"""Patient Repository providing clean async database/memory access abstraction."""

from datetime import date, datetime, timezone
from typing import List, Optional, Tuple
from uuid import uuid4

from src.app.schemas.patient import PatientCreate, PatientFilterParams, PatientRead, PatientUpdate, GenderEnum


class PatientRepository:
    """Repository interface for Patient entities with sample seed data."""

    def __init__(self):
        # In-memory seed database for robust API testing & unit test mockability
        self._patients: dict[str, dict] = {
            "pat_01": {
                "id": "pat_01",
                "first_name": "Eleanor",
                "last_name": "Vance",
                "phone_number": "+15550192834",
                "email": "eleanor.vance@example.com",
                "date_of_birth": date(1982, 4, 15),
                "gender": GenderEnum.FEMALE,
                "preferred_language": "en",
                "address": "742 Evergreen Terrace, Springfield",
                "is_active": True,
                "created_at": datetime(2026, 7, 20, 9, 30, 0, tzinfo=timezone.utc),
                "updated_at": datetime(2026, 7, 20, 9, 30, 0, tzinfo=timezone.utc),
            },
            "pat_02": {
                "id": "pat_02",
                "first_name": "Arthur",
                "last_name": "Pendelton",
                "phone_number": "+15550192900",
                "email": "arthur.p@example.com",
                "date_of_birth": date(1965, 11, 3),
                "gender": GenderEnum.MALE,
                "preferred_language": "en",
                "address": "128 Baker Street, Suite 4",
                "is_active": True,
                "created_at": datetime(2026, 7, 21, 11, 15, 0, tzinfo=timezone.utc),
                "updated_at": datetime(2026, 7, 21, 11, 15, 0, tzinfo=timezone.utc),
            },
            "pat_03": {
                "id": "pat_03",
                "first_name": "Maria",
                "last_name": "Gonzales",
                "phone_number": "+15550193388",
                "email": "maria.gonzales@example.com",
                "date_of_birth": date(1990, 8, 22),
                "gender": GenderEnum.FEMALE,
                "preferred_language": "es",
                "address": "450 Avenida Del Sol, San Jose",
                "is_active": True,
                "created_at": datetime(2026, 7, 22, 14, 0, 0, tzinfo=timezone.utc),
                "updated_at": datetime(2026, 7, 22, 14, 0, 0, tzinfo=timezone.utc),
            },
        }

    async def get_by_id(self, patient_id: str) -> Optional[PatientRead]:
        """Fetch a single patient by ID."""
        data = self._patients.get(patient_id)
        if not data:
            return None
        return PatientRead(**data)

    async def list_patients(
        self,
        filters: PatientFilterParams,
        offset: int = 0,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[PatientRead], int]:
        """List patients with pagination, filtering, and sorting."""
        results = list(self._patients.values())

        # Filtering
        if filters.search:
            search_term = filters.search.lower()
            results = [
                p
                for p in results
                if search_term in p["first_name"].lower()
                or search_term in p["last_name"].lower()
                or search_term in p["phone_number"].lower()
                or (p["email"] and search_term in p["email"].lower())
            ]

        if filters.is_active is not None:
            results = [p for p in results if p["is_active"] == filters.is_active]

        if filters.preferred_language:
            results = [
                p
                for p in results
                if p["preferred_language"].lower() == filters.preferred_language.lower()
            ]

        total_count = len(results)

        # Sorting
        reverse = sort_order.lower() == "desc"
        valid_sort_keys = {"created_at", "first_name", "last_name", "id", "updated_at"}
        sort_key = sort_by if sort_by in valid_sort_keys else "created_at"

        results.sort(key=lambda x: x.get(sort_key) or "", reverse=reverse)

        # Pagination
        paginated = results[offset : offset + limit]
        return [PatientRead(**item) for item in paginated], total_count

    async def create(self, payload: PatientCreate) -> PatientRead:
        """Create a new patient record."""
        now = datetime.now(timezone.utc)
        new_id = f"pat_{uuid4().hex[:8]}"
        patient_data = {
            "id": new_id,
            **payload.model_dump(),
            "created_at": now,
            "updated_at": now,
        }
        self._patients[new_id] = patient_data
        return PatientRead(**patient_data)

    async def update(self, patient_id: str, payload: PatientUpdate) -> Optional[PatientRead]:
        """Update an existing patient record."""
        if patient_id not in self._patients:
            return None

        current = self._patients[patient_id]
        update_data = payload.model_dump(exclude_unset=True)
        current.update(update_data)
        current["updated_at"] = datetime.now(timezone.utc)
        self._patients[patient_id] = current
        return PatientRead(**current)
