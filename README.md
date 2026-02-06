# Bewerbungsgenerator 🚀
Vollautomatisiertes System zur Erstellung professioneller Bewerbungsunterlagen mit KI-gestützter Stellenanzeigen-Analyse, intelligentem Skill-Matching und QR-Code-Integration für den Lebenslauf.

## 🔒 DSGVO-Konformität & Datenschutz

**100% DSGVO-konform durch lokale Verarbeitung:**
- ✅ **Keine Cloud-Dienste**: Alle Daten bleiben auf deinem Computer
- ✅ **Lokale LLMs**: KI-Analyse erfolgt ausschließlich über Ollama (lokal installiert)
- ✅ **Keine Datenweitergabe**: Keinerlei personenbezogene Daten werden an Dritte übertragen
- ✅ **Offline-Fähig**: System funktioniert komplett ohne Internetverbindung
- ✅ **Volle Kontrolle**: Du behältst die absolute Kontrolle über alle deine Bewerbungsdaten

**Repository-Schutz:**
- Sensible Daten (persönliche Informationen, Dokumente, generierte PDFs) werden durch `.gitignore` vom Repository ausgeschlossen
- Nur Code und Templates werden versioniert

## Überblick

Das System analysiert Stellenanzeigen, extrahiert Firmendaten, gleicht Anforderungen mit persönlichen Skills ab und generiert automatisch personalisierte PDF-Bewerbungen (Anschreiben + Lebenslauf) mit LLM-generiertem Bewerbungstext. Optional kann ein QR-Code zur persönlichen Website in das Anschreiben integriert werden.

### Kernfunktionen ✨

- **Hybrid-Extraktion**: Regex + Ollama LLM für maximale Präzision
- **Skill-Matching**: Automatischer Abgleich von 77+ Skills mit Stellenanforderungen
- **LLM-Textgenerierung**: Personalisierte Anschreiben-Texte mit Ollama Mistral 7B (bessere deutsche Grammatik)
- **QR-Code-Integration**: Automatische Generierung und Einbindung von QR-Codes im Lebenslauf zur persönlichen Website
- **Intelligente Formatierung**: Automatische Anrede-Erkennung und -Bereinigung
- **Dynamische Dateinamen**: PDFs mit Name und Generierungsdatum (z.B. `Anschreiben_Max_Mustermann_20260206.pdf`)
- **PDF-Ausgabe**: Professionelle HTML/CSS-Templates mit WeasyPrint
- **Bild-Optimierung**: Automatische Profilbild-Verarbeitung für optimale Darstellung
- **Analyse-Archiv**: Automatische JSON-Speicherung aller Analysen mit Zeitstempel
- **Daten-Extraktion**: Automatisiertes Parsen persönlicher Daten aus Markdown-Dateien

## Installation

### 1. Repository klonen
```bash
git clone <repository-url>
cd BewerbungV1
```

### 2. Python-Umgebung einrichten
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 4. Ollama installieren (optional, aber empfohlen)
Ollama ermöglicht die intelligente LLM-Analyse für bessere Ergebnisse.

```bash
# Ollama von https://ollama.ai/download herunterladen
# Nach Installation:
ollama pull mistral:7b

# Alternativ (kleinere Modelle für schwächere Hardware):
# ollama pull llama3.2:3b
# ollama pull mistral
```

## Quick Start 🚀

### In 3 Schritten zur fertigen Bewerbung:

**1. Stellenanzeige kopieren**
```bash
# Kopiere komplette Stellenanzeige in Datei
nano input/aktuelle_stellenanzeige.txt
# Paste & Save (Strg+O, Strg+X)
```

**2. Analysieren**
```bash
python analyze_stelle.py -f input/aktuelle_stellenanzeige.txt --save
# Zeigt Skill-Match und speichert JSON
```

**3. PDFs generieren**
```bash
python generator.py
# Fertig! PDFs in output/ mit LLM-generiertem Text
```

