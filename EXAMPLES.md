# 💡 Usage Examples - Olcia AI Agent

See how Olcia helps in daily programming work.

## 🚀 Task Routing

### API Development
```
@olcia-ai-agent route: "Implement REST API for user management with CRUD operations"

Olcia's Response:
{
  "agent": "general",
  "confidence": 0.91,
  "reasoning": "User management API involves backend development, database design, and REST principles...",
  "steps": [
    "Design API endpoints and data models",
    "Implement authentication middleware",
    "Create database schema and migrations",
    "Build CRUD operations with error handling",
    "Add input validation and sanitization",
    "Write comprehensive tests"
  ]
}
```

### Database Design
```
@olcia-ai-agent route: "Design PostgreSQL schema for e-commerce platform with products, orders, and users"

Olcia's Response:
{
  "agent": "database",
  "confidence": 0.94,
  "reasoning": "E-commerce schema requires understanding of relational design, normalization, and business logic...",
  "steps": [
    "Analyze business requirements and entities",
    "Design normalized table structure",
    "Define relationships and constraints",
    "Plan indexing strategy for performance",
    "Create migration scripts",
    "Design backup and recovery procedures"
  ]
}
```

### Testing Strategy
```
@olcia-ai-agent route: "Create comprehensive test suite for payment processing system with TDD approach"

Olcia's Response:
{
  "agent": "tests",
  "confidence": 0.96,
  "reasoning": "Payment systems require thorough testing, security validation, and TDD methodology...",
  "steps": [
    "Analyze payment flow and edge cases",
    "Set up testing framework and mocking",
    "Write failing tests for payment logic",
    "Implement payment processing with validation",
    "Add security and fraud detection tests",
    "Create integration tests for payment gateways"
  ]
}
```

## 🔍 Knowledge Search

### Microservices Architecture
```
@olcia-ai-agent search: "microservices communication patterns"

Found 3 documents:
1. "Microservices Architecture Guide" (similarity: 0.89)
   - Service mesh patterns
   - Event-driven communication
   - API Gateway design

2. "Distributed Systems Best Practices" (similarity: 0.82)
   - Circuit breaker pattern
   - Saga pattern for transactions
   - Event sourcing

3. "API Design Principles" (similarity: 0.78)
   - REST vs GraphQL
   - Versioning strategies
   - Documentation standards
```

### API Security
```
@olcia-ai-agent search: "JWT token security best practices"

Found 4 documents:
1. "API Security Guidelines" (similarity: 0.92)
   - Token expiration and rotation
   - Secure storage practices
   - CSRF protection

2. "Authentication Patterns" (similarity: 0.88)
   - Refresh token implementation
   - Secure cookie settings
   - Multi-factor authentication

3. "OWASP Security Checklist" (similarity: 0.85)
   - Common JWT vulnerabilities
   - Token replay attacks
   - Key management
```

## 📚 Experience Logging

### After Successful Implementation
```
@olcia-ai-agent log: "JWT authentication implementation successful - used refresh token rotation pattern from OWASP guidelines"

Saved to memory:
- Pattern: JWT with refresh tokens
- Success: High security implementation
- Reference: OWASP API Security
- Confidence: 0.95
```

### After Problem Resolution
```
@olcia-ai-agent log: "Fixed PostgreSQL connection pooling issue - increased max_connections from 20 to 100 for high-traffic API"

Saved to memory:
- Issue: Connection pool exhaustion
- Solution: Increased pool size
- Context: High-traffic REST API
- Performance impact: +300% throughput
```

## 🎯 Advanced Applications

### Code Review
```
@olcia-ai-agent route: "Review this authentication middleware for security vulnerabilities"

Olcia analizuje kod i zwraca:
- Security assessment
- Best practice recommendations
- Potential improvements
- References to security standards
```

### Architekturalne Decyzje
```
@olcia-ai-agent search: "CQRS pattern implementation in Node.js"

Znaleziono dokumenty:
- Command Query Responsibility Segregation
- Event sourcing integration
- Read/write model separation
- Performance optimization patterns
```

### Performance Optimization
```
@olcia-ai-agent route: "Optimize database queries for user dashboard with 10k+ concurrent users"

Olcia proponuje:
- Query optimization strategies
- Indexing recommendations
- Caching patterns
- Database connection pooling
- Monitoring and alerting setup
```

## 💡 Tips for Effective Use

### 1. Be Specific
❌ `@olcia-ai-agent route: "build api"`
✅ `@olcia-ai-agent route: "build REST API for product catalog with search and filtering"`

### 2. Provide Context
❌ `@olcia-ai-agent search: "testing"`
✅ `@olcia-ai-agent search: "unit testing patterns for async Node.js functions"`

### 3. Log Results
After each successful implementation:
```
@olcia-ai-agent log: "Successfully implemented Redis caching for API responses - 5x performance improvement"
```

### 4. Combine Tools
```
1. @olcia-ai-agent route: "implement user auth"     # plan
2. @olcia-ai-agent search: "JWT best practices"     # research
3. implementation...
4. @olcia-ai-agent log: "JWT auth completed"        # learn
```

## 🚀 Real Workflow

### Scenario: New E-commerce Feature

```
1. Architecture: @olcia-ai-agent route: "design product catalog API with search"
2. Research: @olcia-ai-agent search: "elasticsearch integration patterns"
3. Implementation: coding with Olcia's advice
4. Testing: @olcia-ai-agent route: "create integration tests for catalog API"
5. Optimization: @olcia-ai-agent search: "database query optimization"
6. Documentation: @olcia-ai-agent log: "catalog API deployed - handles 1000 req/min"
```

### Scenario: Refactoring Legacy Code

```
1. Analysis: @olcia-ai-agent route: "refactor monolithic user service to microservices"
2. Search: @olcia-ai-agent search: "microservices migration strategies"
3. Planning: @olcia-ai-agent search: "database splitting patterns"
4. Implementation: gradual code splitting
5. Logging: @olcia-ai-agent log: "microservices migration successful - 40% performance gain"
```

## 🎉 Benefits of Using Olcia

- **🔄 Faster Development** - AI suggests best approaches
- **📚 Continuous Learning** - Agent learns from your projects
- **🎯 Better Decisions** - Access to best practices
- **⚡ Efficiency** - Automatic pattern recognition
- **🔒 Security** - Built-in security knowledge

Olcia is not just an AI assistant - it's an intelligent programming partner! 🚀
