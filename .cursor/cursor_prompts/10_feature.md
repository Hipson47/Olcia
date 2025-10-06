<<<<<<< HEAD
# Enterprise Feature Development (TDD + Safe Editing Protocol)

Implement production-grade features using Test-Driven Development with comprehensive validation, security auditing, and enterprise-grade quality assurance.

## Feature Specification (TDD-First Approach)

**Feature Description:** [Precise behavioral specification with acceptance criteria]

**Business Value:** [Quantifiable impact and success metrics]

**Security/Compliance Requirements:** [GDPR, SOC 2, or other compliance needs]

## Context Scoping & Planning
=======
# Feature Implementation (OLCIA)

Add a new feature leveraging MCP+RAG and the assistant’s automatic tools.

## Plan (8 steps)

1) 🔍 `auto_context_search` – gather context (similar implementations, best practices, lessons)
2) 🧠 `track_user_preferences(retrieve, ...)` – align with user style
3) 🏗️ Implement – minimal diff, types, validation
4) 💡 `suggest_improvements` – code review (security/perf/maint/testing)
5) 🧪 Tests – unit + integration
6) 📚 Docs – README + KB (`add_knowledge` for patterns)
7) 🔁 E2E with MCP – `tools/list`, `tools/call`
8) ✅ Quality gates – ruff, mypy, pytest

## Acceptance criteria

- Requirements implemented with no regressions
- Quality gates pass
- MCP tools used (at least `auto_context_search` + `suggest_improvements`)
- Patterns added to KB; preferences updated; `memory.log` filled

## Commands
>>>>>>> fec084309b53ab95eb9c5ffa65d7e600bc0a616a

### Knowledge Mining (RAG-Enhanced)
```bash
<<<<<<< HEAD
@cursor-agent search_knowledge "similar feature implementations"
@cursor-agent search_knowledge "security patterns for [domain]"
@cursor-agent search_memory "previous implementation challenges"
=======
# Context for the feature
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"auto_context_search","arguments":{"task_description":"[desc]","task_type":"implement"}}}' | python .cursor/mcp/server.py

# Code review
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"suggest_improvements","arguments":{"code":"<CODE>","focus_areas":["security","maintainability","testing"]}}}' | python .cursor/mcp/server.py

# Preferences
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"track_user_preferences","arguments":{"action":"store","preference_key":"coding_style","preference_value":"clean_code"}}}' | python .cursor/mcp/server.py

# Tests
pytest -v
ruff check .
mypy . --strict
>>>>>>> fec084309b53ab95eb9c5ffa65d7e600bc0a616a
```

### Context Limitation (Token Optimization)
```bash
@file:requirements.md @folder:affected_modules
@symbol:existing_integration_points
@cursor-agent route "feature complexity assessment"
```

<<<<<<< HEAD
### Risk Assessment & Planning
- **Complexity Level**: [Simple/Moderate/Complex/Enterprise]
- **Security Impact**: [None/Low/Medium/High/Critical]
- **Performance Requirements**: [Latency, throughput, resource constraints]
- **Rollback Strategy**: [Automated recovery procedures]

## TDD Implementation Protocol (Red-Green-Refactor)

### Phase 1: Specification (Red Phase)
1. **Behavioral Tests**: Write failing tests defining exact behavior
2. **Contract Tests**: API/interface specifications with error conditions
3. **Integration Tests**: End-to-end scenarios with realistic data
4. **Security Tests**: Authorization, input validation, and attack vectors

### Phase 2: Implementation (Green Phase)
1. **Minimal Code**: Smallest implementation to pass tests
2. **Incremental Validation**: Test after each change (< 5 lines)
3. **Pattern Compliance**: Follow established project patterns
4. **Security-First**: Input validation and secure defaults

### Phase 3: Refinement (Refactor Phase)
1. **Code Quality**: Apply enterprise coding standards
2. **Performance Optimization**: Meet latency and resource targets
3. **Documentation**: Comprehensive inline and API documentation
4. **Security Hardening**: Additional security layers and monitoring

## Enterprise Quality Gates (Zero Tolerance)

### Code Quality Assurance
- ✅ **Security Audit**: `safety check --full-report` - Zero vulnerabilities
- ✅ **Static Analysis**: `ruff check . --fix` - Enterprise standards
- ✅ **Type Safety**: `mypy . --strict` - 100% coverage required
- ✅ **Complexity Metrics**: Maintainability index > 75

