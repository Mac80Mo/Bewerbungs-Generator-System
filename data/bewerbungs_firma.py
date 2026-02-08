#!/usr/bin/env python3
"""
Bewerbungs-Firma Modul
======================
Extrahiert und verarbeitet Daten aus Stellenanzeigen.
Nutzt Regex für Basisdaten und Ollama LLM für intelligente Analyse.

Autor: Marcus Moser
Datum: 04.02.2026
"""

import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict

# Importiere persönliche Skills für Matching
try:
    from persoenliche_daten import KENNTNISSE, SOFTSKILLS, ZERTIFIKATE, WEITERBILDUNGEN
except ImportError:
    from data.persoenliche_daten import KENNTNISSE, SOFTSKILLS, ZERTIFIKATE, WEITERBILDUNGEN


# ============================================================================
# DATENSTRUKTUREN
# ============================================================================

@dataclass
class FirmenDaten:
    """Strukturierte Firmendaten aus der Stellenanzeige"""
    name: str = ""
    standort: str = ""
    strasse: str = ""
    plz: str = ""
    ort: str = ""
    branche: str = ""
    website: str = ""
    ansprechpartner: str = ""
    email: str = ""
    telefon: str = ""


@dataclass
class StellenDaten:
    """Strukturierte Stellendaten"""
    titel: str = ""
    referenznummer: str = ""
    abteilung: str = ""
    arbeitszeit: str = "Vollzeit"
    befristung: str = ""
    eintrittsdatum: str = "zum nächstmöglichen Zeitpunkt"
    homeoffice: str = ""
    gehalt: str = ""


@dataclass
class Anforderungen:
    """Kategorisierte Anforderungen"""
    must_have: list = field(default_factory=list)
    nice_to_have: list = field(default_factory=list)
    soft_skills: list = field(default_factory=list)
    ausbildung: list = field(default_factory=list)
    erfahrung: list = field(default_factory=list)


@dataclass
class SkillMatch:
    """Ein gematchter Skill"""
    skill: str
    relevanz: float
    mein_level: int
    kategorie: str
    aus_anforderung: str


@dataclass
class MatchingErgebnis:
    """Ergebnis des Skill-Matchings"""
    deckungsgrad: float = 0.0
    matched_skills: list = field(default_factory=list)
    fehlende_skills: list = field(default_factory=list)
    top_matches: list = field(default_factory=list)