**Ergebnis:**
- `output/Anschreiben_Vorname_Nachname_20260206.pdf`
- `output/Lebenslauf_Vorname_Nachname_20260206.pdf`

## Verzeichnisstruktur

```
BewerbungV1/
├── input/                          # Eingabedateien
│   └── aktuelle_stellenanzeige.txt # Hier Stellenanzeige einfügen
├── output/                         # Generierte PDFs
│   ├── analysen/                   # JSON-Analysen (Archiv)
│   ├── Anschreiben_*.pdf
│   └── Lebenslauf_*.pdf
├── templates/                      # HTML/CSS-Templates
│   ├── anschreiben.html
│   ├── lebenslauf.html
│   ├── styles.css
│   ├── profilbild.jpg              # Optimiertes Bewerbungsfoto
│   └── qr_code.png                 # QR-Code für Website (generiert)
├── images/                         # Bild-Ressourcen
│   ├── profilbild.jpg              # Optimiertes Bewerbungsfoto
│   ├── qr_code.png                 # QR-Code für Website
│   └── icons/                      # Optionale Icons
├── data/                           # Datenmodule
│   ├── persoenliche_daten.py       # Persönliche Daten & Skills (autogeneriert)
│   └── bewerbungs_firma.py         # Analyse-Engine
├── personal_documents/             # Persönliche Dokumente
│   ├── meine_daten.md              # Master-Datei für persönliche Daten
│   ├── ausbildung/                 # Ausbildungsnachweise
│   ├── lebenslauf/                 # Lebenslauf-Versionen
│   ├── projekte/                   # Projektbeschreibungen
│   │   └── eigene_projekte.json    # Projektdetails
│   ├── weiterbildungen/            # Weiterbildungszertifikate
│   ├── zertifikate/                # Zertifikate
│   └── zeugnisse/                  # Arbeitszeugnisse
├── generator.py                    # PDF-Generator (Hauptprogramm)
├── analyze_stelle.py               # CLI für Stellenanzeigen-Analyse
├── extract_personal_data.py        # Datenextraktion aus Dokumenten
├── generate_qr_code.py             # QR-Code-Generator
├── optimize_image.py               # Bild-Optimierung für Profilbild
└── requirements.txt
```

## Workflow

### Standard-Ablauf

1. **Stellenanzeige vorbereiten**
   ```bash
   # Kopiere die komplette Stellenanzeige (inkl. Firma, Adresse, Kontakt)
   nano input/aktuelle_stellenanzeige.txt
   ```

2. **Stellenanzeige analysieren**
   ```bash
   python analyze_stelle.py -f input/aktuelle_stellenanzeige.txt --save
   ```
   
   Ausgabe:
   - Extrahierte Firmendaten (Name, Adresse, Ansprechpartner)
   - Stellendaten (Titel, Eintrittsdatum, Arbeitszeit)
   - Anforderungen (Must-Have, Nice-to-Have, Soft Skills)
   - **Skill-Match-Report** (Deckungsgrad in %, Top-Matches)
   - JSON-Export nach `output/analysen/`

3. **PDF-Bewerbung generieren**
   ```bash
   python generator.py
   ```
   
   Generiert automatisch:
   - `output/Anschreiben_Vorname_Nachname_JJJJMMTT.pdf` (personalisiert mit LLM-generiertem Text)
   - `output/Lebenslauf_Vorname_Nachname_JJJJMMTT.pdf` (mit QR-Code zur Website)
   
   **Features:**
   - Lädt automatisch die neueste Stellenanalyse aus `output/analysen/`
   - Generiert personalisierten Anschreiben-Text mit Ollama LLM
   - Nutzt Top-Skill-Matches für optimale Passung
   - Generiert QR-Code aus Website-URL und fügt ihn in den Lebenslauf ein
   - Intelligente Anrede-Logik (Herr/Frau oder "Damen und Herren")
   - Entfernt doppelte Anreden automatisch
   - Dateinamen mit Datum für Nachverfolgbarkeit

