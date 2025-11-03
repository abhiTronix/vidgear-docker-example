# Contributing to VidGear Docker Streamer

First off, thank you for considering contributing to VidGear Docker Streamer! It's people like you that make this project great.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Configure with '...'
2. Run command '....'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Environment:**
 - OS: [e.g., Ubuntu 22.04]
 - Docker Version: [e.g., 24.0.5]
 - VidGear Version: [e.g., 0.3.2]

**Logs**
```
Include relevant log output
```

**Additional context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- A detailed description of the proposed functionality
- Explain why this enhancement would be useful
- List any alternatives you've considered

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** if you've added code that should be tested
4. **Ensure the test suite passes** (`make test`)
5. **Update documentation** as needed
6. **Write clear commit messages** following conventional commits
7. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.10+
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Local Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/vidgear-docker-streamer.git
   cd vidgear-docker-streamer
   ```

2. **Set up development environment**

   ```bash
   make dev-setup
   ```

3. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes and test**

   ```bash
   # Run tests
   make test
   
   # Run linting
   make lint
   
   # Format code
   make format
   ```

5. **Build and test Docker image**

   ```bash
   make build
   make run
   ```

## Coding Standards

### Python Code Style

We follow PEP 8 with some modifications:

- **Line length**: Maximum 100 characters
- **Formatting**: Use Black for automatic formatting
- **Linting**: Use Ruff for linting
- **Type hints**: Use type hints where appropriate
- **Docstrings**: Use Google-style docstrings

Example:

```python
def process_video(
    source_url: str,
    output_path: str,
    quality: str = "best"
) -> bool:
    """
    Process a video from the given source URL.
    
    Args:
        source_url: The URL of the video to process
        output_path: Where to save the processed video
        quality: Video quality setting (default: "best")
    
    Returns:
        True if processing was successful, False otherwise
    
    Raises:
        ValueError: If source_url is invalid
        IOError: If output_path is not writable
    """
    # Implementation here
    pass
```

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning (formatting, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Changes to build process or auxiliary tools
- `ci`: Changes to CI configuration files and scripts

**Examples:**

```sh
feat(streamer): add support for HLS streaming

Implement HLS output format with configurable segment duration
and playlist generation.

Closes #123
```

```sh
fix(docker): resolve permission issues with output directory

Change ownership of output directory to vidgear user to fix
permission denied errors when running container.

Fixes #456
```

### Docker Best Practices

- Use multi-stage builds to minimize image size
- Run containers as non-root user
- Use specific versions for base images
- Clean up temporary files in the same layer
- Add labels for better maintainability
- Use .dockerignore to exclude unnecessary files

### Testing

- Write tests for new features
- Maintain test coverage above 80%
- Use meaningful test names that describe what they test
- Mock external dependencies
- Test edge cases and error conditions

**Running Tests:**

```bash
# All tests
make test

# Specific test file
pytest tests/test_streamer.py

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/test_streamer.py::test_specific_function
```

### Documentation

- Update README.md for user-facing changes
- Update CONFIGURATION.md for new environment variables
- Add docstrings to all public functions and classes
- Include examples for new features
- Keep documentation in sync with code

## Release Process

Releases are automated through GitHub Actions:

1. Update version numbers
2. Update CHANGELOG.md
3. Create and push a version tag:

   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

4. GitHub Actions will automatically:
   - Build Docker images
   - Create GitHub release
   - Publish to container registry

## Getting Help

- 📖 Check the [documentation](docs/)
- 💬 Join our [discussions](https://github.com/yourusername/vidgear-docker-streamer/discussions)
- 🐛 Search [existing issues](https://github.com/yourusername/vidgear-docker-streamer/issues)

Thank you for contributing! 🎉
