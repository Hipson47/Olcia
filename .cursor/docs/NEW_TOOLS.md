# 🚀 Nowe Narzędzia OLCIA - Dokumentacja

## Przegląd Nowych Możliwości

OLCIA Agent został rozszerzony o 4 nowe inteligentne narzędzia, które automatyzują proces development i zapewniają proaktywne wsparcie dla programistów.

---

## 🔍 1. Auto Context Search

**Nazwa narzędzia:** `auto_context_search`

### Opis
Automatycznie przeszukuje bazę wiedzy przed rozpoczęciem zadania, zwracając podobne implementacje, best practices i lekcje wyniesione z przeszłości.

### Kiedy używać
- **Przed implementacją** nowej funkcjonalności
- **Przed refaktoryzacją** istniejącego kodu
- **Przed debugowaniem** problemu
- **Przed pisaniem testów** dla nowego modułu

### Parametry
```json
{
  "task_description": "Description of the task to implement",
  "task_type": "implement" | "debug" | "refactor" | "test"
}
```

### Przykład użycia
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "auto_context_search",
    "arguments": {
      "task_description": "Instagram webhook handler with message processing",
      "task_type": "implement"
    }
  }
}
```

### Zwracane dane
```json
{
  "similar_implementations": [
    {
      "id": "doc_123",
      "content": "Webhook handler implementation...",
      "relevance_score": 0.89
    }
  ],
  "lessons_learned": [
    {
      "id": "mem_456",
      "content": "Remember to validate webhook signatures...",
      "relevance_score": 0.92
    }
  ],
  "best_practices": [
    {
      "content": "Always use async handlers for webhooks...",
      "relevance_score": 0.85
    }
  ],
  "recommendations": [
    "Start with RAG search for similar implementations",
    "Write tests before/during implementation",
    "Add proper type hints and error handling"
  ]
}
```

### Korzyści
- ✅ **Oszczędność czasu** - Nie musisz szukać podobnych implementacji ręcznie
- ✅ **Unikanie błędów** - Widzisz, jakie problemy wystąpiły wcześniej
- ✅ **Lepsze decyzje** - Decyzje oparte na sprawdzonych wzorcach
- ✅ **Spójność kodu** - Konsystentny styl z resztą projektu

---

## 💡 2. Suggest Improvements

**Nazwa narzędzia:** `suggest_improvements`

### Opis
Analizuje kod i sugeruje ulepszenia w oparciu o bazę wiedzy i best practices. Skupia się na określonych obszarach: performance, security, maintainability, testing.

### Kiedy używać
- **Po napisaniu kodu** - Code review przed commitem
- **Przed refaktoryzacją** - Identyfikacja obszarów do poprawy
- **Przy code review** - Automatyczne sugestie dla zespołu
- **Optymalizacja** - Sprawdzenie performance bottlenecks

### Parametry
```json
{
  "code": "string - kod do analizy",
  "focus_areas": ["performance", "security", "maintainability", "testing"]
}
```

### Przykład użycia
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "suggest_improvements",
    "arguments": {
      "code": "def process_webhook(data):\n    user_id = data['user_id']\n    return db.query(user_id)",
      "focus_areas": ["security", "performance"]
    }
  }
}
```

### Zwracane dane
```json
{
  "suggestions": [
    {
      "area": "security",
      "recommendations": [
        "Validate and sanitize all input data before processing",
        "Use parameterized queries to prevent SQL injection",
        "Implement rate limiting for webhook endpoints"
      ],
      "relevance_scores": [0.92, 0.88, 0.85]
    },
    {
      "area": "performance",
      "recommendations": [
        "Use async database queries for better throughput",
        "Implement connection pooling for database access",
        "Add caching layer for frequently accessed data"
      ],
      "relevance_scores": [0.90, 0.87, 0.83]
    }
  ],
  "analyzed_areas": ["security", "performance"],
  "code_length": 95
}
```

### Korzyści
- ✅ **Automatyczny code review** - Natychmiastowy feedback
- ✅ **Uczenie się best practices** - Ciągłe doskonalenie
- ✅ **Bezpieczeństwo** - Wykrywanie potencjalnych luk
- ✅ **Performance** - Identyfikacja bottlenecks

