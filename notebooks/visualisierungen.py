"""
Verwendung im Notebook:
from visualisierungen import *
from visualisierungen import heatmap
from visualisierungen import heatmap as heat
"""

import math
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ══════════════════════════════════════════════════════════════
# FARBEN & PALETTEN  (Paul Tol «muted», farbenblind-sicher)
# ══════════════════════════════════════════════════════════════

HAUPTFARBE = "#4477AA"
AKZENTFARBE = "#CC6677"

PALETTE_KATEGORIAL = ["#4477AA", "#CC6677", "#DDCC77", "#88CCEE", "#AA4499", "#44AA99"]
PALETTE_KATEGORIAL_VIELE_WERTE = [
    "#4477AA", "#CC6677", "#DDCC77", "#88CCEE", "#AA4499", "#44AA99",
    "#332288", "#882255", "#999933", "#66CCEE", "#117733", "#AA7744",
    "#6699CC", "#CC9988", "#44BB99",
]
PALETTE_SNS = sns.color_palette(PALETTE_KATEGORIAL)

CMAP_HEATMAP = "coolwarm"
CMAP_DIVERGIEREND = "coolwarm"


# ══════════════════════════════════════════════════════════════
# SCHRIFT, STIL, LAYOUT  (zentral, damit überall konsistent)
# ══════════════════════════════════════════════════════════════

# Schriftgrössen für Matplotlib/Seaborn
FONTSIZE_TITEL = 14
FONTSIZE_ACHSEN = 12
FONTSIZE_TICKS = 10
FONTSIZE_KLEIN = 9          # Annotations, kleine Ticks, Heatmap-Werte
FONTWEIGHT_ACHSEN = "bold"

# Hilfslinien (hlines, vlines) in Matplotlib
HLINE_LINESTYLE = "--"
HLINE_LINEWIDTH = 1
HLINE_ALPHA = 0.7
HLINE_COLOR = AKZENTFARBE

# Plotly defaults
PLOTLY_TEMPLATE = "simple_white"
PLOTLY_FONT_FAMILY = "Arial"
PLOTLY_FONT_SIZE = 13
PLOTLY_FONT_SIZE_SUBPLOT = 12
PLOTLY_BG_TRANSPARENT = "rgba(0,0,0,0)"


_DEFAULT_CH_GEOJSON = Path(__file__).resolve().parent.parent / "data" / "raw" / "ch.json"


# ══════════════════════════════════════════════════════════════
# HILFSFUNKTIONEN
# ══════════════════════════════════════════════════════════════

def palette_farben(n):
    # sns.color_palette wiederholt die Palette automatisch, wenn n > len(palette)
    return sns.color_palette(PALETTE_KATEGORIAL, n_colors=n)


def hex_zu_rgba(hex_farbe, alpha):
    """Konvertiert eine Hex-Farbe in einen rgba-String mit gegebener Deckkraft."""
    if hex_farbe is None:
        return None
    h = hex_farbe.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f'rgba({r}, {g}, {b}, {alpha})'


def _annotate_bars(ax, fmt=".0f"):
    for p in ax.patches:
        h = p.get_height()
        if pd.notna(h) and h != 0:
            ax.annotate(f"{h:{fmt}}",
                        (p.get_x() + p.get_width() / 2, h),
                        ha="center", va="bottom",
                        fontsize=FONTSIZE_KLEIN, xytext=(0, 3),
                        textcoords="offset points")


def _transparent(fig, ax=None):
    """Setzt Figure- und Axes-Hintergrund auf transparent."""
    fig.patch.set_facecolor("none")
    if ax is None:
        return
    # ax kann eine einzelne Axes oder ein Array von Axes sein
    for a in np.atleast_1d(ax).ravel():
        a.set_facecolor("none")


