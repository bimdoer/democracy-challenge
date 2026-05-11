# Prädiktive Direkte Demokratie

Datenprojekt zur Frage, wie stark die Empfehlungen politischer Akteure mit eidgenössischen Volksentscheiden in der Schweiz übereinstimmen.

Im Zentrum stehen:

- **Institutionelle Kongruenz** (Bundesrat, Bundesversammlung, Parteien)
- **Zeitliche Entwicklung** (seit 1848)
- **Thematische Unterschiede** (Politikbereiche)
- **Geografische Unterschiede** (kantonale Muster)

Grundlage ist der Swissvotes-Datensatz (Universität Bern / Année Politique Suisse).

## Forschungsfrage

Wie stark stimmen die Abstimmungsempfehlungen von Bundesrat, Bundesversammlung und grossen Parteien mit dem effektiven Volksentscheid überein, und wie verändert sich diese Übereinstimmung über Zeit, Themenfelder und Regionen?

## Datengrundlage

- **Quelle:** Swissvotes
- **Zeitraum:** 1848 bis 2026 (abhängig vom Datenstand)
- **Rohdaten:** `data/raw/DATASET CSV 11-02-2026.csv`
- **Codebook:** `data/raw/CODEBOOK.pdf`

## Projektstruktur

```text
.
├── data/
│   ├── raw/                  # Rohdaten und GeoJSON
│   └── processed/            # Aufbereitete Zwischenstände (CSV)
├── notebooks/                # Hauptanalysen in Jupyter Notebooks
│   ├── data_wrangling.ipynb
│   ├── Berechnung_Positionen.ipynb
│   ├── Institutionelle_Analyse.ipynb
│   ├── Zeitliche_Analyse.ipynb
│   ├── Thematisch_Analyse.ipynb
│   ├── heatmap.ipynb
│   ├── geomap.ipynb
│   └── visualisierungen.py   # Wiederverwendbare Plot-Funktionen
├── Blog/                     # Blogtexte und exportierte Visualisierungen
│   └── blog_plots/
├── Grundlagen/               # Zusatzanalysen, Tabellen, Chart-Generator
└── pyproject.toml
```

## Setup

### Voraussetzungen

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/)

### Installation

```bash
uv sync --dev
```

Jupyter starten:

```bash
uv run jupyter lab
```

## Reproduzierbarer Workflow

Die Notebooks bauen aufeinander auf. Für eine saubere Reproduktion in dieser Reihenfolge ausführen:

1. `notebooks/data_wrangling.ipynb`  
   - liest Rohdaten aus `data/raw/`
   - erstellt `data/processed/swissvotes_processed.csv`

2. `notebooks/Berechnung_Positionen.ipynb`  
   - berechnet Kongruenz-/Zustimmungswerte
   - erstellt:
     - `data/processed/df_with_positions.csv`
     - `data/processed/df_heatmap_with_positions.csv`

3. Analyse-Notebooks:
   - `notebooks/Institutionelle_Analyse.ipynb`
   - `notebooks/Zeitliche_Analyse.ipynb`
   - `notebooks/Thematisch_Analyse.ipynb`
   - `notebooks/heatmap.ipynb`
   - `notebooks/geomap.ipynb`

4. Blog-Visualisierungen und Texte:
   - Export-Grafiken landen vor allem in `Blog/blog_plots/`
   - Textbausteine liegen in `Blog/*.md`

## Zusätzliche Auswertungen

Im Ordner `Grundlagen/` gibt es ergänzende Skripte und Artefakte:

- `generate_charts.py` (zusätzliche deskriptive Charts)
- `Swissvotes_Uebersicht.md` (dokumentierte Datensatzübersicht)
- CSV-Tabellen für Einbindung in Berichte/Blog

Ausführung (im Ordner `Grundlagen`):

```bash
uv run python generate_charts.py
```

## Technologie-Stack

- `pandas`, `numpy`
- `matplotlib`, `seaborn`, `plotly`
- `scikit-learn`, `statsmodels`
- `geopandas`
- Jupyter Notebooks

## Hinweise

- Das Repository enthält auch ältere Notebook-Versionen unter `notebooks/Old Notebooks/`.
- Geodaten für Karten liegen in `data/raw/ch.json`.
- Einige Outputs sind bereits versioniert, damit Ergebnisse direkt nachvollzogen werden können.
