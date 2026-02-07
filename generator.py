#!/usr/bin/env python3
"""
Bewerbungsgenerator - Erstellt professionelle PDFs aus HTML-Templates
Autor: Marcus Mustermann
Datum: 04.02.2026
"""

import os
import sys
from pathlib import Path
from weasyprint import HTML, CSS
from datetime import datetime
import json

# Projekt-Pfade
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
TEMPLATES_DIR = BASE_DIR / 'templates'
OUTPUT_DIR = BASE_DIR / 'output'
PERSONAL_DOCS_DIR = BASE_DIR / 'personal_documents'

# Daten importieren
sys.path.insert(0, str(DATA_DIR))
from persoenliche_daten import (  # type: ignore
    PERSOENLICHE_DATEN, BERUFSERFAHRUNG, 
    AUSBILDUNG, KENNTNISSE, SPRACHEN, ZERTIFIKATE
)


def load_latest_bewerbung():
    """Lädt die neueste Stellenanzeigen-Analyse und konvertiert zu BEWERBUNG"""
    analysen_dir = OUTPUT_DIR / 'analysen'
    
    if not analysen_dir.exists():
        return None
    
    # Finde alle JSON-Dateien
    json_files = list(analysen_dir.glob("*.json"))
    
    if not json_files:
        return None
    
    # Neueste Datei nach Änderungsdatum
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Konvertiere zu BEWERBUNG-Format
        bewerbung = {
            "firma": data.get('firma', {}).get('name', ''),
            "ansprechpartner": data.get('firma', {}).get('ansprechpartner', 'Damen und Herren'),
            "position": data.get('stelle', {}).get('titel', 'Fachinformatiker Anwendungsentwicklung'),
            "strasse": data.get('firma', {}).get('strasse', ''),
            "plz": data.get('firma', {}).get('plz', ''),
            "ort": data.get('firma', {}).get('ort', ''),
            "datum": datetime.now().strftime("%d.%m.%Y"),
        }
        
        print(f"\n📋 Lade Bewerbungsdaten aus: {latest_file.name}")
        print(f"   Firma: {bewerbung['firma']}")
        print(f"   Position: {bewerbung['position']}\n")
        
        return bewerbung
        
    except Exception as e:
        print(f"⚠️  Fehler beim Laden der Analyse: {e}")
        return None


def get_bewerbung():
    """Lädt BEWERBUNG aus neuester Analyse oder verwendet Fallback"""
    bewerbung = load_latest_bewerbung()
    
    if bewerbung:
        return bewerbung
    
    # Fallback: Manuelle Eingabe erforderlich
    print("\n⚠️  Keine Stellenanzeigen-Analyse gefunden!")
    print("   Bitte erst eine Stellenanzeige analysieren:")
    print("   python3 analyze_stelle.py --file <stellenanzeige.txt> --save\n")
    
    return {
        "firma": "FIRMA FEHLT - Bitte Analyse durchführen",
        "ansprechpartner": "Damen und Herren",
        "position": "Fachinformatiker Anwendungsentwicklung",
        "strasse": "",
        "plz": "",
        "ort": "",
        "datum": datetime.now().strftime("%d.%m.%Y"),
    }


# Lade Bewerbungsdaten
BEWERBUNG = get_bewerbung()