@dataclass
class BewerbungsFirma:
    """Hauptcontainer für alle extrahierten Daten"""
    firma: FirmenDaten = field(default_factory=FirmenDaten)
    stelle: StellenDaten = field(default_factory=StellenDaten)
    anforderungen: Anforderungen = field(default_factory=Anforderungen)
    matching: MatchingErgebnis = field(default_factory=MatchingErgebnis)
    rohtext: str = ""
    analysiert_am: str = field(default_factory=lambda: datetime.now().strftime("%d.%m.%Y %H:%M"))
    
    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary für JSON-Export"""
        return asdict(self)
    
    def to_bewerbung_dict(self) -> dict:
        """Konvertiert zu Format für persoenliche_daten.BEWERBUNG"""
        return {
            "firma": self.firma.name,
            "ansprechpartner": self.firma.ansprechpartner,
            "position": self.stelle.titel or "Fachinformatiker Anwendungsentwicklung",
            "strasse": self.firma.strasse,
            "plz": self.firma.plz,
            "ort": self.firma.ort,
            "datum": datetime.now().strftime("%d.%m.%Y"),
        }


# ============================================================================
# OLLAMA LLM INTEGRATION
# ============================================================================

class OllamaClient:
    """Client für lokales Ollama LLM"""
    
    DEFAULT_MODEL = "mistral:7b"  # Bessere deutsche Grammatik
    FALLBACK_MODELS = ["llama3.2:3b", "mistral", "llama3.1:8b", "gemma2:9b"]
    
    def __init__(self, model: Optional[str] = None):
        self.model = model or self.DEFAULT_MODEL
        self._available = None
    
    def is_available(self) -> bool:
        """Prüft ob Ollama verfügbar ist"""
        if self._available is not None:
            return self._available
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            self._available = result.returncode == 0
            return self._available
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self._available = False
            return False
    
    def get_available_model(self) -> Optional[str]:
        """Findet ein verfügbares Modell"""
        if not self.is_available():
            return None
        
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            installed_models = result.stdout.lower()
            
            # Prüfe bevorzugtes Modell
            if self.model.split(":")[0] in installed_models:
                return self.model
            
            # Prüfe Fallback-Modelle
            for model in self.FALLBACK_MODELS:
                if model.split(":")[0] in installed_models:
                    return model
            
            return None
        except Exception:
            return None
    
    def query(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.3) -> Optional[str]:
        """Führt eine LLM-Abfrage aus"""
        model = self.get_available_model()
        if not model:
            return None
        
        try:
            # Baue den Befehl
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            
            result = subprocess.run(
                ["ollama", "run", model, full_prompt],
                capture_output=True,
                text=True,
                timeout=180  # 3 Minuten für mistral:7b
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"⚠️  LLM-Fehler: {e}")
            return None


# ============================================================================
# REGEX-BASIERTE EXTRAKTION (Fallback & Basisdaten)
# ============================================================================

class RegexExtractor:
    """Extrahiert Basisdaten mit Regex-Patterns"""
    
    # Patterns für deutsche Stellenanzeigen
    PATTERNS = {
        # Firma - verbesserte Patterns
        "firma_name": [
            r"^([A-ZÄÖÜ][A-Za-zäöüßÄÖÜ\s&\-\.]+(?:GmbH|AG|SE|KG|OHG|UG|e\.V\.|mbH|& Co\. KG|GmbH & Co\.))\s*$",
            r"(?:bei der|bei|für die|für|Firma|Unternehmen|Arbeitgeber)[:\s]+([A-ZÄÖÜ][A-Za-zäöüßÄÖÜ\s&\-\.]+(?:GmbH|AG|SE|KG|OHG|UG))",
            r"([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-Za-zäöüß]+)*\s+(?:GmbH|AG|SE|KG|OHG|UG|GmbH & Co\. KG))",
        ],
        "plz_ort": [
            r"(\d{5})\s+([A-ZÄÖÜ][a-zäöüß]+(?:\s+[a-zäöüß]+)?)",
        ],
        "strasse": [
            r"(?:Adresse:|Straße:|Str\.:|Anschrift:)?\s*([A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.|weg|allee|platz|ring|gasse|anlage)\.?\s*\d+[a-zA-Z]?(?:/\d+)?)",
            r"([A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.|weg|allee|platz|ring|gasse|anlage)\.?\s*\d+[a-zA-Z]?(?:/\d+)?)",
        ],
        "email": [
            r"[\w.+-]+@[\w-]+\.[\w.-]+",
        ],
        "telefon": [
            r"(?:Tel\.?|Telefon|Phone)[:\s]*([+\d\s/()-]{10,})",
            r"(\+49[\s\d/()-]{10,})",
            r"(0\d{2,4}[\s/()-]?\d{4,}[\s/()-]?\d{0,4})",
        ],
        "website": [
            r"(?:www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,})",
            r"(?:https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)",
        ],
        # Ansprechpartner
        "ansprechpartner": [
            r"(?:Ansprechpartner(?:in)?|Kontakt|Ihr Kontakt)[:\s]*([A-ZÄÖÜ][a-zäöüß.\s]+(?:Dr\.|Prof\.)?\s+[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)",
            r"(?:Herr|Frau)\s+((?:Dr\.|Prof\.)?\s*[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)+?)(?:\s*\n|$)",
        ],
        # Stelle - verbesserte Jobtitel-Erkennung
        "jobtitel": [
            r"^((?:Junior|Senior|Lead|Full[ -]?Stack|Backend|Frontend)?\s*[A-Za-zäöüÄÖÜ\-]+\s*(?:Developer|Entwickler|Engineer|Programmierer|Architect|Consultant|Manager|Analyst|Administrator|DevOps|Specialist|Expert)(?:\s*\([mwfd/]+\))?)",
            r"(?:als|Position(?::|))\s+((?:Junior|Senior|Lead)?\s*[A-Za-zäöüÄÖÜ\s\-]+(?:Developer|Entwickler|Engineer|Programmierer)(?:\s*\([mwfd/]+\))?)",
            r"(?:suchen(?:\s+wir)?(?:\s+eine?n?)?)\s+((?:Junior|Senior)?\s*[A-Za-zäöüÄÖÜ\s\-]+(?:Developer|Entwickler|Engineer))",
        ],
        "referenznummer": [
            r"(?:Referenz(?:nummer)?|Kennziffer|Job-?ID)[:\s#]*([A-Z0-9-]+)",
        ],
        # Arbeitszeit
        "arbeitszeit": [
            r"\b(Vollzeit|Teilzeit|Full[ -]?time|Part[ -]?time)\b",
            r"(\d{1,2}\s*(?:bis|-)\s*\d{1,2}\s*(?:Stunden|h)\s*/\s*Woche)",
        ],
        "homeoffice": [
            r"((?:\d{1,3}\s*%?\s*)?(?:Home\s*Office|Remote|Homeoffice|mobiles Arbeiten))",
            r"(hybrid(?:es Arbeiten)?)",
        ],
        "gehalt": [
            r"(\d{2,3}\.?\d{3}\s*(?:€|EUR|Euro)(?:\s*(?:bis|-)\s*\d{2,3}\.?\d{3}\s*(?:€|EUR|Euro))?)",
            r"((?:ab|bis zu|ca\.?)?\s*\d{2,3}[.,]?\d{3}\s*(?:€|EUR|Euro))",
        ],
    }
    
    # Keywords für Anforderungen
    SKILL_KEYWORDS = {
        "programmiersprachen": [
            "python", "java", "javascript", "typescript", "c#", "c++", 
            "php", "ruby", "go", "rust", "kotlin", "swift", "sql", "nosql"
        ],
        "frameworks": [
            "react", "angular", "vue", "node", "express", "django", "flask",
            "spring", "springboot", "fastapi", ".net", "laravel", "rails",
            "next.js", "nuxt", "svelte", "bootstrap", "tailwind", "angularjs"
        ],
        "tools": [
            "git", "github", "gitlab", "docker", "kubernetes", "aws", "azure",
            "jenkins", "jira", "confluence", "linux", "postgresql", "mysql",
            "mongodb", "redis", "elasticsearch", "terraform", "ansible",
            # Testing Tools
            "cypress", "playwright", "selenium", "jest", "mocha", "jasmine",
            "junit", "testng", "pytest", "xray",
            # State Management
            "redux", "pinia", "vuex", "rxjs", "mobx",
            # CI/CD & Deployment
            "gitlab ci", "github actions", "circleci", "travis"
        ],
        "methoden": [
            "agile", "scrum", "kanban", "devops", "ci/cd", "tdd", "bdd",
            "rest", "api", "microservices", "clean code", "solid"
        ]
    }
    
    # Marker für Must-Have Anforderungen
    MUST_HAVE_MARKERS = [
        "erforderlich", "vorausgesetzt", "zwingend", "notwendig",
        "voraussetzung", "benötigt", "erfahrung mit", "kenntnisse in",
        "know-how", "abgeschlossen", "setzen voraus"
    ]
    
    # Marker für Nice-to-Have Anforderungen
    NICE_TO_HAVE_MARKERS = [
        "idealerweise", "wünschenswert", "von vorteil", "plus", "gerne",
        "optional", "nicht zwingend", "nicht erforderlich", "nice to have",
        "hilfreich", "bevorzugt", "schön wäre"
    ]
    
    def extract_all(self, text: str) -> BewerbungsFirma:
        """Extrahiert alle Basisdaten aus dem Text"""
        result = BewerbungsFirma(rohtext=text)
        
        # Firma
        result.firma.name = self._find_first(text, self.PATTERNS["firma_name"])
        result.firma.email = self._find_first(text, self.PATTERNS["email"])
        result.firma.telefon = self._find_first(text, self.PATTERNS["telefon"])
        result.firma.website = self._find_first(text, self.PATTERNS["website"])
        result.firma.ansprechpartner = self._find_first(text, self.PATTERNS["ansprechpartner"])
        result.firma.strasse = self._find_first(text, self.PATTERNS["strasse"])
        
        # PLZ/Ort
        plz_ort = self._find_first(text, self.PATTERNS["plz_ort"], group=0)
        if plz_ort:
            match = re.search(r"(\d{5})\s+(.+)", plz_ort)
            if match:
                result.firma.plz = match.group(1)
                result.firma.ort = match.group(2)
        
        # Stelle
        result.stelle.titel = self._find_first(text, self.PATTERNS["jobtitel"])
        result.stelle.referenznummer = self._find_first(text, self.PATTERNS["referenznummer"])
        result.stelle.arbeitszeit = self._find_first(text, self.PATTERNS["arbeitszeit"]) or "Vollzeit"
        result.stelle.homeoffice = self._find_first(text, self.PATTERNS["homeoffice"])
        result.stelle.gehalt = self._find_first(text, self.PATTERNS["gehalt"])
        
        # Anforderungen (Keyword-basiert)
        result.anforderungen = self._extract_requirements(text)
        
        return result
    
    def _find_first(self, text: str, patterns: list, group: int = 1) -> str:
        """Findet den ersten Match aus einer Liste von Patterns"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    result = match.group(group).strip()
                    # Bereinige ungewollte Zeilenumbrüche und nachfolgende Wörter
                    result = re.split(r'\n|Adresse|E-?Mail|Telefon|Website', result)[0].strip()
                    return result
                except IndexError:
                    return match.group(0).strip()
        return ""
    
    def _extract_requirements(self, text: str) -> Anforderungen:
        """Extrahiert Anforderungen basierend auf Keywords und Struktur"""
        anforderungen = Anforderungen()
        text_lower = text.lower()
        
        # Extrahiere Profil-Sektion (enthält die eigentlichen Anforderungen)
        profil_section = self._extract_profil_section(text)
        has_profil = bool(profil_section)
        profil_lower = profil_section.lower() if profil_section else ""
        
        # Tracking für Duplikate (case-insensitive)
        seen_skills = {}  # lowercase -> (original, typ)
        
        # Technische Skills
        for category, keywords in self.SKILL_KEYWORDS.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # Prüfe zuerst im Profil-Abschnitt
                if has_profil and re.search(rf"\b{re.escape(keyword)}\b", profil_lower):
                    # Im Profil gefunden - prüfe ob explizit "nice to have"
                    if self._is_nice_to_have(profil_lower, keyword):
                        typ = "nice_to_have"
                        target_list = anforderungen.nice_to_have
                    else:
                        # Im Profil ohne "idealerweise" etc. = Must-Have!
                        typ = "must_have"
                        target_list = anforderungen.must_have
                    
                    # Duplikatscheck: Bevorzuge Must-Have
                    if keyword_lower in seen_skills:
                        old_keyword, old_typ = seen_skills[keyword_lower]
                        if old_typ == "nice_to_have" and typ == "must_have":
                            # Upgrade von Nice-to-Have zu Must-Have
                            if old_keyword in anforderungen.nice_to_have:
                                anforderungen.nice_to_have.remove(old_keyword)
                            if keyword not in anforderungen.must_have:
                                anforderungen.must_have.append(keyword)
                            seen_skills[keyword_lower] = (keyword, typ)
                        # Sonst: Behalte den ersten (höherwertigen) Eintrag
                    else:
                        # Neu hinzufügen
                        if keyword not in target_list:
                            target_list.append(keyword)
                        seen_skills[keyword_lower] = (keyword, typ)
                        
                # Sonst prüfe im gesamten Text (nur wenn noch nicht als Must-Have erfasst)
                elif re.search(rf"\b{re.escape(keyword)}\b", text_lower):
                    if keyword_lower not in seen_skills:
                        # Außerhalb Profil = Nice-to-Have
                        if keyword not in anforderungen.nice_to_have:
                            anforderungen.nice_to_have.append(keyword)
                        seen_skills[keyword_lower] = (keyword, "nice_to_have")
        
        # Soft Skills
        soft_skill_keywords = [
            "teamfähig", "kommunikativ", "selbstständig", "eigenverantwortlich",
            "flexibel", "belastbar", "zuverlässig", "engagiert", "motiviert",
            "lernbereit", "analytisch", "strukturiert", "kreativ"
        ]
        for skill in soft_skill_keywords:
            if skill in text_lower:
                anforderungen.soft_skills.append(skill.capitalize())
        
        return anforderungen
    
    def _extract_profil_section(self, text: str) -> str:
        """Extrahiert die Profil/Anforderungs-Sektion aus der Stellenanzeige"""
        # Suche nach typischen Profil-Überschriften
        profil_patterns = [
            r'Profil\s*\n\n(.*?)(?=\n\n(?:Wir bieten|Benefits|Kontakt|Bewerbung|$))',
            r'(?:Ihr Profil|Ihre Qualifikation|Anforderungen|Was Sie mitbringen)\s*[:\n]+(.*?)(?=\n\n(?:Wir bieten|Benefits|Das bieten wir|Unser Angebot|$))',
            r'(?:Das bringen Sie mit|Ihre Skills)\s*[:\n]+(.*?)(?=\n\n)',
        ]
        
        for pattern in profil_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def _is_nice_to_have(self, text: str, keyword: str) -> bool:
        """Prüft ob ein Skill explizit als 'nice to have' markiert ist"""
        # Suche in einem Fenster um das Keyword
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return False
        
        window_start = max(0, keyword_pos - 150)
        window_end = min(len(text), keyword_pos + 150)
        window = text[window_start:window_end]
        
        # Prüfe auf Nice-to-Have Marker
        for marker in self.NICE_TO_HAVE_MARKERS:
            if re.search(marker, window):
                return True
        
        return False


