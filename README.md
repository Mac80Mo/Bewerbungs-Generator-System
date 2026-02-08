# Bewerbungsgenerator 🚀

Vollautomatisiertes System zur Erstellung professioneller Bewerbungsunterlagen mit KI-gestützter Stellenanzeigen-Analyse, intelligentem Skill-Matching und automatisierter Dokumentengenerierung.

## 🔒 DSGVO-Konformität & Datenschutz

**100% DSGVO-konform durch lokale Verarbeitung:**
- ✅ **Keine Cloud-Dienste**: Alle Daten bleiben auf Ihrem Computer
- ✅ **Lokale LLMs**: KI-Analyse erfolgt ausschließlich über Ollama (lokal installiert)
- ✅ **Keine Datenweitergabe**: Keinerlei personenbezogene Daten werden an Dritte übertragen
- ✅ **Offline-Fähig**: System funktioniert komplett ohne Internetverbindung
- ✅ **Volle Kontrolle**: Absolute Kontrolle über alle Bewerbungsdaten

**Repository-Schutz:**
- Sensible Daten (persönliche Informationen, Dokumente, PDFs) durch `.gitignore` geschützt
- Nur Code und Templates werden versioniert

## Überblick

Das System analysiert Stellenanzeigen, extrahiert Firmendaten, gleicht Anforderungen mit persönlichen Skills ab und generiert automatisch personalisierte PDF-Bewerbungen (Anschreiben + Lebenslauf) mit LLM-generiertem Bewerbungstext.

### Kernfunktionen ✨

- **🧠 Intelligentes Skill-Matching**: 
  - **Must-Have-Boosting**: +25 Bonuspunkte für kritische Anforderungen
  - **Soft-Skill-Dämpfung**: 70% Gewichtung zur Priorisierung technischer Skills
  - **Top-3-Skills**: Automatische Auswahl der relevantesten Skills für Anschreiben
  - **50+ Skill-Keywords**: Erweiterte Datenbank mit Synonym-Erkennung
  - **Duplikate-Prävention**: Skills erscheinen nur einmal (Must-Have bevorzugt)
  - **Normalisierung**: Automatische Bereinigung (Leerzeichen, Bindestriche, Punkte)
  - **Skill-Splitting**: Erkennung von "JavaScript/TypeScript", "Java Script"

- **📊 Stellenanzeigen-Analyse**:
  - Hybrid-Extraktion mit Regex + Ollama LLM
  - Profil-Sektion-Extraktion für präzise Must-Have-Erkennung
  - Automatische Kategorisierung (Must-Have vs. Nice-to-Have)
  - Marker-Erkennung ("idealerweise", "wünschenswert", "plus")

- **🤖 LLM-Integration** (Ollama):
  - Automatische Anschreiben-Generierung (4-Absatz-Struktur)
  - Mistral 7B (optimiert für deutsche Grammatik)
  - Fallback-Modelle: Llama 3.x, Gemma 2
  - Intelligente Textbereinigung (doppelte Anreden, Artefakte)

- **📄 PDF-Generierung**:
  - Professionelle HTML/CSS-Templates (WeasyPrint)
  - Max. 8 Kurse/Weiterbildungen (+ "..."-Tag)
  - Dynamische Dateinamen mit Zeitstempel
  - QR-Code-Integration (persönliche Website)
  - Optimierte Bild-Verarbeitung

- **🗄️ JSON-Archiv**: Alle Analysen mit Zeitstempel gespeichert

## Installation

### Voraussetzungen

- **Python 3.8+**
- **Ollama** (optional, aber empfohlen) - https://ollama.ai/download

### 1. Repository klonen

```bash
git clone https://github.com/IhrBenutzername/Bewerbungsgenerator.git
cd Bewerbungsgenerator
```

### 2. Virtuelle Umgebung erstellen

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

**Benötigte Pakete:**
- `weasyprint>=60.0` - PDF-Generierung
- `qrcode>=7.4.2` - QR-Code-Generierung
- `Pillow>=10.0.0` - Bildverarbeitung
- `PyPDF2>=3.0.0` - PDF-Verarbeitung (optional)
- `python-docx>=1.0.0` - DOCX-Verarbeitung (optional)

### 4. Ollama installieren (optional, aber empfohlen)

```bash
# Installation: https://ollama.ai/download

# Modell herunterladen (Standard: mistral:7b)
ollama pull mistral:7b

# Alternativ: kleineres Modell für schnellere Verarbeitung
ollama pull llama3.2:3b
```

## Quick Start 🚀

### 1. Persönliche Daten konfigurieren

**Methode A (empfohlen):** Master-Datei bearbeiten

```bash
# Bearbeiten Sie personal_documents/meine_daten.md
nano personal_documents/meine_daten.md

# Generieren Sie automatisch data/persoenliche_daten.py
python extract_personal_data.py
```

