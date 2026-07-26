"""Call Repository providing data access for voice agent call records."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import uuid4

from src.app.schemas.call import CallCreate, CallFilterParams, CallRead, CallStatusEnum, CallTypeEnum, CallUpdate


class CallRepository:
    """Repository interface for Call log records."""

    def __init__(self):
        # In-memory sample data for testing and mock execution
        self._calls: dict[str, dict] = {
            "call_101": {
                "id": "call_101",
                "patient_id": "pat_01",
                "call_type": CallTypeEnum.INBOUND,
                "status": CallStatusEnum.COMPLETED,
                "vapi_call_id": "vapi_call_882310",
                "duration_seconds": 145,
                "summary": "Patient confirmed cardiology follow-up appointment for tomorrow at 10 AM.",
                "transcript": "Agent: Hello Eleanor, calling from City Health. Patient: Hi, I wanted to confirm my 10 AM appointment.",
                "recording_url": "https://api.vapi.ai/recordings/call_882310.mp3",
                "cost": 0.12,
                "metadata": {"department": "Cardiology", "intent": "Appointment Confirmation"},
                "started_at": datetime(2026, 7, 26, 14, 0, 0, tzinfo=timezone.utc),
                "ended_at": datetime(2026, 7, 26, 14, 2, 25, tzinfo=timezone.utc),
                "created_at": datetime(2026, 7, 26, 14, 0, 0, tzinfo=timezone.utc),
            },
            "call_102": {
                "id": "call_102",
                "patient_id": "pat_02",
                "call_type": CallTypeEnum.OUTBOUND,
                "status": CallStatusEnum.COMPLETED,
                "vapi_call_id": "vapi_call_882311",
                "duration_seconds": 92,
                "summary": "Prescription renewal reminder delivered successfully.",
                "transcript": "Agent: Hello Arthur, reminding you about your Lisinopril refill. Patient: Thank you, I will pick it up today.",
                "recording_url": "https://api.vapi.ai/recordings/call_882311.mp3",
                "cost": 0.08,
                "metadata": {"department": "Pharmacy", "intent": "Refill Reminder"},
                "started_at": datetime(2026, 7, 26, 14, 30, 0, tzinfo=timezone.utc),
                "ended_at": datetime(2026, 7, 26, 14, 31, 32, tzinfo=timezone.utc),
                "created_at": datetime(2026, 7, 26, 14, 30, 0, tzinfo=timezone.utc),
            },
            "call_103": {
                "id": "call_103",
                "patient_id": "pat_03",
                "call_type": CallTypeEnum.INBOUND,
                "status": CallStatusEnum.NO_ANSWER,
                "vapi_call_id": "vapi_call_882312",
                "duration_seconds": 0,
                "summary": "No answer from patient. Voicemail message left.",
                "transcript": "Agent: Hello Maria, please call back City Health Clinic.",
                "recording_url": None,
                "cost": 0.02,
                "metadata": {"department": "General", "intent": "Follow-up"},
                "started_at": datetime(2026, 7, 26, 15, 0, 0, tzinfo=timezone.utc),
                "ended_at": datetime(2026, 7, 26, 15, 0, 20, tzinfo=timezone.utc),
                "created_at": datetime(2026, 7, 26, 15, 0, 0, tzinfo=timezone.utc),
            },
        }

    async def get_by_id(self, call_id: str) -> Optional[CallRead]:
        """Get call details by call ID."""
        data = self._calls.get(call_id)
        if not data:
            return None
        return CallRead(**data)

    async def list_calls(
        self,
        filters: CallFilterParams,
        offset: int = 0,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[CallRead], int]:
        """List calls with filtering, sorting, and pagination."""
        results = list(self._calls.values())

        # Filtering
        if filters.patient_id:
            results = [c for c in results if c["patient_id"] == filters.patient_id]

        if filters.status:
            results = [c for c in results if c["status"] == filters.status]

        if filters.call_type:
            results = [c for c in results if c["call_type"] == filters.call_type]

        if filters.min_duration is not None:
            results = [c for c in results if c["duration_seconds"] >= filters.min_duration]

        total_count = len(results)

        # Sorting
        reverse = sort_order.lower() == "desc"
        valid_sort_keys = {"created_at", "started_at", "duration_seconds", "cost", "id"}
        sort_key = sort_by if sort_by in valid_sort_keys else "created_at"

        results.sort(key=lambda x: x.get(sort_key) or "", reverse=reverse)

        # Pagination
        paginated = results[offset : offset + limit]
        return [CallRead(**item) for item in paginated], total_count

    async def create(self, payload: CallCreate) -> CallRead:
        """Create a new call log entry."""
        now = datetime.now(timezone.utc)
        new_id = f"call_{uuid4().hex[:8]}"
        call_data = {
            "id": new_id,
            **payload.model_dump(),
            "started_at": now,
            "ended_at": None,
            "created_at": now,
        }
        self._calls[new_id] = call_data
        return CallRead(**call_data)

    async def update(self, call_id: str, payload: CallUpdate) -> Optional[CallRead]:
        """Update call log status or metadata."""
        if call_id not in self._calls:
            return None

        current = self._calls[call_id]
        update_data = payload.model_dump(exclude_unset=True)
        current.update(update_data)
        self._calls[call_id] = current
        return CallRead(**current)
