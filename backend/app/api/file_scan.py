"""
File scanning API endpoints.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict

from ..core.database import get_db
from ..core.firebase_auth import get_current_user
from ..services.file_scanner import FileScanner
from ..models.file_scan import FileScan

router = APIRouter(prefix="/api", tags=["file_scan"])


@router.post("/scan-file")
async def scan_file(
    file: UploadFile = File(...),
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scan an uploaded file for threats.

    Args:
        file: Uploaded file
        user: Authenticated user
        db: Database session

    Returns:
        Scan result
    """
    # Check file size
    from ..core.config import settings

    # Read file to check size
    contents = await file.read()
    file_size = len(contents)

    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE / 1024 / 1024:.1f} MB"
        )

    # Reset file pointer
    await file.seek(0)

    # Scan file
    scanner = FileScanner(db)
    scan_result = await scanner.scan_file(file, user['email'])

    return {
        "success": True,
        "scan": scan_result.to_dict()
    }


@router.get("/scan-results")
async def get_scan_results(
    limit: int = Query(100, ge=1, le=1000),
    result_filter: str = Query(None),
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get file scan results.

    Args:
        limit: Maximum number of results to return
        result_filter: Filter by scan result (safe, suspicious, malicious)
        user: Authenticated user
        db: Database session

    Returns:
        List of scan results
    """
    query = db.query(FileScan)

    if result_filter:
        query = query.filter(FileScan.scan_result == result_filter)

    scans = query.order_by(desc(FileScan.scan_timestamp)).limit(limit).all()
    return [scan.to_dict() for scan in scans]


@router.get("/scan-results/stats")
async def get_scan_stats(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get file scan statistics.

    Args:
        user: Authenticated user
        db: Database session

    Returns:
        Scan statistics
    """
    total_scans = db.query(FileScan).count()
    safe_count = db.query(FileScan).filter(FileScan.scan_result == "safe").count()
    suspicious_count = db.query(FileScan).filter(FileScan.scan_result == "suspicious").count()
    malicious_count = db.query(FileScan).filter(FileScan.scan_result == "malicious").count()
    quarantined_count = db.query(FileScan).filter(FileScan.is_quarantined == True).count()

    return {
        'total_scans': total_scans,
        'safe': safe_count,
        'suspicious': suspicious_count,
        'malicious': malicious_count,
        'quarantined': quarantined_count,
    }


@router.get("/scan-results/{scan_id}")
async def get_scan_result(
    scan_id: int,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific scan result by ID.

    Args:
        scan_id: Scan ID
        user: Authenticated user
        db: Database session

    Returns:
        Scan result details
    """
    scan = db.query(FileScan).filter(FileScan.id == scan_id).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan result not found")

    return scan.to_dict()