### Erweiterte Nutzung

**Nur Analyse ohne Speichern:**
```bash
python analyze_stelle.py -f input/aktuelle_stellenanzeige.txt
```

**Interaktive Eingabe:**
```bash
python analyze_stelle.py
# Füge Text ein, beende mit Strg+D (Linux) / Strg+Z (Windows)
```

**Pipe-Eingabe:**
```bash
cat input/aktuelle_stellenanzeige.txt | python analyze_stelle.py
```

**Ohne LLM (nur Regex):**
```bash
python analyze_stelle.py --no-llm -f input/aktuelle_stellenanzeige.txt
```

**Mit LLM-generiertem Anschreiben-Absatz:**
```bash
python analyze_stelle.py -f input/aktuelle_stellenanzeige.txt --generate-text
```

## Konfiguration

### Persönliche Daten anpassen

**Empfohlene Methode:** Bearbeite `personal_documents/meine_daten.md` und generiere die Python-Datei automatisch:

```bash
python extract_personal_data.py
```

Dies erstellt/aktualisiert automatisch `data/persoenliche_daten.py` mit:
- Persönlichen Daten (Name, Adresse, Kontakt, Links)
- Berufserfahrung
- Ausbildung
- Skills mit Levels
- Zertifikate und Weiterbildungen

**Alternative:** Manuelle Bearbeitung von `data/persoenliche_daten.py`:

```python
PERSOENLICHE_DATEN = {
    "vorname": "Dein Vorname",
    "nachname": "Dein Nachname",
    "email": "deine.email@example.com",
    "website": "https://deine-website.de",
    # ...
}

KENNTNISSE = [
    {"skill": "Python", "level": 4},
    {"skill": "Docker", "level": 3},
    # Füge deine Skills hinzu
]
```

### Templates anpassen

HTML/CSS-Templates in `templates/`:
- `anschreiben.html` - Layout und Platzhalter
- `lebenslauf.html` - Struktur des Lebenslaufs (inkl. QR-Code-Bereich)
- `styles.css` - Styling beider Dokumente
- `profilbild.jpg` - Dein Bewerbungsfoto (wird von `images/` kopiert)
- `qr_code.png` - QR-Code für Website (automatisch generiert, wird in Lebenslauf eingebunden)

Platzhalter werden automatisch ersetzt:
- `{vorname}`, `{nachname}`, `{email}`, etc.
- `{anschreiben_text}` - Dynamisch generierter Text basierend auf Skill-Matching
- QR-Code wird automatisch aus der Website-URL generiert und in den Lebenslauf eingefügt

### Bilder optimieren

**Profilbild:**
```bash
python optimize_image.py
```
Optimiert automatisch das Profilbild aus `images/_S3A4489_3.jpeg` zu `images/profilbild.jpg` (400x400px, optimiert).

**QR-Code:**
```bash
python generate_qr_code.py
```
Generiert QR-Code aus der Website-URL in `personal_documents/meine_daten.md` und speichert ihn in `images/qr_code.png` (2.5cm x 2.5cm, 300 DPI).

## Skill-Matching-System

Das System vergleicht deine Skills (`data/persoenliche_daten.py`) mit den Stellenanforderungen:

### Matching-Algorithmus

1. **Synonyme**: Erkennt Varianten (z.B. "JavaScript" = "JS" = "ECMAScript")
2. **Kategorisierung**: Must-Have vs. Nice-to-Have
3. **Scoring**: Kombination aus Relevanz und persönlichem Skill-Level
4. **Top-Matches**: Die 3 besten Übereinstimmungen für Anschreiben

### Ausgabe

```
✅ Skill-Match: 72.7%
Top-Matches:
  1. Python (4/5) - Must-Have
  2. Docker (3/5) - Nice-to-Have
  3. Git (4/5) - Must-Have

Fehlende Skills:
  - Kubernetes (Nice-to-Have)
  - GraphQL (Nice-to-Have)
```

