"""
API routes package.
"""
from .activities import router as activities_router
from .threats import router as threats_router
from .file_scan import router as file_scan_router
from .reports import router as reports_router
from .models import router as models_router

__all__ = [
    "activities_router",
    "threats_router",
    "file_scan_router",
    "reports_router",
    "models_router",
]
