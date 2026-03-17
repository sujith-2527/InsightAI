# Contributing to Conversational Dashboard

Thank you for your interest in contributing to the Conversational Dashboard project! Here are guidelines to help you get started.

## Code of Conduct

Please be respectful and inclusive. All contributors are expected to follow basic principles of professionalism and respect.

## How to Contribute

### 1. Report Issues
- Check existing issues first to avoid duplicates
- Provide detailed descriptions of bugs found
- Include steps to reproduce, expected behavior, and actual behavior
- For feature requests, explain the use case and benefits

### 2. Fork and Clone
```bash
git clone https://github.com/your-username/conversational-dashboard.git
cd conversational-dashboard
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 4. Make Changes
- Keep commits atomic and meaningful
- Follow existing code style
- Add tests for new features
- Update documentation as needed

### 5. Test Your Changes
```bash
# Run backend tests
python Backend/test_intelligent.py

# Run integration tests
python Backend/integration_test.py
```

### 6. Submit a Pull Request
- Provide a clear description of changes
- Reference any related issues
- Ensure all tests pass
- Request review from maintainers

## Development Setup

### Prerequisites
- Python 3.11+
- pip package manager

### Installation
```bash
# Install dependencies
pip install fastapi uvicorn pandas

# Run the backend
python Backend/app.py

# Open frontend in browser
start Frontend/index.html
```

## Code Style

### Python
- Follow PEP 8 standards
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and modular

### JavaScript
- Use clear variable names
- Add inline comments for API interactions
- Keep functions under 50 lines when possible
- Use const/let appropriately

## Testing Guidelines

### Adding Tests
- Write tests for new functions
- Test both success and error cases
- Use descriptive test names

### Example Test
```python
def test_parse_query_with_aggregation():
    result = parse_query("What is the average price?")
    assert "aggregation" in result
    assert result["aggregation"] == "mean"
```

## Documentation

Updates to documentation are highly appreciated:
- Fix typos and clarity issues
- Improve examples
- Add troubleshooting guides
- Document new features

## Commit Messages

Use clear commit messages:
```
Good: "Add fuzzy matching for column names in query parser"
Good: "Fix port binding issue on Windows"

Avoid: "Update code"
Avoid: "Fix bug"
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open a discussion or issue for questions. We're happy to help!

---

**Happy Contributing! 🚀**
