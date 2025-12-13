# Contributing to INARA HRIS

Thank you for considering contributing to INARA HRIS! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, browser, versions)

### Suggesting Features

1. Check if the feature has been suggested in Issues
2. Create a new issue with:
   - Clear feature description
   - Use case and benefits
   - Proposed implementation (optional)

### Code Contributions

#### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/your-username/inara-hris.git
cd inara-hris

# Run setup script
chmod +x setup.sh
./setup.sh

# Create a new branch
git checkout -b feature/your-feature-name
```

#### Coding Standards

**Python (Backend):**
- Follow PEP 8
- Use type hints
- Write docstrings for functions/classes
- Keep functions small and focused
- Add unit tests for new features

**TypeScript (Frontend):**
- Follow ESLint rules
- Use TypeScript types
- Write clear component names
- Add comments for complex logic
- Test components

#### Commit Messages

Use conventional commits format:

```
type(scope): brief description

- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance tasks
```

Examples:
```
feat(employees): add employee photo upload
fix(leave): correct leave balance calculation
docs(api): update authentication guide
```

#### Pull Request Process

1. **Before submitting:**
   - Update documentation if needed
   - Add tests for new features
   - Ensure all tests pass
   - Follow code style guidelines

2. **Submit PR:**
   - Use clear title and description
   - Reference related issues
   - Add screenshots for UI changes
   - Request review from maintainers

3. **After submission:**
   - Respond to review comments
   - Make requested changes
   - Keep PR up to date with main branch

#### Code Review Criteria

- Code quality and readability
- Test coverage
- Documentation completeness
- Performance considerations
- Security implications
- Adherence to architecture

## 🏗️ Architecture Guidelines

### Backend

- Keep modules independent
- Use dependency injection
- Follow repository pattern
- Separate business logic from routes
- Use async/await consistently

### Frontend

- Keep components small
- Use React hooks
- Implement proper loading states
- Handle errors gracefully
- Optimize performance

### Database

- Use migrations for schema changes
- Index foreign keys
- Use UUID for primary keys
- Add appropriate constraints

## 🧪 Testing

### Backend Tests

```bash
cd apps/api
pytest
pytest --cov=.
```

### Frontend Tests

```bash
cd apps/frontend
npm test
npm test -- --coverage
```

## 📚 Documentation

- Update README.md for major changes
- Add JSDoc/docstrings to code
- Update API documentation
- Include examples where helpful

## 🔒 Security

- Never commit sensitive data
- Use environment variables
- Follow OWASP guidelines
- Report security issues privately

## 💬 Communication

- Be respectful and professional
- Ask questions when unclear
- Provide constructive feedback
- Help others when possible

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## 🙏 Thank You

Your contributions help make INARA HRIS better for everyone!
