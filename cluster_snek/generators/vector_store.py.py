from typing import Dict
from cluster_snek.config.schema import VectorStoreType, ClusterConfig, ClusterSize

class VectorStoreGenerator:
    """Manages vector store configurations."""

    @staticmethod
    def generate(self, store_type: VectorStoreType, cluster_config: ClusterConfig) -> dict:
        """Generate vector store configuration."""
        if store_type == VectorStoreType.DISABLED:
            return {}
        
        base_config = {
            "enabled": True,
            "namespace": "vector-stores",
            "authentication_enabled": True,
            "encryption_enabled": True,
            "monitoring_enabled": True
        }
        
        if store_type == VectorStoreType.WEAVIATE:
            return {
                **base_config,
                "weaviate": {
                    "provider": "weaviate",
                    "replicas": 3 if cluster_config.size != ClusterSize.MINIMAL else 1,
                    "storage_size": "500Gi",
                    "memory_allocation": "32Gi",
                    "config": {
                        "vectorizer_module": "text2vec-transformers",
                        "enable_modules": [
                            "text2vec-transformers",
                            "qna-transformers"
                        ]
                    }
                }
            }
        elif store_type == VectorStoreType.IN_MEMORY:
            return {
                **base_config,
                "chroma": {
                    "provider": "chroma",
                    "deployment_mode": "in-memory",
                    "replicas": 1,
                    "use_case": "rapid-prototyping"
                }
            }
        # Add other vector store types as needed
        
        return base_config
