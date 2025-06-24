import shutil
import tarfile
import zipfile
from pathlib import Path
import git
from cluster_snek.config.schema import SourceConfig, DeploymentMode

class SourceManager:
    """Manages different source types for airgapped deployments"""
    
    def __init__(self, source_config: SourceConfig, temp_dir: Path):
        self.config = source_config
        self.temp_dir = temp_dir
        self.local_path = temp_dir / "sources"
        self.local_path.mkdir(exist_ok=True)
    
    def fetch_sources(self) -> Path:
        """Fetch sources based on configuration"""
        if self.config.type == DeploymentMode.INTERNET:
            return self._fetch_internet_sources()
        elif self.config.type == DeploymentMode.AIRGAPPED_VC:
            return self._fetch_vc_sources()
        elif self.config.type == DeploymentMode.AIRGAPPED_LOCAL:
            return self._copy_local_sources()
        elif self.config.type == DeploymentMode.AIRGAPPED_NETWORK:
            return self._fetch_network_sources()
        elif self.config.type == DeploymentMode.AIRGAPPED_ARCHIVE:
            return self._extract_archive_sources()
        else:
            raise ValueError(f"Unsupported deployment mode: {self.config.type}")
    
    def _fetch_internet_sources(self) -> Path:
        """Use standard internet-based sources"""
        return self.local_path
    
    def _fetch_vc_sources(self) -> Path:
        """Clone from version control"""
        repo_path = self.local_path / "repositories"
        if self.config.url:
            git.Repo.clone_from(
                self.config.url,
                repo_path,
                env={
                    "GIT_USERNAME": self.config.username or "",
                    "GIT_PASSWORD": self.config.token or self.config.password or ""
                }
            )
        return repo_path
    
    def _copy_local_sources(self) -> Path:
        """Copy from local directory"""
        if self.config.path and self.config.path.exists():
            shutil.copytree(self.config.path, self.local_path / "local", dirs_exist_ok=True)
        return self.local_path / "local"
    
    def _fetch_network_sources(self) -> Path:
        """Fetch from network location"""
        # Implementation for network file systems, HTTP endpoints, etc.
        network_path = self.local_path / "network"
        network_path.mkdir(exist_ok=True)
        
        if self.config.url:
            # Handle HTTP/HTTPS downloads
            if self.config.url.startswith(('http://', 'https://')):
                self._download_from_http(self.config.url, network_path)
            # Handle SMB/NFS/SSH mounts
            else:
                self._mount_network_path(self.config.url, network_path)
        
        return network_path
    
    def _extract_archive_sources(self) -> Path:
        """Extract from archive files"""
        archive_path = self.local_path / "archive"
        archive_path.mkdir(exist_ok=True)
        
        if self.config.path and self.config.path.exists():
            self._extract_archive(self.config.path, archive_path)
        elif self.config.url:
            # Download and extract
            downloaded_archive = self._download_archive(self.config.url)
            self._extract_archive(downloaded_archive, archive_path)
        
        return archive_path
    
    def _extract_archive(self, archive_file: Path, extract_to: Path):
        """Extract various archive formats"""
        if archive_file.suffix in ['.tar', '.tar.gz', '.tgz']:
            with tarfile.open(archive_file) as tar:
                tar.extractall(extract_to)
        elif archive_file.suffix == '.zip':
            with zipfile.ZipFile(archive_file) as zip_file:
                zip_file.extractall(extract_to)
        else:
            raise ValueError(f"Unsupported archive format: {archive_file.suffix}")
