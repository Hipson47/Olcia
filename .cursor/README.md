# Olcia - Cursor MCP+RAG Agent

Inteligentny agent Cursor z RAG (Retrieval-Augmented Generation) i MCP (Model Context Protocol).

## 🚀 Szybki Start

### 1. Sklonuj repozytorium
```bash
git clone https://github.com/Hipson47/Olcia.git
cd Olcia
```

### 2. Zainstaluj zależności
```bash
# Użyj Poetry (zalecane)
poetry install

# LUB użyj pip
pip install -r requirements.txt
```

### 3. Skonfiguruj klucze API
```bash
# Skopiuj szablon i uzupełnij klucze
cp .env.example .env
```

Następnie edytuj `.env` w głównym katalogu projektu i uzupełnij:
- `OPENAI_API_KEY` - twój klucz OpenAI
- `ANTHROPIC_API_KEY` - twój klucz Anthropic

### 4. Uruchom Cursor
Otwórz projekt w Cursor - MCP server zostanie automatycznie uruchomiony!

## 🛠️ Dostępne Narzędzia MCP

Użyj `@cursor-agent` w promptach, aby uzyskać dostęp do:

- **`search_knowledge`** - Wyszukaj w bazie wiedzy projektu
- **`add_knowledge`** - Dodaj nową wiedzę do bazy
- **`search_memory`** - Przeszukaj pamięć konwersacji
- **`add_memory`** - Zapisz ważne informacje w pamięci
- **`route`** - Deleguj zadania do wyspecjalizowanych agentów
- **`memory.log`** - Loguj błędy i problemy

## 📁 Struktura Projektu

```
.cursor/
├── mcp/                    # MCP Server
│   ├── server.py          # Główny serwer MCP
│   ├── memory.py          # System pamięci
│   ├── orchestrator.py    # Orkiestracja agentów
│   └── rag.py             # RAG system
├── knowledge/             # Baza wiedzy (PDF, MD, TXT)
├── rules/                 # Reguły i zasady agentów
├── cursor_prompts/        # Gotowe prompty
├── mcp.json              # Konfiguracja MCP
└── pyproject.toml        # Zależności projektu
```

## 🔧 Konfiguracja MCP

Plik `.cursor/mcp.json` jest już skonfigurowany i działa out-of-the-box:

```json
{
  "mcpServers": {
    "cursor-agent": {
      "command": "python",
      "args": [".cursor/mcp/server.py"]
    }
  }
}
```

## 📚 Dodawanie Wiedzy

Umieść pliki w katalogu `.cursor/knowledge/`:
- **PDF** - dokumentacja techniczna
- **Markdown** - notatki, plany
- **TXT** - proste teksty

RAG system automatycznie zindeksuje je dla wyszukiwania semantycznego.

## 🤝 Współpraca Zespołowa

### Dla nowych developerów:
1. Sklonuj repo
2. Zainstaluj zależności: `poetry install`
3. Skopiuj `.env.example` → `.env`
4. Uzupełnij klucze API w `.env`
5. Otwórz w Cursor i zacznij pracę!

### Dla maintainerów:
- **NIE commituj** pliku `.env` z kluczami API (tylko `.env.example`)
- **Dodawaj** wiedzę do `.cursor/knowledge/`
- **Aktualizuj** prompty w `.cursor/cursor_prompts/`
- **Dokumentuj** zmiany w `.cursor/rules/`

## 🐛 Rozwiązywanie Problemów

### MCP nie działa (czerwona ikona)
1. Sprawdź czy Python jest w PATH
2. Zainstaluj zależności: `poetry install`
3. Zrestartuj Cursor
4. Sprawdź logi w konsoli Cursor

### Brak klucza API
```
Error: OPENAI_API_KEY not found
```
→ Uzupełnij `.env` w głównym katalogu kluczami API

### Import errors
```
ModuleNotFoundError: No module named 'chromadb'
```
→ Zainstaluj zależności: `poetry install`

## 📖 Dokumentacja

- [MCP Protocol](https://modelcontextprotocol.io/)
- [ChromaDB](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)

## 📝 Licencja

MIT License - zobacz [LICENSE](../LICENSE)

## 🙋 Wsparcie

Jeśli masz problemy:
1. Sprawdź [Issues](https://github.com/yourusername/Olcia/issues)
2. Przeczytaj dokumentację MCP
3. Utwórz nowy Issue z opisem problemu

