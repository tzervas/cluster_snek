# Migration and Deployment Guides

## 📦 Migration Guide: Old to New System

### Overview of Changes

The VectorWeight refactoring introduces significant improvements while maintaining backward compatibility where possible:

| Aspect | Old System | New System | Migration Required |
|--------|------------|------------|-------------------|
| Configuration | Complex YAML (200+ lines) | Simplified Schema (<20 lines) | ✅ Yes |
| Repository Creation | Manual/GitHub CLI | GitHub API (PyGithub) | ⚠️ Token needed |
| Deployment Modes | Internet only | Multi-mode (airgapped support) | ⚠️ If airgapped |
| Vector Stores | Not supported | Weaviate, Qdrant, Chroma | ⚠️ If needed |
| Authorization | Basic RBAC | Cerbos integration | ⚠️ If enabled |
| State Management | Stateless | Idempotent with state tracking | ✅ Automatic |

### Migration Steps

#### 1. Backup Current Configuration

```bash
# Backup your existing configuration
cp example-config.yaml example-config.yaml.backup
cp -r example-cluster/ example-cluster-backup/
```

#### 2. Install New System

```bash
# Install the new VectorWeight system
pip install example-cluster

# Verify installation
example --version
```

#### 3. Migrate Configuration

Use the migration utility to convert your old configuration:

```python
#!/usr/bin/env python3
"""
Configuration Migration Utility
Converts old VectorWeight configurations to new simplified format
"""

import yaml
from pathlib import Path
from example.config.loader import ConfigurationLoader

def migrate_old_configuration(old_config_path: Path) -> dict:
    """Migrate old configuration to new format"""
    
    with open(old_config_path) as f:
        old_config = yaml.safe_load(f)
    
    # Extract cluster information
    clusters = []
    for cluster_data in old_config.get('clusters', []):
        # Map old size to new size
        size_mapping = {
            1: 'minimal',
            2: 'small', 
            3: 'small',
            4: 'medium',
            5: 'medium'
        }
        
        node_count = cluster_data.get('node_count', 2)
        cluster_size = size_mapping.get(node_count, 'small')
        
        cluster = {
            'name': cluster_data['name'],
            'domain': cluster_data.get('domain', f"{cluster_data['name']}.example.com"),
            'size': cluster_size,
            'gpu_enabled': cluster_data.get('gpu_enabled', False),
            'vector_store': 'disabled',  # Default, configure manually if needed
            'cerbos_enabled': False,     # Default, configure manually if needed
            'specialized_workloads': cluster_data.get('specialized_workloads', [])
        }
        
        clusters.append(cluster)
    
    # Build new configuration
    new_config = {
        'project_name': old_config.get('project_name', 'example-cluster'),
        'environment': old_config.get('environment', 'production'),
        'deployment_mode': 'internet',  # Default, change if airgapped needed
        'clusters': clusters,
        'github_organization': old_config.get('github_organization', 'example'),
        'auto_create_repositories': True,
        'base_domain': old_config.get('domain', 'example.com')
    }
    
    # Copy network settings if present
    if 'metallb_ip_range' in old_config:
        new_config['metallb_ip_range'] = old_config['metallb_ip_range']
    
    return new_config

# Usage
if __name__ == "__main__":
    old_config_path = Path("example-config.yaml.backup")
    new_config = migrate_old_configuration(old_config_path)
    
    with open("example-config-new.yaml", "w") as f:
        yaml.dump(new_config, f, default_flow_style=False)
    
    print("Migration complete! Review example-config-new.yaml")
```

#### 4. Validate New Configuration

```bash
# Validate the migrated configuration
example validate --config example-config-new.yaml --detailed

# Fix any validation issues
# Edit example-config-new.yaml as needed
```

#### 5. Test Generation

```bash
# Test the new configuration with dry run
example generate --config example-config-new.yaml --dry-run

# Generate actual deployment if validation passes
example generate --config example-config-new.yaml --output example-new/
```