### Testing Excellence
- ✅ **Unit Coverage**: `pytest --cov=. --cov-fail-under=95` - Branch coverage
- ✅ **Integration Tests**: Full system validation with realistic scenarios
- ✅ **Performance Tests**: Load testing against SLAs
- ✅ **Security Tests**: Penetration testing and vulnerability scanning

### Operational Readiness
- ✅ **Monitoring**: Metrics, logging, and alerting instrumentation
- ✅ **Documentation**: Auto-generated API docs and runbooks
- ✅ **Deployment**: Infrastructure-as-code validation
- ✅ **Rollback**: Automated recovery procedures tested

## Advanced Implementation Commands

```bash
# Phase 1: TDD Specification (Red)
poetry run python -m pytest tests/test_feature.py -v  # Should fail
poetry run python -m pytest tests/test_security.py -v  # Security tests

# Phase 2: Implementation (Green)
poetry run python -m pytest tests/test_feature.py::test_minimal_implementation -v
poetry run ruff check mcp/feature_module.py  # Incremental quality check

# Phase 3: Refinement (Refactor)
poetry run mypy mcp/feature_module.py --strict
poetry run python -m pytest tests/ --cov=mcp --cov-fail-under=95

# Enterprise Validation
poetry run safety check
docker build -t feature-test .
docker run --rm feature-test python -m pytest tests/e2e/ -v
```

## Security & Compliance Checklist

### Authentication & Authorization
- [ ] Role-based access control implemented
- [ ] API key rotation and secure storage
- [ ] Audit logging for all access attempts
- [ ] Rate limiting and abuse prevention

### Data Protection
- [ ] Input validation and sanitization
- [ ] SQL injection prevention (if applicable)
- [ ] XSS protection in web interfaces
- [ ] Data encryption at rest and in transit

### Operational Security
- [ ] Secure logging (no sensitive data leakage)
- [ ] Error messages don't reveal system information
- [ ] Resource exhaustion protection
- [ ] Secure configuration management

## Performance & Scalability Requirements

### Latency Targets
- **P50**: < 100ms for standard operations
- **P95**: < 500ms for complex operations
- **P99**: < 2s for edge cases

### Resource Constraints
- **Memory**: < 256MB per request baseline
- **CPU**: < 10% average utilization
- **Storage**: Predictable growth patterns
- **Network**: Efficient data transfer protocols

## Monitoring & Observability

### Metrics Collection
```python
# mcp/feature_module.py
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('feature_requests_total', 'Total feature requests')
REQUEST_LATENCY = Histogram('feature_request_duration_seconds', 'Request duration')
ERROR_COUNT = Counter('feature_errors_total', 'Total feature errors')
```

### Logging Standards
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG/INFO/WARNING/ERROR with appropriate detail
- **Security Events**: Dedicated security log stream
- **Performance Metrics**: Request timing and resource usage

## Deployment & Rollback Strategy

### Blue-Green Deployment
```bash
# Zero-downtime deployment with rollback capability
kubectl set image deployment/feature-app feature-app=feature:v2
kubectl rollout status deployment/feature-app
# Automatic rollback on health check failure
```

### Feature Flags
```python
# Gradual rollout with feature flags
if feature_flags.is_enabled('advanced_feature'):
    return advanced_implementation()
else:
    return baseline_implementation()
```

## Success Metrics & Validation

- **Functional Completeness**: 100% acceptance criteria met
- **Performance Targets**: All SLAs achieved and monitored
- **Security Posture**: Zero critical vulnerabilities
- **Code Quality**: All automated quality gates passing
- **Operational Readiness**: Full monitoring and alerting in place
- **Documentation**: Complete user and developer documentation

## Enterprise Notes

- **Security First**: All features must pass security review before implementation
- **Performance Baseline**: Establish and monitor performance from day one
- **Monitoring Integration**: Features must emit proper metrics and logs
- **Documentation Automation**: Generate docs from code and tests
- **Compliance by Design**: Security and compliance built into architecture
- **Scalability Proofing**: Design for 10x growth from initial requirements
=======
- Always start with RAG + memory context
- Treat `suggest_improvements` as automated code review
- Document important decisions in KB (`add_knowledge`) and `memory.log`
>>>>>>> fec084309b53ab95eb9c5ffa65d7e600bc0a616a
