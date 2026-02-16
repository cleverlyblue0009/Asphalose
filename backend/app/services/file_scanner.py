"""
File scanning service for malware detection.
"""
import hashlib
import os
import shutil
from datetime import datetime
from typing import Dict, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from ..models.file_scan import FileScan
from ..models.alert import Alert
from ..ml.behavioral_classifier import BehavioralClassifier
from ..core.config import settings


class FileScanner:
    """Service for scanning files for threats."""

    def __init__(self, db: Session):
        """
        Initialize file scanner.

        Args:
            db: Database session
        """
        self.db = db
        self.classifier_path = os.path.join(settings.MODEL_PATH, 'behavioral_classifier.joblib')

        # Try to load classifier
        try:
            self.classifier = BehavioralClassifier(self.classifier_path)
        except:
            print("Warning: Could not load behavioral classifier for file scanning")
            self.classifier = None

    def compute_file_hash(self, file_path: str) -> str:
        """
        Compute SHA-256 hash of file.

        Args:
            file_path: Path to file

        Returns:
            SHA-256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def extract_file_metadata(self, file_path: str, filename: str) -> Dict:
        """
        Extract file metadata.

        Args:
            file_path: Path to file
            filename: Original filename

        Returns:
            Dictionary of metadata
        """
        stat = os.stat(file_path)
        file_extension = os.path.splitext(filename)[1].lower()

        # Suspicious file extensions
        suspicious_extensions = [
            '.exe', '.dll', '.bat', '.cmd', '.vbs', '.js', '.jar',
            '.ps1', '.scr', '.com', '.pif', '.sh', '.app'
        ]

        metadata = {
            'size': stat.st_size,
            'extension': file_extension,
            'is_suspicious_extension': file_extension in suspicious_extensions,
        }

        return metadata

    def classify_file(self, metadata: Dict) -> tuple[str, float]:
        """
        Classify file as safe, suspicious, or malicious.

        Args:
            metadata: File metadata

        Returns:
            Tuple of (classification, confidence)
        """
        # Simple rule-based classification (can be enhanced with ML)
        confidence = 0.8

        # Check file size (very large or very small files can be suspicious)
        if metadata['size'] < 100 or metadata['size'] > 100 * 1024 * 1024:  # < 100 bytes or > 100MB
            return 'suspicious', 0.6

        # Check extension
        if metadata['is_suspicious_extension']:
            return 'malicious', 0.9

        # Check if file hash is in known malware database (simplified)
        # In production, you'd check against VirusTotal or similar

        # For demo, randomly mark some files as suspicious
        import random
        if random.random() < 0.15:  # 15% chance
            return 'suspicious', 0.7

        return 'safe', confidence

    async def scan_file(
        self,
        file: UploadFile,
        user_email: str
    ) -> FileScan:
        """
        Scan uploaded file for threats.

        Args:
            file: Uploaded file
            user_email: Email of user who uploaded file

        Returns:
            FileScan result
        """
        # Save file temporarily
        temp_path = os.path.join(settings.UPLOAD_DIR, f"temp_{datetime.now().timestamp()}_{file.filename}")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Compute hash
        file_hash = self.compute_file_hash(temp_path)

        # Check if file was scanned before
        existing_scan = self.db.query(FileScan).filter(
            FileScan.file_hash == file_hash
        ).first()

        if existing_scan:
            # Return cached result
            os.remove(temp_path)
            return existing_scan

        # Extract metadata
        metadata = self.extract_file_metadata(temp_path, file.filename)

        # Classify file
        scan_result, confidence = self.classify_file(metadata)

        # Quarantine if suspicious or malicious
        quarantine_path = None
        if scan_result in ['suspicious', 'malicious']:
            quarantine_path = os.path.join(
                settings.QUARANTINE_DIR,
                f"{file_hash}_{file.filename}"
            )
            shutil.move(temp_path, quarantine_path)
        else:
            os.remove(temp_path)

        # Create file scan record
        file_scan = FileScan(
            filename=file.filename,
            file_hash=file_hash,
            file_size=metadata['size'],
            file_type=metadata['extension'],
            scan_result=scan_result,
            confidence_score=confidence,
            is_quarantined=scan_result in ['suspicious', 'malicious'],
            quarantine_path=quarantine_path,
            scanned_by=user_email,
        )

        self.db.add(file_scan)
        self.db.commit()
        self.db.refresh(file_scan)

        # Create alert if threat detected
        if scan_result in ['suspicious', 'malicious']:
            severity = 'critical' if scan_result == 'malicious' else 'high'
            alert = Alert(
                alert_type='malware',
                title=f"{scan_result.capitalize()} file detected",
                description=f"File '{file.filename}' has been classified as {scan_result}. "
                           f"Confidence: {confidence:.2%}. File quarantined.",
                severity=severity,
                file_scan_id=file_scan.id,
            )
            self.db.add(alert)
            self.db.commit()

        return file_scan
