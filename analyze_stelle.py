#!/usr/bin/env python3
"""
Stellenanzeigen-Analyzer CLI
============================
Kommandozeilen-Interface für die Analyse von Stellenanzeigen.
Kann auch über Datei-Eingabe oder Pipe verwendet werden.

Verwendung:
  python3 analyze_stelle.py                    # Interaktive Eingabe
  python3 analyze_stelle.py < anzeige.txt      # Aus Datei
  cat anzeige.txt | python3 analyze_stelle.py  # Via Pipe
  python3 analyze_stelle.py --no-llm           # Ohne LLM

Autor: Marcus Moser
Datum: 04.02.2026
"""

import sys
import argparse
from pathlib import Path

# Füge data-Verzeichnis zum Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent / "data"))

from data.bewerbungs_firma import (
    StellenanzeigenAnalyzer,
    print_analysis_report,
    input_stellenanzeige,
    OllamaClient
)


def main():
    parser = argparse.ArgumentParser(
        description="Analysiert Stellenanzeigen und führt Skill-Matching durch."
    )
    parser.add_argument(
        "--no-llm", 
        action="store_true",
        help="Deaktiviert LLM-Analyse (nur Regex)"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Stellenanzeige aus Datei lesen"
    )
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="Analyseergebnis als JSON speichern"
    )
    parser.add_argument(
        "--generate-text", "-g",
        action="store_true",
        help="Generiert Anschreiben-Text mit LLM"
    )
    
    args = parser.parse_args()
    
    print("\n🚀 Stellenanzeigen-Analyzer")
    print("-" * 40)
    
    # Prüfe Ollama
    client = OllamaClient()
    use_llm = not args.no_llm and client.is_available()
    
    if use_llm:
        model = client.get_available_model()
        print(f"✅ Ollama verfügbar (Modell: {model})")
    else:
        if args.no_llm:
            print("ℹ️  LLM deaktiviert per --no-llm")
        else:
            print("⚠️  Ollama nicht verfügbar - nutze nur Regex")
    
    # Stellenanzeige einlesen
    if args.file:
        # Aus Datei
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"❌ Datei nicht gefunden: {filepath}")
            sys.exit(1)
        with open(filepath, 'r', encoding='utf-8') as f:
            stellenanzeige = f.read()
        print(f"📄 Stellenanzeige aus {filepath} geladen")
    elif not sys.stdin.isatty():
        # Via Pipe
        stellenanzeige = sys.stdin.read()
        print("📄 Stellenanzeige via Pipe empfangen")
    else:
        # Interaktive Eingabe
        stellenanzeige = input_stellenanzeige()
    
    if not stellenanzeige.strip():
        print("❌ Keine Stellenanzeige eingegeben!")
        sys.exit(1)
    
    # Analysieren
    analyzer = StellenanzeigenAnalyzer(use_llm=use_llm)
    result = analyzer.analyze(stellenanzeige)
    
    # Bericht ausgeben
    print_analysis_report(result)
    
    # Optional: Speichern
    if args.save:
        analyzer.save_analysis(result)
    
    # Optional: Anschreiben-Text generieren
    if args.generate_text and use_llm:
        print("\n🤖 Generiere Anschreiben-Text...")
        text = analyzer.generate_anschreiben_text(result)
        if text:
            print("\n" + "="*50)
            print("📝 GENERIERTER ABSATZ:")
            print("="*50)
            print(text)
            print("="*50)
        else:
            print("⚠️  Konnte keinen Text generieren")
    
    # Bewerbungsdaten ausgeben
    print("\n📝 Für persoenliche_daten.py BEWERBUNG:")
    print("-" * 40)
    bewerbung = result.to_bewerbung_dict()
    print("BEWERBUNG = {")
    for key, value in bewerbung.items():
        print(f'    "{key}": "{value}",')
    print("}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
