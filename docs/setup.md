# Setup-Anleitung – Schritt für Schritt

## 1. n8n-Instanz
- Kostenlos starten: https://n8n.io (Cloud-Trial) oder selbst hosten
  (`docker run -it --rm -p 5678:5678 n8nio/n8n`)
- Workflow importieren: n8n-Oberfläche → "Import from File" →
  `workflows/01-content-planning.json`

## 2. Google Sheet als Redaktionsplan
1. Neues Google Sheet anlegen, Tabellenblatt `Redaktionsplan` mit Spalten:
   `pillar | hook | caption | hashtags | bildidee | format | begruendung_relevanz | datum_erstellt | status`
2. In n8n unter Credentials einen **Google Sheets OAuth2**-Zugang anlegen
   (Google Cloud Projekt → Sheets API aktivieren → OAuth-Client erstellen).
3. Im Node "In Redaktionsplan speichern" die Sheet-ID eintragen (aus der URL
   des Google Sheets) und den Credential auswählen.

## 3. Anthropic API-Key
1. Account auf https://console.anthropic.com anlegen, API-Key erzeugen.
2. In n8n Credential vom Typ "Anthropic API" anlegen, Key eintragen.
3. Im Node "Content-Konzepte erstellen (Claude)" diesen Credential zuweisen.

## 4. Web-Recherche (Tavily, für aktuelle/virale Themen)
1. Kostenlosen Key auf https://tavily.com holen (Free-Tier reicht zum Start).
2. In n8n Credential anlegen oder Key direkt im HTTP-Body des Nodes
   "Trend & Themen-Recherche" hinterlegen (`$credentials.tavilyApi.apiKey`
   anpassen bzw. durch den Key ersetzen).

## 5. Telegram-Bot für Freigaben
1. In Telegram mit `@BotFather` einen neuen Bot erstellen → Token erhalten.
2. Mit dem Bot selbst eine Nachricht schreiben, dann über
   `https://api.telegram.org/bot<TOKEN>/getUpdates` deine `chat_id` auslesen.
3. In n8n Telegram-Credential mit dem Bot-Token anlegen, im Node
   "Freigabe per Telegram anfordern" Credential + `chat_id` eintragen.

## 6. Workflow aktivieren
- Workflow in n8n speichern und **aktivieren** (Schalter oben rechts).
- Läuft danach automatisch jeden Montag 8 Uhr; manuell testen über
  "Execute Workflow" in der n8n-Oberfläche.

## 7. Wöchentlicher Ablauf für dich
1. Telegram-Nachricht mit 3 neuen Post-Entwürfen kommt an.
2. Du öffnest das Google Sheet, prüfst/passt Caption & Bildidee an.
3. Du erstellst/bearbeitest das passende eigene Foto/Grafik laut Bildidee.
4. Status im Sheet auf `Freigegeben` setzen.
5. Aktuell: manuell in der Instagram-App posten (Copy&Paste aus dem Sheet).

## 8. Phase 2 – automatisches Posten (optional, später)
Voraussetzungen, bevor `workflows/02-publish-on-approval.json` sinnvoll ist:
1. Instagram-Account auf **Business oder Creator** umstellen.
2. Mit einer **Facebook-Seite** verknüpfen (Pflicht für die Graph API).
3. Meta Developer App unter https://developers.facebook.com erstellen,
   Produkt "Instagram Graph API" hinzufügen.
4. Berechtigung `instagram_content_publish` beantragen (App Review nötig,
   kann einige Tage dauern).
5. Erst danach lohnt sich der zweite Workflow – bis dahin manuell posten und
   die Caption/Hashtag-Vorschläge anhand der Performance (Insights) verfeinern.

Sag Bescheid, wenn du bei einem der Schritte (z.B. Google Sheet, Telegram-Bot,
Anthropic-Key) Hilfe brauchst – ich kann die jeweiligen Credentials und Node-
Konfigurationen im Detail mit dir durchgehen.
