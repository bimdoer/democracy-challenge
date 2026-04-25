"""
Verwendung im Notebook:
from visualisierungen import *
from visualisierungen import heatmap
from visualisierungen import heatmap as heat
"""

# BALKENDIAGRAMM

from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


# ══════════════════════════════════════════════════════════════
# FARBEN & PALETTEN  (Paul Tol «muted», farbenblind-sicher)
# ══════════════════════════════════════════════════════════════

HAUPTFARBE = "#4477AA"
AKZENTFARBE = "#CC6677"

# Blau, Altrosa, Sand, Himmel, Purpur, Teal
PALETTE_KATEGORIAL = ["#4477AA", "#CC6677", "#DDCC77", "#88CCEE", "#AA4499", "#44AA99"]
PALETTE_KATEGORIAL_VIELE_WERTE = ["#4477AA", "#CC6677", "#DDCC77", "#88CCEE", "#AA4499", "#44AA99", "#332288", "#882255", "#999933", "#66CCEE", "#117733", "#AA7744", "#6699CC", "#CC9988", "#44BB99"]
PALETTE_SNS = sns.color_palette(PALETTE_KATEGORIAL)

CMAP_HEATMAP = "coolwarm"
CMAP_DIVERGIEREND = "coolwarm"

# GeoJSON Kantone (Simplemaps, data/raw/ch.json): properties «id» z. B. CHZH, «name» englisch
_DEFAULT_CH_GEOJSON = Path(__file__).resolve().parent.parent / "data" / "raw" / "ch.json"


def palette_farben(n):
    """Gibt n Farben aus der kategorialen Palette zurück."""
    if n <= len(PALETTE_KATEGORIAL):
        return sns.color_palette(PALETTE_KATEGORIAL[:n])
    return sns.color_palette(PALETTE_KATEGORIAL, n_colors=n)


def _annotate_bars(ax, fmt=".0f"):
    """Hilfsfunktion: Werte über Balken schreiben."""
    for p in ax.patches:
        h = p.get_height()
        if pd.notna(h) and h != 0:
            ax.annotate(f"{h:{fmt}}",
                        (p.get_x() + p.get_width() / 2, h),
                        ha="center", va="bottom",
                        fontsize=9, xytext=(0, 3),
                        textcoords="offset points")


# ══════════════════════════════════════════════════════════════
# 1. BALKENDIAGRAMM
# ══════════════════════════════════════════════════════════════

def balkendiagramm(data, x, y, hue=None, xlabel="", ylabel="", titel="",
                   ylim=None, palette=None,
                   figsize=(12, 6), rotation=0, order=None,
                   annotate=False, fmt=".0f"):
    if palette is None:
        palette = PALETTE_KATEGORIAL

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(data=data, x=x, y=y, hue=hue,
                palette=palette, legend=hue is not None, order=order, ax=ax)

    if annotate:
        _annotate_bars(ax, fmt)

    plt.title(titel, fontsize=14) if titel else None
    plt.xlabel(xlabel, fontsize=10, fontweight="bold")
    plt.ylabel(ylabel, fontsize=10, fontweight="bold")
    plt.xticks(fontsize=10, rotation=rotation)
    plt.yticks(fontsize=10)
    if ylim:
        plt.ylim(*ylim)
    if hue:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 2. BALKENDIAGRAMM SORTIERT
# ══════════════════════════════════════════════════════════════

def balkendiagramm_sortiert(data, x, y, xlabel="", ylabel="", titel="",
                            ylim=None, palette=None,
                            figsize=(12, 6), rotation=90,
                            annotate=False, fmt=".0f"):
    if palette is None:
        palette = PALETTE_KATEGORIAL

    sortiert = data.sort_values(y, ascending=False)

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(data=data, x=x, y=y,
                order=sortiert[x], hue=x, hue_order=sortiert[x],
                palette=palette, legend=False, ax=ax)

    if annotate:
        _annotate_bars(ax, fmt)

    plt.title(titel, fontsize=14) if titel else None
    plt.xlabel(xlabel, fontsize=10, fontweight="bold")
    plt.ylabel(ylabel, fontsize=10, fontweight="bold")
    plt.xticks(fontsize=9, rotation=rotation)
    plt.yticks(fontsize=9)
    if ylim:
        plt.ylim(*ylim)
    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 3. GESTAPELTES BALKENDIAGRAMM