## Technische Details

### Architektur-Übersicht 🏗️

```
┌─────────────────────────────────────────────────────────────┐
│                    Bewerbungsgenerator                      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼────────┐                    ┌────────▼─────────┐
│ analyze_stelle │                    │   generator.py   │
│     .py        │                    │                  │
└───────┬────────┘                    └────────┬─────────┘
        │                                      │
        │ 1. Stellenanzeige                    │ 4. Lade JSON
        │    analysieren                       │    (neueste)
        ▼                                      │
┌─────────────────┐                            │
│ bewerbungs_     │◄───────────────────────────┘
│ firma.py        │
│                 │
│ • OllamaClient  │  ◄─── Ollama LLM (mistral:7b)
│ • RegexExtractor│
│ • LLMAnalyzer   │  ──► generate_skill_paragraphs()
│ • SkillMatcher  │
└────────┬────────┘
         │ 2. Skill-Matching
         │    (77+ Skills)
         ▼
┌─────────────────┐
│ persoenliche_   │
│ daten.py        │
│                 │
│ • KENNTNISSE    │
│ • SOFTSKILLS    │
│ • ZERTIFIKATE   │
└─────────────────┘
         │ 3. JSON-Export
         ▼
┌─────────────────┐
│ output/analysen/│
│ Firma_DATUM.json│
└─────────────────┘
         │
         │ 5. Template-Rendering
         ▼
┌─────────────────┐      ┌──────────────┐
│ templates/      │      │ WeasyPrint   │
│ • anschreiben   │─────►│ HTML → PDF   │
│ • lebenslauf    │      └──────┬───────┘
│ • styles.css    │             │
└─────────────────┘             │ 6. PDFs
                                ▼
                    ┌─────────────────────┐
                    │ output/             │
                    │ • Anschreiben_*.pdf │
                    │ • Lebenslauf_*.pdf  │
                    └─────────────────────┘
```

### Komponenten

**bewerbungs_firma.py**
- `OllamaClient`: LLM-Integration (Standard: mistral:7b, Fallbacks: llama3.x, gemma2)
- `RegexExtractor`: Deutsche Patterns für Firmen/Adressen
- `LLMAnalyzer`: Intelligente Textanalyse und Anschreiben-Generierung
- `SkillMatcher`: 77+ Skills mit Synonymen
- `StellenanzeigenAnalyzer`: Hauptorchestrator

**generator.py**
- Auto-Loading der neuesten Analyse aus JSON (neueste nach Zeitstempel)
- LLM-basierte Anschreiben-Textgenerierung mit `generate_skill_paragraphs()`
- QR-Code-Generierung und Integration ins Anschreiben
- Automatische Bereinigung von doppelten Anreden und Formatierungs-Artefakten
- Intelligente Anrede-Logik (Herr/Frau oder "Damen und Herren")
- Dynamische Dateinamen mit persönlichen Daten und Datum (Format: `Name_Vorname_Nachname_JJJJMMTT.pdf`)
- WeasyPrint PDF-Konvertierung mit optimierten CSS-Abständen
- Fallback auf generischen Text wenn Ollama nicht verfügbar

**analyze_stelle.py**
- CLI mit argparse
- Unterstützt Datei, Pipe, interaktive Eingabe
- JSON-Export für Archivierung

**extract_personal_data.py**
- Hybride Datenextraktion aus Markdown und Dokumenten
- Parst `personal_documents/meine_daten.md` direkt
- Extrahiert Zertifikate/Weiterbildungen aus Dateinamen
- Berechnet Skill-Scores aus allen Dokumenten
- Optional: LLM nur für Zeugnisanalyse
- Generiert automatisch `data/persoenliche_daten.py`

**generate_qr_code.py**
- Generiert QR-Codes aus URLs (Standard: Website-URL)
- Unterstützt exakte Größenangaben in cm
- Optimiert für Druckqualität (300 DPI)
- Standardgröße: 2.5cm x 2.5cm

