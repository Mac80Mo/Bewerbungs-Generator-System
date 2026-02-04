#!/usr/bin/env python3
"""
Hybride Datenextraktion für Bewerbungsgenerator
- Parst meine_daten.md direkt (kein LLM nötig!)
- Extrahiert Zertifikate/Weiterbildungen aus Dateinamen
- Berechnet Skill-Scores aus allen Dokumenten
- Optional: LLM nur für Zeugnisanalyse
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# PDF Support
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


class MarkdownParser:
    """Parst meine_daten.md und extrahiert strukturierte Daten"""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.content = ""
        if filepath.exists():
            self.content = filepath.read_text(encoding='utf-8')
    
    def extract_field(self, pattern: str, default: str = "") -> str:
        """Extrahiert ein Feld mit Regex"""
        match = re.search(pattern, self.content, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        return default
    
    def extract_personal_data(self) -> Dict[str, str]:
        """Extrahiert persönliche Daten"""
        # Patterns für die Felder in meine_daten.md
        data = {
            "vorname": "",
            "nachname": "",
            "titel": "",
            "strasse": "",
            "plz": "",
            "ort": "",
            "telefon": "",
            "email": "",
            "geburtsdatum": "",
            "geburtsort": "",
            "nationalitaet": "Deutsch",
            "github": "",
            "linkedin": "",
            "website": ""
        }
        
        # Name extrahieren
        name_match = re.search(r'\*\*Name:\*\*\s*(.+)', self.content)
        if name_match:
            full_name = name_match.group(1).strip()
            parts = full_name.split()
            if len(parts) >= 2:
                data["vorname"] = parts[0]
                data["nachname"] = " ".join(parts[1:])
        
        # Adresse
        addr_match = re.search(r'\*\*Adresse:\*\*\s*(.+)', self.content)
        if addr_match:
            data["strasse"] = addr_match.group(1).strip()
        
        # PLZ/Ort
        plz_match = re.search(r'\*\*PLZ/Ort:\*\*\s*(\d+)\s+(.+)', self.content)
        if plz_match:
            data["plz"] = plz_match.group(1).strip()
            data["ort"] = plz_match.group(2).strip()
        
        # Kontakt
        data["telefon"] = self.extract_field(r'\*\*Telefon:\*\*\s*(.+)')
        data["email"] = self.extract_field(r'\*\*E-Mail:\*\*\s*(.+)')
        data["geburtsdatum"] = self.extract_field(r'\*\*Geburtsdatum:\*\*\s*(.+)')
        data["geburtsort"] = self.extract_field(r'\*\*Geburtsort:\*\*\s*(.+)')
        
        # Links
        github_match = re.search(r'GitHub:\s*(https?://[^\s]+|github\.com/[^\s]+)', self.content)
        if github_match:
            data["github"] = github_match.group(1).strip()
        
        linkedin_match = re.search(r'LinkedIn:\s*(https?://[^\s]+|www\.linkedin\.com/[^\s]+)', self.content)
        if linkedin_match:
            data["linkedin"] = linkedin_match.group(1).strip()
        
        website_match = re.search(r'Website/Portfolio:\s*(https?://[^\s]+)', self.content)
        if website_match:
            data["website"] = website_match.group(1).strip()
        
        return data
    
    def extract_berufserfahrung(self) -> List[Dict[str, Any]]:
        """Extrahiert Berufserfahrung"""
        jobs = []
        
        # Finde den Berufserfahrung-Abschnitt (emoji kann variieren)
        beruf_section = re.search(
            r'##\s*[💼]?\s*Berufserfahrung(.*?)(?=\n##\s|$)', 
            self.content, 
            re.DOTALL
        )
        
        if not beruf_section:
            return jobs
        
        section_text = beruf_section.group(1)
        
        # Finde alle Positionen (### Position X)
        position_blocks = re.split(r'###\s*Position\s*\d*', section_text)
        
        for block in position_blocks[1:]:  # Überspringe den ersten leeren
            job = {
                "zeitraum": "",
                "position": "",
                "firma": "",
                "ort": "",
                "tatigkeiten": []
            }
            
            # Zeitraum extrahieren
            zeitraum = re.search(r'\*\*Zeitraum:\*\*\s*([^\n*]+)', block)
            if zeitraum:
                zr = zeitraum.group(1).strip()
                if zr and not zr.startswith('_') and not zr.startswith('('):
                    job["zeitraum"] = zr
            
            # Position extrahieren
            position = re.search(r'\*\*Position:\*\*\s*([^\n*]+)', block)
            if position:
                pos = position.group(1).strip()
                if pos and not pos.startswith('_') and not pos.startswith('('):
                    job["position"] = pos
            
            # Firma extrahieren
            firma = re.search(r'\*\*Firma:\*\*\s*([^\n*]+)', block)
            if firma:
                f = firma.group(1).strip()
                if f and not f.startswith('_') and not f.startswith('('):
                    job["firma"] = f
            
            # Ort extrahieren
            ort = re.search(r'\*\*Ort:\*\*\s*([^\n*]+)', block)
            if ort:
                o = ort.group(1).strip()
                if o and not o.startswith('_') and not o.startswith('('):
                    job["ort"] = o
            
            # Tätigkeiten extrahieren
            taet_section = re.search(r'\*\*Tätigkeiten:\*\*(.*?)(?=\n###|\n##|\n---|\Z)', block, re.DOTALL)
            if taet_section:
                taet_text = taet_section.group(1)
                for line in taet_text.split('\n'):
                    line = line.strip()
                    if line.startswith('- '):
                        taet = line[2:].strip()
                        # Überspringe Platzhalter
                        if taet and not taet.startswith('_') and not taet.startswith('('):
                            job["tatigkeiten"].append(taet)
            
            # Nur hinzufügen wenn mindestens Firma vorhanden
            if job["firma"]:
                jobs.append(job)
        
        return jobs
    
    def extract_ausbildung(self) -> List[Dict[str, Any]]:
        """Extrahiert Ausbildung"""
        ausbildungen = []
        
        # Finde den Ausbildung-Abschnitt (emoji kann variieren)
        ausb_section = re.search(
            r'##\s*[🎓]?\s*Ausbildung\s*&?\s*Schulbildung(.*?)(?=\n##\s|$)', 
            self.content, 
            re.DOTALL
        )
        
        if not ausb_section:
            return ausbildungen
        
        section_text = ausb_section.group(1)
        
        # Finde alle Ausbildungen/Schulabschlüsse
        blocks = re.split(r'###\s*(?:Ausbildung/Studium\s*\d*|Schulabschluss)', section_text)
        
        for block in blocks[1:]:
            ausb = {
                "zeitraum": "",
                "abschluss": "",
                "institution": "",
                "ort": "",
                "note": "",
                "details": []
            }
            
            # Zeitraum
            zeitraum = re.search(r'\*\*Zeitraum:\*\*\s*([^\n*]+)', block)
            if zeitraum:
                zr = zeitraum.group(1).strip()
                if zr and not zr.startswith('_') and not zr.startswith('('):
                    ausb["zeitraum"] = zr
            
            # Abschluss
            abschluss = re.search(r'\*\*Abschluss:\*\*\s*([^\n*]+)', block)
            if abschluss:
                ab = abschluss.group(1).strip()
                if ab and not ab.startswith('_') and not ab.startswith('('):
                    ausb["abschluss"] = ab
            
            # Institution
            institution = re.search(r'\*\*Institution:\*\*\s*([^\n*]+)', block)
            if institution:
                inst = institution.group(1).strip()
                if inst and not inst.startswith('_') and not inst.startswith('('):
                    ausb["institution"] = inst
            
            # Ort
            ort = re.search(r'\*\*Ort:\*\*\s*([^\n*]+)', block)
            if ort:
                o = ort.group(1).strip()
                if o and not o.startswith('_') and not o.startswith('('):
                    ausb["ort"] = o
            
            # Note
            note = re.search(r'\*\*Note:\*\*\s*([^\n*]+)', block)
            if note:
                n = note.group(1).strip()
                if n and not n.startswith('_') and not n.startswith('('):
                    ausb["note"] = n
            
            # Details
            details_section = re.search(r'\*\*Details:\*\*(.*?)(?=\n###|\n##|\n---|\Z)', block, re.DOTALL)
            if details_section:
                details_text = details_section.group(1)
                for line in details_text.split('\n'):
                    line = line.strip()
                    if line.startswith('- '):
                        detail = line[2:].strip()
                        if detail and not detail.startswith('_') and not detail.startswith('('):
                            ausb["details"].append(detail)
            
            # Nur hinzufügen wenn mindestens Abschluss oder Institution
            if ausb["abschluss"] or ausb["institution"]:
                ausbildungen.append(ausb)
        
        return ausbildungen
    
    def extract_programmiersprachen(self) -> List[Dict[str, int]]:
        """Extrahiert Programmiersprachen mit manuellen Levels"""
        sprachen = []
        
        # Finde die Tabelle
        table_match = re.search(
            r'\| Sprache \| Level.*?\n\|[-\s|]+\n(.*?)(?=\n\n|\n###|\n##|$)',
            self.content,
            re.DOTALL
        )
        
        if table_match:
            rows = table_match.group(1).strip().split('\n')
            for row in rows:
                cols = [c.strip() for c in row.split('|') if c.strip()]
                if len(cols) >= 2:
                    name = cols[0].strip()
                    level_str = cols[1].strip()
                    
                    # Überspringe Platzhalter
                    if name.startswith('_') or not name:
                        continue
                    
                    try:
                        level = int(level_str)
                        sprachen.append({"name": name, "manual_score": level})
                    except ValueError:
                        continue
        
        return sprachen
    
    def extract_list_section(self, header_pattern: str) -> List[str]:
        """Extrahiert eine Listen-Sektion"""
        items = []
        
        section = re.search(
            f'{header_pattern}(.*?)(?=###|##|$)',
            self.content,
            re.DOTALL
        )
        
        if section:
            for line in section.group(1).split('\n'):
                line = line.strip()
                if line.startswith('- ') and not line.startswith('- _'):
                    item = line[2:].strip()
                    if item and not item.startswith('('):
                        items.append(item)
        
        return items
    
    def extract_sprachen(self) -> List[Dict[str, str]]:
        """Extrahiert Sprachkenntnisse"""
        sprachen = []
        
        # Finde die Tabelle
        table_match = re.search(
            r'##\s*[🌍]?\s*Sprachkenntnisse.*?\| Sprache \| Niveau.*?\n\|[-\s|]+\n(.*?)(?=\n\n|\n##|$)',
            self.content,
            re.DOTALL
        )
        
        if table_match:
            rows = table_match.group(1).strip().split('\n')
            for row in rows:
                cols = [c.strip() for c in row.split('|') if c.strip()]
                if len(cols) >= 2:
                    sprache = cols[0].strip()
                    niveau = cols[1].strip()
                    
                    if sprache.startswith('_') or not sprache or sprache.startswith('('):
                        continue
                    
                    sprachen.append({"sprache": sprache, "niveau": niveau})
        
        return sprachen
    
    def extract_hobbys(self) -> List[str]:
        """Extrahiert Hobbys & Interessen"""
        hobbys = []
        
        section = re.search(
            r'##\s*[🎯]?\s*Hobbys\s*&?\s*Interessen.*?\n(.*?)(?=\n##|$)',
            self.content,
            re.DOTALL
        )
        
        if section:
            for line in section.group(1).split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    hobby = line[2:].strip()
                    if hobby and not hobby.startswith('_') and not hobby.startswith('('):
                        hobbys.append(hobby)
        
        return hobbys
    
    def extract_softskills(self) -> List[str]:
        """Extrahiert Softskills"""
        softskills = []
        
        section = re.search(
            r'###\s*Softskills.*?\n(.*?)(?=\n###|\n##|$)',
            self.content,
            re.DOTALL
        )
        
        if section:
            for line in section.group(1).split('\n'):
                line = line.strip()
                if line.startswith('- ') and not line.startswith('*('):
                    skill = line[2:].strip()
                    if skill and not skill.startswith('_') and not skill.startswith('('):
                        softskills.append(skill)
        
        return softskills


class DocumentScanner:
    """Scannt Dokumente und extrahiert Metadaten"""
    
    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
    
    def get_zertifikate(self) -> List[Dict[str, str]]:
        """Extrahiert Zertifikatsnamen und Datum aus Dateinamen"""
        zerts = []
        zert_dir = self.docs_dir / "zertifikate"
        
        if not zert_dir.exists():
            return zerts
        
        for f in zert_dir.glob("*.pdf"):
            # Bereinige Dateinamen
            name = f.stem
            datum = ""
            
            # Versuche Datum aus Dateinamen zu extrahieren (YYYY-MM-DD oder DD.MM.YYYY)
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
                r'(\\d{2}\\.\\d{2}\\.\\d{4})',  # DD.MM.YYYY
                r'(20\d{2})',  # Nur Jahr ab 2000 (20xx)
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, name)
                if match:
                    datum = match.group(1)
                    # Entferne Datum aus Namen
                    name = re.sub(pattern, '', name)
                    break
            
            # Bereinige Namen
            name = name.replace('_', ' ')
            name = name.replace('-', ' ')
            name = re.sub(r'\s+', ' ', name)
            
            # Spezielle Zertifikate erkennen
            cert_name = ""
            cert_date = datum
            
            if 'scrum' in name.lower():
                cert_name = "Scrum Fundamentals Certified"
                if not cert_date:
                    cert_date = "2024"  # Standardwert, kann angepasst werden
            elif 'pcep' in name.lower():
                cert_name = "PCEP - Python Certified Entry-Level Programmer"
                if not cert_date:
                    cert_date = "2024"
            elif 'ki' in name.lower() or 'kompetenz' in name.lower():
                cert_name = "KI-Kompetenz Zertifikat"
                if not cert_date:
                    cert_date = "2025"
            else:
                cert_name = name.strip()
                if not cert_date:
                    cert_date = "o.A."  # ohne Angabe
            
            zerts.append({
                "name": cert_name,
                "datum": cert_date
            })
        
        return zerts
    
    def get_weiterbildungen(self) -> List[str]:
        """Extrahiert Weiterbildungsnamen aus Dateinamen"""
        kurse = []
        weiter_dir = self.docs_dir / "weiterbildungen"
        
        if not weiter_dir.exists():
            return kurse
        
        for f in weiter_dir.glob("*.pdf"):
            name = f.stem
            
            # Udemy-Kurse bereinigen
            if name.startswith('Udemy'):
                name = name[5:]  # "Udemy" entfernen
            
            # Programmieren-starten Kurse
            if 'programmieren-starten' in name.lower():
                if 'python' in name.lower():
                    kurse.append("Python Masterkurs (programmieren-starten)")
                elif 'java' in name.lower():
                    kurse.append("Java Masterkurs (programmieren-starten)")
                continue
            
            # Bereinige Namen
            name = name.replace('_', ' ')
            name = name.replace('-', ' ')
            name = re.sub(r'\s+', ' ', name)
            
            # Kategorisiere
            if name.strip():
                kurse.append(f"{name.strip()} (Udemy)")
        
        return kurse
    
    def calculate_skill_scores(self) -> Dict[str, int]:
        """Berechnet Skill-Scores aus allen Dokumenten"""
        POINTS = {
            'zertifikat': 15,
            'weiterbildung': 10,
            'zeugnis': 8,
            'ausbildung': 12,
            'lebenslauf': 5,
            'general': 2
        }
        
        SKILLS = {
            # Programmiersprachen
            'python': ['python', 'django', 'flask', 'fastapi', 'pytorch', 'pandas', 'numpy'],
            'javascript': ['javascript', 'js', 'typescript', 'ts', 'node', 'nodejs'],
            'java': ['java', 'spring', 'springboot', 'maven', 'gradle'],
            'sql': ['sql', 'mysql', 'postgresql', 'sqlite', 'database', 'datenbank'],
            'html': ['html', 'html5'],
            'css': ['css', 'css3', 'sass', 'scss', 'tailwind', 'bootstrap'],
            
            # Frameworks & Bibliotheken
            'flask': ['flask'],
            'fastapi': ['fastapi'],
            'spring': ['spring', 'springboot', 'spring boot'],
            'node': ['node', 'nodejs', 'express', 'npm', 'nestjs'],
            'react': ['react', 'nextjs', 'next.js', 'jsx'],
            'vue': ['vue', 'vuejs', 'vue.js', 'nuxt'],
            'bootstrap': ['bootstrap'],
            'llm': ['llm', 'langchain', 'openai', 'gpt', 'transformer', 'ki', 'ai', 'artificial intelligence'],
            'langchain': ['langchain'],
            'pandas': ['pandas'],
            'numpy': ['numpy'],
            
            # Tools & Technologien
            'git': ['git', 'github', 'gitlab', 'bitbucket'],
            'atlassian': ['jira', 'confluence', 'bitbucket', 'atlassian'],
            'vscode': ['vs code', 'vscode', 'visual studio code'],
            'devtools': ['devtools', 'debug', 'browser', 'inspector', 'browser devtools'],
            'postman': ['postman', 'api test'],
            'postgresql': ['postgresql', 'postgres'],
            'mysql': ['mysql'],
            'sqlite': ['sqlite'],
            'docker': ['docker', 'container', 'kubernetes', 'k8s'],
            'npm': ['npm', 'yarn'],
            'pip': ['pip', 'python package'],
            'maven': ['maven'],
            'linux': ['linux', 'bash', 'shell', 'ubuntu'],
            'windows': ['windows'],
            'powershell': ['powershell', 'ps1'],
            'cmd': ['cmd', 'command'],
            
            # Methoden & Praktiken
            'scrum': ['scrum', 'agile', 'kanban'],
            'architecture': ['architecture', 'microservice', 'system design', 'software architecture'],
            'api': ['rest', 'restful', 'api', 'graphql', 'soap'],
            'uml': ['uml', 'bpmn', 'diagram', 'modell'],
            'microservices': ['microservice', 'microservices'],
            'tdd': ['test', 'testing', 'jest', 'pytest', 'junit', 'selenium', 'tdd', 'test-driven'],
            'cicd': ['jenkins', 'github actions', 'gitlab ci', 'travis', 'ci/cd', 'continuous'],
        }
        
        scores = {k: 0 for k in SKILLS}
        
        print("\n📊 Analysiere alle Dokumente für Skill-Scores...")
        
        for f in self.docs_dir.glob('**/*'):
            if not f.is_file():
                continue
            
            suffix = f.suffix.lower()
            if suffix not in ['.pdf', '.docx', '.txt', '.md']:
                continue
            
            # Text lesen
            text = ""
            if suffix == '.pdf' and PDF_SUPPORT:
                try:
                    with open(f, 'rb') as pf:
                        reader = PyPDF2.PdfReader(pf)
                        text = "\n".join(p.extract_text() or "" for p in reader.pages)
                except:
                    pass
            elif suffix in ['.txt', '.md']:
                try:
                    text = f.read_text(encoding='utf-8')
                except:
                    pass
            
            if not text:
                continue
            
            text = text.lower()
            
            # Dokumenttyp bestimmen
            path_str = str(f).lower()
            if 'zertifikat' in path_str:
                doc_type = 'zertifikat'
            elif 'weiterbildung' in path_str or 'udemy' in path_str:
                doc_type = 'weiterbildung'
            elif 'zeugnis' in path_str:
                doc_type = 'zeugnis'
            elif 'ausbildung' in path_str or 'ihk' in path_str:
                doc_type = 'ausbildung'
            elif 'lebenslauf' in path_str:
                doc_type = 'lebenslauf'
            else:
                doc_type = 'general'
            
            pts = POINTS.get(doc_type, 2)
            
            # Skills zählen
            for skill, keywords in SKILLS.items():
                if any(kw in text for kw in keywords):
                    scores[skill] += pts
        
        # Normalisieren auf 0-100
        return {k: min(v, 100) for k, v in scores.items()}


class PythonFileGenerator:
    """Generiert die persoenliche_daten.py Datei"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
    
    def generate(self) -> str:
        """Generiert den Python-Code"""
        
        d = self.data
        
        output = f'''# Persönliche Daten für Bewerbungsunterlagen
# Fachinformatiker Anwendungsentwicklung
#
# ⚠️  AUTOMATISCH GENERIERT von extract_personal_data.py
# Letzte Aktualisierung: {datetime.now().strftime("%d.%m.%Y %H:%M")}
#
# SKILL-SCORING: level = 50% Selbsteinschätzung + 50% Dokumentenanalyse

from datetime import datetime

PERSOENLICHE_DATEN = {{
    "vorname": "{d['persoenlich']['vorname']}",
    "nachname": "{d['persoenlich']['nachname']}",
    "titel": "{d['persoenlich']['titel']}",
    "strasse": "{d['persoenlich']['strasse']}",
    "plz": "{d['persoenlich']['plz']}",
    "ort": "{d['persoenlich']['ort']}",
    "telefon": "{d['persoenlich']['telefon']}",
    "email": "{d['persoenlich']['email']}",
    "geburtsdatum": "{d['persoenlich']['geburtsdatum']}",
    "geburtsort": "{d['persoenlich']['geburtsort']}",
    "nationalitaet": "{d['persoenlich']['nationalitaet']}",
    "github": "{d['persoenlich']['github']}",
    "linkedin": "{d['persoenlich']['linkedin']}",
    "website": "{d['persoenlich']['website']}"
}}

'''
        
        # BERUFSERFAHRUNG
        output += "BERUFSERFAHRUNG = [\n"
        for job in d.get('berufserfahrung', []):
            taet_list = ', '.join([f'"{t}"' for t in job.get('tatigkeiten', [])])
            output += f'''    {{
        "zeitraum": "{job.get('zeitraum', '')}",
        "position": "{job.get('position', '')}",
        "firma": "{job.get('firma', '')}",
        "ort": "{job.get('ort', '')}",
        "tatigkeiten": [{taet_list}]
    }},
'''
        output += "]\n\n"
        
        # AUSBILDUNG
        output += "AUSBILDUNG = [\n"
        for ausb in d.get('ausbildung', []):
            output += f'''    {{
        "zeitraum": "{ausb.get('zeitraum', '')}",
        "abschluss": "{ausb.get('abschluss', '')}",
        "institution": "{ausb.get('institution', '')}",
        "ort": "{ausb.get('ort', '')}",
        "note": "{ausb.get('note', '')}",
        "details": []
    }},
'''
        output += "]\n\n"
        
        # KENNTNISSE mit kombiniertem Score
        output += "KENNTNISSE = {\n    \"programmiersprachen\": [\n"
        for prog in d.get('programmiersprachen', []):
            name = prog['name']
            manual = prog['manual_score']
            calculated = prog.get('calculated_score', 0)
            combined = min(int((manual * 0.5) + (calculated * 0.5)), 100)
            output += f'        {{"name": "{name}", "level": {combined}}},  # manual:{manual} + calc:{calculated}\n'
        output += "    ],\n"
        
        # Frameworks mit Scores
        output += '    "frameworks": [\n'
        for fw in d.get('frameworks', []):
            if isinstance(fw, dict):
                output += f'        {{"name": "{fw["name"]}", "level": {fw["level"]}}},\n'
            else:
                output += f'        {{"name": "{fw}", "level": 0}},\n'
        output += "    ],\n"
        
        # Tools mit Scores
        output += '    "tools": [\n'
        for tool in d.get('tools', []):
            if isinstance(tool, dict):
                output += f'        {{"name": "{tool["name"]}", "level": {tool["level"]}}},\n'
            else:
                output += f'        {{"name": "{tool}", "level": 0}},\n'
        output += "    ],\n"
        
        # Methoden mit Scores
        output += '    "methoden": [\n'
        for method in d.get('methoden', []):
            if isinstance(method, dict):
                output += f'        {{"name": "{method["name"]}", "level": {method["level"]}}},\n'
            else:
                output += f'        {{"name": "{method}", "level": 0}},\n'
        output += "    ]\n"
        output += "}\n\n"
        
        # SPRACHEN
        output += "SPRACHEN = [\n"
        for s in d.get('sprachen', []):
            output += f'    {{"sprache": "{s["sprache"]}", "niveau": "{s["niveau"]}"}},\n'
        output += "]\n\n"
        
        # ZERTIFIKATE
        output += "ZERTIFIKATE = [\n"
        for cert in d.get('zertifikate', []):
            if isinstance(cert, dict):
                output += f'    {{"name": "{cert["name"]}", "datum": "{cert["datum"]}"}},\n'
            else:
                output += f'    {{"name": "{cert}", "datum": "o.A."}},\n'
        output += "]\n\n"
        
        # WEITERBILDUNGEN
        weiter = d.get('weiterbildungen', [])
        output += f"WEITERBILDUNGEN = {weiter}\n\n"
        
        # HOBBYS
        hobbys = d.get('hobbys', [])
        output += f"HOBBYS = {hobbys}\n\n"
        
        # SOFTSKILLS
        softskills = d.get('softskills', [])
        output += f"SOFTSKILLS = {softskills}\n\n"
        
        # BEWERBUNG
        output += '''# Bewerbungsdaten (für jede Bewerbung anpassen!)
BEWERBUNG = {
    "firma": "",
    "ansprechpartner": "",
    "position": "Fachinformatiker Anwendungsentwicklung",
    "strasse": "",
    "plz": "",
    "ort": "",
    "datum": datetime.now().strftime("%d.%m.%Y"),
}
'''
        
        return output


