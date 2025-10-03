# Test Development & Quality Assurance

Add, improve, or fix tests to ensure code reliability and prevent regressions.

## Scope

**Test Target:** [Specific functionality, module, or area to test]

**Test Type:** [unit, integration, e2e, performance, coverage improvement, fix failing tests]

**Files to create/modify:**
- `tests/test_[target].py` - New or updated test file
- `@tests/conftest.py` - Shared test fixtures if needed
- `@tests/` - Update existing test structure
- `@mcp/server.py` - May need test hooks or mocks

**Files to reference:**
- `@[target_code]` - Code being tested
- `@tests/` - Existing test patterns and fixtures
- `@pytest.ini` or `@pyproject.toml` - Test configuration

## Implementation Plan (7 steps)

1. **Analyze test requirements** - Understand what needs testing and current coverage
2. **Review existing tests** - Check for gaps, flaky tests, or outdated tests
3. **Design test strategy** - Plan test cases, fixtures, and mocking needs
4. **Implement test cases** - Write comprehensive tests with edge cases
5. **Add test fixtures** - Create reusable test setup and teardown
6. **Run and validate** - Execute tests and verify coverage improvements
7. **Document test scenarios** - Update test documentation and README

## Acceptance Criteria

- ✅ **Test Coverage**: Adequate coverage for target functionality (≥80% line coverage)
- ✅ **Test Quality**: Tests are reliable, fast, and not flaky
- ✅ **Edge Cases**: Cover error conditions, boundary values, and unusual inputs
- ✅ **Documentation**: Clear test names and docstrings explaining test intent
- ✅ **CI/CD Ready**: Tests run cleanly in automated environments
- ✅ **No Regressions**: All existing functionality still works
- ✅ **Quality Gates**: pytest passes with no failures or warnings

## Commands to Run

```bash
# Test execution
python -m pytest tests/test_[target].py -v
python -m pytest tests/ -v  # Full test suite
python -m pytest tests/ --cov=. --cov-report=html  # Coverage report

# Test quality checks
python -m pytest tests/ --tb=short  # Quick failure overview
python -m pytest tests/ --durations=10  # Find slow tests
python -m pytest tests/ --lf  # Run only last failed tests

# Specific test debugging
python -m pytest tests/test_[target].py::TestClass::test_method -v -s
python -m pytest tests/test_[target].py -k "keyword"  # Filter by keyword

# Coverage analysis
python -m pytest tests/ --cov=. --cov-report=term-missing
coverage html  # Generate HTML coverage report
```

## Testing Best Practices

**Test Structure:**
- One test class per unit/module
- Test method names describe expected behavior: `test_should_[expected_behavior]`
- Use descriptive assertions with clear failure messages
- Group related tests in classes with `setUp`/`tearDown` methods

**Test Types to Include:**
- **Happy Path**: Normal operation scenarios
- **Edge Cases**: Boundary values, empty inputs, error conditions
- **Error Handling**: Exception scenarios and error messages
- **Integration**: Component interaction and data flow
- **Regression**: Previously broken functionality

**Mocking Strategy:**
- Mock external dependencies (APIs, databases, file systems)
- Use fixtures for reusable test data
- Avoid over-mocking - test real behavior where possible
- Verify mock interactions with `assert_called*` methods

## Notes

- **Test-Driven Development**: Consider writing tests before implementation when adding features
- **Continuous Integration**: Ensure tests run in CI/CD pipeline
- **Performance**: Keep tests fast (< 30 seconds for full suite)
- **Maintenance**: Update tests when refactoring code to match new interfaces
- **Documentation**: Use docstrings to explain complex test scenarios
- **Flaky Tests**: Investigate and fix any intermittent test failures

## Common Test Patterns

```python
# Unit test example
def test_should_calculate_total_correctly(self):
    calculator = Calculator()
    result = calculator.add(2, 3)
    self.assertEqual(result, 5)

# Integration test example
def test_should_ingest_file_successfully(self):
    ingestor = RAGIngestor()
    result = ingestor.ingest_file(Path("test.md"))
    self.assertTrue(result["status"] == "success")

# Mock example
@patch('mcp.server.RAGIngestor')
def test_should_handle_ingestion_error(self, mock_ingestor):
    mock_ingestor.return_value.ingest_file.side_effect = Exception("Disk full")
    # Test error handling logic
```
