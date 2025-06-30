"""Deployment modes implementation supporting internet, airgapped-vc, airgapped-local, and airgapped-archive modes.

This module handles different deployment scenarios with appropriate validation and security measures.
"""

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Optional, List
import hashlib
import hmac
import json
import os
import gnupg
import yaml
from abc import ABC, abstractmethod


class DeploymentMode(Enum):
    """Supported deployment modes."""
    INTERNET = auto()
    AIRGAPPED_VC = auto()
    AIRGAPPED_LOCAL = auto()
    AIRGAPPED_ARCHIVE = auto()


@dataclass
class SourceConfig:
    """Configuration for deployment sources."""
    url: Optional[str] = None
    local_path: Optional[Path] = None
    archive_path: Optional[Path] = None
    version: Optional[str] = None
    checksums: Optional[Dict[str, str]] = None
    signature_path: Optional[Path] = None
    public_key_path: Optional[Path] = None


class DeploymentValidator:
    """Validates deployment configurations and credentials."""

    @staticmethod
    def validate_source_config(config: SourceConfig, mode: DeploymentMode) -> bool:
        """Validate source configuration based on deployment mode.
        
        Args:
            config: Source configuration to validate
            mode: Deployment mode being used
            
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid for the specified mode
        """
        if mode == DeploymentMode.INTERNET:
            if not config.url:
                raise ValueError("URL required for internet mode deployment")
                
        elif mode == DeploymentMode.AIRGAPPED_VC:
            if not config.local_path:
                raise ValueError("Local path required for airgapped-vc mode")
                
        elif mode == DeploymentMode.AIRGAPPED_LOCAL:
            if not config.local_path:
                raise ValueError("Local path required for airgapped-local mode")
                
        elif mode == DeploymentMode.AIRGAPPED_ARCHIVE:
            if not (config.archive_path and config.checksums):
                raise ValueError(
                    "Archive path and checksums required for airgapped-archive mode"
                )
        
        return True

    @staticmethod
    def validate_credentials(credentials_path: Path) -> bool:
        """Validate deployment credentials.
        
        Args:
            credentials_path: Path to credentials file
            
        Returns:
            bool: True if credentials are valid
            
        Raises:
            ValueError: If credentials are invalid or missing required fields
        """
        if not credentials_path.exists():
            raise ValueError(f"Credentials file not found: {credentials_path}")

        try:
            with open(credentials_path) as f:
                creds = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Malformed credentials file: {credentials_path}: {e}")

        required_fields = ['api_key', 'access_token']
        missing = [f for f in required_fields if f not in creds]
        
        if missing:
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")
            
        return True


class ArchiveVerifier:
    """Handles verification of deployment archives."""
    
    @staticmethod
    def verify_checksums(archive_path: Path, checksums: Dict[str, str]) -> bool:
        """Verify archive checksums.
        
        Args:
            archive_path: Path to archive file
            checksums: Dictionary of filename to expected checksum
            
        Returns:
            bool: True if checksums match
            
        Raises:
            ValueError: If checksum verification fails
        """
        if not archive_path.exists():
            raise ValueError(f"Archive not found: {archive_path}")
            
        filename = archive_path.name
        if filename not in checksums:
            raise ValueError(f"No checksum found for {filename}")
            
        expected = checksums[filename]
        
        sha256 = hashlib.sha256()
        with open(archive_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
                
        if sha256.hexdigest() != expected:
            raise ValueError(f"Checksum mismatch for {filename}")
            
        return True

    @staticmethod
    def verify_signature(
        archive_path: Path,
        signature_path: Path,
        public_key_path: Path
    ) -> bool:
        """Verify archive signature.
        
        Args:
            archive_path: Path to archive file
            signature_path: Path to signature file  
            public_key_path: Path to public key file
            
        Returns:
            bool: True if signature is valid
            
        Raises:
            ValueError: If signature verification fails
        """
        if not all(p.exists() for p in (archive_path, signature_path, public_key_path)):
            raise ValueError("Archive, signature or public key file not found")
            
        gpg = gnupg.GPG()
        
        with open(public_key_path, "rb") as f:
            key_data = f.read()
            gpg.import_keys(key_data)
            
        with open(signature_path, "rb") as sig:
            verify = gpg.verify_file(sig, archive_path)
        if not verify:
            raise ValueError(f"Signature verification failed: {verify.status}")
            
        return True


class DeploymentBase(ABC):
    """Base class for deployment implementations."""
    
    def __init__(self, config: SourceConfig):
        self.config = config
        DeploymentValidator.validate_source_config(config, self.mode)
        
    @property
    @abstractmethod
    def mode(self) -> DeploymentMode:
        """Get deployment mode."""
        pass
        
    @abstractmethod
    def deploy(self) -> bool:
        """Execute deployment."""
        pass


class InternetDeployment(DeploymentBase):
    """Internet-connected deployment implementation."""
    
    @property
    def mode(self) -> DeploymentMode:
        return DeploymentMode.INTERNET
        
    def deploy(self) -> bool:
        # Implementation for internet deployment
        return True


class AirgappedVCDeployment(DeploymentBase):
    """Airgapped version control deployment implementation."""
    
    @property
    def mode(self) -> DeploymentMode:
        return DeploymentMode.AIRGAPPED_VC
        
    def deploy(self) -> bool:
        # Implementation for airgapped VC deployment  
        return True


class AirgappedLocalDeployment(DeploymentBase):
    """Airgapped local deployment implementation."""
    
    @property
    def mode(self) -> DeploymentMode:
        return DeploymentMode.AIRGAPPED_LOCAL
        
    def deploy(self) -> bool:
        # Implementation for airgapped local deployment
        return True


class AirgappedArchiveDeployment(DeploymentBase):
    """Airgapped archive deployment implementation."""
    
    @property
    def mode(self) -> DeploymentMode:
        return DeploymentMode.AIRGAPPED_ARCHIVE
        
    def deploy(self) -> bool:
        verifier = ArchiveVerifier()
        
        # Verify archive integrity
        verifier.verify_checksums(
            self.config.archive_path,
            self.config.checksums
        )
        
        # Verify signature if provided
        if self.config.signature_path and self.config.public_key_path:
            verifier.verify_signature(
                self.config.archive_path,
                self.config.signature_path,
                self.config.public_key_path
            )
            
        # Implementation for airgapped archive deployment
        return True


def create_deployment(
    mode: DeploymentMode,
    config: SourceConfig
) -> DeploymentBase:
    """Factory function to create appropriate deployment instance.
    
    Args:
        mode: Deployment mode to use
        config: Source configuration
        
    Returns:
        DeploymentBase: Configured deployment instance
        
    Raises:
        ValueError: If invalid mode specified
    """
    deployments = {
        DeploymentMode.INTERNET: InternetDeployment,
        DeploymentMode.AIRGAPPED_VC: AirgappedVCDeployment,
        DeploymentMode.AIRGAPPED_LOCAL: AirgappedLocalDeployment,
        DeploymentMode.AIRGAPPED_ARCHIVE: AirgappedArchiveDeployment
    }
    
    if mode not in deployments:
        raise ValueError(f"Invalid deployment mode: {mode}")
        
    return deployments[mode](config)