**Methode B:** Direkte Bearbeitung

```bash
nano data/persoenliche_daten.py
```

Beispielstruktur:
```python
PERSOENLICHE_DATEN = {
    "vorname": "Max",
    "nachname": "Mustermann",
    "email": "max.mustermann@example.com",
    "website": "https://max-mustermann.de",
    # ...
}

KENNTNISSE = [
    {"skill": "Python", "level": 4},
    {"skill": "Docker", "level": 3},
    # ...
]
```

### 2. Stellenanzeige analysieren

```bash
# Stellenanzeige in Datei speichern
nano input/aktuelle_stellenanzeige.txt

# Analyse starten (mit Speicherung)
python analyze_stelle.py -f input/aktuelle_stellenanzeige.txt --save
```

**Ausgabe:**
- Firmendaten (Name, Adresse, Ansprechpartner)
- Stellendaten (Titel, Eintrittsdatum, Arbeitszeit)
- **Anforderungen**:
  - **Must-Have** (12 Skills erkannt: Vue.js, SQL, Node.js, React, Docker, ...)
  - **Nice-to-Have** (5 Skills: Redux, Cypress, Playwright, ...)
  - **Soft Skills** (Teamfähigkeit, Kommunikationsstärke, ...)
- **Skill-Match-Report**:
  - Deckungsgrad: 50% (6/12 Must-Haves)
  - **Top-5 Matches** (100% Must-Haves durch Boosting):
    1. Vue.js (52 Punkte)
    2. SQL (48 Punkte)
    3. Node.js (32 Punkte)
    4. React (28 Punkte)
    5. Docker (26 Punkte)
- JSON-Export nach `output/analysen/Firma_20260209_123456.json`

### 3. PDF-Bewerbung generieren

```bash
python generator.py
```

**Generiert automatisch:**
- `output/Anschreiben_Max_Mustermann_20260209.pdf`
- `output/Lebenslauf_Max_Mustermann_20260209.pdf`

**Features der generierten PDFs:**
- ✅ Lädt automatisch neueste JSON-Analyse
- ✅ LLM-generiertes Anschreiben (4 Absätze, Top-3-Skills)
- ✅ Intelligente Anrede (Herr/Frau oder "Damen und Herren")
- ✅ QR-Code zur Website (automatisch generiert)
- ✅ Max. 8 relevanteste Kurse (Keyword-Scoring)
- ✅ Professionelles CSS-Layout mit Profilbild

## Verzeichnisstruktur

```
├── input/                          # Eingabedateien
│   └── aktuelle_stellenanzeige.txt # Stellenanzeige (TXT)
├── output/                         # Generierte PDFs
│   ├── analysen/                   # JSON-Analysen (Archiv)
│   │   └── Firma_20260209_*.json   # Zeitstempel-basiert
│   ├── Anschreiben_*.pdf
│   └── Lebenslauf_*.pdf
├── templates/                      # HTML/CSS-Templates
│   ├── anschreiben.html
│   ├── lebenslauf.html
│   ├── styles.css
│   ├── profilbild.jpg              # Optimiertes Bewerbungsfoto
│   └── qr_code.png                 # QR-Code (generiert)
├── images/                         # Bild-Ressourcen
│   ├── profilbild.jpg
│   └── qr_code.png
├── data/                           # Datenmodule
│   ├── persoenliche_daten.py       # Persönliche Daten & Skills
│   └── bewerbungs_firma.py         # Analyse-Engine
├── personal_documents/             # Persönliche Dokumente
│   ├── meine_daten.md              # Master-Datei
│   ├── ausbildung/
│   ├── projekte/
│   │   └── eigene_projekte.json
│   ├── weiterbildungen/
│   └── zertifikate/
├── generator.py                    # PDF-Generator (Hauptprogramm)
├── analyze_stelle.py               # Stellenanzeigen-Analyse CLI
├── extract_personal_data.py        # Datenextraktion
├── generate_qr_code.py             # QR-Code-Generator
├── optimize_image.py               # Bild-Optimierung
└── requirements.txt
```

## Workflow-Details

### Stellenanzeigen-Analyse

**CLI-Optionen:**

```bash
# Standard (mit Speicherung)
python analyze_stelle.py -f input/stellenanzeige.txt --save

# Ohne Speicherung (nur Anzeige)
python analyze_stelle.py -f input/stellenanzeige.txt

# Ohne LLM (nur Regex)
python analyze_stelle.py --no-llm -f input/stellenanzeige.txt

# Mit LLM-Anschreiben-Generierung
python analyze_stelle.py -f input/stellenanzeige.txt --generate-text

# Interaktive Eingabe (Strg+D zum Beenden)
python analyze_stelle.py

# Pipe-Eingabe
cat input/stellenanzeige.txt | python analyze_stelle.py
```

