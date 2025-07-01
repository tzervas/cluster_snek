import yaml
from pathlib import Path
from typing import ClassVar, Dict, Any

# Note: The import for VectorWaveConfig is no longer needed at the class level
# if you pass in the required values directly during initialization.
from cluster_snek.config.schema import ClusterConfig, ClusterSize

class InfrastructureGenerator:
    """
    Generates core infrastructure components like CNI and LoadBalancers
    as self-contained Helm charts.
    """
    # Step 2: Centralize component configuration in one place.
    # This makes adding new components or updating versions trivial.
    _CHART_CONFIG: ClassVar[Dict[str, Any]] = {
        "cilium": {
            "version": "1.17.4",
            "repository": "https://helm.cilium.io/",
        },
        "metallb": {
            "version": "6.4.18",
            "repository": "oci://registry-1.docker.io/bitnamicharts",
            # MetalLB doesn't have size-based resources, so it's omitted.
        }
    }

    def __init__(self, use_vms: bool, ip_pool_start: str, ip_pool_end: str):
        """
        Initializes the generator with only the global configuration it needs.
        """
        self.use_vms = use_vms
        self.ip_pool_start = ip_pool_start
        self.ip_pool_end = ip_pool_end

    def generate(self, cluster_config: ClusterConfig, output_path: Path) -> None:
        """
        Generates all base infrastructure Helm charts for a given cluster.

        Args:
            cluster_config: The configuration for the specific cluster.
            output_path: The root path where the 'infrastructure' directory will be created.
        """
        infra_path = output_path / "infrastructure"
        infra_path.mkdir(exist_ok=True, parents=True)

        # Step 4: Use the abstracted helper for clean, declarative generation.
        self._generate_component("cilium", cluster_config, infra_path)
        self._generate_component("metallb", cluster_config, infra_path)

    # Step 4: Create a private helper to handle the repetitive generation pattern.
    def _generate_component(self, name: str, cluster_config: ClusterConfig, infra_path: Path) -> None:
        """Generates a single infrastructure component's Helm chart."""
        component_path = infra_path / name
        component_path.mkdir(exist_ok=True)

        values = self._get_component_values(name, cluster_config)

        self._write_helm_chart(
            chart_path=component_path,
            chart_name=name,
            values=values
        )

    def _get_component_values(self, name: str, cluster_config: ClusterConfig) -> Dict[str, Any]:
        """Calculates the final values.yaml content for a given component."""
        values: Dict[str, Any] = {}

        # Apply size-based resources if the component requires them.
        if name == "cilium":
            values = self._get_resource_values_for_size(cluster_config.size)
            if not self.use_vms:
                values.update({
                    "hostNetwork": True,
                    "kubeProxyReplacement": "strict"
                })
        
        elif name == "metallb":
            values = {
                "configInline": {
                    "address-pools": [{
                        "name": "default",
                        "protocol": "layer2",
                        "addresses": [f"{self.ip_pool_start}-{self.ip_pool_end}"]
                    }]
                }
            }

        return values

    def _write_helm_chart(self, chart_path: Path, chart_name: str, values: Dict[str, Any]) -> None:
        """
        Writes the Chart.yaml and values.yaml files for a component.

        Note: This method now gets all required info from the centralized config.
        """
        chart_info = self._CHART_CONFIG[chart_name]

        # Chart.yaml
        chart_yaml = {
            "apiVersion": "v2",
            "name": chart_path.name,
            "version": "0.1.0",
            "dependencies": [{
                "name": chart_name,
                "version": chart_info["version"],
                "repository": chart_info["repository"]  # Step 3: Repository is now co-located with config.
            }]
        }
        (chart_path / "Chart.yaml").write_text(yaml.dump(chart_yaml, default_flow_style=False))

        # values.yaml
        (chart_path / "values.yaml").write_text(yaml.dump(values, default_flow_style=False))

    # Step 5: This method is now static as it does not depend on instance state.
    @staticmethod
    def _get_resource_values_for_size(size: ClusterSize) -> Dict[str, Any]:
        """Returns a dictionary of resource values based on the cluster size."""
        size_configs = {
            ClusterSize.MINIMAL: {"replicas": 1, "resources": {"cpu": "100m", "memory": "128Mi"}},
            ClusterSize.SMALL: {"replicas": 2, "resources": {"cpu": "200m", "memory": "256Mi"}},
            ClusterSize.MEDIUM: {"replicas": 3, "resources": {"cpu": "500m", "memory": "512Mi"}},
            ClusterSize.LARGE: {"replicas": 5, "resources": {"cpu": "1", "memory": "1Gi"}}
        }
        # Default to SMALL if an unknown size is provided, ensuring stable behavior.
        return size_configs.get(size, size_configs[ClusterSize.SMALL])
