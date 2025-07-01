#!/usr/bin/env python3
"""
Enhanced VectorWeight Homelab Generator
Idempotent, comprehensive deployment automation with airgapped support
"""

import os
import yaml
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import asdict
import requests
import tarfile
import zipfile
import git
from urllib.parse import urlparse

from enhanced_config_schema import (
    VectorWaveConfig, DeploymentMode, ClusterSize, VectorStoreType,
    SourceConfig, ClusterConfig
)


class CerbosIntegration:
    """Handles Cerbos authorization engine integration"""
    
    @staticmethod
    def generate_cerbos_config(clusters: List[ClusterConfig]) -> Dict:
        """Generate Cerbos configuration"""
        return {
            "cerbos": {
                "enabled": True,
                "deployment_mode": "cluster",
                "replicas": 3,
                "namespace": "authorization",
                "policy_repository": "https://github.com/vectorweight/cerbos-policies",
                "audit_enabled": True,
                "postgres_enabled": True,
                "postgres_config": {
                    "host": "cerbos-postgres.authorization.svc.cluster.local",
                    "database": "cerbos",
                    "username": "${CERBOS_DB_USERNAME}",
                    "password": "${CERBOS_DB_PASSWORD}"
                },
                "jwt_verification": {
                    "enabled": True,
                    "issuers": [
                        {
                            "issuer": "https://auth.vectorweight.com",
                            "audience": "vectorweight-services"
                        }
                    ]
                }
            }
        }


class EnhancedHelmManager:
    """Enhanced Helm repository and chart management"""
    
    def __init__(self, source_manager: SourceManager):
        self.source_manager = source_manager
        self.repositories = self._init_repositories()
        
    def _init_repositories(self) -> Dict:
        """Initialize repositories based on deployment mode"""
        if self.source_manager.config.type == DeploymentMode.INTERNET:
            return self._get_internet_repositories()
        else:
            return self._get_local_repositories()
    
    def _get_internet_repositories(self) -> Dict:
        """Standard internet-based repositories"""
        return {
            "cilium": {"url": "https://helm.cilium.io/"},
            "metallb": {"url": "oci://registry-1.docker.io/bitnamicharts"},
            "istio": {"url": "https://istio-release.storage.googleapis.com/charts"},
            "prometheus": {"url": "https://prometheus-community.github.io/helm-charts"},
            "argo": {"url": "https://argoproj.github.io/argo-helm"},
            "bitnami": {"url": "https://charts.bitnami.com/bitnami"},
            "weaviate": {"url": "https://weaviate.github.io/weaviate-helm"},
            "cerbos": {"url": "https://cerbos.dev/helm-charts"}
        }
    
    def _get_local_repositories(self) -> Dict:
        """Local/airgapped repositories"""
        sources_path = self.source_manager.local_path
        return {
            "local-charts": {"url": f"file://{sources_path}/charts"},
            "internal-registry": {"url": "registry.vectorweight.internal"}
        }


# CLI Interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        with open(config_file) as f:
            config_data = yaml.safe_load(f)
        config = VectorWaveConfig(**config_data)
    else:
        # Use minimal dev example
        from enhanced_config_schema import EXAMPLE_CONFIGS
        config = EXAMPLE_CONFIGS["minimal_dev"]
    
    generator = EnhancedVectorWeightGenerator(config)
    generator.generate_all()
