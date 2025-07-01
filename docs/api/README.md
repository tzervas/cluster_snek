# Cluster Snek API Documentation

## Core APIs

### Config Module
- `Config` class: Main configuration container
- `SourceConfig` class: Source configuration
- `ClusterConfig` class: Cluster configuration

### Context Module
- `Context` class: Application context
- `get_context()`: Get global context
- `set_context()`: Set global context

### Logger Module
- `setup_logging()`: Configure logging

## Deployment APIs

### Modes Module
- `DeploymentMode` enum: Available deployment modes
- `DeploymentBase` class: Base deployment class
- Specific mode implementations:
  - `InternetDeployment`
  - `AirgappedVCDeployment`
  - `AirgappedLocalDeployment`
  - `AirgappedArchiveDeployment`

### Archive Module
- `ArchiveVerifier` class: Archive verification utilities
- Checksum and signature validation

### Validation Module
- `DeploymentValidator` class: Deployment validation utilities

## Security APIs

### Network Module
- Network policy management
- Service mesh configuration

### Pod Module
- Pod security standards
- Container security

### Audit Module
- Security auditing
- Compliance checking

## CLI Commands

### Init Command
```bash
cluster-snek init [OPTIONS]
  --template TEXT     Template to use (minimal_dev, production_full, airgapped_enterprise)
  --output PATH      Output configuration file
  --interactive      Use interactive mode
```

### Validate Command
```bash
cluster-snek validate [OPTIONS] CONFIG
  --detailed         Show detailed validation information
```

### Generate Command
```bash
cluster-snek generate [OPTIONS] CONFIG
  --output PATH      Output directory
  --dry-run         Validate only, don't generate files
  --force           Force regeneration of all files
```

### Deploy Command
```bash
cluster-snek deploy [OPTIONS] DEPLOYMENT_DIR
  --wait            Wait for deployment to complete
```

### Status Command
```bash
cluster-snek status [OPTIONS]
  --namespace TEXT   Namespace to check status for
```

## Utility APIs

### Files Module
- File handling utilities
- Path manipulation

### Crypto Module
- Cryptographic operations
- Key management

### Validation Module
- General validation utilities
- Schema validation