def main():
    print("\n" + "="*60)
    print("🚀 Bewerbungsdaten-Extraktion (Hybrid)")
    print("   Kein LLM nötig - Direkt aus meine_daten.md!")
    print("="*60)
    
    docs_dir = Path("personal_documents")
    meine_daten_path = docs_dir / "meine_daten.md"
    
    if not meine_daten_path.exists():
        print(f"\n❌ {meine_daten_path} nicht gefunden!")
        print("   Bitte erst meine_daten.md ausfüllen.")
        sys.exit(1)
    
    # 1. Parse meine_daten.md
    print("\n📄 Parse meine_daten.md...")
    parser = MarkdownParser(meine_daten_path)
    
    persoenlich = parser.extract_personal_data()
    print(f"   ✓ Persönliche Daten: {persoenlich['vorname']} {persoenlich['nachname']}")
    
    berufserfahrung = parser.extract_berufserfahrung()
    print(f"   ✓ Berufserfahrung: {len(berufserfahrung)} Positionen")
    
    ausbildung = parser.extract_ausbildung()
    print(f"   ✓ Ausbildung: {len(ausbildung)} Einträge")
    
    programmiersprachen = parser.extract_programmiersprachen()
    print(f"   ✓ Programmiersprachen: {len(programmiersprachen)} Sprachen")
    
    frameworks = parser.extract_list_section(r'### Frameworks & Bibliotheken')
    print(f"   ✓ Frameworks: {len(frameworks)}")
    
    tools = parser.extract_list_section(r'### Tools & Technologien')
    print(f"   ✓ Tools: {len(tools)}")
    
    methoden = parser.extract_list_section(r'### Methoden & Praktiken')
    print(f"   ✓ Methoden: {len(methoden)}")
    
    sprachen = parser.extract_sprachen()
    print(f"   ✓ Sprachkenntnisse: {len(sprachen)}")
    
    hobbys = parser.extract_hobbys()
    print(f"   ✓ Hobbys: {len(hobbys)}")
    
    softskills = parser.extract_softskills()
    print(f"   ✓ Softskills: {len(softskills)}")
    
    # 2. Scanne Dokumente
    print("\n📂 Scanne Dokumentenordner...")
    scanner = DocumentScanner(docs_dir)
    
    zertifikate = scanner.get_zertifikate()
    print(f"   ✓ Zertifikate: {len(zertifikate)}")
    for z in zertifikate:
        if isinstance(z, dict):
            print(f"      - {z['name']} ({z['datum']})")
        else:
            print(f"      - {z}")
    
    weiterbildungen = scanner.get_weiterbildungen()
    print(f"   ✓ Weiterbildungen: {len(weiterbildungen)}")
    
    # 3. Berechne Skill-Scores
    skill_scores = scanner.calculate_skill_scores()
    
    print("\n📊 Skill-Scores (aus Dokumentenanalyse):")
    for skill, score in sorted(skill_scores.items(), key=lambda x: -x[1]):
        if score > 0:
            print(f"   • {skill}: {score}/100")
    
    # 4. Kombiniere Programmiersprachen-Scores
    for prog in programmiersprachen:
        name_original = prog['name']
        # Normalisiere: lowercase, nur Buchstaben/Zahlen
        name_normalized = re.sub(r'[^a-z0-9]', '', name_original.lower())
        calc_score = 0
        
        # Spezial-Mappings für bekannte Varianten
        SKILL_MAPPINGS = {
            'javascripttypescript': 'javascript',
            'jsts': 'javascript',
            'htmlcss': 'html',  # Wenn HTML/CSS zusammen, nimm HTML
            'html5': 'html',
            'css3': 'css',
        }
        
        # Versuche zuerst Spezial-Mapping
        if name_normalized in SKILL_MAPPINGS:
            mapped = SKILL_MAPPINGS[name_normalized]
            calc_score = skill_scores.get(mapped, 0)
        else:
            # Exaktes Match (nach Normalisierung)
            for skill, score in skill_scores.items():
                skill_normalized = re.sub(r'[^a-z0-9]', '', skill.lower())
                if name_normalized == skill_normalized:
                    calc_score = score
                    break
        
        prog['calculated_score'] = calc_score
    
    # 4b. Berechne Scores für Frameworks, Tools und Methoden
    def add_scores_to_list(items_list, skill_scores):
        """Konvertiert String-Liste zu Dict mit Scores"""
        result = []
        for item_name in items_list:
            # Normalisiere Namen für Matching
            name_normalized = re.sub(r'[^a-z0-9]', '', item_name.lower())
            calc_score = 0
            
            # Spezial-Mappings
            MAPPINGS = {
                'nodeexpress': 'node',
                'nodejs': 'node',
                'gitgithub': 'git',
                'jira': 'atlassian',
                'confluence': 'atlassian',
                'bitbucket': 'atlassian',
                'springjava': 'spring',
                'vscode': 'vscode',
                'browserdevtools': 'devtools',
                'postgre': 'postgresql',
                'agiledeveloplungscrum': 'scrum',
                'agileentwicklungscrum': 'scrum',
                'softwarearchitecturesystemdesign': 'architecture',
                'restapidesign': 'api',
                'umlbpmnmodellierung': 'uml',
                'microservicesarchitecture': 'microservices',
                'testdrivendevelopmenttdd': 'tdd',
                'testdrivendevelopment': 'tdd',
            }
            
            # Versuche Mapping
            if name_normalized in MAPPINGS:
                mapped = MAPPINGS[name_normalized]
                calc_score = skill_scores.get(mapped, 0)
            else:
                # Exaktes Match
                for skill, score in skill_scores.items():
                    skill_normalized = re.sub(r'[^a-z0-9]', '', skill.lower())
                    if name_normalized == skill_normalized:
                        calc_score = score
                        break
                    # Partial match (skill ist in name enthalten)
                    if skill_normalized in name_normalized:
                        calc_score = max(calc_score, score)
            
            result.append({
                'name': item_name,
                'level': calc_score
            })
        
        # Sortiere nach Score (absteigend)
        return sorted(result, key=lambda x: -x['level'])
    
    frameworks_with_scores = add_scores_to_list(frameworks, skill_scores)
    tools_with_scores = add_scores_to_list(tools, skill_scores)
    methoden_with_scores = add_scores_to_list(methoden, skill_scores)
    
    print("\n📊 Framework-Scores:")
    for fw in frameworks_with_scores[:10]:
        print(f"   • {fw['name']}: {fw['level']}")
    
    print("\n📊 Tool-Scores:")
    for t in tools_with_scores[:10]:
        print(f"   • {t['name']}: {t['level']}")
    
    print("\n📊 Methoden-Scores:")
    for m in methoden_with_scores[:10]:
        print(f"   • {m['name']}: {m['level']}")
    
    # 5. Kombiniere alle Daten
    all_data = {
        'persoenlich': persoenlich,
        'berufserfahrung': berufserfahrung,
        'ausbildung': ausbildung,
        'programmiersprachen': programmiersprachen,
        'frameworks': frameworks_with_scores,
        'tools': tools_with_scores,
        'methoden': methoden_with_scores,
        'sprachen': sprachen,
        'zertifikate': zertifikate,
        'weiterbildungen': weiterbildungen,
        'hobbys': hobbys,
        'softskills': softskills
    }
    
    # 6. Generiere Python-Datei
    generator = PythonFileGenerator(all_data)
    output = generator.generate()
    
    # 7. Vorschau
    print("\n" + "="*60)
    print("📋 VORSCHAU:")
    print("="*60)
    print(output[:2500])
    if len(output) > 2500:
        print("...")
    print("="*60)
    
    # 8. Speichern?
    response = input("\n💾 Speichern in data/persoenliche_daten.py? (j/n): ")
    
    if response.lower() in ['j', 'ja', 'y', 'yes']:
        output_path = Path("data/persoenliche_daten.py")
        
        # Backup
        if output_path.exists():
            backup = output_path.with_suffix('.py.backup')
            backup.write_text(output_path.read_text())
            print(f"✅ Backup: {backup}")
        
        output_path.write_text(output)
        print(f"✅ Gespeichert: {output_path}")
        print("\n🎉 Fertig! Jetzt 'python generator.py' ausführen.")
    else:
        print("\n❌ Nicht gespeichert.")


if __name__ == "__main__":
    main()