def load_custom_anschreiben_text():
    """Generiert personalisierten Anschreiben-Text mit LLM basierend auf Analyse"""
    from data.bewerbungs_firma import OllamaClient, LLMAnalyzer
    
    firma_name = BEWERBUNG.get('firma', '').replace(' ', '_')
    
    # Suche neueste Analyse für diese Firma
    analysen_dir = OUTPUT_DIR / 'analysen'
    if analysen_dir.exists():
        matching_files = list(analysen_dir.glob(f"{firma_name}_*.json"))
        if matching_files:
            # Neueste Datei
            latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
            
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Prüfe ob Ollama verfügbar ist
                analyzer = LLMAnalyzer()
                if analyzer.is_available:
                    print("🤖 Generiere personalisierten Anschreiben-Text mit LLM...")
                    
                    # Hole Top-Matches aus Analyse
                    top_matches = data.get('matching', {}).get('top_matches', [])
                    firma_name = BEWERBUNG['firma']
                    position = BEWERBUNG['position']
                    
                    llm_text = analyzer.generate_skill_paragraphs(
                        matches=top_matches,
                        firma_name=firma_name,
                        position=position
                    )
                    
                    if llm_text and len(llm_text.strip()) > 50:
                        # Bereinige potenzielle Formatierungs-Artefakte
                        cleanup_patterns = [
                            "```html", "```", "<html>", "</html>",
                            "<body>", "</body>", "<div>", "</div>",
                            "[Ihr Name]", "[Your Name]", "[NAME]"
                        ]
                        for pattern in cleanup_patterns:
                            llm_text = llm_text.replace(pattern, "")
                        llm_text = llm_text.strip()
                        
                        # Entferne Anrede-Zeilen und Grußformeln (falls LLM sie trotzdem generiert hat)
                        lines = llm_text.split('\n')
                        filtered_lines = []
                        for line in lines:
                            line_lower = line.strip().lower()
                            # Filtere Zeilen mit Anreden und Grußformeln heraus
                            if not any(phrase in line_lower for phrase in [
                                'sehr geehrte', 'sehr geehrter', 'liebe', 'lieber',
                                'hallo', 'guten tag', 'mit freundlichen grüßen',
                                'mit freundlichem gruß', 'hochachtungsvoll'
                            ]):
                                filtered_lines.append(line)
                        llm_text = '\n'.join(filtered_lines)
                        
                        # Formatiere als HTML-Absätze
                        # Zuerst versuche mit doppelten Zeilenumbrüchen, dann mit einfachen
                        if '\n\n' in llm_text:
                            paragraphs = [p.strip() for p in llm_text.strip().split('\n\n') if p.strip()]
                        else:
                            # Bei einfachen Zeilenumbrüchen: Jede nicht-leere Zeile wird ein Absatz
                            paragraphs = [line.strip() for line in llm_text.strip().split('\n') if line.strip()]
                        
                        html_text = '\n\n'.join([f"            <p>\n                {p}\n            </p>" for p in paragraphs])
                        return html_text
                    else:
                        print("⚠️  LLM konnte keinen Text generieren, verwende Fallback")
                else:
                    print("⚠️  Ollama nicht verfügbar, verwende Fallback-Text")
                
            except Exception as e:
                print(f"⚠️  Fehler bei LLM-Generierung: {e}")
    
    # Fallback: Minimaler Standard-Text wenn kein LLM verfügbar
    return """<p>
                mit großem Interesse habe ich Ihre Stellenausschreibung gelesen. Als frisch ausgebildeter 
                Fachinformatiker für Anwendungsentwicklung mit Schwerpunkten in Web-Development und 
                Künstlicher Intelligenz bringe ich fundierte Kenntnisse und hohe Lernbereitschaft mit.
            </p>

            <p>
                Besonders reizt mich die Möglichkeit, meine Fähigkeiten in einem innovativen Team 
                einzusetzen und kontinuierlich weiterzuentwickeln. Meine Begeisterung für moderne 
                Technologien motiviert mich, mich auch in meiner Freizeit eigenständig weiterzubilden.
            </p>

            <p>
                Gerne überzeuge ich Sie in einem persönlichen Gespräch von meinen Fähigkeiten. 
                Über eine Einladung würde ich mich sehr freuen.
            </p>"""


