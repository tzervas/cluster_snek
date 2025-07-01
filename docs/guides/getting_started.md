# Getting Started with Cluster Snek

This guide will help you get started with Cluster Snek for managing your Kubernetes clusters.

## Prerequisites

- Python 3.12 or newer
- Kubernetes cluster (k3s, kind, or other)
- kubectl configured with cluster access
- (Optional) GPG key for signing commits

## Installation

### Using pip

```bash
pip install cluster-snek
```

### From source

```bash
git clone https://github.com/tzervas/cluster_snek.git
cd cluster_snek
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev,test]"
```

## Quick Start

### 1. Initialize Configuration

Create a new configuration file:

```bash
cluster-snek init --template minimal_dev --output config.yaml
```

This creates a basic configuration for development. You can edit `config.yaml` to customize your setup.

### 2. Validate Configuration

Before deploying, validate your configuration:

```bash
cluster-snek validate --config config.yaml --detailed
```

### 3. Generate Deployment

Generate the deployment files:

```bash
cluster-snek generate --config config.yaml
```

This creates a `example-deployment` directory with all necessary files.

### 4. Deploy

Deploy to your cluster:

```bash
cluster-snek deploy example-deployment/ --wait
```

### 5. Check Status

Monitor your deployment:

```bash
cluster-snek status
```

## Configuration

### Basic Structure

```yaml
project_name: "my-cluster"
environment: "development"
deployment_mode: "internet"

clusters:
  - name: "dev"
    domain: "dev.cluster.local"
    size: "minimal"
```

### Available Sizes

- `minimal`: 1-2 nodes, development
- `small`: 2-3 nodes, testing
- `medium`: 3-5 nodes, production
- `large`: 5+ nodes, enterprise

### Deployment Modes

1. `internet`: Standard internet-connected deployment
2. `airgapped-vc`: Airgapped with version control
3. `airgapped-local`: Airgapped with local files
4. `airgapped-archive`: Airgapped with verified archives

### Security Features

Enable security features in your configuration:

```yaml
enable_security_cluster: true
enable_cerbos_global: true
```

## Next Steps

- Read the [API Documentation](../api/README.md)
- Check out [Example Configurations](../examples/)
- Learn about [Security Features](security.md)
- Understand [Deployment Modes](deployment_modes.md)