# ══════════════════════════════════════════════════════════════

def gestapeltes_balkendiagramm(pivot_prozent, xlabel="", ylabel="Anteil (%)",
                               legend_titel="", figsize=(8, 6),
                               xlabels=None,
                               annotate=False, fmt=".0f", min_anteil=5):
    sns.set_style("whitegrid")
    farben = palette_farben(len(pivot_prozent.columns))

    ax = pivot_prozent.plot(
        kind="bar", stacked=True,
        color=farben, figsize=figsize,
        edgecolor="none", legend=True)

    ax.legend(title=legend_titel, loc="center left",
              bbox_to_anchor=(1, 0.5), frameon=False)

    if xlabels:
        ax.set_xticklabels(xlabels)

    if annotate:
        for c in ax.containers:
            labels = [f"{v.get_height():{fmt}}%" if v.get_height() >= min_anteil else ""
                      for v in c]
            ax.bar_label(c, labels=labels, label_type="center", fontsize=9)

    plt.xlabel(xlabel, fontsize=12, fontweight="bold")
    plt.ylabel(ylabel, fontsize=12, fontweight="bold")
    plt.xticks(fontsize=10, rotation=0)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 4. ANTEILSDIAGRAMM (100% Fill)
# ══════════════════════════════════════════════════════════════

def anteilsdiagramm(data, x, hue, xlabel="", ylabel="Anteil",
                    palette=None, figsize=(8, 5), xlabels=None, titel=''):
    if palette is None:
        palette = PALETTE_KATEGORIAL

    sns.set_style("whitegrid")
    plt.figure(figsize=figsize)
    ax = sns.histplot(
        data=data, x=x, hue=hue,
        palette=palette,
        multiple="fill", stat="percent", discrete=True)

    if xlabels:
        ax.set_xticklabels(xlabels)

    ax.legend(title=titel)
    plt.xlabel(xlabel, fontsize=12, fontweight="bold")
    plt.ylabel(ylabel, fontsize=12, fontweight="bold")
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 5. HEATMAP
# ══════════════════════════════════════════════════════════════

def heatmap(pivot, xlabel="", ylabel="", vmax=None,
            cmap=None, figsize=(6, 7), fmt=".0f",
            xlabels=None, ylabels=None, rotation=0):
    if cmap is None:
        cmap = CMAP_HEATMAP

    sns.set_style("whitegrid")
    plt.figure(figsize=figsize)
    ax = sns.heatmap(
        pivot, cmap=cmap,
        vmin=None, vmax=None,
        linewidths=0.1,
        annot=True, fmt=fmt,
        annot_kws={"size": 9})
    ax.xaxis.tick_top()
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha="center")
    ax.xaxis.set_label_position("top")

    if xlabels:
        ax.set_xticklabels(xlabels)
    if ylabels:
        ax.set_yticklabels(ylabels)

    plt.xlabel(xlabel, fontsize=12, fontweight="bold")
    plt.ylabel(ylabel, fontsize=12, fontweight="bold")
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9, rotation=rotation)
    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 6. BOXPLOT
# ══════════════════════════════════════════════════════════════

def boxplot(data, x=None, y=None, hue=None, titel="", xlabel="", ylabel="",
            farbe=None, palette=None, figsize=(10, 5), width = 0.4, rotation = 0, hline=None):
    if farbe is None and palette is None:
        farbe = HAUPTFARBE

    sns.set_style("whitegrid")
    plt.figure(figsize=figsize)
    sns.boxplot(data=data, x=x, y=y, hue=hue, color=farbe, palette=palette, width=width)

    # Horizontale Referenzlinie
    if hline is not None:
        plt.axhline(hline, color="#CC6677", linestyle="--", linewidth=1, alpha=0.7)

    plt.title(titel, fontsize=14) if titel else None
    plt.xlabel(xlabel, fontsize=12) if xlabel else None
    plt.ylabel(ylabel, fontsize=12) if ylabel else None
    plt.xticks(rotation=rotation)
    if hue:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 7. SCATTERPLOT