**optimize_image.py**
- Optimiert Profilbilder für Bewerbungsunterlagen
- Automatischer quadratischer Zuschnitt
- Skalierung auf 400x400px
- Komprimierung mit hoher Qualität (95%)

### Datenfluss

```
Stellenanzeige (TXT)
    ↓
analyze_stelle.py
    ↓ (Regex + LLM)
Extrahierte Daten
    ↓
Skill-Matching (77+ Skills)
    ↓
JSON-Export (output/analysen/)
    ↓
generator.py
    ↓ (Auto-Load neueste Analyse)
Personalisiertes Anschreiben
    ↓
PDF-Generierung (WeasyPrint)
    ↓
output/Anschreiben_*.pdf
output/Lebenslauf_*.pdf
```

### Regex-Patterns

Erkennt deutsche Adressformate:
- Firmennamen (inkl. GmbH, AG, KG, etc.)
- Straßen (Straße, Str., Allee, Weg, Platz, Ring, Anlage)
- PLZ (5-stellig)
- E-Mail (Standard-Format)
- Telefon (deutsche Formate mit/ohne Leerzeichen)

### LLM-Integration 🤖

Ollama mit **Mistral 7B** wird für folgende Analysen und Generierungen verwendet:

**Modellauswahl:**
- **Standard:** `mistral:7b` (optimiert für deutsche Grammatik)
- Automatischer Fallback auf verfügbare Modelle
- Unterstützt: Mistral, Llama 3.x, Gemma 2

**Analyse-Phase:**
- Firmenbranche (falls nicht per Regex erkannt)
- Anforderungs-Kategorisierung (Must-Have vs. Nice-to-Have)
- Soft-Skills-Extraktion

**PDF-Generierung:**
- **Vollautomatische Anschreiben-Textgenerierung** mit `LLMAnalyzer.generate_skill_paragraphs()`
- Personalisierung basierend auf Top-3 bis Top-5 Skill-Matches
- 4-Absatz-Struktur: Einleitung, Qualifikation, Skill-Match, Abschluss
- Grammatik: Perfekt-Zeitform, aktive Formulierungen
- Tonalität: Kurz, knapp, freundlich, professionell
- Automatische Bereinigung von:
  - Doppelten Anreden ("Sehr geehrte...")
  - HTML/Markdown-Artefakten
  - Formatierungs-Tags

**Fallback:** Bei nicht verfügbarem Ollama:
- Analyse läuft nur mit Regex
- PDF-Generator nutzt generischen Fallback-Text
- Anschreiben-Absatz-Generierung (optional)

Fallback: Bei nicht verfügbarem Ollama läuft das System nur mit Regex.

## Abhängigkeiten

**Python-Pakete:**
- `weasyprint>=60.0` - PDF-Generierung
- `qrcode>=7.4.2` - QR-Code-Generierung
- `Pillow>=10.0.0` - Bildverarbeitung
- `PyPDF2>=3.0.0` - PDF-Verarbeitung (optional für Datenextraktion)
- `python-docx>=1.0.0` - DOCX-Verarbeitung (optional für Datenextraktion)

**Externe Software:**
- Ollama (optional, aber empfohlen) - https://ollama.ai/download
- **Standard-Modell:** `mistral:7b` (beste deutsche Grammatik)
- Fallback-Modelle: `llama3.2:3b`, `mistral`, `llama3.1:8b`, `gemma2:9b`

## Neueste Features (Februar 2026) 🆕

### QR-Code-Integration
Automatische QR-Code-Generierung und -Einbindung:
- Generiert QR-Code aus persönlicher Website-URL
- Optimiert für Druckqualität (300 DPI, 2.5cm x 2.5cm)
- Automatische Integration in den Lebenslauf-Template
- Standalone-Tool: `python generate_qr_code.py`