---

## 🎯 3. Track User Preferences

**Nazwa narzędzia:** `track_user_preferences`

### Opis
Przechowuje i odzyskuje preferencje użytkownika dotyczące stylu kodowania, używanych frameworków, preferowanego języka itp. Agent uczy się Twoich preferencji i adaptuje się do Twojego stylu.

### Kiedy używać
- **Store** - Kiedy chcesz zapisać swoją preferencję
- **Retrieve** - Kiedy chcesz sprawdzić zapisaną preferencję
- **Automatycznie** - Agent sam zapisuje zauważone wzorce

### Parametry
```json
{
  "action": "store" | "retrieve",
  "preference_key": "coding_style | test_framework | language_preference | ...",
  "preference_value": "wartość (tylko dla 'store')"
}
```

### Przykłady użycia

**Zapisanie preferencji:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "track_user_preferences",
    "arguments": {
      "action": "store",
      "preference_key": "test_framework",
      "preference_value": "pytest"
    }
  }
}
```

**Odczyt preferencji:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "track_user_preferences",
    "arguments": {
      "action": "retrieve",
      "preference_key": "test_framework"
    }
  }
}
```

### Zwracane dane

**Store response:**
```json
{
  "ok": true,
  "action": "stored",
  "preference_key": "test_framework",
  "preference_value": "pytest"
}
```

**Retrieve response:**
```json
{
  "ok": true,
  "action": "retrieved",
  "preference_key": "test_framework",
  "preference_value": "User preference: test_framework = pytest",
  "relevance": 0.98
}
```

### Przykładowe preferencje do trackowania
- `coding_style`: "functional", "OOP", "clean_code"
- `test_framework`: "pytest", "unittest", "jest"
- `language_preference`: "polish", "english"
- `documentation_style`: "google", "numpy", "sphinx"
- `error_handling_style`: "explicit", "defensive", "fail-fast"
- `async_preference`: "async/await", "threading", "multiprocessing"

### Korzyści
- ✅ **Personalizacja** - Agent dostosowuje się do Twojego stylu
- ✅ **Spójność** - Konsekwentny styl w całym projekcie
- ✅ **Produktywność** - Mniej decyzji do podejmowania
- ✅ **Uczenie się** - Agent pamięta Twoje wybory

---

## 📊 4. Analyze Project Context

**Nazwa narzędzia:** `analyze_project_context`

### Opis
Analizuje strukturę projektu i dostarcza kontekstowych insightów dotyczących architektury, zależności, wzorców projektowych lub tech stacku.

### Kiedy używać
- **Na początku projektu** - Zrozumienie architektury
- **Przed dużymi zmianami** - Analiza wpływu
- **Code review** - Sprawdzenie zgodności z wzorcami
- **Onboarding** - Wprowadzenie nowych członków zespołu

### Parametry
```json
{
  "analysis_type": "architecture" | "dependencies" | "patterns" | "tech_stack"
}
```

### Przykład użycia
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "analyze_project_context",
    "arguments": {
      "analysis_type": "architecture"
    }
  }
}
```

### Zwracane dane
```json
{
  "analysis_type": "architecture",
  "insights": [
    {
      "insight": "Project follows clean architecture pattern with separation of concerns. Core business logic is isolated from infrastructure...",
      "relevance": 0.91,
      "metadata": {
        "source_file": "architecture_patterns.md",
        "chunk_index": 5
      }
    },
    {
      "insight": "Multi-agent system with LangGraph orchestration. Specialized agents for different domains (general, tests, database)...",
      "relevance": 0.88,
      "metadata": {
        "source_file": "system_design.md",
        "chunk_index": 12
      }
    }
  ],
  "total_findings": 5
}
```

### Typy analiz

**Architecture:**
- Wzorce architektoniczne (MVC, Clean Architecture, Hexagonal)
- Separacja warstw (presentation, business, data)
- Dependency flow i coupling

**Dependencies:**
- Zewnętrzne zależności i ich wersje
- Dependency injection patterns
- Potencjalne circular dependencies

**Patterns:**
- Design patterns w użyciu (Factory, Strategy, Observer)
- Anti-patterns do uniknięcia
- Code smells i technical debt

**Tech Stack:**
- Używane technologie i frameworki
- Wersje i kompatybilność
- Best practices dla stacku

### Korzyści
- ✅ **Szybkie onboarding** - Zrozumienie projektu w minuty
- ✅ **Lepsze decyzje** - Zgodność z architekturą
- ✅ **Quality control** - Wykrywanie odchyleń od standardów
- ✅ **Dokumentacja** - Automatyczny przegląd struktury

---

## 🚀 Workflow z Nowymi Narzędziami

### Przykład 1: Implementacja nowej funkcji

```python
# Krok 1: Auto Context Search
response = await auto_context_search(
    task_description="Instagram webhook handler",
    task_type="implement"
)
# Otrzymujesz: podobne implementacje, best practices, lessons learned

