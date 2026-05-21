# FineFits — Roadmap & geplante Features

Persönliche Feature-Roadmap für **FineFits** (White-Label-Fork von Wardrowbe).  
Stand: Mai 2026 · Prioritäten können sich ändern.

---

## Kurzüberblick

| Priorität | Feature | Status heute |
|-----------|---------|--------------|
| 🔴 Hoch | Automatische Hintergrundentfernung beim Upload | Manuell per Button im Teile-Detail |
| 🔴 Hoch | Etiketten-Scanner (H&M, Zara, …) + offizielle Produktbilder | Noch nicht vorhanden |
| 🟡 Mittel | Erweiterte Marken- & Produktdatenbank | Abhängig vom Scanner |
| 🟢 Nice-to-have | Weitere Ideen (siehe unten) | Backlog |

---

## 1. Automatische Hintergrundentfernung

### Problem heute

Beim Hochladen bleibt der Original-Hintergrund (Bett, Stuhl, Wand) erhalten. Hintergrund entfernen ist **optional** und muss pro Teil manuell in der Detail-Ansicht ausgelöst werden (Radiergummi-Button, Backend: `rembg`).

### Ziel

Hintergrund wird **automatisch beim Upload** entfernt — ohne extra Klick. Der Kleiderschrank wirkt einheitlich und „katalogartig“.

### Geplantes Verhalten

1. Foto hochladen (Einzel- oder Bulk-Upload)
2. Bild speichern & verkleinern (wie bisher)
3. **Neu:** Hintergrundentfernung direkt im Upload-Pipeline-Schritt
4. Ergebnis auf neutralen Hintergrund legen (Standard: Weiß, optional in Einstellungen: Hellgrau, Transparent für Export)
5. Parallel: KI-Tagging wie bisher
6. Bei Fehler der BG-Entfernung: Original behalten, Teil trotzdem anlegen, optional Hinweis „Hintergrund konnte nicht entfernt werden“

### Technische Ansätze

- **Bestehende Infrastruktur nutzen:** `rembg` läuft bereits im Docker-Backend; Modell ist vorinstalliert (`u2net`).
- Upload-Worker erweitern oder BG-Removal in `process_and_store()` optional einschalten.
- Einstellung in `.env` / Benutzer-Präferenzen:
  - `BG_REMOVAL_ON_UPLOAD=true|false` (Default: `true` für FineFits)
  - `BG_REMOVAL_DEFAULT_COLOR=#FFFFFF`
- Performance: BG-Removal blockiert Upload nicht — asynchroner Job wie beim AI-Tagging (Status `processing` → `ready`).

### Offene Fragen

- [ ] Immer automatisch, oder Opt-in in den Einstellungen?
- [ ] Bulk-Upload: alle Bilder oder nur wenn erkannt wird, dass ein Kleidungsstück im Fokus ist?
- [ ] Fallback auf HTTP-Provider (z. B. withoutbg) für bessere Qualität bei Bedarf?

---

## 2. Etiketten-Scanner & offizielle Produktbilder

### Problem heute

Selbst gemachte Fotos sind oft:

- schlecht beleuchtet oder unscharf
- mit unruhigem Hintergrund
- nicht konsistent im Winkel und Schnitt

Offizielle Produktbilder von H&M, Zara, Mango, COS, Uniqlo usw. sind dagegen professionell, freigestellt und farblich korrekt.

### Ziel

Sophia (oder du) **scannt das Schildchen** am Kleidungsstück — Artikelnummer, Barcode oder QR — und FineFits:

1. erkennt Marke und Produkt-ID
2. sucht das passende Produkt in einer Datenbank / über eine Schnittstelle
3. lädt **offizielle Produktbilder** und Metadaten (Name, Farbe, Material, Kategorie)
4. legt das Teil im Kleiderschrank an — optional mit eigenem Foto als Zusatzbild oder komplett ersetzt durch Katalogbilder

### Geplanter Ablauf (UX)

```
Kleiderschrank → „Teil hinzufügen“ → Tab „Etikett scannen“
    → Kamera / Foto vom Label
    → OCR + Barcode-Erkennung
    → Treffer anzeigen („Zara – Leinen-Blazer, Art.-Nr. …“)
    → Bestätigen → Produktbilder + Metadaten importieren
    → optional: eigenes Tragefoto als zweites Bild
```

Alternativ: Beim normalen Upload automatisch prüfen, ob im Bild ein Etikett sichtbar ist, und vorschlagen „Produkt gefunden — Katalogbild übernehmen?“

### Technische Bausteine