#### 6. Update GitHub Settings

```bash
# Set GitHub token for repository automation
export GITHUB_TOKEN=your_github_token

# Or disable auto-creation if preferred
# Set auto_create_repositories: false in config
```

### Configuration Mapping Reference

#### Old to New Cluster Configuration

```yaml
# OLD FORMAT
clusters:
  - name: "ai-cluster"
    kubernetes_distribution: "microk8s"
    node_count: 4
    resources:
      cpu_cores: 16
      memory_gb: 128
      storage_gb: 2000
      gpu_enabled: true
    storage_class: "openebs-hostpath"
    specialized_workloads:
      - "machine-learning"
      - "artificial-intelligence"

# NEW FORMAT  
clusters:
  - name: "ai-cluster"
    domain: "ai.example.com"
    size: "large"
    gpu_enabled: true
    vector_store: "weaviate"  # NEW: Vector store integration
    cerbos_enabled: true      # NEW: Authorization
    specialized_workloads:
      - "machine-learning"
      - "ai-inference"
```

#### Feature Additions

New features that weren't in the old system:

```yaml
# NEW: Deployment modes
deployment_mode: "airgapped-vc"
source:
  mode: "airgapped-vc"
  url: "https://git.internal.company.com"

# NEW: Vector store integration
vector_store: "weaviate"
custom_values:
  weaviate:
    replicas: 3
    modules:
      text2vec-transformers:
        enabled: true

# NEW: Cerbos authorization
cerbos_enabled: true

# NEW: MCP integration
enable_mcp: true

# NEW: Direct host deployment
deployment_target: "direct"
```

---

## 🚀 Comprehensive Deployment Guide

### Prerequisites

#### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.12+ | 3.12+ |
| Memory | 4GB | 8GB+ |
| Storage | 50GB | 100GB+ |
| Kubernetes | 1.30+ | 1.32+ |

#### Required Tools

```bash
# Install required tools
# Kubernetes CLI
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Docker (if using local development)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify installations
kubectl version --client
helm version
docker version
```

#### Network Requirements

- **Internet Access**: For downloading charts and images (internet mode)
- **GitHub Access**: For repository creation and management
- **Internal DNS**: Properly configured for cluster communication
- **Load Balancer Range**: Available IP range for MetalLB

### Deployment Scenarios

#### Scenario 1: Development Setup

**Objective**: Single-node development environment

```bash
# 1. Initialize minimal configuration
cluster_snek init --template minimal_dev --output dev-config.yaml

# 2. Customize for your environment
cat > dev-config.yaml << EOF
project_name: "my-dev-cluster"
environment: "development"
deployment_mode: "internet"
deployment_target: "direct"

clusters:
  - name: "dev"
    domain: "dev.cluster.local"
    size: "minimal"

enable_security_cluster: false
auto_create_repositories: true
base_domain: "cluster.local"
metallb_ip_range: "192.168.1.200-192.168.1.210"
EOF

# 3. Generate deployment
cluster_snek generate --config dev-config.yaml

# 4. Deploy
cd example-deployment
./deploy.sh
```

#### Scenario 2: Production AI/ML Environment

**Objective**: Multi-cluster setup with AI capabilities

```bash
# 1. Create production configuration
cat > prod-config.yaml << EOF
project_name: "example-production"
environment: "production"
deployment_mode: "internet"

clusters:
  - name: "ai-cluster"
    domain: "ai.example.com"
    size: "large"
    gpu_enabled: true
    vector_store: "weaviate"
    cerbos_enabled: true
    specialized_workloads:
      - "machine-learning"
      - "ai-inference"

  - name: "security-cluster"
    domain: "sec.example.com"
    size: "small"
    cerbos_enabled: true
    specialized_workloads:
      - "security"
      - "monitoring"

enable_cerbos_global: true
enable_gpu_operator: true
github_organization: "your-org"
github_token: "${GITHUB_TOKEN}"
EOF

# 2. Set environment variables
export GITHUB_TOKEN=your_github_token_here

# 3. Validate configuration
cluster_snek validate --config prod-config.yaml --detailed

# 4. Generate deployment
cluster_snek generate --config prod-config.yaml

# 5. Deploy to clusters
cd example-deployment
./deploy.sh
```