# ══════════════════════════════════════════════════════════════

def scatterplot(data, x, y, size=None, titel="", xlabel="", ylabel="",
                sizes=(20, 800), alpha=0.4, farbe=None, hue=None, figsize=(10, 5), rotation=0, legendentitel='', palette=None):
    if farbe is None:
        farbe = HAUPTFARBE

    sns.set_style("whitegrid")
    plt.figure(figsize=figsize)
    ax = sns.scatterplot(
        data=data, x=x, y=y,
        size=size, sizes=sizes,
        alpha=alpha, color=farbe, hue=hue, palette=palette)

    ax.legend(title=legendentitel)
    plt.title(titel, fontsize=14) if titel else None
    plt.xlabel(xlabel, fontsize=12, fontweight="bold")
    plt.ylabel(ylabel, fontsize=12, fontweight="bold")
    plt.xticks(rotation=rotation)
    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 8. HISTOGRAMM
# ══════════════════════════════════════════════════════════════

def histogramm(data, spalte, bins=50, titel="", xlabel="", ylabel="Anzahl",
               farbe=None, xlim=None, figsize=(10, 5), vlines=None, rotation=0):
    if farbe is None:
        farbe = HAUPTFARBE

    sns.set_style("whitegrid")
    plt.figure(figsize=figsize)
    sns.histplot(data[spalte], bins=bins, color=farbe)

    if vlines:
        for val, label in vlines:
            plt.axvline(val, color=AKZENTFARBE, linestyle='--', label=label)
        plt.legend()

    plt.title(titel, fontsize=14) if titel else None
    plt.xlabel(xlabel, fontsize=12, fontweight="bold")
    plt.ylabel(ylabel, fontsize=12, fontweight="bold", rotation=rotation)
    if xlim:
        plt.xlim(*xlim)
    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 9. COUNTPLOT
# ══════════════════════════════════════════════════════════════

def countplot(data, x, titel="", xlabel="", ylabel="Anzahl Nennungen",
              farbe=None, figsize=(10, 5), rotation=0,
              annotate=False):
    if farbe is None:
        farbe = HAUPTFARBE

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=figsize)
    sns.countplot(data=data, x=x, color=farbe, ax=ax)

    if annotate:
        _annotate_bars(ax, fmt=".0f")

    plt.title(titel, fontsize=14) if titel else None
    plt.xlabel(xlabel, fontsize=12, fontweight="bold")
    plt.ylabel(ylabel, fontsize=12, fontweight="bold")
    plt.xticks(fontsize=9, rotation=rotation)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 10. LINIENDIAGRAMM
# ══════════════════════════════════════════════════════════════

def liniendiagramm(data, x, y, hue=None, titel="", xlabel="", ylabel="",
                   palette=None, farbe=None, figsize=(10, 5),
                   marker="o", linewidth=2, rotation=0, errorbar=False, hline=None):
    if palette is None and hue:
        palette = PALETTE_KATEGORIAL
    if farbe is None and not hue:
        farbe = HAUPTFARBE

    sns.set_style("whitegrid")
    plt.figure(figsize=figsize)
    sns.lineplot(
        data=data, x=x, y=y, hue=hue,
        palette=palette, color=farbe,
        marker=marker, linewidth=linewidth,  errorbar="ci" if errorbar else None)

    # Horizontale Referenzlinie
    if hline is not None:
        plt.axhline(hline, color="#CC6677", linestyle="--", linewidth=1, alpha=0.7)

    plt.title(titel, fontsize=14) if titel else None
    plt.xlabel(xlabel, fontsize=12, fontweight="bold")
    plt.ylabel(ylabel, fontsize=12, fontweight="bold")
    plt.xticks(fontsize=10, rotation=rotation)
    plt.yticks(fontsize=10)
    plt.ylim(-0.5, 0.5)
    plt.tight_layout()
    plt.show()