# ============================================================================
# LLM-BASIERTE ANALYSE
# ============================================================================

class LLMAnalyzer:
    """Nutzt Ollama für intelligente Textanalyse"""
    
    def __init__(self):
        self.client = OllamaClient()
        self.is_available = self.client.is_available()
    
    def analyze_stellenanzeige(self, text: str) -> Optional[dict]:
        """Analysiert Stellenanzeige mit LLM"""
        if not self.is_available:
            return None
        
        system_prompt = """Du bist ein Experte für die Analyse von deutschen Stellenanzeigen.
Extrahiere präzise alle technischen Anforderungen und Skills.
Antworte AUSSCHLIESSLICH mit validem JSON, keine zusätzlichen Erklärungen."""
        
        prompt = f"""Analysiere diese Stellenanzeige und extrahiere ALLE technischen Anforderungen:

{text}

WICHTIGE REGELN:
1. MUST_HAVE: Alle Skills die im "Profil"-Abschnitt stehen (außer explizit als "idealerweise", "wünschenswert", "Plus" markiert)
2. NICE_TO_HAVE: Skills mit Markern wie "idealerweise", "wünschenswert", "von Vorteil", "Plus", "nicht zwingend"
3. Extrahiere ALLE genannten Technologien, auch wenn sie in Klammern oder Beispielen stehen
4. Beispiele für Tools: Redux, Pinia, RxJS, Cypress, Playwright, Selenium, Jira Xray
5. Ignoriere den "Aufgaben"-Abschnitt (beschreibt Tätigkeiten, keine Anforderungen)

Antworte NUR mit diesem JSON-Format:
{{
    "firma": {{
        "name": "Firmenname",
        "branche": "Branche falls genannt"
    }},
    "stelle": {{
        "titel": "Jobtitel",
        "arbeitszeit": "Vollzeit/Teilzeit"
    }},
    "anforderungen": {{
        "must_have": ["skill1", "skill2", "skill3", ...],
        "nice_to_have": ["skill4", "skill5", ...],
        "soft_skills": ["teamfähig", ...],
        "ausbildung": ["Studium", "Ausbildung", ...]
    }}
}}"""
        
        response = self.client.query(prompt, system_prompt, temperature=0.2)
        
        if response:
            try:
                # Extrahiere JSON aus Antwort
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return None
    
    def generate_skill_paragraphs(self, matches: list, firma_name: str, position: str, ansprechpartner: str = "Damen und Herren") -> Optional[str]:
        """Generiert vollständiges Anschreiben mit 4 Absätzen"""
        if not self.is_available or not matches:
            return None
        
        # Dedupliziere Skills (behalte nur ersten Match pro Skill)
        seen_skills = set()
        unique_matches = []
        for m in matches[:5]:
            if m['skill'] not in seen_skills:
                seen_skills.add(m['skill'])
                unique_matches.append(m)
        
        # Top 3 Skills für Absatz 3
        top_skills = unique_matches[:3]
        skills_text = ", ".join([m['skill'] for m in top_skills])
        
        # Anrede vorbereiten
        # Prüfe ob ansprechpartner eine echte Person ist (nicht Firma oder generisch)
        is_valid_person = (
            ansprechpartner and 
            ansprechpartner not in ['Damen und Herren', '', 'Nicht erkannt', firma_name] and
            not any(suffix in ansprechpartner for suffix in ['GmbH', 'AG', 'SE', 'KG', 'UG', 'e.V.', 'mbH'])
        )
        
        if is_valid_person:
            # Echte Person gefunden
            if ansprechpartner.startswith('Herr'):
                anrede = f"Sehr geehrter {ansprechpartner}"
            elif ansprechpartner.startswith('Frau'):
                anrede = f"Sehr geehrte {ansprechpartner}"
            else:
                # Falls nur Name ohne Herr/Frau
                anrede = f"Sehr geehrte/r {ansprechpartner}"
        else:
            # Kein Ansprechpartner oder Firma als Ansprechpartner
            anrede = "Sehr geehrte Damen und Herren"
        
        system_prompt = """Du bist professioneller Bewerbungsschreiber.
Schreibe kurz, knapp, freundlich und professionell.
Perfekte deutsche Grammatik, aktive Formulierungen."""
        
        prompt = f"""Schreibe den Haupttext eines Bewerbungsanschreibens (4 Absätze, max. 10 Sätze).

TONALITÄT: Kurz, knapp, freundlich, professionell

GRAMMATIK:
- Perfekt-Zeitform: "habe entwickelt", "habe abgeschlossen"
- Komma vor Relativsätzen
- Aktive Formulierungen (kein "würde", "könnte")

VERBOTEN: "kennengelernt", "beschäftigt", "würde gerne", "könnte bieten"
VERWENDEN: "gearbeitet mit", "entwickelt", "freue mich auf", "bringe mit"

STRUKTUR (genau 4 Absätze):

ABSATZ 1 (Einleitung, 1 Satz):
ich beziehe mich auf Ihre Stellenausschreibung "{position}" und bewerbe mich hiermit um diese Position.

ABSATZ 2 (Qualifikation, 2-3 Sätze):
Meine Ausbildung zum Fachinformatiker Anwendungsentwicklung habe ich erfolgreich abgeschlossen, mit Schwerpunkt auf Künstliche Intelligenz und Web-Entwicklung. Das Thema Anwendungsentwicklung fasziniert mich, weshalb ich mich kontinuierlich in verschiedenen IT-Bereichen weiterbilde.

ABSATZ 3 (Skill-Match, 2-3 Sätze):
Besonders relevant für diese Position sind meine Kenntnisse in {skills_text}. Weitere Details zu meinen Projekten und Erfahrungen finden Sie in meinem Lebenslauf.

ABSATZ 4 (Abschluss, 1 Satz):
Ich freue mich auf die Möglichkeit, mich persönlich vorzustellen.

WICHTIG:
- KEINE Anrede schreiben (kommt separat ins Dokument)
- Starte direkt mit "ich beziehe mich..." (Kleinschreibung nach Anrede!)
- MAX. 10 Sätze gesamt
- Anrede ist vorgegeben: {anrede}
- In Absatz 3 MÜSSEN alle 3 Skills genannt werden: {skills_text}
- KEINE konkreten Beispiele, nur Verweis auf Lebenslauf
- Kurze, prägnante Sätze

Schreibe NUR die 4 Absätze:"""
        
        # Generiere Anschreiben-Text (ohne zweite Korrektur-Stufe)
        anschreiben_text = self.client.query(prompt, system_prompt, temperature=0.3)
        
        if not anschreiben_text or len(anschreiben_text) < 100:
            return None
        
        return anschreiben_text.strip()
    
    def optimize_anschreiben(self, template: str, firma_data: 'BewerbungsFirma') -> Optional[str]:
        """Optimiert das gesamte Anschreiben basierend auf der Analyse"""
        if not self.is_available:
            return None
        
        anforderungen = ", ".join(
            firma_data.anforderungen.must_have[:5] + 
            firma_data.anforderungen.nice_to_have[:3]
        )
        
        top_matches = ", ".join([
            m['skill'] for m in firma_data.matching.top_matches[:5]
        ])
        
        system_prompt = """Du bist ein professioneller Karriereberater.
Optimiere Bewerbungsanschreiben so, dass sie perfekt zur Stellenausschreibung passen.
Behalte die Grundstruktur bei, passe aber Formulierungen an."""
        
        deckungsgrad_text = f"{firma_data.matching.deckungsgrad:.1f}%"
        
        prompt = f"""Optimiere dieses Anschreiben für folgende Stelle:

Firma: {firma_data.firma.name}
Position: {firma_data.stelle.titel}
Gesuchte Skills: {anforderungen}
Meine passenden Skills: {top_matches}
Deckungsgrad: {deckungsgrad_text}

Aktuelles Anschreiben:
{template[:2000]}

Gib das optimierte Anschreiben zurück. Passe die Formulierungen an, um:
1. Die gesuchten Skills explizit zu erwähnen
2. Konkrete Bezüge zur Firma herzustellen
3. Die Relevanz meiner Erfahrung zu betonen"""
        
        return self.client.query(prompt, system_prompt, temperature=0.5)