def generate_anschreiben():
    """Generiert das Bewerbungsanschreiben als PDF"""
    print("📄 Generiere Anschreiben...")
    
    # QR-Code für Website generieren
    from generate_qr_code import generate_qr_code
    website_url = PERSOENLICHE_DATEN.get('website', '')
    if website_url:
        qr_output_path = BASE_DIR / 'images' / 'qr_code.png'
        generate_qr_code(website_url, qr_output_path, size_cm=2.5)
        
        # QR-Code ins Template-Verzeichnis kopieren
        qr_template_path = TEMPLATES_DIR / 'qr_code.png'
        import shutil
        shutil.copy2(qr_output_path, qr_template_path)
    else:
        print("⚠️  Keine Website-URL gefunden, QR-Code wird übersprungen")
    
    # Template laden
    template_path = TEMPLATES_DIR / 'anschreiben.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Profilbild kopieren
    source_img = BASE_DIR / 'images' / 'profilbild.jpg'
    target_img = TEMPLATES_DIR / 'profilbild.jpg'
    if source_img.exists():
        import shutil
        shutil.copy2(source_img, target_img)
    
    # Anschrift und Anrede bestimmen
    ansprechpartner_raw = BEWERBUNG['ansprechpartner']
    firma_name = BEWERBUNG['firma']
    
    # Für Anschriftsfeld: Nur konkreten Namen, sonst leer
    # Filtere aus: "Damen und Herren", leere Strings, "Nicht erkannt", oder wenn = Firmenname
    if (ansprechpartner_raw and 
        ansprechpartner_raw not in ['Damen und Herren', '', 'Nicht erkannt'] and
        ansprechpartner_raw != firma_name):
        anschriftsfeld = ansprechpartner_raw
    else:
        anschriftsfeld = ''  # Bleibt leer wenn kein konkreter Name
    
    # Für Anrede im Text
    if ansprechpartner_raw and ansprechpartner_raw.startswith('Herr'):
        anrede = ansprechpartner_raw  # z.B. "Herr Dr. Müller"
    elif ansprechpartner_raw and ansprechpartner_raw.startswith('Frau'):
        anrede = ansprechpartner_raw  # z.B. "Frau Schmidt"
    else:
        anrede = 'Damen und Herren'
    
    # Lade ggf. personalisierten Anschreiben-Text
    custom_text = load_custom_anschreiben_text()
    
    # Platzhalter ersetzen
    replacements = {
        '{vorname}': PERSOENLICHE_DATEN['vorname'],
        '{nachname}': PERSOENLICHE_DATEN['nachname'],
        '{email}': PERSOENLICHE_DATEN['email'],
        '{telefon}': PERSOENLICHE_DATEN['telefon'],
        '{strasse}': PERSOENLICHE_DATEN['strasse'],
        '{plz}': PERSOENLICHE_DATEN['plz'],
        '{ort}': PERSOENLICHE_DATEN['ort'],
        '{linkedin}': PERSOENLICHE_DATEN.get('linkedin', ''),
        '{website}': PERSOENLICHE_DATEN.get('website', ''),
        '{firma}': BEWERBUNG['firma'],
        '{ansprechpartner}': anschriftsfeld,  # NUR konkreter Name oder leer
        '{position}': BEWERBUNG['position'],
        '{firma_strasse}': BEWERBUNG['strasse'],
        '{firma_plz}': BEWERBUNG['plz'],
        '{firma_ort}': BEWERBUNG['ort'],
        '{datum}': BEWERBUNG['datum'],
        '{anrede}': anrede,
        '{anschreiben_text}': custom_text,  # Personalisierter Text
    }
    
    for placeholder, value in replacements.items():
        html_content = html_content.replace(placeholder, value)
    
    # CSS laden
    css_path = TEMPLATES_DIR / 'styles.css'
    
    # PDF generieren mit dynamischem Dateinamen (Name + Datum)
    vorname = PERSOENLICHE_DATEN['vorname']
    nachname = PERSOENLICHE_DATEN['nachname']
    datum_heute = datetime.now().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f'Anschreiben_{vorname}_{nachname}_{datum_heute}.pdf'
    HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf(
        output_path,
        stylesheets=[CSS(filename=str(css_path))]
    )
    
    print(f"✅ Anschreiben erstellt: {output_path}")
    return output_path