### Automatische Datenextraktion
Hybrides System zur Verwaltung persönlicher Daten:
- Master-Datei: `personal_documents/meine_daten.md`
- Automatisches Parsing und Generierung von `data/persoenliche_daten.py`
- Extraktion von Zertifikaten und Weiterbildungen aus Dateinamen
- Skill-Scoring basierend auf Dokumentenanalyse
- Tool: `python extract_personal_data.py`

### Bild-Optimierung
Professionelle Profilbild-Verarbeitung:
- Automatischer quadratischer Zuschnitt
- Optimale Größe: 400x400px
- Hohe Qualität bei geringer Dateigröße
- Tool: `python optimize_image.py`

### Dynamische Dateinamen mit Datum
PDFs enthalten jetzt automatisch Vor-/Nachname und Generierungsdatum:
- Format: `Anschreiben_Marcus_Moser_20260206.pdf`
- Ermöglicht einfache Nachverfolgung und Archivierung
- Keine manuellen Umbenennungen mehr nötig

### LLM-basierte Anschreiben-Textgenerierung
Vollautomatische Erstellung professioneller Bewerbungstexte:
- Nutzt `LLMAnalyzer.generate_skill_paragraphs()` aus `bewerbungs_firma.py`
- 4-Absatz-Struktur mit perfekter deutscher Grammatik
- Personalisierung basierend auf Top-5 Skill-Matches
- Automatische Anredebereinigung (keine doppelten "Sehr geehrte...")
- Fallback auf generischen Text wenn Ollama nicht verfügbar

### Optimierte Layout-Abstände
Professionelle, lesbare Formatierung:
- Datum: 2 Zeilen Abstand unter Empfängeradresse (40px)
- Betreff: 2 Zeilen Abstand unter Datum (35px)  
- Anrede: 1 Zeile Abstand vor Text (15px)
- Absätze: Klarer Abstand für bessere Lesbarkeit (12px)
- An DIN 5008 angelehnt, aber moderner

### Intelligente Textbereinigung
Automatische Filterung von:
- Doppelten Anreden aus LLM-Output
- HTML/Markdown-Formatierungs-Artefakten
- Überflüssigen Leerzeilen
- Template-Tags und Code-Blocks

## Ausgabe-Beispiele

### Analyse-Report