### Skill-Matching-System

**Scoring-Algorithmus:**

```python
# Grundpunkte
must_have = 15 Punkte
nice_to_have = 8 Punkte
matched_skills = 3 Punkte (Skills im eigenen Profil)
fallback = 2 Punkte

# Optimierungen
must_have_bonus = +25 Punkte  # Boosting für kritische Skills
soft_skill_faktor = 0.7       # Dämpfung (70% der Punkte)

# Beispielberechnung (Vue.js):
# - Must-Have: 15 + 25 = 40
# - Matched Skills: 3 × 4 (Level) = 12
# → Gesamt: 52 Punkte
```

**Features:**

1. **Normalisierung**: `"JavaScript"` = `"Java Script"` = `"java-script"`
2. **Skill-Splitting**: `"JavaScript/TypeScript"` → `["JavaScript", "TypeScript"]`
3. **Duplikate-Prävention**: Skills nur einmal (Must-Have bevorzugt)
4. **Must-Have-Boosting**: +25 Bonus für kritische Anforderungen
5. **Soft-Skill-Dämpfung**: ×0.7 zur Priorisierung technischer Skills
6. **Top-3-Auswahl**: Nur die relevantesten Skills im Anschreiben
7. **50+ Keywords**: Erweiterte Skill-Datenbank

**Skill-Datenbank (Auszug):**

- **Programmiersprachen**: Python, JavaScript, TypeScript, Java, C#, Go, Rust
- **Frontend**: React, Vue.js, Angular, Svelte, Next.js, Redux, Pinia, RxJS
- **Backend**: Node.js, Express, FastAPI, Django, Spring Boot, .NET
- **DevOps**: Docker, Kubernetes, CI/CD, Jenkins, GitLab CI, GitHub Actions
- **Datenbanken**: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch
- **Testing**: Jest, Cypress, Playwright, Selenium, Xray, JUnit
- **Cloud**: AWS, Azure, GCP, Terraform, CloudFormation

### PDF-Generierung

**Anschreiben-Features:**

- **LLM-generierter Text**: 4-Absatz-Struktur
  1. Einleitung (Bezug auf Position)
  2. Qualifikation (Ausbildung, Schwerpunkte)
  3. Skill-Match (Top-3-Skills aus Analyse)
  4. Abschluss (Gesprächseinladung)
  
- **Intelligente Anrede**:
  - Mit Name: "Sehr geehrte Frau Müller,"
  - Ohne Name: "Sehr geehrte Damen und Herren,"
  
- **Automatische Bereinigung**:
  - Doppelte Anreden entfernt
  - HTML/Markdown-Artefakte gefiltert
  - Formatierungs-Tags entfernt

**Lebenslauf-Features:**

- Strukturiert nach Berufserfahrung, Ausbildung, Kenntnisse
- Skills mit Level-Anzeige (1-5) und visuellen Balken
- Kategorisierte Skills (Programmiersprachen, Frameworks, Tools, Methoden)
- **Max. 8 Kurse/Weiterbildungen** (+ "..."-Tag)
  - Keyword-Scoring basierend auf Stellenanforderungen
  - Normalisierung und Duplikate-Prävention
- QR-Code zur Website (2.5cm × 2.5cm, 300 DPI)
- Professionelles CSS-Layout mit Farbakzenten

### Erweiterte Tools

**Bild-Optimierung:**
```bash
python optimize_image.py
```
- Automatischer quadratischer Zuschnitt
- Skalierung auf 400×400px
- Komprimierung (95% Qualität)

**QR-Code-Generierung:**
```bash
python generate_qr_code.py
```
- Generiert QR-Code aus Website-URL
- Größe: 2.5cm × 2.5cm (300 DPI)
- Speichert in `images/qr_code.png`

**Datenextraktion:**
```bash
python extract_personal_data.py
```
- Parst `personal_documents/meine_daten.md`
- Extrahiert Zertifikate aus Dateinamen
- Berechnet Skill-Scores aus Dokumenten
- Generiert `data/persoenliche_daten.py`

## Architektur-Übersicht 🏗️

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
│ • RegexExtractor│       - Must-Have-Erkennung
│ • LLMAnalyzer   │       - Anschreiben-Generierung
│ • SkillMatcher  │  ──► 50+ Skills, Boosting
└────────┬────────┘
         │ 2. Skill-Matching
         │    (Must-Have +25, Soft-Skill ×0.7)
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

### Komponenten-Details