| Baustein | Beschreibung |
|----------|--------------|
| **Label-Erkennung** | OCR (z. B. Tesseract, Cloud Vision, oder Vision-LLM) auf Crop des Etiketts |
| **Barcode/QR** | ZXing / QuaggaJS im Frontend oder Backend |
| **Artikelnummer-Parsing** | Regeln pro Marke (H&M: `Art. Nr.`, Zara: `REF.`, etc.) |
| **Produktsuche** | Marke-spezifische Lookup-Logik oder aggregierte API |
| **Bild-Import** | Offizielle URLs herunterladen, lokal speichern, Thumbnails erzeugen |
| **Metadaten-Mapping** | Katalog-Felder → FineFits-Felder (`type`, `colors`, `material`, `brand`, …) |

### Datenquellen (Recherche nötig)

- **Öffentliche Produkt-APIs** einzelner Marken (selten, oft eingeschränkt)
- **Barcode-Datenbanken** (GS1, Open Product Data) — decken nicht alle Fashion-Artikel ab
- **Web-Scraping / strukturierte Suche** auf Marken-Websites — rechtlich und technisch fragil (Robots, AGB, Rate Limits)
- **Manuelle Kuratierung** für Top-Marken als MVP (Regex + feste URL-Muster)
- **Community / Crowdsourcing** — Nutzer bestätigen Treffer, Datenbank wächst mit

Empfehlung für MVP: **2–3 Marken** (z. B. H&M + Zara), manuelles Mapping der Artikelnummer-Formate, Bestätigung durch Nutzer vor Import.

### Rechtliches & Fair Use

- Produktbilder sind urheberrechtlich geschützt; Nutzung nur **privat** im Self-Hosted-Kontext ist das eine, öffentliche App das andere.
- Markennamen und Logos in der UI: nur zur Identifikation, keine suggerierte Partnerschaft.
- Vor breiterem Rollout: Nutzungsbedingungen der Marken prüfen oder auf „Nutzer lädt Bild-URL selbst ein“ als Fallback setzen.

### Akzeptanzkriterien (Definition of Done)

- [ ] Etikett per Foto scannen und Artikelnummer extrahieren (mind. 80 % bei klaren H&M/Zara-Labels in Tests)
- [ ] Produktvorschau mit offiziellem Bild und Metadaten
- [ ] Ein-Klick-Import in den Kleiderschrank
- [ ] Duplikat-Erkennung (gleiche Artikelnummer nicht doppelt anlegen)
- [ ] Fallback: normaler Foto-Upload wenn kein Treffer

### Offene Fragen

- [ ] Welche Marken zuerst? (Vorschlag: H&M, Zara — häufig bei uns)
- [ ] Eigenes Foto behalten als „Realitäts-Check“ (Farbe abgenutzt, Falten)?
- [ ] Offline-Modus oder nur mit Internet?

---

## 3. Weitere Ideen (Backlog)

Diese Features hängen teilweise von 1 und 2 ab oder ergänzen sie sinnvoll.

### Bild & Kleiderschrank

- **Auto-Crop:** Kleidungsstück im Foto erkennen und zuschneiden (nicht nur Hintergrund entfernen)
- **Farbanpassung:** Katalogfarbe vs. real getragene Farbe abgleichen
- **Mehrere Ansichten:** Vorder-/Rückseite, Detail (Knöpfe, Stoff) als Galerie pro Teil

### Outfit & KI

- **„Was fehlt mir?“** — Lücken im Schrank erkennen (z. B. „keine passende Regenjacke“)
- **Capsule-Wardrobe-Modus** — minimalistische Schrank-Optimierung
- **Saisonaler Wechsel** — Teile ein-/auspacken, automatisch aus Vorschlägen filtern

### Alltag & Sharing

- **Packliste** für Urlaub basierend auf Wetter am Zielort
- **Geteilte Einkaufsliste** — „Steht dir gut, fehlt noch in deiner Größe“
- **Kalender-Sync** — Outfit-Vorschlag passend zu Terminen (Arbeit, Date, Sport)

### Technik & Betrieb

- **PWA / Installierbar** auf Sophias Handy (Add to Home Screen)
- **Push ohne ntfy** — native Web Push
- **Backup/Export** des gesamten Kleiderschranks (JSON + Bilder)

---

## Empfohlene Reihenfolge

1. **Automatische Hintergrundentfernung** — wenig UX-Aufwand, nutzt vorhandenen Code, sofort sichtbarer Gewinn im Schrank.
2. **Etiketten-Scanner MVP** — eine Marke, manueller Bestätigungsdialog, Katalogbild importieren.
3. **Zweite Marke + bessere OCR** — aus Erfahrung mit echten Etiketten iterieren.
4. Backlog nach Bedarf.

---

## Notizen

- Aktueller Stack: Next.js Frontend, FastAPI Backend, OpenAI für Vision/Text, `rembg` für Hintergrund, Docker.
- White-Label-Konfiguration: `APP_NAME=FineFits` in `.env`
- Feedback aus dem Alltag mit Sophia fließt direkt in Prioritäten ein — diese Roadmap lebt.