```
🏢 FIRMA: Muster IT GmbH
📍 STANDORT: Musterstadt
📧 ANSPRECHPARTNER: Nicht erkannt
📞 TELEFON: Nicht erkannt

💼 STELLE
  Titel: Full-Stack-Entwickler (m/w/d)
  Eintrittsdatum: zum nächstmöglichen Zeitpunkt
  Arbeitszeit: Vollzeit
 📄

**Anschreiben** (`Anschreiben_Max_Mustermann_20260204.pdf`):
- Moderner Header mit Profilbild (50x50px) und Kontaktdaten
- Firmenadresse im Anschriftsfeld
- Personalisierte Anrede (Herr/Frau oder "Damen und Herren")
- **LLM-generierter Bewerbungstext** (4 Absätze):
  - Bezug auf Position und Bewerbung als Junior
  - Qualifikation (Ausbildung, Schwerpunkte)
  - Skill-Match mit Top-5-Skills aus Analyse
  - Abschluss mit Gesprächseinladung
- Optimierte Abstände nach DIN-Anlehnung
- Grußformel und Unterschrift
- Anlagen-Vermerk

**Lebenslauf** (`Lebenslauf_Max_Mustermann_20260204.pdf`):
- Strukturiert nach Berufserfahrung, Ausbildung, Kenntnisse
- Skills mit Level-Anzeige (1-5) und visuellen Balken
- Kategorisierte Skills (Programmiersprachen, Frameworks, Tools, Methoden)
- Zertifikate, Weiterbildungen, Sprachen
- Professionelles CSS-Layout mit Farbakzenten
### Generierte PDFs

**Anschreiben:**
- Firmenadresse im Anschriftsfeld
- Personalisierte Anrede (Herr/Frau oder "Damen und Herren")
- Dynamischer Einleitungsabsatz mit Top-3-Skills
- Skill-Match-Prozentsatz im Text
- Profilbild

### Generierte PDFs

**Anschreiben** (`Anschreiben_Vorname_Nachname_20260206.pdf`):
- Moderner Header mit Profilbild (50x50px) und Kontaktdaten
- Firmenadresse im Anschriftsfeld
- Personalisierte Anrede (Herr/Frau oder "Damen und Herren")
- **LLM-generierter Bewerbungstext** (4 Absätze):
  - Bezug auf Position und Bewerbung
  - Qualifikation (Ausbildung, Schwerpunkte)
  - Skill-Match mit Top-5-Skills aus Analyse
  - Abschluss mit Gesprächseinladung
- Optimierte Abstände nach DIN-Anlehnung
- Grußformel und Unterschrift
- Anlagen-Vermerk

**Lebenslauf** (`Lebenslauf_Vorname_Nachname_20260206.pdf`):
- Profilbild im Header
- QR-Code zur persönlichen Website (2.5cm x 2.5cm)
- Strukturiert nach Berufserfahrung, Ausbildung, Kenntnisse
- Skills mit Level-Anzeige (1-5) und visuellen Balken
- Kategorisierte Skills (Programmiersprachen, Frameworks, Tools, Methoden)
- Zertifikate, Weiterbildungen, Sprachen
- Professionelles CSS-Layout mit Farbakzenten

## Best Practices 💡

1. **Vollständige Stellenanzeigen**: Kopiere den kompletten Text inkl. Kontaktdaten und Firmenadresse
2. **Daten-Master-Datei**: Pflege `personal_documents/meine_daten.md` und generiere mit `python extract_personal_data.py`
3. **Skill-Pflege**: Halte Skills aktuell und bewerte realistisch (1-5)
4. **Analyse-Archiv**: JSON-Dateien in `output/analysen/` dokumentieren alle Bewerbungen mit Zeitstempel
5. **Template-Anpassung**: Passe `templates/anschreiben.html` und `styles.css` an deinen Stil an
6. **Ollama nutzen**: LLM verbessert Matching-Ergebnisse (72% vs. 60%) und generiert professionelle Texte
7. **Profilbild optimieren**: Nutze `python optimize_image.py` für optimale Bildqualität
8. **QR-Code**: Website-URL in `meine_daten.md` pflegen für automatische QR-Code-Generierung
9. **Dateiorganisation**: PDFs haben Datum im Namen - archiviere alte Versionen regelmäßig
10. **Text-Review**: Prüfe den LLM-generierten Text vor dem Versenden (meist 95%+ perfekt, selten Anpassungen nötig)

## Fehlerbehebung 🛠️

Das System gibt hilfreiche Fehler aus:

```
⚠️  FEHLENDE INFORMATIONEN:
   Fehlende Informationen: E-Mail, Telefon

   💡 Zum Vervollständigen:
      1. Öffne die Eingabedatei (z.B. input/aktuelle_stellenanzeige.txt)
      2. Füge die fehlenden Daten am Anfang oder Ende hinzu:
         Beispiel:
         Kontakt: bewerbung@firma.de, Tel: 0621/12345
```

### Häufige Probleme

**Problem: Doppelte Anreden im PDF**
- Lösung: System filtert diese automatisch - regeneriere mit `python generator.py`

**Problem: QR-Code wird nicht angezeigt**
- Lösung: Stelle sicher, dass Website-URL in `meine_daten.md` eingetragen ist
- Regeneriere QR-Code: `python generate_qr_code.py`

**Problem: Profilbild zu groß/klein**
- Lösung: Nutze `python optimize_image.py` für automatische Optimierung
- Manuell: Speichere Bild als 400x400px in `images/profilbild.jpg`

**Problem: Persönliche Daten nicht aktuell**
- Lösung: Bearbeite `personal_documents/meine_daten.md` und führe aus: `python extract_personal_data.py`

**Problem: Ollama-Timeout bei mistral:7b**
- Lösung: Nutze kleineres Modell: `ollama pull llama3.2:3b`
- System verwendet automatisch verfügbare Fallback-Modelle

---

**System-Status:** ✅ Produktiv (Stand: Februar 2026)  
**Repository:** [Mac80Mo/Bewerbungs-Generator-System](https://github.com/Mac80Mo/Bewerbungs-Generator-System)

**Problem: "Ollama nicht verfügbar"**
```bash
# Prüfe Ollama-Status
ollama list
ollama serve  # Falls nicht läuft