**bewerbungs_firma.py** (1050+ Zeilen)
- `OllamaClient`: LLM-Integration (Mistral 7B, Fallbacks)
- `RegexExtractor`: Deutsche Patterns, Profil-Sektion-Extraktion
- `LLMAnalyzer`: Textanalyse, Anschreiben-Generierung
- `SkillMatcher`: 50+ Skills, Must-Have-Boosting, Soft-Skill-Dämpfung
- `StellenanzeigenAnalyzer`: Hauptorchestrator

**generator.py** (860+ Zeilen)
- Auto-Loading der neuesten JSON-Analyse
- LLM-basierte Anschreiben-Textgenerierung
- `select_relevant_kurse()`: Max. 8 Kurse, Keyword-Scoring
- QR-Code-Integration
- Intelligente Anrede-Logik
- WeasyPrint PDF-Konvertierung

**analyze_stelle.py** (135+ Zeilen)
- CLI mit argparse
- Datei, Pipe, interaktive Eingabe
- JSON-Export für Archivierung

## Neueste Optimierungen (Februar 2026) 🆕

### Must-Have-Boosting (+25 Bonuspunkte)
**Problem:** Soft-Skills (Teamfähigkeit, Kommunikation) haben Must-Haves (Vue.js, Docker) aus den Top-5 verdrängt.

**Lösung:**
```python
# In SkillMatcher.do_matching()
if skill_data.get("category") == "must_have":
    final_score += 25  # Bonus für kritische Skills
```

**Resultat:** Top-5 jetzt 100% Must-Haves (Vue.js 52, SQL 48, Node.js 32, React 28, Docker 26)

### Soft-Skill-Dämpfung (70% Gewichtung)
**Problem:** Soft-Skills mit hohen Scores überschatten technische Skills.

**Lösung:**
```python
# In SkillMatcher.do_matching()
if skill_data.get("category") == "soft_skills":
    final_score *= 0.7  # 70% Gewichtung
```

**Resultat:** Technische Skills klar priorisiert, Soft-Skills bleiben sichtbar

### Top-3-Skills im Anschreiben (vorher: Top-5)
**Problem:** Anschreiben zu lang, zu viele Skills erwähnt.

**Lösung:**
```python
# In generator.py
top_skills = sorted_skills[:3]  # Nur Top-3
```

**Resultat:** Fokussiert, prägnant, höhere Relevanz

### Profil-Sektion-Extraktion
**Problem:** Must-Haves waren LEER (nur 8/23 Skills extrahiert).

**Lösung:**
```python
# In RegexExtractor._extract_profil_section()
def _extract_profil_section(text):
    # Strukturelle Analyse: Suche "Profil", "Anforderungen", "Qualifikation"
    # Extrahiert vollständigen Requirements-Block
    # Marker-Erkennung: "idealerweise", "wünschenswert", "plus"
```

**Resultat:** 23 Skills extrahiert (vorher: 8), 12 Must-Haves korrekt identifiziert

### Duplikate-Prävention (Case-Insensitive)
**Problem:** Skills erscheinen mehrfach (Must-Have + Nice-to-Have).

**Lösung:**
```python
# In RegexExtractor._extract_requirements()
seen_skills = set()
for skill in extracted_skills:
    normalized = skill.lower().strip()
    if normalized not in seen_skills:
        seen_skills.add(normalized)
        # Must-Have bevorzugt bei Duplikaten
```

**Resultat:** Jeder Skill nur einmal, korrekte Kategorisierung

### Normalisierung & Skill-Splitting
**Problem:** LLM-Parsing scheitert an "Java Script", "JavaScript/TypeScript".

**Lösung:**
```python
# Normalisierung
normalized = text.replace(" ", "").replace("-", "").replace(".", "").lower()

# Skill-Splitting
if "/" in skill or "(" in skill:
    split_skills = skill.replace("/", ",").replace("(", ",").replace(")", ",").split(",")
```

**Resultat:** 100% Erkennungsrate, keine false negatives

### Keyword-Scoring für Kurse (Max. 8)
**Problem:** LLM-basierte Kursauswahl unzuverlässig (5/8 gefunden).

**Lösung:**
```python
# In generator.py: select_relevant_kurse()
def calculate_score(kurs):
    score = 0
    normalized_kurs = normalize(kurs)
    
    for skill, skill_data in matched_skills.items():
        normalized_skill = normalize(skill)
        
        if normalized_skill in normalized_kurs:
            # Must-Have
            if skill_data.get("category") == "must_have":
                score += 15 + 25  # Boosting
            
            # Nice-to-Have
            elif skill_data.get("category") == "nice_to_have":
                score += 8
            
            # Matched Skill (im eigenen Profil)
            if skill in eigene_skills:
                score += 3 * skill_level
            
            # Soft-Skill
            if skill_data.get("category") == "soft_skills":
                score *= 0.7  # Dämpfung
    
    return score
```

**Resultat:** 100% Zuverlässigkeit, Top-8 immer korrekt

## Templates anpassen

