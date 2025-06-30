# Contributing to Cluster-Snek

Thank you for your interest in contributing to Cluster-Snek! This document provides guidelines and instructions for contributing to the project.

## Development Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/tzervas/cluster-snek.git
cd cluster-snek
```

2. We use Visual Studio Code with Dev Containers for development. Make sure you have:
   - Visual Studio Code installed
   - Docker installed and running
   - Dev Containers extension installed in VS Code

3. Open the project in VS Code and select "Reopen in Container" when prompted.

## Development Standards

### Python Version
- We use Python 3.12 or higher
- All code must include proper type hints
- All functions must have docstring documentation following Google style

### Code Style
- Black formatting is enforced (automatically run on save)
- Flake8 linting is enforced
- MyPy type checking is enforced
- Pre-commit hooks are in place for all of the above

### Testing
- All new features must include unit tests
- Tests are written using pytest
- Run tests with: `pytest`

### Commit Guidelines
- All commits must be signed with GPG
- Use clear, descriptive commit messages
- Follow conventional commits format:
  ```
  type(scope): description
  
  [optional body]
  
  [optional footer]
  ```

## Pull Request Process

1. Create a new branch for your feature/fix
2. Make your changes, following our development standards
3. Write/update tests as needed
4. Update documentation if needed
5. Submit a pull request
6. Ensure all checks pass

## License

By contributing to Cluster-Snek, you agree that your contributions will be licensed under the MIT License.