# Teste ohne LLM (nur Regex)
python analyze_stelle.py --no-llm -f input/stellenanzeige.txt
```

**Problem: Leere oder fehlerhafte PDFs**
```bash
# Prüfe WeasyPrint Installation
python -c "import weasyprint; print(weasyprint.__version__)"

# Reinstalliere
pip install --upgrade weasyprint
```

**Problem: Keine Analyse gefunden**
- Generator lädt automatisch neueste JSON aus `output/analysen/`
- Stelle sicher, dass `analyze_stelle.py --save` ausgeführt wurde
- Prüfe ob JSON-Dateien in `output/analysen/` vorhanden sind

**Problem: LLM generiert keinen Text**
- Fallback-Text wird automatisch verwendet
- Prüfe `ollama list` - Modell `mistral:7b` sollte vorhanden sein
- System nutzt automatisch Fallback-Modelle (llama3.2:3b, mistral, etc.)
- Console-Ausgabe zeigt: "🤖 Generiere personalisierten Anschreiben-Text mit LLM..."

### Debug-Befehle

```bash
# Prüfe Python-Environment
python --version  # Sollte >= 3.8 sein

# Prüfe Ollama-Verfügbarkeit
ollama list

# Teste Analyse ohne Speichern
python analyze_stelle.py -f input/aktuelle_stellenanzeige.txt

# Validiere persönliche Daten
python -c "from data.persoenliche_daten import PERSOENLICHE_DATEN; print(PERSOENLICHE_DATEN)"

# Teste PDF-Generator direkt
python generator.py
```

### Kontakt & Feedback

Bei Fragen oder Problemen:
1. Prüfe Console-Ausgabe auf Fehlermeldungen
2. Validiere `requirements.txt`-Installation: `pip list`
3. Teste Komponenten einzeln (siehe Debug-Befehle)
4. Überprüfe `data/persoenliche_daten.py`-Syntax

## Projektstatus 📊

**Version:** 1.0 (Stand: Februar 2026)

**Features:**
- ✅ Stellenanzeigen-Analyse (Regex + LLM)
- ✅ Skill-Matching (77+ Skills)
- ✅ LLM-Textgenerierung (Ollama)
- ✅ PDF-Generierung (Anschreiben + Lebenslauf)
- ✅ Dynamische Dateinamen mit Datum
- ✅ Intelligente Anrede-Logik
- ✅ Automatische Textbereinigung
- ✅ JSON-Analyse-Archiv

**Geplante Verbesserungen:**
- [ ] GUI für einfachere Bedienung
- [ ] Multi-Bewerbung-Batch-Processing
- [ ] Export nach Word/DOCX
- [ ] LinkedIn-Integration für Skill-Import
- [ ] Bewerbungstracking-Dashboard

**Statistiken:**
- ~1000 Zeilen Code (Python)
- 2 HTML-Templates
- 1 CSS-Stylesheet (~470 Zeilen)
- 77+ Skills im Matching-System
- Durchschnittliche Skill-Match-Rate: 60-75%
- PDF-Generierung: ~2-5 Sekunden (mit LLM)

## Lizenz

Persönliches Projekt - Alle Rechte vorbehalten.

---

*Dieses Tool entstand aus dem Bedarf, den Bewerbungsprozess zu optimieren und gleichzeitig moderne KI-Technologien praktisch einzusetzen.*