#### Scenario 3: Airgapped Enterprise Deployment

**Objective**: Secure airgapped deployment

```bash
# 1. Prepare airgapped sources
mkdir -p /opt/k8s-sources
# Download/sync your charts and manifests to /opt/k8s-sources

# 2. Create airgapped configuration
cat > airgapped-config.yaml << EOF
project_name: "example-enterprise"
environment: "production"
deployment_mode: "airgapped-local"

source:
  mode: "airgapped-local"
  path: "/opt/k8s-sources"
  verification_enabled: true

clusters:
  - name: "secure-ai"
    domain: "ai.internal.company.com"
    size: "large"
    gpu_enabled: true
    vector_store: "weaviate"
    cerbos_enabled: true

auto_create_repositories: false
base_domain: "internal.company.com"
EOF

# 3. Generate deployment
cluster_snek generate --config airgapped-config.yaml

# 4. Manual repository setup (airgapped)
# Copy generated configurations to your internal Git repositories

# 5. Deploy using internal GitOps
# Follow your organization's deployment procedures
```

### Step-by-Step Deployment Process

#### Phase 1: Preparation

```bash
# 1. Environment setup
export GITHUB_TOKEN=your_token
export KUBECONFIG=/path/to/your/kubeconfig

# 2. Verify Kubernetes access
kubectl cluster-info
kubectl get nodes

# 3. Check resource availability
kubectl describe nodes
```

#### Phase 2: Configuration

```bash
# 1. Create configuration
cluster_snek init --interactive

# 2. Validate configuration
cluster_snek validate --config config.yaml --detailed

# 3. Review and adjust
nano config.yaml
```

#### Phase 3: Generation

```bash
# 1. Generate deployment
cluster_snek generate --config config.yaml --output my-deployment

# 2. Review generated files
tree my-deployment/
cat my-deployment/deploy.sh
```

#### Phase 4: Deployment

```bash
# 1. Navigate to deployment directory
cd my-deployment

# 2. Bootstrap ArgoCD
kubectl apply -f orchestration-repo/bootstrap/

# 3. Wait for ArgoCD readiness
kubectl wait --for=condition=available --timeout=300s deployment/argo-cd-argocd-server -n argocd

# 4. Deploy ApplicationSets
kubectl apply -f orchestration-repo/applicationsets/

# 5. Monitor deployment
cluster_snek status
```

#### Phase 5: Verification

```bash
# 1. Check ArgoCD applications
kubectl get applications -n argocd

# 2. Verify cluster components
kubectl get pods --all-namespaces

# 3. Access ArgoCD UI
kubectl port-forward -n argocd svc/argo-cd-argocd-server 8080:80

# 4. Check service mesh
kubectl get pods -n istio-system

# 5. Verify vector stores (if enabled)
kubectl get pods -n vector-stores
```

### Monitoring Deployment Progress

#### ArgoCD Dashboard

```bash
# Port forward to ArgoCD
kubectl port-forward -n argocd svc/argo-cd-argocd-server 8080:80

# Get admin password
kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Access: http://localhost:8080
# Username: admin
# Password: (from above command)
```

#### Command Line Monitoring

```bash
# Watch application sync status
watch -n 5 'kubectl get applications -n argocd'

# Monitor pod deployment
watch -n 5 'kubectl get pods --all-namespaces | grep -E "(ContainerCreating|Pending|Error)"'

# Check events for issues
kubectl get events --all-namespaces --sort-by='.lastTimestamp'
```

### Troubleshooting Common Issues

#### Issue: Repository Creation Fails

