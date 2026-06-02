# Democracy Challenge — Congruence Analysis of Swiss Federal Votes

Data project investigating how closely the voting recommendations of political actors align with actual popular vote outcomes at the federal level in Switzerland.

The analysis covers four perspectives:

- **Institutional congruence** (Federal Council, Federal Assembly, political parties)
- **Temporal development** (since 1848)
- **Thematic differences** (policy areas)
- **Geographical differences** (cantonal patterns)

Results are published in a Jekyll blog: `Blog/`  
**Live blog: https://bimdoer.github.io/democracy-challenge/**

The project is based on the Swissvotes dataset (University of Bern / Année Politique Suisse), a comprehensive database documenting all Swiss federal popular votes since 1848. The key variables used are national and cantonal vote outcomes (yes shares), voting recommendations from seven political actors (Federal Council, Federal Assembly, SP, Greens, The Centre, FDP, SVP), and the thematic classification of each ballot proposition.

## Research Question

How closely do the voting recommendations of the Federal Council, the Federal Assembly, and the major parties align with actual popular vote outcomes — and how does this alignment change over time, across policy topics, and across regions?

## Data Foundation

- **Source:** Swissvotes
- **Period:** 1848 to 2026
- **Raw data:** `data/raw/DATASET CSV 11-02-2026.csv`
- **Codebook:** `data/raw/CODEBOOK.pdf`

## Project Structure

```text
.
├── data/
│   ├── raw/                  # Raw data and GeoJSON
│   └── processed/            # Processed intermediate outputs (CSV)
├── notebooks/                # Analyses in Jupyter notebooks
│   ├── 1_data_wrangling.ipynb
│   ├── 2_berechnung.ipynb
│   ├── 3a_allgemeine_analyse.ipynb
│   ├── 3b_zeitliche_analyse.ipynb
│   ├── 3c_1_geomap.ipynb
│   ├── 3c_2_heatmap.ipynb
│   ├── 3d_thematisch_analyse.ipynb
│   ├── visualisierungen.py   # Reusable plotting functions
│   └── Old Notebooks/        # Discarded approaches and earlier versions (see below)
├── Blog/                     # Jekyll blog with texts and visualizations
│   ├── blog_plots/           # Exported charts
│   └── *.md                  # Blog pages
├── pitches/                  # Presentations used to document project progress
├── .github/workflows/        # CI/CD: auto-deploys the blog to GitHub Pages on push to main
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

Start the blog locally (Jekyll):

```bash
cd Blog
bundle exec jekyll serve --livereload
```

## Reproducible Workflow

The notebooks build on each other. For clean reproduction, run them in this order:

1. `notebooks/1_data_wrangling.ipynb`
   - Reads raw data from `data/raw/`
   - Creates `data/processed/swissvotes_processed.csv`

2. `notebooks/2_berechnung.ipynb`
   - Computes congruence scores
   - Creates:
     - `data/processed/df_with_positions.csv`
     - `data/processed/df_heatmap_with_positions.csv`

3. Analysis notebooks:
   - `notebooks/3a_allgemeine_analyse.ipynb`
   - `notebooks/3b_zeitliche_analyse.ipynb`
   - `notebooks/3c_1_geomap.ipynb`
   - `notebooks/3c_2_heatmap.ipynb`
   - `notebooks/3d_thematisch_analyse.ipynb`

4. Blog visualizations and texts:
   - Exported charts are written to `Blog/blog_plots/`
   - Blog texts are stored in `Blog/*.md`

## Technology Stack

- `pandas`, `numpy`
- `matplotlib`, `seaborn`, `plotly`
- `scikit-learn`, `statsmodels`
- `geopandas`
- Jupyter Notebooks
- Jekyll (Blog)

## Notes

- Geodata for maps: `data/raw/ch.json`.

### Old Notebooks (`notebooks/Old Notebooks/`)

Contains discarded approaches and earlier versions kept for reference:

| File | Description |
|---|---|
| `PCA_Regression_Trials_and_Failures.ipynb` | Discarded approach: attempted PCA and regression to explain or predict congruence scores. Abandoned in favour of the direct congruence metric. |
| `Zeitliche_Analyse_old.ipynb` | Earlier version of `3b_zeitliche_analyse.ipynb`, superseded by the current notebook. |
| `prädikative_demokratie_safety_file.ipynb` | Safety backup of early pitch visualizations using the raw dataset directly. |
| `visualisierung_csc.ipynb` | Early pitch visualization explorations. |
| `visualisierung_to.ipynb` | Early pitch visualization explorations, uses a local `praed.csv`. |
| `visualisierungen_archiv.py` | Plot functions from `visualisierungen.py` that are not currently used in any active notebook, archived for potential future use. |
