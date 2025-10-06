# 🚀 Setup Guide - Olcia MCP+RAG

## Dla Nowych Developerów

Ten przewodnik pokazuje jak uruchomić projekt **krok po kroku** w prosty sposób.

---

## 📋 Wymagania

- **Python 3.11+** 
- **Poetry** (opcjonalnie, ale zalecane)
- **Cursor IDE**
- Klucze API: OpenAI lub Anthropic

---

## 🔧 Krok 1: Sklonuj Repozytorium

```bash
git clone https://github.com/yourusername/Olcia.git
cd Olcia
```

---

## 📦 Krok 2: Zainstaluj Zależności

### Opcja A: Poetry (zalecane)
```bash
poetry install
```

### Opcja B: pip
```bash
pip install -r .cursor/requirements.txt
```

---

## 🔑 Krok 3: Skonfiguruj Klucze API

### 1. Skopiuj szablon
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### 2. Uzupełnij klucze API

Edytuj plik `.env` w głównym katalogu projektu:

```bash
# Minimum jeden klucz jest wymagany:

# OpenAI (GPT-4, GPT-4o)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Opcjonalnie: wybierz model (domyślnie gpt-4o-mini)
AI_AGENT_MODEL=gpt-4o-mini
```

### Gdzie zdobyć klucze?

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys

---

## 🎯 Krok 4: Otwórz w Cursor

```bash
cursor .
```

MCP server powinien **automatycznie się uruchomić**!

---

## ✅ Weryfikacja Instalacji

### 1. Sprawdź status MCP
- Otwórz Cursor
- Sprawdź dolny pasek - powinieneś zobaczyć **zieloną ikonę MCP**
- Jeśli ikona jest **czerwona**, zobacz sekcję "Rozwiązywanie Problemów"

### 2. Przetestuj narzędzia MCP

W promptach Cursor użyj:
```
@cursor-agent search "python best practices"
```

Jeśli działa, zobaczysz wyniki wyszukiwania z bazy wiedzy!

---

## 🐛 Rozwiązywanie Problemów

### Problem 1: MCP ikona czerwona ❌

**Przyczyny:**
1. Brak zainstalowanych zależności
2. Brak klucza API w `.cursor/.env`
3. Python nie jest w PATH

**Rozwiązanie:**
```bash
# 1. Zainstaluj zależności ponownie
poetry install

# 2. Sprawdź czy .env istnieje w głównym katalogu
ls .env

# 3. Sprawdź Python
python --version  # powinno pokazać 3.11+

# 4. Restartuj Cursor
```

---

### Problem 2: `ModuleNotFoundError`

```
ModuleNotFoundError: No module named 'chromadb'
```

**Rozwiązanie:**
```bash
# Zainstaluj wszystkie zależności
poetry install

# LUB
pip install chromadb sentence-transformers
```

---

### Problem 3: Brak klucza API

```
Error: OPENAI_API_KEY not found
```

**Rozwiązanie:**
1. Upewnij się, że plik `.env` istnieje w głównym katalogu projektu
2. Uzupełnij `OPENAI_API_KEY` lub `ANTHROPIC_API_KEY`
3. **Nie** usuwaj cudzysłowów, jeśli są
4. Restartuj Cursor

---

### Problem 4: Ścieżki względne nie działają

Jeśli `mcp.json` pokazuje błędy, możesz użyć **pełnych ścieżek**:

```json
{
  "mcpServers": {
    "cursor-agent": {
      "command": "python",
      "args": ["C:\\PEŁNA\\ŚCIEŻKA\\DO\\Olcia\\.cursor\\mcp\\server.py"]
    }
  }
}
```

Zastąp `C:\\PEŁNA\\ŚCIEŻKA\\DO\\Olcia` swoją ścieżką projektu.

---

## 📚 Dodawanie Własnej Wiedzy

Umieść pliki w `.cursor/knowledge/`:

```
.cursor/knowledge/
├── project_documentation.pdf
├── api_reference.md
└── best_practices.txt
```

RAG automatycznie zindeksuje te pliki!

---

## 🤝 Współpraca Zespołowa

### Dla wszystkich developerów:

✅ **Commituj:**
- `.cursor/mcp.json` (konfiguracja MCP)
- `.env.example` (szablon z przykładowymi kluczami)
- `.cursor/knowledge/` (wiedza projektu)
- `.cursor/rules/` (zasady agentów)

❌ **NIE commituj:**
- `.env` (zawiera prawdziwe klucze API!)
- `.cursor/test_mcp.py` (plik testowy)
- `__pycache__/` i `*.pyc`

---

## 🎉 Gotowe!

Teraz możesz używać Olcia w Cursor:

```
@cursor-agent search "jak dodać nową funkcję?"
@cursor-agent route "napisz testy dla user.py"
```

---

## 📖 Więcej Informacji

- **README**: `.cursor/README.md`
- **MCP Docs**: https://modelcontextprotocol.io/
- **Issues**: https://github.com/yourusername/Olcia/issues

---

**Powodzenia! 🚀**