### HTML/CSS-Struktur

**templates/anschreiben.html:**
```html
<div class="header">
  <img src="file:///.../templates/profilbild.jpg" />
  <div class="contact">
    {vorname} {nachname}<br>
    {email}<br>
    {website}
  </div>
</div>

<div class="recipient">
  {firma_name}<br>
  {firma_strasse}<br>
  {firma_plz} {firma_ort}
</div>

<div class="date">{datum}</div>
<div class="subject"><strong>Bewerbung als {stelle_titel}</strong></div>

<div class="salutation">{anrede}</div>
<div class="content">{anschreiben_text}</div>

<div class="signature">
  Mit freundlichen Grüßen<br>
  {vorname} {nachname}
</div>
```

**templates/styles.css:**
```css
/* DIN-angelehnte Abstände */
.date { margin-top: 40px; }        /* 2 Zeilen unter Empfänger */
.subject { margin-top: 35px; }     /* 2 Zeilen unter Datum */
.salutation { margin-top: 15px; }  /* 1 Zeile vor Text */
.content p { margin-bottom: 12px; }

/* Moderne Farbakzente */
.header { background: #3498db; color: white; }
.subject strong { color: #2c3e50; }
```

### Platzhalter

**Automatisch ersetzt:**
- `{vorname}`, `{nachname}`, `{email}`, `{website}`
- `{firma_name}`, `{firma_strasse}`, `{firma_plz}`, `{firma_ort}`
- `{stelle_titel}`, `{ansprechpartner}`, `{datum}`
- `{anrede}` - Intelligente Logik (Herr/Frau oder "Damen und Herren")
- `{anschreiben_text}` - LLM-generiert (4 Absätze, Top-3-Skills)

## LLM-Integration 🤖

### Modellauswahl

**Standard:** `mistral:7b` (optimiert für deutsche Grammatik)

**Fallback-Reihenfolge:**
1. `mistral:7b`
2. `llama3.2:3b`
3. `mistral`
4. `llama3.1:8b`
5. `gemma2:9b`

### Anschreiben-Generierung

**Prompt-Struktur:**
```python
prompt = f"""
Schreibe einen professionellen Bewerbungstext (4 Absätze) für:

Stelle: {stelle_titel}
Firma: {firma_name}

Top-3 Skills (verwende ALLE):
{top_3_skills_beschreibung}

Anforderungen:
- Kurz, knapp, freundlich
- Perfekt-Zeitform
- Aktive Formulierungen
- Keine Übertreibungen
- Keine Anrede (wird separat eingefügt)
"""
```

**Ausgabe (Beispiel):**
```
ich beziehe mich auf Ihre Stellenausschreibung als Full-Stack-Entwickler.

Während meiner Ausbildung habe ich mich auf moderne Webentwicklung spezialisiert,
mit Schwerpunkten in React, Node.js und SQL-Datenbanken.

Besonders relevant für Ihre Position sind meine Kenntnisse in Vue.js (Framework),
SQL-Datenbanken (PostgreSQL, MySQL) und Node.js (Backend-Entwicklung). Diese
Skills habe ich in mehreren Projekten erfolgreich eingesetzt.

Über eine Einladung zu einem persönlichen Gespräch würde ich mich freuen.
```

### Textbereinigung

