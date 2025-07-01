from typing import Dict, List
from cluster_snek.config.schema import ClusterConfig

class IAMGenerator:
    """Handles Cerbos authorization engine integration."""

    def generate(self, clusters: list[ClusterConfig]) -> dict: # Using modern list[T] type hint
        """Generate Cerbos configuration."""
        # ... (paste the body of the old generate_cerbos_config method here) ...
        return {
            "cerbos": {
                # ... cerbos config ...
            }
        }
