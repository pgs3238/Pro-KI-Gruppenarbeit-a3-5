# FINLY Tests

Unit Tests für das FINLY Projekt.

## Struktur

```
tests/
├── __init__.py           # Tests Package
├── conftest.py           # Pytest Fixtures und Konfiguration
├── test_models.py        # Tests für Datenbank-Modelle
└── test_konto_manager.py # Tests für KontoManager
```

## Tests ausführen

### Alle Tests ausführen
```bash
pytest
```

### Tests mit Coverage
```bash
pytest --cov=src --cov-report=html
```

### Nur Datenbank-Tests
```bash
pytest tests/test_models.py tests/test_konto_manager.py
```

### Einzelnen Test ausführen
```bash
pytest tests/test_konto_manager.py::TestKontoManager::test_erstelle_konto
```

### Verbose Mode (detaillierte Ausgabe)
```bash
pytest -v
```

## Fixtures

Die wichtigsten Fixtures sind in `conftest.py` definiert:

- **test_engine**: In-Memory SQLite Datenbank
- **test_session**: Neue Session für jeden Test
- **sample_konto**: Beispiel-Konto
- **sample_category**: Beispiel-Kategorie
- **sample_transaktion**: Beispiel-Transaktion

## Test-Kategorien

### Datenbank-Tests (`test_models.py`)
- Modell-Erstellung und Validierung
- Beziehungen zwischen Modellen
- Unique Constraints
- Default-Werte

### KontoManager-Tests (`test_konto_manager.py`)
- CRUD-Operationen
- Kontostandsberechnung
- IBAN-Suche
- Lösch-Validierung

## Best Practices

1. **Arrange-Act-Assert Pattern**: Jeder Test folgt diesem Muster
2. **Isolierte Tests**: Jeder Test verwendet eigene Session (function scope)
3. **Aussagekräftige Namen**: Test-Namen beschreiben was getestet wird
4. **In-Memory DB**: Tests nutzen SQLite in-memory für Geschwindigkeit

## Requirements

Tests benötigen:
- `pytest>=7.4.0`
- `pytest-cov>=4.1.0`

Installation:
```bash
pip install -r requirements.txt
```