# ============================================================================
# SKILL MATCHING
# ============================================================================

class SkillMatcher:
    """Matched Anforderungen mit eigenen Skills"""
    
    # Synonyme für besseres Matching
    SYNONYME = {
        "javascript": ["js", "ecmascript", "es6", "es2015"],
        "typescript": ["ts"],
        "python": ["py"],
        "postgresql": ["postgres", "psql"],
        "kubernetes": ["k8s"],
        "react": ["reactjs", "react.js"],
        "vue": ["vuejs", "vue.js"],
        "node": ["nodejs", "node.js"],
        "git": ["github", "gitlab", "bitbucket"],
        "agile": ["scrum", "kanban"],
        "linux": ["unix", "bash", "shell"],
    }
    
    def __init__(self):
        self.meine_skills = self._load_my_skills()
    
    def _load_my_skills(self) -> dict:
        """Lädt alle eigenen Skills aus persoenliche_daten.py"""
        skills = {}
        
        for kategorie, skill_liste in KENNTNISSE.items():
            for skill in skill_liste:
                name = skill["name"].lower()
                skills[name] = {
                    "name": skill["name"],
                    "level": skill["level"],
                    "kategorie": kategorie
                }
                
                # Füge auch einzelne Teile hinzu (z.B. "Git/GitHub" -> "git", "github")
                for part in re.split(r'[/,\s]+', name):
                    if len(part) > 1 and part not in skills:
                        skills[part] = {
                            "name": skill["name"],
                            "level": skill["level"],
                            "kategorie": kategorie
                        }
        
        # Füge Soft Skills hinzu
        for soft_skill in SOFTSKILLS:
            skills[soft_skill.lower()] = {
                "name": soft_skill,
                "level": 80,  # Annahme: Soft Skills werden hoch bewertet
                "kategorie": "soft_skills"
            }
        
        return skills
    
    def match(self, anforderungen: Anforderungen) -> MatchingErgebnis:
        """Führt das Skill-Matching durch"""
        ergebnis = MatchingErgebnis()
        
        alle_anforderungen = (
            [(s, "must_have") for s in anforderungen.must_have] +
            [(s, "nice_to_have") for s in anforderungen.nice_to_have] +
            [(s, "soft_skill") for s in anforderungen.soft_skills]
        )
        
        if not alle_anforderungen:
            return ergebnis
        
        matched = []
        missing = []
        
        for anforderung, typ in alle_anforderungen:
            match_result = self._find_match(anforderung.lower())
            
            if match_result:
                relevanz = 1.0 if typ == "must_have" else (0.7 if typ == "nice_to_have" else 0.5)
                matched.append({
                    "skill": match_result["name"],
                    "relevanz": relevanz,
                    "mein_level": match_result["level"],
                    "kategorie": match_result["kategorie"],
                    "aus_anforderung": anforderung
                })
            else:
                missing.append({
                    "skill": anforderung,
                    "typ": typ
                })
        
        ergebnis.matched_skills = matched
        ergebnis.fehlende_skills = missing
        
        # Berechne Deckungsgrad (gewichtet)
        if alle_anforderungen:
            total_weight = sum(1.0 if t == "must_have" else 0.5 for _, t in alle_anforderungen)
            matched_weight = sum(m["relevanz"] for m in matched)
            ergebnis.deckungsgrad = (matched_weight / total_weight * 100) if total_weight > 0 else 0
        
        # Top Matches: Dedupliziere und sortiere nach Score
        # Behalte nur den besten Match pro Skill
        best_matches = {}
        for m in matched:
            skill = m["skill"]
            # Must-Have Boosting: Must-Haves erhalten +25 Bonus-Punkte
            # Soft-Skill Dämpfung: Soft-Skills nur 70% vom berechneten Score
            base_score = m["relevanz"] * m["mein_level"]
            
            if m["relevanz"] == 1.0:  # Must-Have
                score = base_score + 25  # Boost für Must-Haves
            elif m["kategorie"] == "soft_skills":
                score = base_score * 0.7  # Dämpfung für Soft-Skills
            else:
                score = base_score
            
            if skill not in best_matches or score > best_matches[skill]["score"]:
                best_matches[skill] = {**m, "score": score}
        
        # Sortiere nach Score absteigend
        ergebnis.top_matches = sorted(
            best_matches.values(),
            key=lambda x: x["score"],
            reverse=True
        )[:5]
        
        # Entferne Score aus Ergebnis (nur für Sortierung verwendet)
        for match in ergebnis.top_matches:
            match.pop("score", None)
        
        return ergebnis
    
    def _find_match(self, anforderung: str) -> Optional[dict]:
        """Findet einen passenden eigenen Skill"""
        anforderung_clean = anforderung.strip().lower()
        
        # Direkte Übereinstimmung
        if anforderung_clean in self.meine_skills:
            return self.meine_skills[anforderung_clean]
        
        # Prüfe Synonyme
        for haupt_skill, synonyme in self.SYNONYME.items():
            if anforderung_clean in synonyme or anforderung_clean == haupt_skill:
                if haupt_skill in self.meine_skills:
                    return self.meine_skills[haupt_skill]
                for syn in synonyme:
                    if syn in self.meine_skills:
                        return self.meine_skills[syn]
        
        # Teilübereinstimmung
        for skill_key, skill_data in self.meine_skills.items():
            if anforderung_clean in skill_key or skill_key in anforderung_clean:
                return skill_data
        
        return None


