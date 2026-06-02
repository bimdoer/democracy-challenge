# Archivierte Plotfunktionen – derzeit nicht in Notebooks verwendet.
# Alle Konstanten und geteilten Hilfsfunktionen werden aus visualisierungen.py importiert.
from visualisierungen import (
    PALETTE_KATEGORIAL,
    HAUPTFARBE, AKZENTFARBE, CMAP_HEATMAP,
    FONTSIZE_TITEL, FONTSIZE_ACHSEN, FONTSIZE_TICKS, FONTSIZE_KLEIN, FONTWEIGHT_ACHSEN,
    HLINE_LINESTYLE, HLINE_LINEWIDTH, HLINE_ALPHA, HLINE_COLOR,
    PLOTLY_TEMPLATE, PLOTLY_FONT_FAMILY, PLOTLY_FONT_SIZE, PLOTLY_FONT_SIZE_SUBPLOT,
    PLOTLY_BG_TRANSPARENT, PLOTLY_PAPER_BG, PLOTLY_PLOT_BG, PLOTLY_GRID_COLOR,
    _DEFAULT_CH_GEOJSON,
    _transparent, hex_zu_rgba, _baue_zeitwahl_buttons,
)

import math
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _annotate_bars(ax, fmt=".0f"):
    # Wert über jeden Balken schreiben
    for p in ax.patches:
        h = p.get_height()
        if pd.notna(h) and h != 0:
            ax.annotate(f"{h:{fmt}}",
                        (p.get_x() + p.get_width() / 2, h),
                        ha="center", va="bottom",
                        fontsize=FONTSIZE_KLEIN, xytext=(0, 3),
                        textcoords="offset points")


# ══════════════════════════════════════════════════════════════
# HILFSFUNKTIONEN
# ══════════════════════════════════════════════════════════════

def palette_farben(n):
    # sns.color_palette wiederholt die Palette automatisch, wenn n > len(palette)
    return sns.color_palette(PALETTE_KATEGORIAL, n_colors=n)


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
    # hue=x damit jeder Balken eine eigene Farbe bekommt
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
    # Legend_titel wird nicht gerendert

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
        # Nur beschriften wenn Segment gross genug – sonst wird es unlesbar
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
    # Titel wird nicht gerendert
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
# 7. SCATTERPLOT
# ══════════════════════════════════════════════════════════════

def scatterplot(data, x, y, size=None, titel="", xlabel="", ylabel="",
                sizes=(20, 800), alpha=0.4, farbe=None, hue=None,
                figsize=(10, 5), rotation=0, legendentitel='', palette=None):
    # Legendentitel wird nicht gerendert
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
        # Vertikale Referenzlinien, z.B. Mittelwert oder Schwellenwert
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
    # Y-Achse fix auf -0.5 bis 0.5, nur für Kongruenzwerte
    ax.set_ylim(-0.5, 0.5)
    fig.tight_layout()
    plt.show()


# ══════════════════════════════════════════════════════════════
# 11. MAP SCHWEIZERKARTE (statisch)
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

    # Kantone aus GeoJSON mit Datensatz verknüpfen – left join damit alle Kantone sichtbar bleiben
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
    # Legend_titel wird nicht gerendert
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
        paper_bgcolor=PLOTLY_PAPER_BG,
        plot_bgcolor=PLOTLY_PAPER_BG,
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

    # Ohne fixe Reihenfolge sortiert Plotly alphabetisch
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

    # Traces in Reihenfolge: Zeitperiode → Hauptgruppe → Akteur
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

    # Gleicher Dummy-Trick wie oben
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
        paper_bgcolor=PLOTLY_PAPER_BG,
        plot_bgcolor=PLOTLY_PAPER_BG,
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
