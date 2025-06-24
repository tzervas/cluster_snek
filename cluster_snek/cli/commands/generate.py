def _generate_deployment_scripts(self):
        """Generate deployment automation scripts"""
        deploy_script = f"""#!/bin/bash
set -e

echo "🚀 Deploying VectorWeight Homelab ({self.config.environment})..."

# Deployment mode: {self.config.deployment_mode.value}
# Clusters: {', '.join([c.name for c in self.config.clusters])}

# Bootstrap ArgoCD
kubectl apply -f orchestration-repo/bootstrap/

# Deploy ApplicationSets
kubectl apply -f orchestration-repo/applicationsets/

echo "✅ Deployment initiated! Monitor via ArgoCD UI"
"""
        
        script_path = self.output_path / "deploy.sh"
        script_path.write_text(deploy_script)
        script_path.chmod(0o755)
    
    def _generate_cluster_readme(self, cluster: ClusterConfig, cluster_path: Path):
        """Generate cluster-specific README"""
        readme_content = f"""# {cluster.name.title()}

Configuration for {cluster.domain}

## Features
- Size: {cluster.size.value}
- GPU: {'✅' if cluster.gpu_enabled else '❌'}
- Vector Store: {cluster.vector_store.value}
- Cerbos: {'✅' if cluster.cerbos_enabled else '❌'}

## Workloads
{chr(10).join(f'- {w}' for w in cluster.specialized_workloads)}
"""
        
        with open(cluster_path / "README.md", "w") as f:
            f.write(readme_content)
    
    def _print_next_steps(self):
        """Print deployment next steps"""
        print("\n" + "="*60)
        print("🎯 NEXT STEPS:")
        print("="*60)
        print("1. Review generated configurations")
        print("2. Execute deployment script: ./deploy.sh")
        print("3. Monitor via ArgoCD UI")
        print("="*60)
