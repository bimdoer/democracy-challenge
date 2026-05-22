# Predictive Direct Democracy

Data project investigating how closely the recommendations of political actors align with federal popular vote outcomes in Switzerland.

The main focus areas are:

- **Institutional congruence** (Federal Council, Federal Assembly, political parties)
- **Temporal development** (since 1848)
- **Thematic differences** (policy areas)
- **Geographical differences** (cantonal patterns)

The project is based on the Swissvotes dataset (University of Bern / Année Politique Suisse).

## Research Question

How closely do the voting recommendations of the Federal Council, the Federal Assembly, and major parties match actual popular vote outcomes, and how does this alignment change over time, across policy topics, and across regions?

## Data Foundation

- **Source:** Swissvotes
- **Period:** 1848 to 2026 (depending on dataset updates)
- **Raw data:** `data/raw/DATASET CSV 11-02-2026.csv`
- **Codebook:** `data/raw/CODEBOOK.pdf`

## Project Structure

```text
.
├── data/
│   ├── raw/                  # Raw data and GeoJSON
│   └── processed/            # Processed intermediate outputs (CSV)
├── notebooks/                # Main analyses in Jupyter notebooks
│   ├── data_wrangling.ipynb
│   ├── Berechnung_Positionen.ipynb
│   ├── Institutionelle_Analyse.ipynb
│   ├── Zeitliche_Analyse.ipynb
│   ├── Thematisch_Analyse.ipynb
│   ├── heatmap.ipynb
│   ├── geomap.ipynb
│   └── visualisierungen.py   # Reusable plotting functions
├── Blog/                     # Blog texts and exported visualizations
│   └── blog_plots/
├── Grundlagen/               # Additional analyses, tables, chart generator
└── pyproject.toml
```

## Setup

### Requirements

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/)

### Installation

```bash
uv sync --dev
```

Start Jupyter:

```bash
uv run jupyter lab
```

## Reproducible Workflow

The notebooks build on each other. For clean reproduction, run them in this order:

1. `notebooks/data_wrangling.ipynb`  
   - reads raw data from `data/raw/`
   - creates `data/processed/swissvotes_processed.csv`

2. `notebooks/Berechnung_Positionen.ipynb`  
   - computes congruence/agreement scores
   - creates:
     - `data/processed/df_with_positions.csv`
     - `data/processed/df_heatmap_with_positions.csv`

3. Analysis notebooks:
   - `notebooks/Institutionelle_Analyse.ipynb`
   - `notebooks/Zeitliche_Analyse.ipynb`
   - `notebooks/Thematisch_Analyse.ipynb`
   - `notebooks/heatmap.ipynb`
   - `notebooks/geomap.ipynb`

4. Blog visualizations and text:
   - Exported charts are mainly written to `Blog/blog_plots/`
   - Text modules are stored in `Blog/*.md`

## Additional Evaluations

The `Grundlagen/` folder contains supplementary scripts and artifacts:

- `generate_charts.py` (additional descriptive charts)
- `Swissvotes_Uebersicht.md` (documented dataset overview)
- CSV tables for use in reports/blog posts

Run (inside `Grundlagen`):

```bash
uv run python generate_charts.py
```

## Technology Stack

- `pandas`, `numpy`
- `matplotlib`, `seaborn`, `plotly`
- `scikit-learn`, `statsmodels`
- `geopandas`
- Jupyter notebooks

## Notes

- The repository also contains older notebook versions in `notebooks/Old Notebooks/`.
- Geodata for maps is located in `data/raw/ch.json`.
- Some outputs are versioned so results can be inspected directly.
