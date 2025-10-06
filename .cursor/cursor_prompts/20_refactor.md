<<<<<<< HEAD
# Enterprise Code Refactoring (Safe Editing Protocol)

Perform production-grade code refactoring with zero functional changes, comprehensive testing, and enterprise-grade quality assurance using Composer mode and safe editing practices.

## Refactoring Specification (Zero-Functional-Change Contract)

**Refactoring Target:** [Precise code scope - function/class/module boundaries]

**Refactoring Objectives:** [Performance/Readability/Maintainability/Architecture goals with measurable metrics]

**Business Impact:** [Quantifiable benefits: performance improvement %, maintainability score increase]

**Risk Assessment:** [Critical/Medium/Low - based on code complexity and usage patterns]

## Safe Editing Protocol (Zero-Tolerance for Regressions)
=======
# Code Refactoring (OLCIA)

Refactor to improve clarity and maintainability, preserving behavior, with automatic RAG context and quality control.

## Plan (6 steps)

1) 🔍 Context: `auto_context_search(task_type="refactor")` + `analyze_project_context("patterns")`
2) 🗺️ Scope: minimal diff, no public API changes
3) 🛠️ Incremental changes, clear names, early returns, avoid unnecessary try/except
4) 🧪 Tests: establish baseline, then iterate on target tests
5) 💡 `suggest_improvements` – ensure security/maintainability/performance
6) 📝 `memory.log` + `add_knowledge` – capture patterns and lessons

## Acceptance criteria

- No behavior change; tests pass
- Readability/maintainability improved
- Lint/type/tests green
- Patterns documented in KB

## Commands
>>>>>>> fec084309b53ab95eb9c5ffa65d7e600bc0a616a

### Pre-Refactoring Baseline Establishment
```bash
<<<<<<< HEAD
# Establish immutable baseline
git checkout -b refactor/[target]
poetry run python -m pytest tests/ --cov=. --cov-report=html -v > baseline_test_results.txt
poetry run python -c "import memory_profiler; memory_profiler.profile_function([target_function])" > baseline_performance.txt
```

### Context Scoping & Planning
```bash
# RAG-enhanced planning
@cursor-agent search_knowledge "refactoring patterns for [pattern_type]"
@cursor-agent search_memory "similar refactoring challenges"
@file:target_module.py @folder:tests @symbol:public_interfaces

# Impact analysis
@cursor-agent route "refactoring complexity assessment"
```

### Dependency Analysis (Composer Mode Preparation)
- **Import Dependencies**: Map all modules importing target code
- **Interface Contracts**: Document all public APIs and contracts
- **Test Coverage**: Identify tests covering refactored functionality
- **Integration Points**: Map external system interactions

## Implementation Protocol (Composer Mode + Safe Editing)

### Phase 1: Analysis & Design (Planning Phase)
1. **Code Metrics Baseline**: Cyclomatic complexity, maintainability index, duplication metrics
2. **Dependency Graph**: Complete call graph and data flow analysis
3. **Test Coverage Analysis**: Identify gaps and high-risk areas
4. **Performance Profiling**: Establish current performance baselines

### Phase 2: Incremental Refactoring (Execution Phase)
1. **Composer Mode Execution**: Use for multi-file dependency-aware changes
2. **Minimal Diff Principle**: Changes < 5 lines per file, incremental commits
3. **Continuous Validation**: Test after each atomic change
4. **Safe Rollback Points**: Git commits after each validated step

### Phase 3: Validation & Optimization (Quality Assurance)
1. **Behavioral Verification**: 100% test pass rate, no functional regressions
2. **Performance Validation**: Meet or exceed baseline performance metrics
3. **Code Quality Gates**: All linting, type checking, and complexity checks
4. **Integration Testing**: Full system validation including external dependencies

## Enterprise Quality Gates (Zero Functional Change)

### Code Quality Assurance
- ✅ **Behavioral Preservation**: `pytest tests/ --strict-markers` - Zero test failures
- ✅ **Type Safety**: `mypy . --strict` - All type checks passing
- ✅ **Code Standards**: `ruff check . --fix` - Enterprise formatting
- ✅ **Security Scan**: `safety check` - No new vulnerabilities introduced

### Performance & Scalability
- ✅ **Performance Baseline**: Meet or improve established SLAs
- ✅ **Memory Usage**: No memory leaks or significant increases
- ✅ **Resource Efficiency**: CPU and I/O usage within acceptable ranges
- ✅ **Scalability Impact**: No degradation under load

### Operational Excellence
- ✅ **Monitoring**: All metrics and logging preserved/enhanced
- ✅ **Documentation**: Updated inline docs and architectural documentation
- ✅ **Deployment**: Zero-downtime deployment capability maintained
- ✅ **Rollback**: Automated rollback procedures tested and working