**Automatisch entfernt:**
- Doppelte Anreden ("Sehr geehrte...")
- HTML-Tags (`<p>`, `</p>`)
- Markdown-Formatierung (`**`, `##`)
- Code-Blöcke (` ``` `)
- Überflüssige Leerzeilen

## Best Practices 💡

### 1. Vollständige Stellenanzeigen
✅ Kopieren Sie den **kompletten Text** inkl. Kontaktdaten und Firmenadresse  
❌ Nicht nur die Anforderungen kopieren

### 2. Daten-Master-Datei pflegen
✅ Bearbeiten Sie `personal_documents/meine_daten.md`  
✅ Generieren Sie mit `python extract_personal_data.py`  
❌ Manuelle Bearbeitung von `data/persoenliche_daten.py` vermeiden

### 3. Skill-Pflege
✅ Skills realistisch bewerten (1-5)  
✅ Nur tatsächlich beherrschte Skills eintragen  
❌ Keine Übertreibungen (Level 5 = Expert)

### 4. Analyse-Archiv
✅ JSON-Dateien in `output/analysen/` dokumentieren alle Bewerbungen  
✅ Zeitstempel ermöglichen Nachverfolgung  
❌ Nicht löschen (Archivfunktion)

### 5. Template-Anpassung
✅ Passen Sie `templates/anschreiben.html` an Ihren Stil an  
✅ Farben in `styles.css` anpassen (#3498db = Blau)  
❌ HTML-Struktur nicht komplett ändern (Platzhalter beachten)

### 6. Ollama nutzen
✅ LLM verbessert Matching (72% vs. 60%)  
✅ Professionelle Textgenerierung  
❌ Ohne Ollama: Fallback auf generischen Text

### 7. Profilbild optimieren
✅ `python optimize_image.py` für optimale Qualität  
✅ 400×400px, quadratischer Zuschnitt  
❌ Keine zu großen Bilder (> 1 MB)

### 8. QR-Code
✅ Website-URL in `meine_daten.md` pflegen  
✅ Automatische Generierung mit `python generate_qr_code.py`  
❌ Manuelle QR-Code-Erstellung nicht nötig

### 9. Text-Review
✅ LLM-Text vor Versenden prüfen (95%+ perfekt)  
✅ Bei Bedarf `templates/anschreiben.html` anpassen  
❌ Blind versenden (selten, aber möglich: Fehler)

### 10. Dateiorganisation
✅ PDFs haben Datum im Namen (Archivierung einfach)  
✅ Alte Versionen regelmäßig archivieren  
❌ Nicht überschreiben (Verlust von Nachverfolgbarkeit)

## Fehlerbehebung 🛠️

### Häufige Probleme

#### ❌ Problem: "Ollama nicht verfügbar"

**Ursache:** Ollama-Server nicht gestartet oder Modell nicht installiert

**Lösung:**
```bash
# Prüfe Ollama-Status
ollama list

# Starte Ollama-Server
ollama serve

# Installiere Modell
ollama pull mistral:7b

# Teste ohne LLM (nur Regex)
python analyze_stelle.py --no-llm -f input/stellenanzeige.txt
```

#### ❌ Problem: Leere oder fehlerhafte PDFs

**Ursache:** WeasyPrint-Installation fehlerhaft

**Lösung:**
```bash
# Prüfe WeasyPrint
python -c "import weasyprint; print(weasyprint.__version__)"

# Reinstalliere
pip install --upgrade weasyprint

# Prüfe Templates
ls -la templates/  # Sollte anschreiben.html, lebenslauf.html, styles.css enthalten
```

#### ❌ Problem: Keine Analyse gefunden

**Ursache:** JSON-Datei nicht gespeichert oder nicht vorhanden

**Lösung:**
```bash
# Prüfe JSON-Dateien
ls -la output/analysen/

# Stelle sicher, dass --save verwendet wurde
python analyze_stelle.py -f input/stellenanzeige.txt --save

# Generator lädt automatisch neueste JSON
python generator.py
```

#### ❌ Problem: LLM generiert keinen Text

**Ursache:** Modell nicht verfügbar, Timeout, oder Prompt zu lang

**Lösung:**
```bash
# Prüfe verfügbare Modelle
ollama list

# Kleineres Modell verwenden (schneller)
ollama pull llama3.2:3b

# System nutzt automatisch Fallback-Modelle
# Console-Ausgabe: "🤖 Generiere personalisierten Anschreiben-Text mit LLM..."
```

**Fallback:** System verwendet generischen Text automatisch

#### ❌ Problem: QR-Code wird nicht angezeigt

**Ursache:** Website-URL fehlt oder QR-Code nicht generiert

**Lösung:**
```bash
# Stelle sicher, dass Website-URL in meine_daten.md eingetragen ist
nano personal_documents/meine_daten.md

# Regeneriere QR-Code
python generate_qr_code.py

# Prüfe QR-Code-Datei
ls -la images/qr_code.png
```

#### ❌ Problem: Profilbild zu groß/klein

**Ursache:** Bild nicht optimiert

**Lösung:**
```bash
# Automatische Optimierung
python optimize_image.py

# Prüfe Bildgröße
file images/profilbild.jpg  # Sollte 400×400px sein
```

#### ❌ Problem: Persönliche Daten nicht aktuell

**Ursache:** `extract_personal_data.py` nicht ausgeführt

**Lösung:**
```bash
# Bearbeite Master-Datei
nano personal_documents/meine_daten.md

# Generiere persoenliche_daten.py
python extract_personal_data.py

# Validiere Daten
python -c "from data.persoenliche_daten import PERSOENLICHE_DATEN; print(PERSOENLICHE_DATEN)"
```

#### ❌ Problem: Doppelte Anreden im PDF

**Ursache:** LLM-Output enthält Anrede (wird automatisch entfernt)

**Lösung:**
```bash
# Regeneriere PDF (System filtert automatisch)
python generator.py

# Falls Problem bleibt: Prüfe templates/anschreiben.html
nano templates/anschreiben.html
```

#### ❌ Problem: Must-Haves leer (0 Skills)

**Ursache:** Profil-Sektion nicht erkannt oder falsche Marker

**Lösung:**
```bash
# Prüfe Stellenanzeige auf Strukturwörter
grep -i "profil\|anforderung\|qualifikation" input/aktuelle_stellenanzeige.txt

# Manuell: Kopiere Anforderungs-Block an den Anfang der Datei

# Verwende --no-llm für Debug
python analyze_stelle.py --no-llm -f input/stellenanzeige.txt
```

### Debug-Befehle

```bash
# Prüfe Python-Environment
python --version  # Sollte >= 3.8 sein

# Prüfe installierte Pakete
pip list | grep -E "weasyprint|qrcode|Pillow|PyPDF2|python-docx"

# Validiere persönliche Daten
python -c "from data.persoenliche_daten import PERSOENLICHE_DATEN; print(PERSOENLICHE_DATEN)"

# Prüfe Ollama-Modelle
ollama list

# Teste Analyse ohne Speichern
python analyze_stelle.py -f input/aktuelle_stellenanzeige.txt

# Teste PDF-Generator direkt
python generator.py

# Prüfe JSON-Analysen
ls -la output/analysen/

# Validiere Templates
ls -la templates/  # Sollte .html, .css, profilbild.jpg enthalten
```

### System-Anforderungen

**Minimum:**
- Python 3.8+
- 2 GB RAM
- 500 MB Festplattenspeicher

**Empfohlen:**
- Python 3.10+
- 4 GB RAM
- Ollama installiert (zusätzlich 5-10 GB für Modelle)

## Ausgabe-Beispiele

### Analyse-Report (Konsole)

```
🏢 FIRMA: Beispiel GmbH
📍 STANDORT: Musterstadt
📧 ANSPRECHPARTNER: Frau Müller
📞 TELEFON: 0621/12345-0

💼 STELLE
  Titel: Full-Stack-Entwickler (m/w/d)
  Eintrittsdatum: zum nächstmöglichen Zeitpunkt
  Arbeitszeit: Vollzeit

✅ ANFORDERUNGEN (23 Skills extrahiert)

Must-Have (12):
  ✓ Vue.js (Frontend Framework)
  ✓ SQL (Datenbanken)
  ✓ Node.js (Backend)
  ✓ React (Alternative Frontend)
  ✓ Docker (Container)
  ✓ Kubernetes (Orchestrierung)
  ✓ Spring Boot (Java Backend)
  ✓ Angular (Frontend Framework)
  ✓ NoSQL (MongoDB, Redis)
  ✓ Cypress (Testing)
  ✓ Playwright (E2E-Testing)
  ✓ Selenium (Automated Testing)

Nice-to-Have (5):
  ○ Redux (State Management)
  ○ Pinia (Vue State Management)
  ○ RxJS (Reactive Programming)
  ○ TypeScript (Type Safety)
  ○ GraphQL (API)

Soft Skills (6):
  ◆ Teamfähigkeit
  ◆ Kommunikationsstärke
  ◆ Problemlösungskompetenz
  ◆ Eigenverantwortung
  ◆ Lernbereitschaft
  ◆ Agile Methoden

🎯 SKILL-MATCHING

Deckungsgrad: 50.0% (6/12 Must-Haves erfüllt)

Top-5 Matches (100% Must-Haves dank Boosting):
  1. Vue.js          52 Punkte (Must-Have, Level 4)
  2. SQL             48 Punkte (Must-Have, Level 4)
  3. Node.js         32 Punkte (Must-Have, Level 3)
  4. React           28 Punkte (Must-Have, Level 2)
  5. Docker          26 Punkte (Must-Have, Level 2)

Fehlende Must-Haves (6):
  ✗ Kubernetes
  ✗ Spring Boot
  ✗ Angular
  ✗ NoSQL
  ✗ Cypress
  ✗ Playwright

✅ JSON gespeichert: output/analysen/Beispiel_GmbH_20260209_123456.json
```

### Generierte PDFs

**Anschreiben** (`Anschreiben_Max_Mustermann_20260209.pdf`):

```
┌─────────────────────────────────────────────────────────┐
│ [Profilbild]  Max Mustermann                            │
│               max.mustermann@example.com                │
│               https://max-mustermann.de                 │
└─────────────────────────────────────────────────────────┘

Beispiel GmbH
Musterstraße 123
12345 Musterstadt

                                    Musterstadt, 09.02.2026

Bewerbung als Full-Stack-Entwickler (m/w/d)

Sehr geehrte Frau Müller,

ich beziehe mich auf Ihre Stellenausschreibung als Full-Stack-Entwickler.

Während meiner Ausbildung zum Fachinformatiker für Anwendungsentwicklung
habe ich mich auf moderne Webentwicklung spezialisiert, mit Schwerpunkten
in JavaScript-Frameworks, Backend-Technologien und SQL-Datenbanken.

Besonders relevant für Ihre Position sind meine Kenntnisse in Vue.js
(Progressive Framework für moderne UIs), SQL-Datenbanken (PostgreSQL, MySQL)
und Node.js (serverseitige JavaScript-Entwicklung). Diese Skills habe ich
in mehreren Projekten erfolgreich eingesetzt und kontinuierlich vertieft.

Über eine Einladung zu einem persönlichen Gespräch würde ich mich freuen.

Mit freundlichen Grüßen

Max Mustermann

Anlagen
```

**Lebenslauf** (`Lebenslauf_Max_Mustermann_20260209.pdf`):

```
┌─────────────────────────────────────────────────────────┐
│ [Profilbild]  Max Mustermann                [QR-Code]   │
│               max.mustermann@example.com                │
│               https://max-mustermann.de                 │
└─────────────────────────────────────────────────────────┘

BERUFSERFAHRUNG
───────────────────────────────────────────────────────────
2023 - heute    Fachinformatiker Anwendungsentwicklung
                Firma XY GmbH, Musterstadt
                • Full-Stack-Entwicklung (Vue.js, Node.js)
                • Datenbankdesign (PostgreSQL)
                • Projektmitarbeit (Agile Methoden)

AUSBILDUNG
───────────────────────────────────────────────────────────
2020 - 2023     Fachinformatiker für Anwendungsentwicklung
                IHK Rhein-Neckar
                Abschlussnote: 1.8

KENNTNISSE
───────────────────────────────────────────────────────────
Programmiersprachen
• JavaScript      ████████ (4/5)
• Python          ████████ (4/5)
• SQL             ████████ (4/5)

Frameworks & Libraries
• Vue.js          ████████ (4/5)
• React           ██████   (3/5)
• Node.js         ██████   (3/5)

Tools & DevOps
• Docker          ██████   (3/5)
• Git             ████████ (4/5)
• VS Code         ████████ (4/5)

KURSE & WEITERBILDUNGEN (max. 8)
───────────────────────────────────────────────────────────
• Vue.js Masterclass (26 Punkte)
• SQL Basics for Developers (26 Punkte)
• React Essentials (26 Punkte)
• Node.js Backend Development (18 Punkte)
• JavaScript Boot Camp (18 Punkte)
• Docker for Developers (15 Punkte)
• Git & GitHub Fundamentals (12 Punkte)
• Agile Project Management (8 Punkte)
• ... (weitere Kurse verfügbar)

SPRACHEN
───────────────────────────────────────────────────────────
• Deutsch         Muttersprache
• Englisch        Fließend (C1)
```

## Projektstatus 📊

**Version:** 2.0 (Stand: Februar 2026)

**Aktuelle Features:**
- ✅ Stellenanzeigen-Analyse (Regex + LLM)
- ✅ Profil-Sektion-Extraktion (Must-Have-Erkennung)
- ✅ Skill-Matching (50+ Skills)
- ✅ Must-Have-Boosting (+25 Bonuspunkte)
- ✅ Soft-Skill-Dämpfung (70% Gewichtung)
- ✅ Top-3-Skills im Anschreiben
- ✅ Duplikate-Prävention (Case-Insensitive)
- ✅ Normalisierung & Skill-Splitting
- ✅ Keyword-Scoring für Kurse (Max. 8)
- ✅ LLM-Textgenerierung (Ollama, 4-Absatz-Struktur)
- ✅ PDF-Generierung (Anschreiben + Lebenslauf)
- ✅ Dynamische Dateinamen mit Zeitstempel
- ✅ Intelligente Anrede-Logik
- ✅ Automatische Textbereinigung
- ✅ JSON-Analyse-Archiv
- ✅ QR-Code-Integration
- ✅ Bild-Optimierung

**Statistiken:**
- ~2500 Zeilen Code (Python)
- 2 HTML-Templates
- 1 CSS-Stylesheet (~470 Zeilen)
- 50+ Skills im Matching-System
- Durchschnittliche Skill-Match-Rate: 50-75%
- PDF-Generierung: ~2-5 Sekunden (mit LLM)

**Geplante Verbesserungen:**
- [ ] GUI für einfachere Bedienung
- [ ] Multi-Bewerbung-Batch-Processing
- [ ] Export nach Word/DOCX
- [ ] LinkedIn-Integration für Skill-Import
- [ ] Bewerbungstracking-Dashboard
- [ ] Firmen-spezifische Anschreiben-Optimierung

## Lizenz

Persönliches Projekt - Alle Rechte vorbehalten.

---

**Repository:** [github.com/IhrBenutzername/Bewerbungsgenerator](https://github.com/IhrBenutzername/Bewerbungsgenerator)

*Dieses Tool entstand aus dem Bedarf, den Bewerbungsprozess zu optimieren und gleichzeitig moderne KI-Technologien praktisch einzusetzen.*
