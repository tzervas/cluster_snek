This plan focuses on achieving the modular, single-responsibility structure outlined in your project goals.

### High-Level Summary of Changes

The primary goal is to **decouple the application-specific manifest generation from the GitOps connector logic**. Currently, `engine/generator.py` is doing both. We will split this into a dedicated `generators/` package for applications (Prometheus, Keycloak) and a `connectors/` package for GitOps tools (ArgoCD). We will also formalize the CLI structure.

---

### What to Keep (No Changes Needed)

These files are well-structured and align with the project's goals.

*   `cluster_snek/config/schema.py`: **Keep.** This is the core of your configuration definition and is perfectly placed.
*   `cluster_snek/config/config_loader.py`: **Keep.** This has a single, clear responsibility: loading the configuration file.
*   `cluster_snek/utils/logger.py`: **Keep.** A standard and correct location for utility functions.
*   `cluster_snek/tui/app.py`: **Keep.** The TUI is a distinct component and is correctly isolated.
*   `cluster_snek/security/`: **Keep as a placeholder.** This directory is correctly positioned for future security framework implementation.

---

### What to Relocate / Rename

These changes align the current structure with the terminology and layout in the PDF guide.

1.  **Rename `providers/` to `connectors/`**
    *   **Why:** The PDF guide consistently uses the term `connectors` to describe modules that interface with external GitOps platforms. This aligns the codebase with the documentation.
    *   **Action:** Rename the directory `cluster_snek/providers/` to `cluster_snek/connectors/`.

2.  **Rename `engine/` to `generators/`**
    *   **Why:** The "engine" is currently responsible for *generating* Kubernetes manifests for specific applications. The term `generators` is more descriptive of this function and matches the PDF's "Final State" diagram. This directory will house the logic for building manifests for Prometheus, Keycloak, etc.
    *   **Action:** Rename the directory `cluster_snek/engine/` to `cluster_snek/generators/`.

---

### What to Split (The Core Refactoring)

This is the most critical part of the refactoring. We will break up monolithic files into single-responsibility modules.

#### 1. Split `engine/generator.py` (now `generators/generator.py`)

*   **Problem:** This file currently contains the `ArgoCDGenerator` (a connector) and specific manifest generation logic for Monitoring and Identity (generators).
*   **Action:**
    1.  **Move the ArgoCD logic:**
        *   Cut the entire `ArgoCDGenerator` class from this file.
        *   Create a new file: `cluster_snek/connectors/argocd.py`.
        *   Paste the `ArgoCDGenerator` class into this new file.
        *   **New Responsibility of `connectors/argocd.py`**: Solely to take a list of Kubernetes manifests and a configuration, and wrap them in a valid ArgoCD `Application` manifest.

    2.  **Create a Monitoring Generator:**
        *   Create a new file: `cluster_snek/generators/monitoring.py`.
        *   Create a class `MonitoringGenerator` inside it.
        *   Move all functions and logic related to generating Prometheus, Grafana, and Loki manifests from the old `generator.py` into methods within this `MonitoringGenerator` class (e.g., `generate_prometheus_manifests`, `generate_grafana_manifests`).

    3.  **Create an Identity Generator:**
        *   Create a new file: `cluster_snek/generators/identity.py`.
        *   Create a class `IdentityGenerator` inside it.
        *   Move all functions and logic related to generating Keycloak manifests from the old `generator.py` into methods within this `IdentityGenerator` class.

    4.  **The original `generator.py` should be deleted after its contents are moved.**

#### 2. Refactor `main.py` into a proper CLI structure

*   **Problem:** `main.py` at the project root is acting as the main orchestrator, containing logic for loading config, calling generators, and writing files. This logic belongs in a dedicated CLI command.
*   **Action:**
    1.  **Create the CLI command file:**
        *   Create a new directory: `cluster_snek/cli/commands/`.
        *   Create a new file inside it: `cluster_snek/cli/commands/generate.py`.

    2.  **Move the orchestration logic:**
        *   Cut the core logic from the `main()` function in the root `main.py`. This includes:
            *   Loading the config (`load_config`).
            *   Initializing the generators (`MonitoringGenerator`, `IdentityGenerator`).
            *   Iterating through the config to see which components are enabled.
            *   Calling the `.generate()` methods on the active generators.
            *   Aggregating the generated manifests.
            *   Initializing the `ArgoCDGenerator` connector.
            *   Calling the connector to produce the final ArgoCD manifest.
            *   Writing the output to a file.
        *   Paste this logic into a function within `cluster_snek/cli/commands/generate.py`, decorated with `@click.command()` (or `@typer.command()`). For example: `def generate(...)`.

    3.  **Simplify the root `main.py`:**
        *   The root `main.py` should now become a very simple entrypoint. Its only job is to set up the Click/Typer app and add the commands from the `cli/commands/` directory.

---

### Resulting Structure (Simplified View)

After these changes, your core project structure will look like this, perfectly aligning with the PDF guide:

```
cluster-snek/
├── main.py                     # Lean CLI entrypoint
└── cluster_snek/
    ├── cli/
    │   └── commands/
    │       └── generate.py     # Contains the primary "generate" command logic
    ├── config/
    │   ├── config_loader.py
    │   └── schema.py
    ├── connectors/             # Was 'providers'
    │   ├── argocd.py           # NEW: Contains only the ArgoCDGenerator
    │   └── github.py
    ├── generators/             # Was 'engine'
    │   ├── monitoring.py       # NEW: Contains MonitoringGenerator (Prom, Grafana)
    │   └── identity.py         # NEW: Contains IdentityGenerator (Keycloak)
    ├── security/               # (For future work)
    ├── tui/
    └── utils/
```