# ══════════════════════════════════════════════════════════════
# 11. MAP SCHWEIZERKARTE
# ══════════════════════════════════════════════════════════════


def schweiz_karte_choropleth(
    data,
    wert_spalte,
    join_data="id",
    geojson_pfad=None,
    join_geo="id",
    titel="",
    cmap=None,
    figsize=(8, 6),
    legend_label="",
    kante_farbe="#333333",
    kante_linewidth=0.4,
    fehlend_farbe="#EEEEEE",
    vmin=None,
    vmax=None,
):
    """
    Statische Choroplethenkarte (Schweiz), Kantone.

    Standard ist ``data/raw/ch.json`` (Simplemaps): Join-Spalte ``id`` mit Werten wie
    «CHZH», «CHBE». Bei zwei Buchstaben im Datensatz z. B. ``df['id'] = 'CH' + df['kt']``.

    Parameters
    ----------
    data : pandas.DataFrame
        Enthält ``join_data`` und ``wert_spalte``.
    geojson_pfad : str oder pathlib.Path, optional
        GeoJSON mit Kantonsgrenzen. Standard: Projektdatei ``data/raw/ch.json``.
    join_data / join_geo : str
        Spalte in ``data`` bzw. in den Geometriedaten (bei ch.json typisch beide ``id``
        oder z. B. ``name`` für englische Kantonsnamen).
    vmin, vmax : float, optional
        Farbskala-Grenzen (wie bei klassischen Heatmaps).
    """
    if cmap is None:
        cmap = CMAP_HEATMAP

    path = Path(geojson_pfad) if geojson_pfad is not None else _DEFAULT_CH_GEOJSON
    if not path.is_file():
        raise FileNotFoundError(f"GeoJSON nicht gefunden: {path}")

    if join_data not in data.columns:
        raise ValueError(f"Spalte «{join_data}» fehlt in data. Vorhanden: {list(data.columns)!r}")
    if wert_spalte not in data.columns:
        raise ValueError(f"Spalte «{wert_spalte}» fehlt in data.")

    kantone = gpd.read_file(path)
    if join_geo not in kantone.columns:
        raise ValueError(
            f"Spalte «{join_geo}» fehlt in den Geodaten. Vorhanden: {list(kantone.columns)!r}"
        )

    data_sub = data[[join_data, wert_spalte]].drop_duplicates(subset=[join_data])
    if join_geo == join_data:
        merged = kantone.merge(data_sub, on=join_geo, how="left")
    else:
        merged = kantone.merge(data_sub, left_on=join_geo, right_on=join_data, how="left")

    sns.set_style("white")
    fig, ax = plt.subplots(figsize=figsize)

    plot_kwds = {
        "column": wert_spalte,
        "cmap": cmap,
        "linewidth": kante_linewidth,
        "edgecolor": kante_farbe,
        "legend": True,
        "legend_kwds": {"label": legend_label or str(wert_spalte), "shrink": 0.6},
        "missing_kwds": {"color": fehlend_farbe, "label": "keine Daten"},
        "ax": ax,
    }
    if vmin is not None:
        plot_kwds["vmin"] = vmin
    if vmax is not None:
        plot_kwds["vmax"] = vmax

    merged.plot(**plot_kwds)

    ax.set_title(titel, fontsize=14)
    ax.set_axis_off()
    plt.tight_layout()
    plt.show()

# ══════════════════════════════════════════════════════════════
# 12. Interaktiver Lineplot
# ══════════════════════════════════════════════════════════════
import plotly.express as px
import plotly.graph_objects as go

def liniendiagramm_interaktiv(df, x, y, titel="", xlabel="", ylabel="",
                                  farbe=HAUPTFARBE, hover_data=None):
    fig = px.line(
        df, x=x, y=y,
        title=titel,
        hover_data=hover_data,
        color_discrete_sequence=[farbe],
    )
    fig.update_layout(
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        template="simple_white",
        font=dict(family="Arial", size=13),
    )
    return fig