def generate_lebenslauf():
    """Generiert den Lebenslauf als PDF"""
    print("📄 Generiere Lebenslauf...")
    
    # Template laden
    template_path = TEMPLATES_DIR / 'lebenslauf.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Profilbild kopieren
    source_img = BASE_DIR / 'images' / 'profilbild.jpg'
    target_img = TEMPLATES_DIR / 'profilbild.jpg'
    if source_img.exists():
        import shutil
        shutil.copy2(source_img, target_img)
    
    # Berufserfahrung formatieren
    berufserfahrung_html = ""
    for job in BERUFSERFAHRUNG:
        tatigkeiten_html = ""
        if job['tatigkeiten']:
            tatigkeiten_html = "<ul>\n"
            for task in job['tatigkeiten']:
                tatigkeiten_html += f"                <li>{task}</li>\n"
            tatigkeiten_html += "            </ul>"
        
        berufserfahrung_html += f"""
        <div class="cv-entry">
            <div class="timeframe">{job['zeitraum']}</div>
            <div class="details">
                <div class="position">{job['position']}</div>
                <div class="company">{job['firma']}</div>
                <div class="location">{job['ort']}</div>
                {tatigkeiten_html}
            </div>
        </div>
        """
    
    # Ausbildung formatieren
    ausbildung_html = ""
    for edu in AUSBILDUNG:
        details_html = ""
        if edu['details']:
            details_html = "<ul>\n"
            for detail in edu['details']:
                details_html += f"                <li>{detail}</li>\n"
            details_html += "            </ul>"
        
        ausbildung_html += f"""
        <div class="cv-entry">
            <div class="timeframe">{edu['zeitraum']}</div>
            <div class="details">
                <div class="position">{edu['abschluss']}</div>
                <div class="company">{edu['institution']}, {edu['ort']}</div>
                {f'<div class="location">{edu["note"]}</div>' if edu['note'] else ''}
                {details_html}
            </div>
        </div>
        """
    
    # Programmiersprachen mit Skill-Balken (Top 5)
    programmiersprachen_html = ""
    # Icon-Mapping für Programmiersprachen
    icon_map = {
        "Python": "python.svg",
        "TypeScript": "typescript.svg",
        "JavaScript": "javascript.svg",
        "Java": "java.svg",
        "SQL": "sql.svg",
        "HTML/CSS": "html.svg",
    }
    # Sortiere nach Level absteigend und nimm Top 5
    top_programmiersprachen = sorted(KENNTNISSE['programmiersprachen'], key=lambda x: x['level'], reverse=True)[:5]
    
    for skill in top_programmiersprachen:
        icon_file = icon_map.get(skill['name'], "code.svg")  # Fallback zu generischem Icon
        programmiersprachen_html += f"""
        <div class="skill-bar">
            <img src="images/icons/{icon_file}" class="skill-icon" alt="{skill['name']}">
            <div class="skill-name">{skill['name']}</div>
            <div class="bar-container">
                <div class="bar-fill" style="width: {skill['level']}%;"></div>
            </div>
        </div>
        """
    # Zeige "..." wenn es mehr als 5 gibt
    if len(KENNTNISSE['programmiersprachen']) > 5:
        programmiersprachen_html += """
        <div class="skill-bar">
            <div class="skill-name" style="margin-left: 30px;">...</div>
        </div>
        """
    
    # AI/ML als Tags (Top 5)
    ai_ml_html = ""
    # Sortiere nach Level absteigend und nimm Top 5
    top_ai_ml = sorted(KENNTNISSE['ai_ml'], key=lambda x: -x['level'])[:5]
    for item in top_ai_ml:
        name = item['name'] if isinstance(item, dict) else item
        ai_ml_html += f'<span class="tag">{name}</span>\n                        '
    # Zeige "..." wenn es mehr als 5 gibt
    if len(KENNTNISSE['ai_ml']) > 5:
        ai_ml_html += '<span class="tag">...</span>\n                        '
    
    # Frameworks als Tags (Top 5)
    frameworks_html = ""
    # Sortiere nach Level absteigend und nimm Top 5
    top_frameworks = sorted(KENNTNISSE['frameworks'], key=lambda x: -x['level'])[:5]
    for framework in top_frameworks:
        name = framework['name'] if isinstance(framework, dict) else framework
        frameworks_html += f'<span class="tag">{name}</span>\n                        '
    # Zeige "..." wenn es mehr als 5 gibt
    if len(KENNTNISSE['frameworks']) > 5:
        frameworks_html += '<span class="tag">...</span>\n                        '
    
    # Tools als Tags (Top 5 - inkl. Methoden)
    tools_html = ""
    # Sortiere nach Level absteigend und nimm Top 5
    top_tools = sorted(KENNTNISSE['tools'], key=lambda x: -x['level'])[:5]
    for tool in top_tools:
        name = tool['name'] if isinstance(tool, dict) else tool
        tools_html += f'<span class="tag">{name}</span>\n                        '
    # Zeige "..." wenn es mehr als 5 gibt
    if len(KENNTNISSE['tools']) > 5:
        tools_html += '<span class="tag">...</span>\n                        '
    
    # Sprachkenntnisse
    sprachen_html = ""
    # Icon-Mapping für Sprachen (Flaggen)
    sprachen_icon_map = {
        "Deutsch": "flag-de.svg",
        "Englisch": "flag-gb.svg",
        "Französisch": "flag-fr.svg",
        "Spanisch": "flag-es.svg",
        "Italienisch": "flag-it.svg",
    }
    for sprache in SPRACHEN:
        icon_file = sprachen_icon_map.get(sprache['sprache'], "globe.svg")  # Fallback zu Globe
        sprachen_html += f"""
        <div class="language-entry">
            <img src="images/icons/{icon_file}" class="language-icon" alt="{sprache['sprache']}">
            <div class="language-info">
                <div class="timeframe">{sprache['sprache']}</div>
                <div class="details">{sprache['niveau']}</div>
            </div>
        </div>
        """
    
    # Zertifikate
    zertifikate_html = ""
    for cert in ZERTIFIKATE:
        if isinstance(cert, dict):
            zertifikate_html += f"""
                <div class="certificate-entry">
                    <img src="images/icons/certificate.svg" class="certificate-icon" alt="Zertifikat">
                    <span>{cert['name']} ({cert['datum']})</span>
                </div>
                """
        else:
            zertifikate_html += f"""
                <div class="certificate-entry">
                    <img src="images/icons/certificate.svg" class="certificate-icon" alt="Zertifikat">
                    <span>{cert}</span>
                </div>
                """
    
    # Projekte laden
    projekte_html = ""
    projekte_path = PERSONAL_DOCS_DIR / 'projekte' / 'projekte.json'
    try:
        if projekte_path.exists():
            with open(projekte_path, 'r', encoding='utf-8') as f:
                projekte = json.load(f)
            
            # Zeige alle Projekte
            for projekt in projekte:
                name = projekt.get('name', '')
                bezug = projekt.get('bezug', '')
                beschreibung = projekt.get('beschreibung', '')
                buzzwords = projekt.get('buzzwords', [])
                
                # Buzzwords als Tags
                tags_html = ""
                for buzzword in buzzwords:
                    tags_html += f'<span class="project-tag">{buzzword}</span>\n                        '
                
                # Füge "..." Tag hinzu
                tags_html += '<span class="project-tag">...</span>\n                        '
                
                projekte_html += f"""
            <div class="project-entry">
                <div class="project-header">
                    <span class="project-title">{name}</span>
                    <span class="project-category">{bezug}</span>
                </div>
                <div class="project-description">{beschreibung}</div>
                <div class="project-tags">
                    {tags_html}
                </div>
            </div>
            """
            
            # Füge "..." Tag mit Disclaimer hinzu
            projekte_html += """
            <div class="project-entry">
                <div class="project-tags">
                    <span class="project-tag">...</span>
                </div>
                <div class="project-description" style="font-style: italic; color: #7f8c8d; margin-top: 6px;">Weitere private Projekte sind bei Interesse auf meiner GitHub-Page zu finden.</div>
            </div>
            """
        else:
            print(f"⚠️  Projekte-Datei nicht gefunden: {projekte_path}")
    except Exception as e:
        print(f"⚠️  Fehler beim Laden der Projekte: {e}")
    
    # Private Kurse laden
    kurse_html = ""
    weiterbildungen_dir = PERSONAL_DOCS_DIR / 'weiterbildungen'
    try:
        if weiterbildungen_dir.exists():
            # Alle PDF-Dateien auflisten
            pdf_files = list(weiterbildungen_dir.glob("*.pdf"))
            
            # Kursnamen extrahieren und bereinigen
            kurse_liste = []
            for pdf_file in pdf_files:
                # Dateiname ohne Extension
                kurs_name = pdf_file.stem
                
                # Bereinige Dateinamen
                kurs_name = kurs_name.replace('Udemy', '')
                kurs_name = kurs_name.replace('-zertifikat - programmieren-starten', '')
                kurs_name = kurs_name.replace('CK', '')
                
                # CamelCase in lesbare Form umwandeln
                import re
                kurs_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', kurs_name)
                kurs_name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', kurs_name)
                
                # Mehrfache Leerzeichen entfernen
                kurs_name = ' '.join(kurs_name.split())
                
                kurse_liste.append(kurs_name.strip())
            
            # Sortiere nach Relevanz basierend auf Programmierfähigkeiten
            # Priorität: Python, JavaScript, TypeScript, Vue, Web-Dev/Browser
            def kurs_prioritaet(kurs_name):
                kurs_lower = kurs_name.lower()
                if 'python' in kurs_lower or 'ki' in kurs_lower or 'llm' in kurs_lower:
                    return 0
                elif 'javascript' in kurs_lower and 'typescript' not in kurs_lower:
                    return 1
                elif 'typescript' in kurs_lower:
                    return 2
                elif 'vue' in kurs_lower or 'react' in kurs_lower:
                    return 3
                elif 'html' in kurs_lower or 'css' in kurs_lower or 'browser' in kurs_lower:
                    return 4
                elif 'git' in kurs_lower or 'jira' in kurs_lower or 'bpmn' in kurs_lower or 'uml' in kurs_lower:
                    return 5
                elif 'sql' in kurs_lower or 'datenbank' in kurs_lower:
                    return 6
                elif 'netzwerk' in kurs_lower or 'osi' in kurs_lower or 'ipv4' in kurs_lower:
                    return 7
                elif 'architektur' in kurs_lower or 'design' in kurs_lower:
                    return 8
                elif 'java' in kurs_lower and 'javascript' not in kurs_lower:
                    return 9
                elif 'powershell' in kurs_lower or 'cmd' in kurs_lower:
                    return 10
                else:
                    return 11
            
            kurse_liste.sort(key=kurs_prioritaet)
            
            # Zeige alle Kurse
            for kurs in kurse_liste:
                kurse_html += f'<span class="tag">{kurs}</span>\n                        '
            
            # Füge "..." Tag hinzu
            kurse_html += '<span class="tag">...</span>\n                        '
            kurse_html += '<p style="font-style: italic; color: #7f8c8d; font-size: 8.5pt; margin-top: 8px;">Weitere private Kurse finden Sie bei Interesse auf meiner Portfolio-Website.</p>'
        else:
            print(f"⚠️  Weiterbildungen-Verzeichnis nicht gefunden: {weiterbildungen_dir}")
    except Exception as e:
        print(f"⚠️  Fehler beim Laden der Kurse: {e}")
    
    # Optionale Links
    optional_links_html = ""
    if PERSOENLICHE_DATEN.get('github'):
        optional_links_html += f"""
                <div class="data-row">
                    <img src="images/icons/github.svg" class="data-icon" alt="GitHub">
                    <div class="data-value">{PERSOENLICHE_DATEN['github']}</div>
                </div>"""
    if PERSOENLICHE_DATEN.get('linkedin'):
        optional_links_html += f"""
                <div class="data-row">
                    <img src="images/icons/linkedin.svg" class="data-icon" alt="LinkedIn">
                    <div class="data-value">{PERSOENLICHE_DATEN['linkedin']}</div>
                </div>"""
    if PERSOENLICHE_DATEN.get('website'):
        optional_links_html += f"""
                <div class="data-row">
                    <img src="images/icons/globe.svg" class="data-icon" alt="Website">
                    <div class="data-value">{PERSOENLICHE_DATEN['website']}</div>
                </div>"""
    
    # Platzhalter ersetzen
    replacements = {
        '{vorname}': PERSOENLICHE_DATEN['vorname'],
        '{nachname}': PERSOENLICHE_DATEN['nachname'],
        '{email}': PERSOENLICHE_DATEN['email'],
        '{telefon}': PERSOENLICHE_DATEN['telefon'],
        '{strasse}': PERSOENLICHE_DATEN['strasse'],
        '{plz}': PERSOENLICHE_DATEN['plz'],
        '{ort}': PERSOENLICHE_DATEN['ort'],
        '{linkedin}': PERSOENLICHE_DATEN.get('linkedin', ''),
        '{website}': PERSOENLICHE_DATEN.get('website', ''),
        '{geburtsdatum}': PERSOENLICHE_DATEN['geburtsdatum'],
        '{geburtsort}': PERSOENLICHE_DATEN['geburtsort'],
        '{nationalitaet}': PERSOENLICHE_DATEN['nationalitaet'],
        '{datum}': datetime.now().strftime("%d.%m.%Y"),
        '{optional_links}': optional_links_html,
        '{berufserfahrung_entries}': berufserfahrung_html,
        '{ausbildung_entries}': ausbildung_html,
        '{programmiersprachen_skills}': programmiersprachen_html,
        '{ai_ml_tags}': ai_ml_html,
        '{frameworks_tags}': frameworks_html,
        '{tools_tags}': tools_html,
        '{sprachen_entries}': sprachen_html,
        '{zertifikate_entries}': zertifikate_html,
        '{projekte_entries}': projekte_html,
        '{kurse_tags}': kurse_html,
    }
    
    for placeholder, value in replacements.items():
        html_content = html_content.replace(placeholder, value)
    
    # CSS laden
    css_path = TEMPLATES_DIR / 'styles.css'
    
    # PDF generieren mit dynamischem Dateinamen (Name + Datum)
    vorname = PERSOENLICHE_DATEN['vorname']
    nachname = PERSOENLICHE_DATEN['nachname']
    datum_heute = datetime.now().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f'Lebenslauf_{vorname}_{nachname}_{datum_heute}.pdf'
    HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf(
        output_path,
        stylesheets=[CSS(filename=str(css_path))]
    )
    
    print(f"✅ Lebenslauf erstellt: {output_path}")
    return output_path


def main():
    """Hauptfunktion - Erstellt alle Bewerbungsunterlagen"""
    print("=" * 60)
    print("🚀 Bewerbungsgenerator")
    print("=" * 60)
    
    # Output-Verzeichnis sicherstellen
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    try:
        # PDFs generieren
        anschreiben_path = generate_anschreiben()
        lebenslauf_path = generate_lebenslauf()
        
        print("\n" + "=" * 60)
        print("✨ Alle Dokumente erfolgreich erstellt!")
        print("=" * 60)
        print(f"\n📂 Ausgabeverzeichnis: {OUTPUT_DIR}")
        print(f"\n   • Anschreiben: {anschreiben_path.name}")
        print(f"   • Lebenslauf:  {lebenslauf_path.name}")
        print("\n💡 Tipp: Passe die Daten in 'data/persoenliche_daten.py' an!")
        
    except Exception as e:
        print(f"\n❌ Fehler bei der PDF-Generierung: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