## Advanced Refactoring Commands

```bash
# Phase 1: Baseline & Analysis
poetry run python -m pytest tests/ --cov=refactored_module --cov-report=term-missing
poetry run mypy refactored_module.py --strict
poetry run radon cc refactored_module.py  # Complexity analysis

# Phase 2: Incremental Refactoring
poetry run python -m pytest tests/test_refactored.py -v  # After each change
poetry run ruff check refactored_module.py  # Style validation
git add -p  # Selective staging for minimal diffs

# Phase 3: Comprehensive Validation
poetry run python -m pytest tests/ --cov=. --cov-fail-under=95
poetry run mypy . --strict
poetry run safety check
docker build -t refactor-validation .
docker run --rm refactor-validation python -m pytest tests/e2e/ -v

# Performance Validation
poetry run python -c "import cProfile; cProfile.run('target_function()')" > performance_profile.txt
```

## Refactoring Patterns & Techniques

### Performance Optimization Patterns
```python
# Before: Inefficient list comprehension
result = [expensive_operation(x) for x in large_list if condition(x)]

# After: Optimized with early exit and batching
def optimized_process(items):
    results = []
    for batch in batch_items(items, batch_size=100):
        filtered_batch = [x for x in batch if condition(x)]
        if not filtered_batch:
            continue
        batch_results = [expensive_operation(x) for x in filtered_batch]
        results.extend(batch_results)
    return results
```

### Maintainability Improvements
```python
# Before: Large function with multiple responsibilities
def process_data(data, config, logger):
    # Validation logic
    # Processing logic
    # Storage logic
    # Error handling

# After: Single Responsibility Principle
class DataProcessor:
    def __init__(self, config: ProcessingConfig, logger: Logger):
        self.config = config
        self.logger = logger
        self.validator = DataValidator(config)
        self.storage = DataStorage(config)

    def process(self, data: DataFrame) -> ProcessingResult:
        validated_data = self.validator.validate(data)
        processed_data = self._apply_business_logic(validated_data)
        return self.storage.store(processed_data)
```

## Success Metrics & Validation

### Quantitative Metrics
- **Cyclomatic Complexity**: Reduction by X% (target: < 10 per function)
- **Maintainability Index**: Improvement by Y points (target: > 75)
- **Test Coverage**: Maintained > 95% with improved assertion quality
- **Performance**: P95 latency improvement or maintained within 5% variance

### Qualitative Improvements
- **Code Readability**: Improved variable naming and structure
- **Documentation**: Comprehensive docstrings and architectural docs
- **Error Handling**: Robust error handling with proper logging
- **Type Safety**: Complete type annotations with generic support

## Enterprise Refactoring Notes

- **Zero Downtime**: All refactoring supports live system operation
- **Gradual Rollout**: Feature flags for complex refactoring deployment
- **Monitoring Integration**: Enhanced metrics and alerting post-refactoring
- **Knowledge Capture**: Document patterns and lessons for future refactoring
- **Team Alignment**: Peer review and architectural review for complex changes
- **Compliance Preservation**: Maintain all security and regulatory compliance

## Rollback Strategy

### Automated Rollback
```bash
# Immediate rollback on validation failure
git reset --hard HEAD~1
poetry run python -m pytest tests/  # Verify rollback success
```

### Gradual Rollback (Feature Flags)
```python
# Feature flag controlled refactoring
if feature_flags.is_enabled('refactored_implementation'):
    return refactored_function()
else:
    return original_function()
```

## Documentation & Knowledge Capture

- **Refactoring Rationale**: Detailed documentation of why and how changes were made
- **Pattern Library**: Add successful patterns to project knowledge base
- **Lessons Learned**: Update team memory with refactoring insights
- **Future Guidelines**: Establish patterns for similar future refactoring tasks
=======
# Baseline
pytest -v --tb=short
ruff check .
mypy . --strict

# RAG context
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"auto_context_search","arguments":{"task_description":"[refactor area]","task_type":"refactor"}}}' | python .cursor/mcp/server.py

echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"analyze_project_context","arguments":{"analysis_type":"patterns"}}}' | python .cursor/mcp/server.py

# Review after changes
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"suggest_improvements","arguments":{"code":"<CHANGED_CODE>","focus_areas":["maintainability","security","performance"]}}}' | python .cursor/mcp/server.py
```

## Tips

- Do not expand scope — aim for minimal diff
- Apply user preferences (`track_user_preferences`) for coding style
>>>>>>> fec084309b53ab95eb9c5ffa65d7e600bc0a616a