```bash
# Solution 1: Check GitHub token permissions
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Solution 2: Disable auto-creation
auto_create_repositories: false
```

#### Issue: ArgoCD Can't Access Repositories

```bash
# Solution: Add repository credentials
kubectl create secret generic repo-secret \
  --from-literal=username=your-username \
  --from-literal=password=your-token \
  -n argocd

kubectl label secret repo-secret argocd.argoproj.io/secret-type=repository -n argocd
```

#### Issue: Vector Store Won't Start

```bash
# Check storage class
kubectl get storageclass

# Check persistent volume claims
kubectl get pvc -n vector-stores

# Check pod logs
kubectl logs -n vector-stores deployment/weaviate
```

#### Issue: GPU Operator Installation Fails

```bash
# Check node labels
kubectl get nodes --show-labels | grep nvidia

# Verify GPU availability
kubectl describe nodes | grep nvidia

# Check operator logs
kubectl logs -n gpu-operator deployment/gpu-operator
```

### Performance Optimization

#### Resource Sizing Guidelines

```yaml
# Cluster size recommendations
sizes:
  minimal:    # 1 node,  2 CPU,  4GB RAM
    use_case: "Development, testing"
    max_applications: 10
    
  small:      # 2 nodes, 4 CPU,  8GB RAM
    use_case: "Small production, staging"
    max_applications: 25
    
  medium:     # 3 nodes, 8 CPU, 16GB RAM
    use_case: "Production workloads"
    max_applications: 50
    
  large:      # 5+ nodes, 16+ CPU, 32+ GB RAM
    use_case: "Enterprise, AI/ML"
    max_applications: 100+
```

#### Network Optimization

```yaml
# Optimize for your network
metallb_ip_range: "192.168.1.200-192.168.1.250"  # Adjust for your subnet

global_overrides:
  networking:
    high_throughput: true    # For AI/ML workloads
    low_latency: true        # For real-time applications
```

### Security Hardening

#### Network Security

```bash
# Verify network policies
# automate as a cluster_snek functionality kubectl get networkpolicies --all-namespaces
cluster_snek net-policy --verify

# Check Cilium status
# automate as a cluster_snek functionality kubectl exec -n kube-system ds/cilium -- cilium status
cluster_snek status cni

# Verify Istio mTLS
# automate as a cluster_snek functionality kubectl exec -n istio-system deploy/istiod -- pilot-discovery proxy-status
cluster_snek service-mesh --verify
```

#### Pod Security

```bash
# Check pod security standards
# automate as a cluster_snek functionality kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext}{"\n"}{end}' --all-namespaces
cluster_snek check-security --standards

# Validate cluster/pod security standards via a differential
cluster_snek diff --security-standards

# Verify no privileged containers
# automate as a cluster_snek functionality kubectl get pods --all-namespaces -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].securityContext.privileged}{"\n"}{end}' | grep true
cluster_snek privileged-containers --check
```

### Maintenance and Updates

#### Regular Maintenance Tasks

```bash
# Update Helm charts (monthly)
cluster_snek generate --config config.yaml --force

# Check for security updates
# automate as a cluster_snek functionality kubectl get pods --all-namespaces -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}' | sort -u
cluster_snek check-security --updates

# Backup configurations
cluster_snek backup example-deployment/

# Monitor resource usage
kubectl top nodes
kubectl top pods --all-namespaces
```

#### Upgrade Process

```bash
# 1. Backup current state
cluster_snek backup --target example-cluster -o cluster-backup.yaml

# 2. Update VectorWeight
cluster_snek upgrade example-cluster

# 3. Regenerate with force flag
cluster_snek generate --config config.yaml --force

# 4. Review changes
cluster_snek diff example-cluster example-deployment/

# 5. Apply updates
cd example-deployment && cluster_snek deploy example-cluster
```

This comprehensive deployment guide ensures successful cluster deployments across all scenarios while providing troubleshooting and optimization guidance.
