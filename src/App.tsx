import React, { useState } from 'react';
import {
  Phone,
  Server,
  Database,
  Shield,
  Activity,
  GitBranch,
  FolderTree,
  Box,
  Key,
  FileText,
  AlertTriangle,
  Lock,
  Globe,
  Radio,
  CheckCircle2,
  Copy,
  Check,
  ChevronRight,
  Layers,
  Cpu,
  Code,
  Terminal,
  Play,
  Filter,
  Search,
  Zap,
  Tag
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState<'tester' | 'code' | 'tree' | 'settings'>('tester');
  const [copied, setCopied] = useState(false);
  const [selectedSkeletonFile, setSelectedSkeletonFile] = useState<string>('src/app/api/v1/endpoints/patients.py');
  const [codeCopied, setCodeCopied] = useState(false);

  // REST API Tester State
  const [selectedEndpoint, setSelectedEndpoint] = useState<'root' | 'health' | 'patients_list' | 'patient_detail' | 'calls_list' | 'call_detail'>('patients_list');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [searchFilter, setSearchFilter] = useState<string>('');
  const [patientIdFilter, setPatientIdFilter] = useState<string>('pat_01');
  const [callIdFilter, setCallIdFilter] = useState<string>('call_101');
  const [callStatusFilter, setCallStatusFilter] = useState<string>('all');

  const handleCopyEnv = () => {
    const envText = `APP_NAME="Healthcare Voice Agent"
APP_ENV="development"
DEBUG=true
API_V1_STR="/api/v1"
HOST="0.0.0.0"
WORKERS=2
ALLOWED_ORIGINS="http://localhost:3000,https://internexus.tech,https://api.internexus.tech"
POSTGRES_SERVER="postgres"
POSTGRES_PORT=5432
POSTGRES_USER="voiceagent"
POSTGRES_PASSWORD="ChooseAStrongPassword123!"
POSTGRES_DB="voiceagentdb"
DATABASE_URL="postgresql://voiceagent:ChooseAStrongPassword123!@postgres:5432/voiceagentdb"
VAPI_API_KEY="5d47d14d-8512-4d3e-85c8-24e9290dc9aa"`;
    navigator.clipboard.writeText(envText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const skeletonCodeFiles: Record<string, { title: string; language: string; content: string }> = {
    'src/app/main.py': {
      title: 'main.py (FastAPI Root Application & OpenAPI Setup)',
      language: 'python',
      content: `"""Healthcare Voice Agent FastAPI Main Application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, status
import uvicorn

from src.app.core.config import settings
from src.app.core.database import init_db, close_db
from src.app.core.logging import setup_logging, logger
from src.app.core.middleware import setup_cors, setup_exception_handlers, RequestTraceMiddleware
from src.app.api.v1.router import api_v1_router
from src.app.api.v1.endpoints import health, patients, calls


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context managing startup and shutdown tasks."""
    setup_logging()
    logger.info("Starting Healthcare Voice Agent FastAPI backend...", env=settings.APP_ENV)
    await init_db()
    yield
    await close_db()


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="Production-Ready Healthcare Voice Agent REST API Backend",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {"name": "Root & Health", "description": "Core application root and health check endpoints"},
            {"name": "Patients", "description": "Patient record management, search, and filtering"},
            {"name": "Calls", "description": "Voice call logs, transcripts, and session analytics"},
        ],
        lifespan=lifespan,
    )

    setup_cors(app)
    app.add_middleware(RequestTraceMiddleware)
    setup_exception_handlers(app)

    @app.get("/", status_code=status.HTTP_200_OK, tags=["Root & Health"])
    async def root() -> dict[str, str]:
        return {
            "app_name": settings.APP_NAME,
            "status": "running",
            "environment": settings.APP_ENV,
            "version": "0.1.0",
            "docs_url": "/docs",
            "api_v1": settings.API_V1_STR,
        }

    app.include_router(health.router, tags=["Root & Health"])
    app.include_router(patients.router)
    app.include_router(calls.router)
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return app

app = create_application()`
    },
    'src/app/api/v1/endpoints/patients.py': {
      title: 'patients.py (GET /patients & GET /patients/{id} Endpoints)',
      language: 'python',
      content: `"""Patient REST API Endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from src.app.api.deps import get_patient_service
from src.app.schemas.common import ErrorResponse, PaginatedResponse, PaginationParams
from src.app.schemas.patient import PatientFilterParams, PatientRead
from src.app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get(
    "",
    response_model=PaginatedResponse[PatientRead],
    status_code=status.HTTP_200_OK,
    summary="List patients",
    description="Retrieve a paginated list of patients with search, filtering, and sorting support.",
    responses={
        200: {"description": "Paginated list of patients returned successfully"},
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
    },
)
async def list_patients(
    page: int = Query(1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc|ASC|DESC)$", description="Sort order"),
    search: Optional[str] = Query(None, description="Search keyword in name, phone, or email"),
    is_active: Optional[bool] = Query(None, description="Filter active or inactive status"),
    preferred_language: Optional[str] = Query(None, description="Filter by language code"),
    service: PatientService = Depends(get_patient_service),
) -> PaginatedResponse[PatientRead]:
    pagination = PaginationParams(page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order)
    filters = PatientFilterParams(search=search, is_active=is_active, preferred_language=preferred_language)
    return await service.get_patients_paginated(pagination=pagination, filters=filters)


@router.get(
    "/{id}",
    response_model=PatientRead,
    status_code=status.HTTP_200_OK,
    summary="Get patient details",
    description="Fetch a single patient by unique ID.",
    responses={
        200: {"description": "Patient record found and returned"},
        404: {"model": ErrorResponse, "description": "Patient not found"},
    },
)
async def get_patient(
    id: str,
    service: PatientService = Depends(get_patient_service),
) -> PatientRead:
    return await service.get_patient_by_id(id)`
    },
    'src/app/api/v1/endpoints/calls.py': {
      title: 'calls.py (GET /calls & GET /calls/{id} Endpoints)',
      language: 'python',
      content: `"""Call Logs REST API Endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from src.app.api.deps import get_call_service
from src.app.schemas.call import CallFilterParams, CallRead, CallStatusEnum, CallTypeEnum
from src.app.schemas.common import ErrorResponse, PaginatedResponse, PaginationParams
from src.app.services.call_service import CallService

router = APIRouter(prefix="/calls", tags=["Calls"])


@router.get(
    "",
    response_model=PaginatedResponse[CallRead],
    status_code=status.HTTP_200_OK,
    summary="List call logs",
    description="Retrieve a paginated list of call logs with filtering by patient, status, and call type.",
    responses={
        200: {"description": "Paginated call logs returned successfully"},
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
    },
)
async def list_calls(
    page: int = Query(1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc|ASC|DESC)$", description="Sort order"),
    patient_id: Optional[str] = Query(None, description="Filter calls by patient ID"),
    status_filter: Optional[CallStatusEnum] = Query(None, alias="status", description="Filter by call status"),
    call_type: Optional[CallTypeEnum] = Query(None, description="Filter by call type"),
    min_duration: Optional[int] = Query(None, ge=0, description="Minimum call duration in seconds"),
    service: CallService = Depends(get_call_service),
) -> PaginatedResponse[CallRead]:
    pagination = PaginationParams(page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order)
    filters = CallFilterParams(patient_id=patient_id, status=status_filter, call_type=call_type, min_duration=min_duration)
    return await service.get_calls_paginated(pagination=pagination, filters=filters)


@router.get(
    "/{id}",
    response_model=CallRead,
    status_code=status.HTTP_200_OK,
    summary="Get call log details",
    description="Fetch a specific call log record by unique ID.",
    responses={
        200: {"description": "Call log record found and returned"},
        404: {"model": ErrorResponse, "description": "Call record not found"},
    },
)
async def get_call(
    id: str,
    service: CallService = Depends(get_call_service),
) -> CallRead:
    return await service.get_call_by_id(id)`
    },
    'src/app/schemas/patient.py': {
      title: 'schemas/patient.py (Pydantic v2 Patient Schemas)',
      language: 'python',
      content: `"""Patient Schemas for Validation and Response Serialization."""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=7, max_length=20)
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    gender: GenderEnum = Field(default=GenderEnum.UNKNOWN)
    preferred_language: str = Field(default="en")
    address: Optional[str] = None
    is_active: bool = Field(default=True)


class PatientRead(PatientBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True`
    },
    'src/app/schemas/call.py': {
      title: 'schemas/call.py (Pydantic v2 Call Session Schemas)',
      language: 'python',
      content: `"""Call Log Schemas for Validation and API Responses."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class CallTypeEnum(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallStatusEnum(str, Enum):
    QUEUED = "queued"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no_answer"


class CallRead(BaseModel):
    id: str
    patient_id: str
    call_type: CallTypeEnum
    status: CallStatusEnum
    vapi_call_id: Optional[str] = None
    duration_seconds: int = 0
    summary: Optional[str] = None
    transcript: Optional[str] = None
    recording_url: Optional[str] = None
    cost: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True`
    },
    'src/app/services/patient_service.py': {
      title: 'services/patient_service.py (Patient Service Layer)',
      language: 'python',
      content: `"""Patient Business Logic Service."""

from fastapi import HTTPException, status
from src.app.core.logging import logger
from src.app.repositories.patient_repository import PatientRepository
from src.app.schemas.common import PaginatedMeta, PaginatedResponse, PaginationParams
from src.app.schemas.patient import PatientFilterParams, PatientRead


class PatientService:
    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo

    async def get_patient_by_id(self, patient_id: str) -> PatientRead:
        logger.info("Fetching patient details", patient_id=patient_id)
        patient = await self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PATIENT_NOT_FOUND", "message": f"Patient '{patient_id}' not found."},
            )
        return patient

    async def get_patients_paginated(
        self,
        pagination: PaginationParams,
        filters: PatientFilterParams,
    ) -> PaginatedResponse[PatientRead]:
        items, total_count = await self.patient_repo.list_patients(
            filters=filters,
            offset=pagination.offset,
            limit=pagination.page_size,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order,
        )
        total_pages = max(1, (total_count + pagination.page_size - 1) // pagination.page_size)
        meta = PaginatedMeta(
            page=pagination.page,
            page_size=pagination.page_size,
            total_items=total_count,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1,
        )
        return PaginatedResponse[PatientRead](items=items, meta=meta)`
    }
  };

  const getMockApiResponse = () => {
    if (selectedEndpoint === 'root') {
      return {
        status_code: 200,
        headers: { 'content-type': 'application/json', 'x-request-id': 'req_root_99812' },
        body: {
          app_name: "Healthcare Voice Agent",
          status: "running",
          environment: "development",
          version: "0.1.0",
          docs_url: "/docs",
          api_v1: "/api/v1"
        }
      };
    }
    if (selectedEndpoint === 'health') {
      return {
        status_code: 200,
        headers: { 'content-type': 'application/json', 'x-request-id': 'req_health_10293' },
        body: {
          status: "ok",
          environment: "development",
          version: "0.1.0",
          database: "healthy"
        }
      };
    }
    if (selectedEndpoint === 'patient_detail') {
      if (patientIdFilter === 'pat_01') {
        return {
          status_code: 200,
          headers: { 'content-type': 'application/json', 'x-request-id': 'req_pat_01' },
          body: {
            id: "pat_01",
            first_name: "Eleanor",
            last_name: "Vance",
            phone_number: "+15550192834",
            email: "eleanor.vance@example.com",
            date_of_birth: "1982-04-15",
            gender: "female",
            preferred_language: "en",
            address: "742 Evergreen Terrace, Springfield",
            is_active: true,
            created_at: "2026-07-20T09:30:00Z",
            updated_at: "2026-07-20T09:30:00Z"
          }
        };
      }
      return {
        status_code: 404,
        headers: { 'content-type': 'application/json', 'x-request-id': 'req_pat_err' },
        body: {
          success: false,
          error: {
            code: "PATIENT_NOT_FOUND",
            message: `Patient with ID '${patientIdFilter}' was not found.`,
            field: "id"
          }
        }
      };
    }
    if (selectedEndpoint === 'patients_list') {
      let patients = [
        {
          id: "pat_01",
          first_name: "Eleanor",
          last_name: "Vance",
          phone_number: "+15550192834",
          email: "eleanor.vance@example.com",
          date_of_birth: "1982-04-15",
          gender: "female",
          preferred_language: "en",
          address: "742 Evergreen Terrace, Springfield",
          is_active: true,
          created_at: "2026-07-20T09:30:00Z",
          updated_at: "2026-07-20T09:30:00Z"
        },
        {
          id: "pat_02",
          first_name: "Arthur",
          last_name: "Pendelton",
          phone_number: "+15550192900",
          email: "arthur.p@example.com",
          date_of_birth: "1965-11-03",
          gender: "male",
          preferred_language: "en",
          address: "128 Baker Street, Suite 4",
          is_active: true,
          created_at: "2026-07-21T11:15:00Z",
          updated_at: "2026-07-21T11:15:00Z"
        },
        {
          id: "pat_03",
          first_name: "Maria",
          last_name: "Gonzales",
          phone_number: "+15550193388",
          email: "maria.gonzales@example.com",
          date_of_birth: "1990-08-22",
          gender: "female",
          preferred_language: "es",
          address: "450 Avenida Del Sol, San Jose",
          is_active: true,
          created_at: "2026-07-22T14:00:00Z",
          updated_at: "2026-07-22T14:00:00Z"
        }
      ];

      if (searchFilter) {
        patients = patients.filter(p =>
          p.first_name.toLowerCase().includes(searchFilter.toLowerCase()) ||
          p.last_name.toLowerCase().includes(searchFilter.toLowerCase()) ||
          p.phone_number.includes(searchFilter)
        );
      }

      return {
        status_code: 200,
        headers: { 'content-type': 'application/json', 'x-request-id': 'req_pat_list' },
        body: {
          items: patients,
          meta: {
            page: page,
            page_size: pageSize,
            total_items: patients.length,
            total_pages: 1,
            has_next: false,
            has_prev: false
          }
        }
      };
    }
    if (selectedEndpoint === 'call_detail') {
      if (callIdFilter === 'call_101') {
        return {
          status_code: 200,
          headers: { 'content-type': 'application/json', 'x-request-id': 'req_call_101' },
          body: {
            id: "call_101",
            patient_id: "pat_01",
            call_type: "inbound",
            status: "completed",
            vapi_call_id: "vapi_call_882310",
            duration_seconds: 145,
            summary: "Patient confirmed cardiology follow-up appointment for tomorrow at 10 AM.",
            transcript: "Agent: Hello Eleanor, calling from City Health. Patient: Hi, I wanted to confirm my appointment.",
            recording_url: "https://api.vapi.ai/recordings/call_882310.mp3",
            cost: 0.12,
            metadata: { department: "Cardiology", intent: "Appointment Confirmation" },
            started_at: "2026-07-26T14:00:00Z",
            ended_at: "2026-07-26T14:02:25Z",
            created_at: "2026-07-26T14:00:00Z"
          }
        };
      }
      return {
        status_code: 404,
        headers: { 'content-type': 'application/json', 'x-request-id': 'req_call_err' },
        body: {
          success: false,
          error: {
            code: "CALL_NOT_FOUND",
            message: `Call record with ID '${callIdFilter}' was not found.`,
            field: "id"
          }
        }
      };
    }
    // calls list
    let calls = [
      {
        id: "call_101",
        patient_id: "pat_01",
        call_type: "inbound",
        status: "completed",
        vapi_call_id: "vapi_call_882310",
        duration_seconds: 145,
        summary: "Patient confirmed cardiology follow-up appointment for tomorrow at 10 AM.",
        transcript: "Agent: Hello Eleanor, calling from City Health. Patient: Hi, I wanted to confirm my appointment.",
        recording_url: "https://api.vapi.ai/recordings/call_882310.mp3",
        cost: 0.12,
        metadata: { department: "Cardiology", intent: "Appointment Confirmation" },
        started_at: "2026-07-26T14:00:00Z",
        ended_at: "2026-07-26T14:02:25Z",
        created_at: "2026-07-26T14:00:00Z"
      },
      {
        id: "call_102",
        patient_id: "pat_02",
        call_type: "outbound",
        status: "completed",
        vapi_call_id: "vapi_call_882311",
        duration_seconds: 92,
        summary: "Prescription renewal reminder delivered successfully.",
        transcript: "Agent: Hello Arthur, reminding you about your Lisinopril refill. Patient: Thank you.",
        recording_url: "https://api.vapi.ai/recordings/call_882311.mp3",
        cost: 0.08,
        metadata: { department: "Pharmacy", intent: "Refill Reminder" },
        started_at: "2026-07-26T14:30:00Z",
        ended_at: "2026-07-26T14:31:32Z",
        created_at: "2026-07-26T14:30:00Z"
      }
    ];

    if (callStatusFilter !== 'all') {
      calls = calls.filter(c => c.status === callStatusFilter);
    }

    return {
      status_code: 200,
      headers: { 'content-type': 'application/json', 'x-request-id': 'req_calls_list' },
      body: {
        items: calls,
        meta: {
          page: page,
          page_size: pageSize,
          total_items: calls.length,
          total_pages: 1,
          has_next: false,
          has_prev: false
        }
      }
    };
  };

  const responseData = getMockApiResponse();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col">
      {/* Top Header Navigation */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400">
            <Phone className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-wide text-white">Healthcare Voice Agent</h1>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                REST API Ready
              </span>
            </div>
            <p className="text-xs text-slate-400">Production-Ready FastAPI + Pydantic v2 Backend Specifications</p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('tester')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'tester'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Play className="w-3.5 h-3.5" /> REST API Tester
          </button>
          <button
            onClick={() => setActiveTab('code')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'code'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Code className="w-3.5 h-3.5" /> API Source Files
          </button>
          <button
            onClick={() => setActiveTab('tree')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'tree'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <FolderTree className="w-3.5 h-3.5" /> Project Structure
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeTab === 'settings'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Key className="w-3.5 h-3.5" /> Environment & Config
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 flex flex-col gap-6">
        {/* TAB 1: REST API TESTER */}
        {activeTab === 'tester' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Endpoint selector & controls */}
            <div className="lg:col-span-5 flex flex-col gap-4">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                <div className="flex items-center gap-2 mb-4 text-emerald-400 font-semibold text-sm">
                  <Globe className="w-4 h-4" />
                  <span>Select Endpoint to Test</span>
                </div>

                <div className="space-y-2">
                  <button
                    onClick={() => setSelectedEndpoint('root')}
                    className={`w-full text-left p-3 rounded-xl border text-xs font-mono transition-all flex items-center justify-between ${
                      selectedEndpoint === 'root'
                        ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-300'
                        : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px] font-bold">GET</span>
                      <span>/</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Root Metadata</span>
                  </button>

                  <button
                    onClick={() => setSelectedEndpoint('health')}
                    className={`w-full text-left p-3 rounded-xl border text-xs font-mono transition-all flex items-center justify-between ${
                      selectedEndpoint === 'health'
                        ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-300'
                        : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px] font-bold">GET</span>
                      <span>/health</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Health Probe</span>
                  </button>

                  <button
                    onClick={() => setSelectedEndpoint('patients_list')}
                    className={`w-full text-left p-3 rounded-xl border text-xs font-mono transition-all flex items-center justify-between ${
                      selectedEndpoint === 'patients_list'
                        ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-300'
                        : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px] font-bold">GET</span>
                      <span>/patients</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Paginated Patients</span>
                  </button>

                  <button
                    onClick={() => setSelectedEndpoint('patient_detail')}
                    className={`w-full text-left p-3 rounded-xl border text-xs font-mono transition-all flex items-center justify-between ${
                      selectedEndpoint === 'patient_detail'
                        ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-300'
                        : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px] font-bold">GET</span>
                      <span>/patients/{`{id}`}</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Patient Detail</span>
                  </button>

                  <button
                    onClick={() => setSelectedEndpoint('calls_list')}
                    className={`w-full text-left p-3 rounded-xl border text-xs font-mono transition-all flex items-center justify-between ${
                      selectedEndpoint === 'calls_list'
                        ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-300'
                        : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px] font-bold">GET</span>
                      <span>/calls</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Paginated Call Logs</span>
                  </button>

                  <button
                    onClick={() => setSelectedEndpoint('call_detail')}
                    className={`w-full text-left p-3 rounded-xl border text-xs font-mono transition-all flex items-center justify-between ${
                      selectedEndpoint === 'call_detail'
                        ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-300'
                        : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px] font-bold">GET</span>
                      <span>/calls/{`{id}`}</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Call Detail</span>
                  </button>
                </div>
              </div>

              {/* Dynamic Query Controls */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col gap-3">
                <div className="flex items-center gap-2 text-slate-300 font-semibold text-xs">
                  <Filter className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Request Parameters</span>
                </div>

                {selectedEndpoint === 'patients_list' && (
                  <div className="space-y-3 text-xs">
                    <div>
                      <label className="text-slate-400 block mb-1">Search Query (Name/Phone)</label>
                      <input
                        type="text"
                        value={searchFilter}
                        onChange={(e) => setSearchFilter(e.target.value)}
                        placeholder="e.g. Eleanor or 555"
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="text-slate-400 block mb-1">Page</label>
                        <input
                          type="number"
                          value={page}
                          onChange={(e) => setPage(Number(e.target.value))}
                          min={1}
                          className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200"
                        />
                      </div>
                      <div>
                        <label className="text-slate-400 block mb-1">Page Size</label>
                        <input
                          type="number"
                          value={pageSize}
                          onChange={(e) => setPageSize(Number(e.target.value))}
                          min={1}
                          max={100}
                          className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {selectedEndpoint === 'patient_detail' && (
                  <div className="text-xs">
                    <label className="text-slate-400 block mb-1">Patient ID (Try 'pat_01' or 'pat_999')</label>
                    <input
                      type="text"
                      value={patientIdFilter}
                      onChange={(e) => setPatientIdFilter(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500 font-mono"
                    />
                  </div>
                )}

                {selectedEndpoint === 'calls_list' && (
                  <div className="space-y-3 text-xs">
                    <div>
                      <label className="text-slate-400 block mb-1">Status Filter</label>
                      <select
                        value={callStatusFilter}
                        onChange={(e) => setCallStatusFilter(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                      >
                        <option value="all">All Statuses</option>
                        <option value="completed">Completed</option>
                        <option value="no_answer">No Answer</option>
                        <option value="failed">Failed</option>
                      </select>
                    </div>
                  </div>
                )}

                {selectedEndpoint === 'call_detail' && (
                  <div className="text-xs">
                    <label className="text-slate-400 block mb-1">Call ID (Try 'call_101' or 'invalid_id')</label>
                    <input
                      type="text"
                      value={callIdFilter}
                      onChange={(e) => setCallIdFilter(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500 font-mono"
                    />
                  </div>
                )}

                {(selectedEndpoint === 'root' || selectedEndpoint === 'health') && (
                  <div className="text-xs text-slate-500 italic">No query parameters required for this endpoint.</div>
                )}
              </div>
            </div>

            {/* Right Column: Live Response & OpenAPI spec view */}
            <div className="lg:col-span-7 flex flex-col gap-4">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex-1 flex flex-col">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 bg-emerald-500/20 text-emerald-400 font-mono font-bold text-xs rounded-md">GET</span>
                    <span className="font-mono text-xs text-slate-200">
                      {selectedEndpoint === 'root' && '/'}
                      {selectedEndpoint === 'health' && '/health'}
                      {selectedEndpoint === 'patients_list' && `/patients?page=${page}&page_size=${pageSize}${searchFilter ? `&search=${searchFilter}` : ''}`}
                      {selectedEndpoint === 'patient_detail' && `/patients/${patientIdFilter}`}
                      {selectedEndpoint === 'calls_list' && `/calls?page=${page}&page_size=${pageSize}${callStatusFilter !== 'all' ? `&status=${callStatusFilter}` : ''}`}
                      {selectedEndpoint === 'call_detail' && `/calls/${callIdFilter}`}
                    </span>
                  </div>
                  <span className={`px-2 py-0.5 text-xs font-mono font-semibold rounded ${
                    responseData.status_code === 200
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  }`}>
                    {responseData.status_code} {responseData.status_code === 200 ? 'OK' : 'NOT FOUND'}
                  </span>
                </div>

                <div className="flex-1 bg-slate-950 rounded-xl border border-slate-800 p-4 font-mono text-xs overflow-x-auto text-emerald-400 leading-relaxed">
                  <pre>{JSON.stringify(responseData.body, null, 2)}</pre>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: CODE FILES */}
        {activeTab === 'code' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-4 bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-col gap-2">
              <div className="text-xs font-semibold text-slate-400 mb-2 px-2">Implemented Files</div>
              {Object.keys(skeletonCodeFiles).map((path) => (
                <button
                  key={path}
                  onClick={() => setSelectedSkeletonFile(path)}
                  className={`text-left p-2.5 rounded-xl text-xs font-mono transition-all flex items-center justify-between ${
                    selectedSkeletonFile === path
                      ? 'bg-emerald-600/20 border border-emerald-500/50 text-emerald-300'
                      : 'bg-slate-950/40 border border-slate-800/80 text-slate-400 hover:text-white'
                  }`}
                >
                  <span className="truncate">{path}</span>
                  <ChevronRight className="w-3.5 h-3.5 flex-shrink-0" />
                </button>
              ))}
            </div>

            <div className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                <span className="text-xs font-bold text-slate-200">
                  {skeletonCodeFiles[selectedSkeletonFile]?.title}
                </span>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(skeletonCodeFiles[selectedSkeletonFile]?.content || '');
                    setCodeCopied(true);
                    setTimeout(() => setCodeCopied(false), 2000);
                  }}
                  className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg text-[11px] text-slate-300 flex items-center gap-1"
                >
                  {codeCopied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  <span>{codeCopied ? 'Copied' : 'Copy File'}</span>
                </button>
              </div>
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs overflow-x-auto text-slate-300 leading-relaxed max-h-[600px]">
                <pre>{skeletonCodeFiles[selectedSkeletonFile]?.content}</pre>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: PROJECT STRUCTURE */}
        {activeTab === 'tree' && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <FolderTree className="w-4 h-4 text-emerald-400" />
              <span>Modular FastAPI Project Directory</span>
            </h2>
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 font-mono text-xs text-slate-300 overflow-x-auto leading-relaxed">
              <pre>{`healthcare-voice-agent/
├── .env.example                    # Clean env configuration template
├── pyproject.toml                  # Python package specification
├── requirements.txt                # Production FastAPI/Pydantic/SQLAlchemy dependencies
├── README.md                       # Comprehensive API & setup guide
└── src/
    └── app/
        ├── api/
        │   ├── v1/
        │   │   ├── endpoints/
        │   │   │   ├── health.py   # Health check & readiness probes
        │   │   │   ├── patients.py # GET /patients, GET /patients/{id}
        │   │   │   └── calls.py    # GET /calls, GET /calls/{id}
        │   │   └── router.py       # API v1 Router aggregation
        │   └── deps.py             # Service & Repository dependency injection
        ├── core/
        │   ├── config.py           # Config settings re-export
        │   ├── database.py         # Async SQLAlchemy engine & session pool
        │   ├── logging.py          # Structlog JSON logging setup
        │   ├── middleware.py       # Request Trace ID & CORS middleware
        │   └── settings.py         # Pydantic v2 BaseSettings
        ├── repositories/
        │   ├── patient_repository.py # Patient entity repository
        │   └── call_repository.py    # Call log entity repository
        ├── schemas/
        │   ├── common.py           # Pagination & Error response schemas
        │   ├── patient.py          # Patient Pydantic v2 domain schemas
        │   └── call.py             # Call Pydantic v2 domain schemas
        ├── services/
        │   ├── patient_service.py  # Patient business logic layer
        │   └── call_service.py     # Call log business logic layer
        └── main.py                 # FastAPI application factory & root routes`}</pre>
            </div>
          </div>
        )}

        {/* TAB 4: SETTINGS & ENV */}
        {activeTab === 'settings' && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Key className="w-4 h-4 text-emerald-400" />
                <span>Configured Environment Settings</span>
              </h2>
              <button
                onClick={handleCopyEnv}
                className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-xs font-medium text-white flex items-center gap-1.5 transition-all"
              >
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied .env' : 'Copy .env Config'}</span>
              </button>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 font-mono text-xs text-slate-300 leading-relaxed overflow-x-auto">
              <pre>{`APP_NAME="Healthcare Voice Agent"
APP_ENV="development"
DEBUG=true
API_V1_STR="/api/v1"
HOST="0.0.0.0"
WORKERS=2
ALLOWED_ORIGINS="http://localhost:3000,https://internexus.tech,https://api.internexus.tech"
POSTGRES_SERVER="postgres"
POSTGRES_PORT=5432
POSTGRES_USER="voiceagent"
POSTGRES_PASSWORD="ChooseAStrongPassword123!"
POSTGRES_DB="voiceagentdb"
DATABASE_URL="postgresql://voiceagent:ChooseAStrongPassword123!@postgres:5432/voiceagentdb"
LOG_LEVEL="INFO"
PROMETHEUS_METRICS_ENABLED=true
VAPI_API_KEY="5d47d14d-8512-4d3e-85c8-24e9290dc9aa"`}</pre>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
