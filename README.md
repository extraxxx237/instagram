# Norivagrowbags – Instagram Content-Agent

Automatisierter Redaktions-Assistent für den Kanal [@norivagrowbags](https://www.instagram.com/norivagrowbags/)
(Pflanzsäcke/Vließsäcke, Gartentipps, nützliches Wissen rund ums Gärtnern).

Der Agent **plant, recherchiert und erstellt Content-Entwürfe** – er postet nicht
automatisch. Jeder Vorschlag wird dir vor Veröffentlichung vorgelegt
(Telegram-Freigabe), damit kein urheberrechtlich geschütztes Material und
keine ungeprüften Aussagen live gehen.

## Wie es funktioniert

1. **Strategie-Basis** (`docs/strategy.md`): Content-Pillars, Zielgruppe, Tonalität –
   das Gehirn, das der Agent bei jedem Lauf als Kontext bekommt.
2. **n8n-Workflow** (`workflows/01-content-planning.json`):
   - läuft 1x/Woche automatisch
   - sucht aktuelle/virale Garten- & Pflanzsack-Themen (Web-Suche, keine
     Bilder/Texte werden kopiert, nur Fakten/Ideen als Inspiration)
   - lässt ein LLM (Claude) daraus 3 Post-Konzepte erstellen: Hook, Caption,
     Hashtags, Bildidee (für eigenes Foto/eigene Grafik – nichts wird von
     Dritten übernommen)
   - schreibt die Entwürfe in einen Redaktionsplan (Google Sheet)
   - schickt dir die Entwürfe per Telegram zur Freigabe
3. **Freigabe & Posting**: Du markierst im Sheet "Freigegeben" oder änderst
   den Text. Veröffentlichung erfolgt aktuell manuell (Copy&Paste in die
   Instagram-App) oder, sobald die Meta-API eingerichtet ist, per zweitem
   Workflow automatisch zum geplanten Zeitpunkt.

## Was du noch einrichten musst

Siehe `docs/setup.md` für die Schritt-für-Schritt-Anleitung. Kurzfassung:

| Baustein | Wofür | Status |
|---|---|---|
| n8n-Instanz (Cloud oder selbst gehostet) | Workflow ausführen | offen |
| Anthropic API-Key | Recherche-Auswertung, Strategie, Captions | offen |
| Web-Search API (z.B. Tavily/Serper) | Aktuelle Themen/Trends finden | offen |
| Google Sheet + Service Account | Redaktionsplan/Content-Kalender | offen |
| Telegram Bot | Freigabe-Benachrichtigung | offen |
| Instagram Business-Account + Meta Developer App | Später: automatisches Posten | offen (optional, Phase 2) |

## Phase 2 (optional, später)

Sobald du einen Instagram **Business/Creator-Account**, verknüpfte
**Facebook-Seite** und eine **Meta Developer App** mit `instagram_content_publish`
Berechtigung hast, kann `workflows/02-publish-on-approval.json` freigegebene
Posts automatisch zum Wunschzeitpunkt veröffentlichen (Graph API). Das ist
bewusst getrennt, weil Meta App Review Zeit braucht und du erst die manuelle
Variante testen solltest.
