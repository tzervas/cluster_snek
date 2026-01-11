#!/usr/bin/env python3
"""Script to generate initial secrets for the application deployment.

This script generates secure credentials for various components including:
- Keycloak admin credentials
- PostgreSQL credentials
- Initial user accounts
"""

import base64
import secrets
import string
import yaml
from pathlib import Path
from typing import Dict, List, Optional

def generate_password(
    length: int = 32,
    punctuation: str = "!#$%&()*+,-./:;<=>?@[]^_{|}~"
) -> str:
    """Generate a secure random password.

    Args:
        length: The length of the password to generate. Defaults to 32.
        punctuation: The set of punctuation characters to use. 
            Defaults to a safe subset that avoids quotes, backslashes, and shell metacharacters.

    Returns:
        A secure random password string.
    """
    alphabet = string.ascii_letters + string.digits + punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_k8s_secret(name: str, namespace: str, data: Dict[str, str]) -> Dict:
    """Create a Kubernetes secret manifest.
    
    Args:
        name: Name of the secret
        namespace: Kubernetes namespace
        data: Dictionary of key-value pairs to store in the secret
        
    Returns:
        Dictionary containing the Kubernetes secret manifest
    """
    encoded_data = {
        k: base64.b64encode(v.encode()).decode()
        for k, v in data.items()
    }
    
    return {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": name,
            "namespace": namespace
        },
        "type": "Opaque",
        "data": encoded_data
    }

def generate_all_secrets(namespace: str = "default") -> List[Dict]:
    """Generate all required secrets for the application.
    
    Args:
        namespace: Kubernetes namespace to create secrets in
        
    Returns:
        List of Kubernetes secret manifests
    """
    secrets = []
    
    # Keycloak admin credentials
    keycloak_admin = create_k8s_secret(
        "keycloak-admin-secret",
        namespace,
        {
            "admin-password": generate_password(),
            "management-password": generate_password()
        }
    )
    secrets.append(keycloak_admin)
    
    # PostgreSQL credentials
    postgres = create_k8s_secret(
        "keycloak-postgresql-secret",
        namespace,
        {
            "postgres-password": generate_password(),
            "replication-password": generate_password()
        }
    )
    secrets.append(postgres)
    
    # Initial user accounts
    initial_users = {
        "admin": "admin",
        "power-user": "power-user",
        "readonly": "readonly"
    }
    
    user_secrets = {
        f"{user}-password": generate_password()
        for user in initial_users.keys()
    }
    
    users = create_k8s_secret(
        "initial-user-credentials",
        namespace,
        user_secrets
    )
    secrets.append(users)
    
    return secrets

def main(output_dir: Optional[str] = None) -> None:
    """Generate secrets and write them to files.
    
    Args:
        output_dir: Directory to write secret files to. If None, uses current directory.
    """
    secrets = generate_all_secrets()
    
    output_path = Path(output_dir) if output_dir else Path.cwd()
    output_path.mkdir(parents=True, exist_ok=True)
    
    for secret in secrets:
        name = secret["metadata"]["name"]
        with open(output_path / f"{name}.yaml", "w") as f:
            yaml.dump(secret, f, sort_keys=False)
            print(f"Generated secret: {name}")

if __name__ == "__main__":
    main("secrets")