# Krok 2: Implementacja z kontekstem
# ... write code based on context ...

# Krok 3: Suggest Improvements
response = await suggest_improvements(
    code=your_code,
    focus_areas=["security", "performance"]
)
# Otrzymujesz: sugestie poprawy bezpieczeństwa i wydajności

# Krok 4: Track Preference
await track_user_preferences(
    action="store",
    preference_key="webhook_pattern",
    preference_value="async_handler_with_validation"
)
# Agent zapamiętuje Twój preferowany wzorzec
```

### Przykład 2: Code Review

```python
# Krok 1: Analyze Project Context
response = await analyze_project_context(
    analysis_type="patterns"
)
# Sprawdź, czy kod jest zgodny z wzorcami projektu

# Krok 2: Suggest Improvements
response = await suggest_improvements(
    code=code_to_review,
    focus_areas=["maintainability", "testing", "security"]
)
# Otrzymaj szczegółowe sugestie poprawy

# Krok 3: Check User Preferences
response = await track_user_preferences(
    action="retrieve",
    preference_key="coding_style"
)
# Upewnij się, że kod jest zgodny z preferencjami zespołu
```

---

## 📋 Integracja z Istniejącymi Narzędziami

Nowe narzędzia działają w synergii z istniejącymi:

```
auto_context_search → rag.search + search_memory + search_knowledge
suggest_improvements → search_knowledge + best practices
track_user_preferences → add_memory + search_memory
analyze_project_context → search_knowledge + project patterns
```

---

## 🎯 Best Practices

1. **Zawsze używaj `auto_context_search` przed implementacją**
   - Oszczędzisz czas i unikniesz błędów

2. **Regularnie używaj `suggest_improvements`**
   - Najlepiej przed commitem lub podczas code review

3. **Trackuj preferencje konsekwentnie**
   - Agent będzie lepiej rozumiał Twój styl

4. **Analizuj kontekst projektu przed dużymi zmianami**
   - Upewnij się, że zmiany są zgodne z architekturą

5. **Kombinuj narzędzia**
   - Najlepsze rezultaty daje użycie wielu narzędzi razem

---

## 🔧 Konfiguracja

Narzędzia działają od razu po restarcie MCP servera. Nie wymagają dodatkowej konfiguracji.

```bash
# Restart MCP server
python .cursor/mcp/server.py
```

---

## 📈 Monitoring

Wszystkie wywołania narzędzi są:
- ✅ Rate-limited (120 req/min)
- ✅ Logowane dla analytics
- ✅ Monitorowane pod kątem performance
- ✅ Zabezpieczone przed nadużyciami

---

## 🆘 Troubleshooting

**Problem:** Narzędzie zwraca puste wyniki
- **Rozwiązanie:** Dodaj więcej wiedzy do knowledge base przez `rag.ingest`

**Problem:** Sugestie nie są relevantne
- **Rozwiązanie:** Użyj bardziej szczegółowego opisu zadania

**Problem:** Preferencje się nie zapisują
- **Rozwiązanie:** Sprawdź czy ChromaDB jest poprawnie skonfigurowane

---

Ciesz się nowymi możliwościami OLCIA! 🚀