# ============================================================================
# HAUPT-INTERFACE
# ============================================================================

class StellenanzeigenAnalyzer:
    """Hauptklasse für die Analyse von Stellenanzeigen"""
    
    def __init__(self, use_llm: bool = True):
        self.regex_extractor = RegexExtractor()
        self.skill_matcher = SkillMatcher()
        self.use_llm = use_llm
        self.llm_analyzer = LLMAnalyzer() if use_llm else None
        
        # Cache für analysierte Stellen
        self.cache_dir = Path(__file__).parent.parent / "output" / "analysen"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze(self, stellenanzeige_text: str) -> BewerbungsFirma:
        """Analysiert eine Stellenanzeige vollständig"""
        print("🔍 Analysiere Stellenanzeige...")
        
        # 1. Basis-Extraktion mit Regex
        print("  📝 Extrahiere Basisdaten (Regex)...")
        result = self.regex_extractor.extract_all(stellenanzeige_text)
        
        # 2. LLM-Analyse (wenn verfügbar)
        if self.use_llm and self.llm_analyzer and self.llm_analyzer.is_available:
            print("  🤖 Analysiere mit LLM (Ollama)...")
            llm_result = self.llm_analyzer.analyze_stellenanzeige(stellenanzeige_text)
            
            if llm_result:
                # Merge LLM-Ergebnisse (überschreiben leere Felder)
                self._merge_llm_results(result, llm_result)
        else:
            print("  ⚠️  LLM nicht verfügbar, nutze nur Regex-Extraktion")
        
        # 3. Skill-Matching
        print("  🎯 Führe Skill-Matching durch...")
        result.matching = self.skill_matcher.match(result.anforderungen)
        
        # 4. Prüfe auf fehlende wichtige Daten
        self._check_missing_data(result)
        
        print(f"  ✅ Analyse abgeschlossen! Deckungsgrad: {result.matching.deckungsgrad:.1f}%")
        
        return result
    
    def _merge_llm_results(self, result: BewerbungsFirma, llm_data: dict):
        """Merged LLM-Ergebnisse in das Hauptergebnis (LLM hat Priorität bei Anforderungen)"""
        if "firma" in llm_data:
            for key, value in llm_data["firma"].items():
                if value and hasattr(result.firma, key) and not getattr(result.firma, key):
                    setattr(result.firma, key, value)
        
        if "stelle" in llm_data:
            for key, value in llm_data["stelle"].items():
                if value and hasattr(result.stelle, key) and not getattr(result.stelle, key):
                    setattr(result.stelle, key, value)
        
        if "anforderungen" in llm_data:
            anf = llm_data["anforderungen"]
            
            # LLM-Ergebnisse haben Priorität - überschreibe komplett wenn LLM etwas gefunden hat
            if "must_have" in anf and len(anf["must_have"]) > 0:
                # Verwende LLM must_haves, füge Regex-Ergebnisse nur hinzu wenn nicht drin
                llm_must = [s.lower() for s in anf["must_have"]]
                result.anforderungen.must_have = anf["must_have"].copy()
                
                # Füge Regex-must_haves hinzu die LLM nicht gefunden hat
                for s in result.anforderungen.must_have:
                    if s.lower() not in llm_must:
                        result.anforderungen.must_have.append(s)
            
            if "nice_to_have" in anf and len(anf["nice_to_have"]) > 0:
                # Merge nice_to_have
                for s in anf["nice_to_have"]:
                    if s not in result.anforderungen.nice_to_have:
                        result.anforderungen.nice_to_have.append(s)
            
            if "soft_skills" in anf:
                result.anforderungen.soft_skills.extend([
                    s for s in anf["soft_skills"]
                    if s not in result.anforderungen.soft_skills
                ])
    
    def _check_missing_data(self, result: BewerbungsFirma):
        """Prüft auf fehlende wichtige Daten und gibt Hinweise"""
        missing = []
        
        # Prüfe Firmendaten
        if not result.firma.name or result.firma.name == "Nicht erkannt":
            missing.append("Firmenname")
        if not result.firma.strasse:
            missing.append("Straße/Hausnummer")
        
        # KRITISCH: Prüfe Anforderungen
        if not result.anforderungen.must_have and not result.anforderungen.nice_to_have:
            print("\n⚠️  KRITISCHE WARNUNG: Keine technischen Anforderungen gefunden!")
            print("   → Prüfe ob die Stellenanzeige einen 'Profil' oder 'Anforderungen' Abschnitt hat")
        elif not result.anforderungen.must_have:
            print("\n⚠️  WARNUNG: Keine Must-Have Skills gefunden!")
            print(f"   → Alle {len(result.anforderungen.nice_to_have)} Skills wurden als Nice-to-Have klassifiziert")
            print("   → Falls dies falsch ist, prüfe die Profil-Sektion der Stellenanzeige")
        else:
            print(f"\n✅ Anforderungen extrahiert:")
            print(f"   Must-Have: {len(result.anforderungen.must_have)} Skills")
            print(f"   Nice-to-Have: {len(result.anforderungen.nice_to_have)} Skills")
        
        if not result.firma.plz:
            missing.append("PLZ")
        if not result.firma.ort:
            missing.append("Ort")
        if not result.firma.ansprechpartner or result.firma.ansprechpartner == "Nicht erkannt":
            missing.append("Ansprechpartner")
        
        # Gib Hinweise aus
        if missing:
            print("\n  ⚠️  FEHLENDE ADRESSDATEN:")
            for item in missing:
                print(f"     - {item}")
            print(f"\n  💡 Tipp: Ergänze die fehlenden Daten in der Eingabedatei")
            print(f"     und führe die Analyse erneut aus.")
    
    def save_analysis(self, result: BewerbungsFirma, filename: Optional[str] = None) -> Path:
        """Speichert die Analyse als JSON"""
        if not filename:
            safe_name = re.sub(r'[^\w\-]', '_', result.firma.name or "unbekannt")
            filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.cache_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"💾 Analyse gespeichert: {filepath}")
        return filepath
    
    def generate_anschreiben_text(self, result: BewerbungsFirma) -> Optional[str]:
        """Generiert optimierten Anschreiben-Text"""
        if not self.llm_analyzer or not self.llm_analyzer.is_available:
            return None
        
        return self.llm_analyzer.generate_skill_paragraphs(
            result.matching.top_matches,
            result.firma.name,
            result.stelle.titel
        )