def _baue_zeitwahl_buttons(zeit_spalten, n_traces_pro_label, anzahl_dummy_traces=0):
    """
    Erzeugt die Plotly-Buttons für die Zeitauswahl.
    Pro Label werden n_traces_pro_label aufeinanderfolgende Traces eingeblendet,
    optional bleiben die letzten anzahl_dummy_traces (typisch Legenden-Dummies)
    immer sichtbar.
    """
    n_box_traces = n_traces_pro_label * len(zeit_spalten)
    buttons = []
    for i, label in enumerate(zeit_spalten.keys()):
        visible = [False] * n_box_traces
        for j in range(n_traces_pro_label):
            visible[i * n_traces_pro_label + j] = True
        if anzahl_dummy_traces > 0:
            visible.extend([True] * anzahl_dummy_traces)
        buttons.append(dict(
            label=label,
            method="update",
            args=[{"visible": visible}],
        ))
    return buttons


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
    _transparent(fig, ax)
    sns.barplot(data=data, x=x, y=y, hue=hue,
                palette=palette, legend=hue is not None, order=order, ax=ax)

    if annotate:
        _annotate_bars(ax, fmt)

    if titel:
        ax.set_title(titel, fontsize=FONTSIZE_TITEL)
    ax.set_xlabel(xlabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.set_ylabel(ylabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.tick_params(axis='x', labelsize=FONTSIZE_TICKS, rotation=rotation)
    ax.tick_params(axis='y', labelsize=FONTSIZE_TICKS)
    if ylim:
        ax.set_ylim(*ylim)
    if hue:
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.tight_layout()
    return fig


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
    _transparent(fig, ax)
    sns.barplot(data=data, x=x, y=y,
                order=sortiert[x], hue=x, hue_order=sortiert[x],
                palette=palette, legend=False, ax=ax)

    if annotate:
        _annotate_bars(ax, fmt)

    if titel:
        ax.set_title(titel, fontsize=FONTSIZE_TITEL)
    ax.set_xlabel(xlabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.set_ylabel(ylabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.tick_params(axis='x', labelsize=FONTSIZE_KLEIN, rotation=rotation)
    ax.tick_params(axis='y', labelsize=FONTSIZE_KLEIN)
    if ylim:
        ax.set_ylim(*ylim)
    fig.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 3. GESTAPELTES BALKENDIAGRAMM
# ══════════════════════════════════════════════════════════════

def gestapeltes_balkendiagramm(df, xlabel="", ylabel="Anteil (%)",
                               legend_titel="", figsize=(8, 6),
                               xlabels=None, palette=PALETTE_KATEGORIAL,
                               annotate=False, fmt=".0f", min_anteil=5):
    # legend_titel-Parameter bleibt für API-Kompatibilität, wird aber nicht gerendert
    sns.set_style("whitegrid")

    ax = df.plot(
        kind="bar", stacked=True,
        color=palette, figsize=figsize,
        edgecolor="none", legend=True)
    fig = ax.figure
    _transparent(fig, ax)

    ax.legend(loc="center left",
              bbox_to_anchor=(1, 0.5), frameon=False)

    if xlabels:
        ax.set_xticklabels(xlabels)

    if annotate:
        for c in ax.containers:
            labels = [f"{v.get_height():{fmt}}%" if v.get_height() >= min_anteil else ""
                      for v in c]
            ax.bar_label(c, labels=labels, label_type="center", fontsize=FONTSIZE_KLEIN)

    ax.set_xlabel(xlabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.set_ylabel(ylabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.tick_params(axis='x', labelsize=FONTSIZE_TICKS, rotation=0)
    ax.tick_params(axis='y', labelsize=FONTSIZE_KLEIN)
    fig.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════
# 4. ANTEILSDIAGRAMM (100% Fill)
# ══════════════════════════════════════════════════════════════

def anteilsdiagramm(data, x, hue, xlabel="", ylabel="Anteil",
                    palette=None, figsize=(8, 5), xlabels=None, titel=''):
    # titel-Parameter bleibt für API-Kompatibilität, wird aber nicht gerendert
    if palette is None:
        palette = PALETTE_KATEGORIAL

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=figsize)
    _transparent(fig, ax)
    sns.histplot(
        data=data, x=x, hue=hue,
        palette=palette,
        multiple="fill", stat="percent", discrete=True, ax=ax)

    if xlabels:
        ax.set_xticklabels(xlabels)

    ax.legend()
    ax.set_xlabel(xlabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.set_ylabel(ylabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.tick_params(axis='x', labelsize=FONTSIZE_KLEIN)
    ax.tick_params(axis='y', labelsize=FONTSIZE_KLEIN)
    fig.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 5. HEATMAP
# ══════════════════════════════════════════════════════════════

def heatmap(pivot, xlabel="", ylabel="", vmax=None,
            cmap=None, figsize=(6, 7), fmt=".2f",
            xlabels=None, ylabels=None, rotation=0):
    if cmap is None:
        cmap = CMAP_HEATMAP

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=figsize)
    _transparent(fig, ax)
    sns.heatmap(
        pivot, cmap=cmap,
        vmin=0, vmax=1,
        linewidths=0.1,
        annot=True, fmt=fmt,
        annot_kws={"size": FONTSIZE_KLEIN},
        ax=ax)
    ax.xaxis.tick_top()
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha="center")
    ax.xaxis.set_label_position("top")

    if xlabels:
        ax.set_xticklabels(xlabels)
    if ylabels:
        ax.set_yticklabels(ylabels)

    ax.set_xlabel(xlabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.set_ylabel(ylabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.tick_params(axis='x', labelsize=FONTSIZE_KLEIN)
    ax.tick_params(axis='y', labelsize=FONTSIZE_KLEIN, rotation=rotation)
    fig.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 6. BOXPLOT
# ══════════════════════════════════════════════════════════════

def boxplot(data, x=None, y=None, hue=None, titel="", xlabel="", ylabel="",
            farbe=None, palette=None, figsize=(10, 5), width=0.4, rotation=0, hline=None):
    if farbe is None and palette is None:
        farbe = HAUPTFARBE

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=figsize)
    _transparent(fig, ax)
    sns.boxplot(data=data, x=x, y=y, hue=hue, color=farbe,
                palette=palette, width=width, ax=ax)

    if hline is not None:
        ax.axhline(hline, color=HLINE_COLOR, linestyle=HLINE_LINESTYLE,
                   linewidth=HLINE_LINEWIDTH, alpha=HLINE_ALPHA)

    if titel:
        ax.set_title(titel, fontsize=FONTSIZE_TITEL)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=FONTSIZE_ACHSEN)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=FONTSIZE_ACHSEN)
    ax.tick_params(axis='x', rotation=rotation)
    if hue:
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════
# 7. SCATTERPLOT
# ══════════════════════════════════════════════════════════════

def scatterplot(data, x, y, size=None, titel="", xlabel="", ylabel="",
                sizes=(20, 800), alpha=0.4, farbe=None, hue=None,
                figsize=(10, 5), rotation=0, legendentitel='', palette=None):
    # legendentitel-Parameter bleibt für API-Kompatibilität, wird aber nicht gerendert
    if farbe is None:
        farbe = HAUPTFARBE

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=figsize)
    _transparent(fig, ax)
    sns.scatterplot(
        data=data, x=x, y=y,
        size=size, sizes=sizes,
        alpha=alpha, color=farbe, hue=hue, palette=palette, ax=ax)

    ax.legend()
    if titel:
        ax.set_title(titel, fontsize=FONTSIZE_TITEL)
    ax.set_xlabel(xlabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.set_ylabel(ylabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.tick_params(axis='x', rotation=rotation)
    fig.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 8. HISTOGRAMM
# ══════════════════════════════════════════════════════════════

def histogramm(data, spalte, bins=50, titel="", xlabel="", ylabel="Anzahl",
               farbe=None, xlim=None, figsize=(10, 5), vlines=None, rotation=0):
    if farbe is None:
        farbe = HAUPTFARBE

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=figsize)
    _transparent(fig, ax)
    sns.histplot(data[spalte], bins=bins, color=farbe, ax=ax)

    if vlines:
        for val, label in vlines:
            ax.axvline(val, color=AKZENTFARBE, linestyle=HLINE_LINESTYLE, label=label)
        ax.legend()

    if titel:
        ax.set_title(titel, fontsize=FONTSIZE_TITEL)
    ax.set_xlabel(xlabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.set_ylabel(ylabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN,
                  rotation=rotation)
    if xlim:
        ax.set_xlim(*xlim)
    fig.tight_layout()
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
    _transparent(fig, ax)
    sns.countplot(data=data, x=x, color=farbe, ax=ax)

    if annotate:
        _annotate_bars(ax, fmt=".0f")

    if titel:
        ax.set_title(titel, fontsize=FONTSIZE_TITEL)
    ax.set_xlabel(xlabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.set_ylabel(ylabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.tick_params(axis='x', labelsize=FONTSIZE_KLEIN, rotation=rotation)
    ax.tick_params(axis='y', labelsize=FONTSIZE_KLEIN)
    fig.tight_layout()
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
    fig, ax = plt.subplots(figsize=figsize)
    _transparent(fig, ax)
    sns.lineplot(
        data=data, x=x, y=y, hue=hue,
        palette=palette, color=farbe,
        marker=marker, linewidth=linewidth,
        errorbar="ci" if errorbar else None,
        ax=ax)

    if hline is not None:
        ax.axhline(hline, color=HLINE_COLOR, linestyle=HLINE_LINESTYLE,
                   linewidth=HLINE_LINEWIDTH, alpha=HLINE_ALPHA)

    if titel:
        ax.set_title(titel, fontsize=FONTSIZE_TITEL)
    ax.set_xlabel(xlabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.set_ylabel(ylabel, fontsize=FONTSIZE_ACHSEN, fontweight=FONTWEIGHT_ACHSEN)
    ax.tick_params(axis='x', labelsize=FONTSIZE_TICKS, rotation=rotation)
    ax.tick_params(axis='y', labelsize=FONTSIZE_TICKS)
    # y-Bereich ist bewusst fix, da diese Funktion für Übereinstimmungswerte
    # zwischen -0.5 und 0.5 gedacht ist
    ax.set_ylim(-0.5, 0.5)
    fig.tight_layout()
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
    _transparent(fig, ax)

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

    ax.set_title(titel, fontsize=FONTSIZE_TITEL)
    ax.set_axis_off()
    fig.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 12. INTERAKTIVES LINIENDIAGRAMM MIT ZEITAUSWAHL
# ══════════════════════════════════════════════════════════════

def liniendiagramm_interaktiv_zeitwahl(
    df,
    wert_cols,
    label_map=None,
    farben_map=None,
    zeit_spalten=None,
    default_label='10 Jahre',
    titel="",
    xlabel="Jahr",
    ylabel="Wert",
    legend_titel="Akteur",
    yrange=None,
    hline=0,
    linien_opazitaet=0.8,
):
    # legend_titel-Parameter bleibt für API-Kompatibilität, wird aber nicht gerendert
    if label_map is None:
        label_map = {col: col for col in wert_cols}
    if farben_map is None:
        farben_map = {}
    if zeit_spalten is None:
        zeit_spalten = {
            '10 Jahre': 'jahrzehnt',
            '5 Jahre':  '5_jahre',
            '1 Jahr':   'jahr',
        }

    fig = go.Figure()
    n_linien = len(wert_cols)

    for label, spalte in zeit_spalten.items():
        agg = df.groupby(spalte)[wert_cols].mean().reset_index()

        for col in wert_cols:
            name = label_map.get(col, col)
            farbe = farben_map.get(name)
            fig.add_trace(go.Scatter(
                x=agg[spalte],
                y=agg[col],
                mode='lines+markers',
                name=name,
                line=dict(color=farbe, width=2),
                marker=dict(size=6),
                opacity=linien_opazitaet,
                visible=(label == default_label),
                hovertemplate=f"<b>{name}</b>: %{{y:.3f}}<extra></extra>",
            ))

    buttons = _baue_zeitwahl_buttons(zeit_spalten, n_linien)

    if hline is not None:
        fig.add_hline(
            y=hline, line_dash="dash",
            line_color=AKZENTFARBE, line_width=1, opacity=HLINE_ALPHA,
        )

    layout_args = dict(
        title=titel,
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        template=PLOTLY_TEMPLATE,
        font=dict(family=PLOTLY_FONT_FAMILY, size=PLOTLY_FONT_SIZE),
        hovermode="x unified",
        paper_bgcolor=PLOTLY_BG_TRANSPARENT,
        plot_bgcolor=PLOTLY_BG_TRANSPARENT,
        updatemenus=[dict(
            type="buttons",
            direction="right",
            x=0.5, xanchor="center",
            y=1.15, yanchor="top",
            buttons=buttons,
            showactive=True,
        )],
        margin=dict(t=100),
    )
    if yrange is not None:
        layout_args['yaxis'] = dict(range=list(yrange))

    fig.update_layout(**layout_args)

    return fig


# ══════════════════════════════════════════════════════════════
# 13. INTERAKTIVER BOXPLOT MIT ZEITAUSWAHL
# ══════════════════════════════════════════════════════════════

def boxplot_interaktiv_zeitwahl(
    df,
    wert_cols,
    hauptgruppe_spalte,
    phasen_spalte,
    label_map=None,
    farben_map=None,
    zeit_spalten=None,
    hauptgruppe_reihenfolge=None,
    default_label='Gesamte Zeitperiode',
    titel="",
    xlabel="Hauptgruppe",
    ylabel="Wert",
    legend_titel="Akteur",
    yrange=None,
    hline=0,
    fuell_alpha=0.3,
):
    fig = go.Figure()
    n_boxen = len(wert_cols)

    for label, phase in zeit_spalten.items():
        if phase is None:
            df_subset = df
        else:
            df_subset = df[df[phasen_spalte] == phase]

        for col in wert_cols:
            name = label_map.get(col, col)
            farbe = farben_map.get(name)
            fuellung = hex_zu_rgba(farbe, fuell_alpha)

            fig.add_trace(go.Box(
                y=df_subset[col],
                x=df_subset[hauptgruppe_spalte],
                name=name,
                fillcolor=fuellung,
                line=dict(color=farbe, width=1.2),
                marker=dict(
                    color=farbe,
                    size=4,
                    opacity=0.85,
                    line=dict(width=0),
                ),
                boxpoints='all',
                jitter=0.4,
                pointpos=0,
                visible=(label == default_label),
                boxmean=True,
                showlegend=False,
            ))

    # Stabile Legende über Dummy-Punkte, immer sichtbar
    for col in wert_cols:
        name = label_map.get(col, col)
        farbe = farben_map.get(name)
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=farbe),
            name=name,
            showlegend=True,
            hoverinfo='skip',
        ))

    buttons = _baue_zeitwahl_buttons(zeit_spalten, n_boxen, anzahl_dummy_traces=n_boxen)

    if hline is not None:
        fig.add_hline(
            y=hline, line_dash="dash",
            line_color=AKZENTFARBE, line_width=1, opacity=1,
        )

    yaxis_settings = {'title': ylabel}
    if yrange is not None:
        yaxis_settings['range'] = list(yrange)

    xaxis_settings = dict(title=xlabel)
    if hauptgruppe_reihenfolge is not None:
        xaxis_settings['categoryorder'] = 'array'
        xaxis_settings['categoryarray'] = hauptgruppe_reihenfolge

    fig.update_layout(
        title=titel,
        hovermode=False,
        boxmode='group',
        xaxis=xaxis_settings,
        yaxis=yaxis_settings,
        template=PLOTLY_TEMPLATE,
        font=dict(family=PLOTLY_FONT_FAMILY, size=PLOTLY_FONT_SIZE),
        paper_bgcolor=PLOTLY_BG_TRANSPARENT,
        plot_bgcolor=PLOTLY_BG_TRANSPARENT,
        updatemenus=[dict(
            type="buttons",
            direction="right",
            x=0.5, xanchor="center",
            y=1.15, yanchor="top",
            buttons=buttons,
            showactive=True,
        )],
        margin=dict(t=100),
    )

    return fig


# ══════════════════════════════════════════════════════════════
# 14. FACETIERTER INTERAKTIVER BOXPLOT MIT ZEITAUSWAHL
# ══════════════════════════════════════════════════════════════

def boxplot_facetiert_zeitwahl(
    df,
    wert_cols,
    hauptgruppe_spalte,
    phasen_spalte,
    hauptgruppe_reihenfolge=None,
    label_map=None,
    farben_map=None,
    zeit_spalten=None,
    default_label='Gesamte Zeitperiode',
    titel="",
    ylabel="Wert",
    legend_titel="Akteur",
    yrange=None,
    hline=0,
    fuell_alpha=0.4,
    n_cols=4,
    hoehe_pro_zeile=300,
):

    # Hauptgruppen-Reihenfolge fixieren, sonst sortiert Plotly alphabetisch
    if hauptgruppe_reihenfolge is None:
        hauptgruppen = df[hauptgruppe_spalte].dropna().unique().tolist()
    else:
        hauptgruppen = list(hauptgruppe_reihenfolge)

    n_gruppen = len(hauptgruppen)
    n_rows = math.ceil(n_gruppen / n_cols)
    n_akteure = len(wert_cols)
    akteur_namen = [label_map.get(c, c) for c in wert_cols]

    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=hauptgruppen,
        shared_yaxes=True,
        vertical_spacing=0.12,
        horizontal_spacing=0.04,
    )

    # Box-Traces: Reihenfolge Zeitperiode -> Hauptgruppe -> Akteur
    for label, phase in zeit_spalten.items():
        if phase is None:
            df_subset = df
        else:
            df_subset = df[df[phasen_spalte] == phase]

        for hg_idx, hg in enumerate(hauptgruppen):
            row = hg_idx // n_cols + 1
            col = hg_idx % n_cols + 1
            df_hg = df_subset[df_subset[hauptgruppe_spalte] == hg]

            for akteur_col in wert_cols:
                name = label_map.get(akteur_col, akteur_col)
                farbe = farben_map.get(name)
                fuellung = hex_zu_rgba(farbe, fuell_alpha)

                fig.add_trace(
                    go.Box(
                        y=df_hg[akteur_col],
                        x=[name] * len(df_hg),
                        name=name,
                        fillcolor=fuellung,
                        line=dict(color=farbe, width=1.2),
                        marker=dict(
                            color=farbe, size=3, opacity=0.75,
                            line=dict(width=0),
                        ),
                        boxpoints='all',
                        jitter=0.4,
                        pointpos=0,
                        visible=(label == default_label),
                        boxmean=True,
                        showlegend=False,
                    ),
                    row=row, col=col,
                )

    # Stabile Legende über Dummy-Punkte, immer sichtbar
    for akteur_col in wert_cols:
        name = label_map.get(akteur_col, akteur_col)
        farbe = farben_map.get(name)
        fig.add_trace(
            go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=10, color=farbe),
                name=name,
                showlegend=True,
                hoverinfo='skip',
            ),
            row=1, col=1,
        )

    buttons = _baue_zeitwahl_buttons(
        zeit_spalten,
        n_traces_pro_label=n_gruppen * n_akteure,
        anzahl_dummy_traces=n_akteure,
    )

    if hline is not None:
        for hg_idx in range(n_gruppen):
            row = hg_idx // n_cols + 1
            col = hg_idx % n_cols + 1
            fig.add_hline(
                y=hline, line_dash="dash",
                line_color=AKZENTFARBE, line_width=1, opacity=0.6,
                row=row, col=col,
            )

    fig.update_layout(
        title=titel,
        hovermode=False,
        template=PLOTLY_TEMPLATE,
        font=dict(family=PLOTLY_FONT_FAMILY, size=PLOTLY_FONT_SIZE_SUBPLOT),
        paper_bgcolor=PLOTLY_BG_TRANSPARENT,
        plot_bgcolor=PLOTLY_BG_TRANSPARENT,
        height=hoehe_pro_zeile * n_rows + 120,
        showlegend=False,
        updatemenus=[dict(
            type="buttons",
            direction="right",
            x=0.5, xanchor="center",
            y=1.08, yanchor="bottom",
            buttons=buttons,
            showactive=True,
        )],
        margin=dict(t=140),
    )

    fig.update_xaxes(
        categoryorder='array',
        categoryarray=akteur_namen,
        title_text="",
    )

    if yrange is not None:
        fig.update_yaxes(range=list(yrange))
    for r in range(1, n_rows + 1):
        fig.update_yaxes(title_text=ylabel, row=r, col=1)

    fig.update_xaxes(tickangle=0, automargin=False)

    return fig