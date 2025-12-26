# Contributing to AI Knowledge Console

Thank you for your interest in contributing to the AI Knowledge Console! This document provides guidelines and workflows for contributing to the project.

## Table of Contents
- [Ways to Contribute](#ways-to-contribute)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

---

## Ways to Contribute

We welcome contributions in many forms:

- **Bug Reports:** Help us identify and fix issues
- **Feature Requests:** Suggest new capabilities or improvements
- **Code Contributions:** Submit pull requests for bug fixes or features
- **Documentation:** Improve guides, fix typos, add examples
- **Testing:** Write tests to improve coverage
- **Community Support:** Help other users in discussions

---

## Development Workflow

### 1. Fork & Clone

Fork the repository on GitHub, then clone your fork:

```bash
git clone https://github.com/YOUR-USERNAME/ai-knowledge-console.git
cd ai-knowledge-console
```

Add the upstream repository as a remote:

```bash
git remote add upstream https://github.com/firechair/ai-knowledge-console.git
```

### 2. Create a Feature Branch

Create a descriptive branch name:

```bash
git checkout -b feature/amazing-feature
# or
git checkout -b fix/bug-description
# or
git checkout -b docs/improve-readme
```

**Branch Naming Convention:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation improvements
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests

### 3. Set Up Development Environment

**Backend:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**

```bash
cd frontend
npm ci
```

### 4. Make Your Changes

- Follow the [Code Standards](#code-standards) below
- Write or update tests for your changes
- Update documentation as needed
- Commit your changes with clear, descriptive messages

### 5. Run Tests

**Backend Tests:**

```bash
cd backend
pytest
```

**Frontend Tests** (if applicable):

```bash
cd frontend
npm test
```

### 6. Commit Your Changes

Use clear, descriptive commit messages following [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m 'feat: add model download progress tracking'
# or
git commit -m 'fix: resolve WebSocket connection issues in dev mode'
# or
git commit -m 'docs: update API reference for new endpoints'
```

**Commit Message Format:**
```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

### 7. Push to Your Fork

```bash
git push origin feature/amazing-feature
```

### 8. Open a Pull Request

1. Go to the original repository on GitHub
2. Click "Pull Requests" → "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template with:
   - Clear description of changes
   - Related issue numbers (if applicable)
   - Testing performed
   - Screenshots (for UI changes)

---

## Code Standards

### Backend (Python)

**Style Guide:** Follow [PEP 8](https://peps.python.org/pep-0008/)

**Key Requirements:**
- Type hints for all function signatures
- Docstrings for public functions and classes
- Max line length: 120 characters
- Use `async`/`await` for I/O operations

**Example:**

```python
async def process_document(
    file_path: str,
    chunk_size: int = 512
) -> list[dict]:
    """
    Process a document and return text chunks.

    Args:
        file_path: Path to the document file
        chunk_size: Maximum size of each chunk

    Returns:
        List of chunks with metadata

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    # Implementation
    pass
```

**Code Formatting:**

```bash
# Format code
black .

# Check style
flake8 .

# Type check
mypy .
```

### Frontend (JavaScript/React)

**Style Guide:** Follow project's ESLint configuration

**Key Requirements:**
- Use functional components with hooks
- Destructure props explicitly
- Use meaningful variable names
- Prefer const over let; avoid var
- Use template literals for string concatenation

**Example:**

```jsx
import { useState, useEffect } from 'react';

/**
 * DocumentList component displays a list of indexed documents.
 *
 * @param {Object} props
 * @param {Array} props.documents - List of documents
 * @param {Function} props.onDelete - Callback for delete action
 */
export function DocumentList({ documents, onDelete }) {
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    // Effect logic
  }, [documents]);

  return (
    <div className="document-list">
      {documents.map((doc) => (
        <div key={doc.id} className="document-item">
          <span>{doc.filename}</span>
          <button onClick={() => onDelete(doc.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
}
```

**Code Formatting:**

```bash
# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code (if configured)
npm run format
```

### Naming Conventions

**Backend:**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

**Frontend:**
- Files: `PascalCase.jsx` for components, `camelCase.js` for utilities
- Components: `PascalCase`
- Functions/Variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`

---

## Testing Requirements

### Backend Testing

**Required:**
- Unit tests for all new services and utilities
- Integration tests for new API endpoints
- Maintain or improve code coverage

**Test Structure:**

```python
import pytest
from services.my_service import MyService

@pytest.mark.unit
def test_my_service_basic():
    """Test basic functionality of MyService."""
    service = MyService()
    result = service.process("input")
    assert result == "expected_output"

@pytest.mark.unit
@pytest.mark.asyncio
async def test_my_service_async():
    """Test async functionality of MyService."""
    service = MyService()
    result = await service.async_process("input")
    assert isinstance(result, dict)
```

**Integration Test Example:**

```python
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.mark.integration
def test_new_endpoint():
    """Test new API endpoint."""
    response = client.post("/api/my-endpoint", json={"data": "test"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

### Frontend Testing

**Recommended:**
- Component tests for complex UI logic
- Integration tests for critical user flows
- Accessibility tests

**Example (if using React Testing Library):**

```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { DocumentList } from './DocumentList';

test('renders documents and handles delete', () => {
  const mockDelete = jest.fn();
  const documents = [
    { id: '1', filename: 'test.pdf' }
  ];

  render(<DocumentList documents={documents} onDelete={mockDelete} />);

  expect(screen.getByText('test.pdf')).toBeInTheDocument();

  fireEvent.click(screen.getByText('Delete'));
  expect(mockDelete).toHaveBeenCalledWith('1');
});
```

### Running Tests Before Committing

**Backend:**
```bash
cd backend
pytest --cov=. --cov-report=term-missing
```

**Frontend:**
```bash
cd frontend
npm test
```

---

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New code has appropriate test coverage
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow conventional format
- [ ] PR description is clear and complete

### PR Description Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Related Issues
Fixes #123
Related to #456

## How Has This Been Tested?
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing
- Describe test scenarios

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review performed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing
- [ ] Dependent changes merged
```

### Review Process

1. **Automated Checks:** CI/CD runs automatically
   - Backend: Linting, import checks, compilation
   - Frontend: Build validation
   - Tests: All test suites

2. **Code Review:** Maintainers review your changes
   - Provide feedback and suggestions
   - May request changes

3. **Iteration:** Address feedback
   - Push additional commits to your branch
   - No need to create a new PR

4. **Approval:** Once approved, maintainers will merge

### Merge Requirements

- All CI checks passing
- At least one maintainer approval
- No unresolved review comments
- Up to date with main branch

---

## Reporting Bugs

Help us improve by reporting bugs you encounter.

### Before Reporting

1. **Search existing issues:** Check if the bug is already reported
2. **Try latest version:** Ensure you're using the latest release
3. **Reproduce:** Verify the bug is reproducible

### Bug Report Template

Use [GitHub Issues](https://github.com/firechair/ai-knowledge-console/issues/new) and include:

**Title:** Clear, descriptive title

**Description:**
```markdown
## Bug Description
Clear description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Screenshots
If applicable, add screenshots.

## Environment
- OS: [e.g., macOS 13.1, Windows 11, Ubuntu 22.04]
- Python Version: [e.g., 3.11.5]
- Node Version: [e.g., 18.17.0]
- Docker Version: [e.g., 24.0.5]
- Browser: [e.g., Chrome 120, Safari 17]

## Logs
```
Paste relevant logs here
```

## Additional Context
Any other context about the problem.
```

---

## Feature Requests

We welcome ideas for new features!

### Before Requesting

1. **Search discussions:** Check if someone already suggested it
2. **Consider scope:** Is it aligned with project goals?
3. **Think about impact:** How many users would benefit?

### Feature Request Process

1. **Open a Discussion** (preferred for new ideas)
   - Go to [GitHub Discussions](https://github.com/firechair/ai-knowledge-console/discussions)
   - Describe your idea
   - Get community feedback

2. **Or Open an Issue** (for well-defined features)

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature.

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How you envision this feature working.

## Alternatives Considered
Other approaches you've thought about.

## Additional Context
Screenshots, mockups, or examples from other tools.

## Implementation Considerations
Technical aspects to consider (if applicable).
```

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what's best for the project and community

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory remarks
- Personal or political attacks
- Publishing others' private information

### Enforcement

Instances of unacceptable behavior may result in temporary or permanent ban from the project.

---

## Getting Help

- **Documentation:** Check [docs/](.) for guides
- **Discussions:** Ask questions in [GitHub Discussions](https://github.com/firechair/ai-knowledge-console/discussions)
- **Issues:** Search [existing issues](https://github.com/firechair/ai-knowledge-console/issues)
- **Developer Guide:** See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for technical details

---

## Recognition

Contributors are recognized in:
- Release notes and CHANGELOG.md
- GitHub contributors page
- Project README (for significant contributions)

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (GPL v3.0 + Non-Commercial).

---

Thank you for contributing to AI Knowledge Console! Your efforts help make this project better for everyone. 🎉