# ============================================================================
# INTERAKTIVES INPUT-INTERFACE
# ============================================================================

def input_stellenanzeige() -> str:
    """Interaktive Eingabe einer Stellenanzeige"""
    print("\n" + "="*60)
    print("📋 STELLENANZEIGEN-EINGABE")
    print("="*60)
    print("Füge den Text der Stellenanzeige ein.")
    print("Beende die Eingabe mit einer Leerzeile gefolgt von 'END'")
    print("-"*60)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        except EOFError:
            break
    
    return "\n".join(lines)


def print_analysis_report(result: BewerbungsFirma):
    """Gibt einen formatierten Analysebericht aus"""
    print("\n" + "="*60)
    print("📊 ANALYSEBERICHT")
    print("="*60)
    
    # Sammle fehlende Daten
    missing_data = []
    if not result.firma.name or result.firma.name == "Nicht erkannt":
        missing_data.append("Firmenname")
    if not result.firma.strasse:
        missing_data.append("Straße")
    if not result.firma.plz:
        missing_data.append("PLZ")
    if not result.firma.ort:
        missing_data.append("Ort")
    if not result.firma.ansprechpartner or result.firma.ansprechpartner == "Nicht erkannt":
        missing_data.append("Ansprechpartner")
    
    print(f"\n🏢 FIRMA")
    print(f"   Name: {result.firma.name or '❌ FEHLT'}")
    print(f"   Standort: {result.firma.ort or '❌ FEHLT'}")
    print(f"   Ansprechpartner: {result.firma.ansprechpartner or '❌ FEHLT'}")
    
    # Zeige vollständige Adresse falls vorhanden
    if result.firma.strasse or result.firma.plz:
        print(f"   Adresse: {result.firma.strasse or '❌ FEHLT'}, {result.firma.plz or '?'} {result.firma.ort or '?'}")
    
    print(f"\n💼 STELLE")
    print(f"   Titel: {result.stelle.titel or 'Nicht erkannt'}")
    print(f"   Arbeitszeit: {result.stelle.arbeitszeit}")
    print(f"   Home Office: {result.stelle.homeoffice or 'Nicht angegeben'}")
    
    print(f"\n📋 ANFORDERUNGEN")
    if result.anforderungen.must_have:
        print(f"   Must-Have: {', '.join(result.anforderungen.must_have[:10])}")
    if result.anforderungen.nice_to_have:
        print(f"   Nice-to-Have: {', '.join(result.anforderungen.nice_to_have[:10])}")
    if result.anforderungen.soft_skills:
        print(f"   Soft Skills: {', '.join(result.anforderungen.soft_skills[:5])}")
    
    print(f"\n🎯 SKILL-MATCHING")
    print(f"   Deckungsgrad: {result.matching.deckungsgrad:.1f}%")
    
    if result.matching.top_matches:
        print(f"\n   Top-Matches:")
        for match in result.matching.top_matches:
            bar = "█" * int(match["mein_level"] / 10) + "░" * (10 - int(match["mein_level"] / 10))
            print(f"   [{bar}] {match['skill']} ({match['mein_level']}%)")
    
    if result.matching.fehlende_skills:
        print(f"\n   ⚠️  Fehlende Skills:")
        for skill in result.matching.fehlende_skills[:5]:
            print(f"      - {skill['skill']} ({skill['typ']})")
    
    # Warnung bei fehlenden Daten
    if missing_data:
        print(f"\n{'='*60}")
        print("⚠️  ACHTUNG: UNVOLLSTÄNDIGE ADRESSDATEN!")
        print("="*60)
        print(f"   Fehlende Informationen: {', '.join(missing_data)}")
        print("\n   💡 Zum Vervollständigen:")
        print("      1. Öffne die Eingabedatei (z.B. input/aktuelle_stellenanzeige.txt)")
        print("      2. Füge die fehlenden Daten am Anfang oder Ende hinzu:")
        print("         Beispiel:")
        print("         ---")
        print("         Firma: Max Mustermann GmbH")
        print("         Ansprechpartner: Herr Thomas Müller")
        print("         Adresse: Hauptstraße 123, 68159 Mannheim")
        print("         ---")
        print("      3. Führe die Analyse erneut aus")
    
    print("\n" + "="*60)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n🚀 Stellenanzeigen-Analyzer gestartet")
    print("-" * 40)
    
    # Prüfe Ollama-Verfügbarkeit
    client = OllamaClient()
    if client.is_available():
        model = client.get_available_model()
        print(f"✅ Ollama verfügbar (Modell: {model})")
    else:
        print("⚠️  Ollama nicht verfügbar - nutze Regex-Fallback")
    
    # Stellenanzeige eingeben
    stellenanzeige = input_stellenanzeige()
    
    if stellenanzeige.strip():
        # Analysieren
        analyzer = StellenanzeigenAnalyzer(use_llm=True)
        result = analyzer.analyze(stellenanzeige)
        
        # Bericht ausgeben
        print_analysis_report(result)
        
        # Speichern
        analyzer.save_analysis(result)
        
        # Bewerbungsdaten ausgeben
        print("\n📝 Für persoenliche_daten.BEWERBUNG:")
        print("-" * 40)
        bewerbung = result.to_bewerbung_dict()
        for key, value in bewerbung.items():
            print(f'    "{key}": "{value}",')
    else:
        print("❌ Keine Eingabe erhalten.")
