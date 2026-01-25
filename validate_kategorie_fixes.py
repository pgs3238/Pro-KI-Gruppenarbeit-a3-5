#!/usr/bin/env python3
"""
Validierungsskript für Kategorie Foreign-Key Implementierung

Überprüft ob alle Stellen im Code korrekt kategorie_id verwenden
"""

import re
import sys
from pathlib import Path

# Kritische Muster die überprüft werden sollen
PATTERNS = {
    "kategorie_id Nutzung": {
        "should_find": [
            r"txn\.kategorie_id\s*=\s*",  # Richtig: kategorie_id setzen
            r"kategorie_id\s*=\s*None",   # Filter nach unkategorisiert
            r"kategorie_id\s*is\s*not\s*None",  # Filter nach kategorisiert
            r"\.kategorie\.name",         # Kategorienamen laden via Relationship
        ],
        "should_not_find": [
            r"txn\.kategorie\s*=\s*[^i]",  # FALSCH: kategorie direkt setzen (außer kategorie_id)
            r"t\.beschreibung.*kategorie",  # FALSCH: Kategoriewerte aus beschreibung
        ]
    }
}

def check_file(filepath, patterns):
    """Prüft eine Datei gegen die Patterns"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None
    
    results = {}
    
    for pattern_name, pattern_dict in patterns.items():
        results[pattern_name] = {
            "should_find": [],
            "should_not_find": []
        }
        
        # Positiv-Muster (sollten vorhanden sein)
        for pattern in pattern_dict.get("should_find", []):
            if re.search(pattern, content, re.IGNORECASE):
                results[pattern_name]["should_find"].append(f"✓ {pattern}")
        
        # Negativ-Muster (sollten NICHT vorhanden sein)
        for pattern in pattern_dict.get("should_not_find", []):
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                results[pattern_name]["should_not_find"].append(
                    f"✗ {pattern} (Zeile {line_num})"
                )
    
    return results

def main():
    """Hauptfunktion"""
    print("=" * 70)
    print("KATEGORIE FOREIGN-KEY VALIDIERUNG")
    print("=" * 70)
    
    files_to_check = [
        "src/categories/categorizer_rules.py",
        "src/api/main.py",
        "src/api/schemas.py",
        "src/chatbot/tools.py",
        "src/categories/categories.py",
    ]
    
    base_path = Path(".")
    all_passed = True
    
    for file_path in files_to_check:
        full_path = base_path / file_path
        
        if not full_path.exists():
            print(f"\n⚠️  Datei nicht gefunden: {file_path}")
            continue
        
        print(f"\n📄 Überprüfe: {file_path}")
        print("-" * 70)
        
        results = check_file(full_path, PATTERNS)
        
        if results is None:
            print(f"  ✗ Fehler beim Lesen der Datei")
            all_passed = False
            continue
        
        for pattern_name, pattern_results in results.items():
            should_find = pattern_results["should_find"]
            should_not_find = pattern_results["should_not_find"]
            
            if should_find:
                print(f"\n  ✓ Gefundene Patterns:")
                for item in should_find:
                    print(f"    {item}")
            
            if should_not_find:
                print(f"\n  ✗ FEHLERHAFTE Patterns gefunden:")
                for item in should_not_find:
                    print(f"    {item}")
                all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALLE ÜBERPRÜFUNGEN BESTANDEN")
        return 0
    else:
        print("❌ FEHLER GEFUNDEN - Bitte überprüfen")
        return 1

if __name__ == "__main__":
    sys.exit(main())
