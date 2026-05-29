# Alle Plotfunktionen für die Analyse – im Notebook einfach importieren:
# from visualisierungen import *
# from visualisierungen import heatmap
"""
Verwendung im Notebook:
from visualisierungen import *
from visualisierungen import heatmap
from visualisierungen import heatmap_interaktiv_phasen
from visualisierungen import heatmap as heat
"""

import math
from pathlib import Path
from tkinter.constants import N

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
PLOTLY_HEATMAP_CELL_FONT = 9
PLOTLY_BG_TRANSPARENT = "rgba(0,0,0,0)"
PLOTLY_DROPDOWN_BG = "#ffffff"
PLOTLY_DROPDOWN_BORDER = "#cccccc"
PLOTLY_PLOT_BG = "#ffffff"
PLOTLY_GRID_COLOR = "#d4d4d4"


_DEFAULT_CH_GEOJSON = Path(__file__).resolve().parent.parent / "data" / "raw" / "ch.json"


# ══════════════════════════════════════════════════════════════
# HILFSFUNKTIONEN
# ══════════════════════════════════════════════════════════════

def palette_farben(n):
    # sns.color_palette wiederholt die Palette automatisch, wenn n > len(palette)
    return sns.color_palette(PALETTE_KATEGORIAL, n_colors=n)


def hex_zu_rgba(hex_farbe, alpha):
    # Für Plotly-Füllfarben mit Transparenz
    if hex_farbe is None:
        return None
    h = hex_farbe.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f'rgba({r}, {g}, {b}, {alpha})'


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


PLOTLY_EMBED_CSS = """<style>
html, body { margin: 0; padding: 0; width: 100%; }
.js-plotly-plot,
.plot-container,
.svg-container,
.plotly-graph-div {
  width: 100% !important;
  max-width: 100% !important;
  margin: 0 !important;
}
</style>"""

PLOTLY_PHASE_BAR_HEIGHT_PX = 44


PLOTLY_PHASE_BAR_CSS = """<style>
.phase-heatmap-embed {
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.phase-btn-bar {
  display: flex;
  gap: 8px;
  width: 100%;
  flex: 0 0 auto;
  margin: 0 0 2px;
  box-sizing: border-box;
}
.phase-btn-bar button {
  flex: 1 1 0;
  min-width: 0;
  margin: 0;
  padding: 4px 2px;
  border: 1px solid #cccccc;
  border-radius: 4px;
  background: #ffffff;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 10px;
  line-height: 1.25;
  cursor: pointer;
  color: #333333;
  text-align: center;
  white-space: pre-line;
  box-sizing: border-box;
}
.phase-btn-bar button.active {
  background: #e8e8e8;
  font-weight: 600;
}
.phase-btn-bar button:hover:not(.active) {
  background: #f5f5f5;
}
.phase-heatmap-embed .updatemenu-container,
.phase-heatmap-embed .updatemenu-header-group {
  display: none !important;
}
</style>"""

PLOTLY_PHASE_BAR_JS = """<script>
(function () {
  var BAR_SEL = ".phase-heatmap-embed .phase-btn-bar button";
  var PLOT_SEL = ".phase-heatmap-embed .plotly-graph-div";
  function wirePhaseBar() {
    var plotDiv = document.querySelector(PLOT_SEL);
    if (!plotDiv || !plotDiv.data) return false;
    var n = plotDiv.data.length;
    document.querySelectorAll(BAR_SEL).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var i = parseInt(btn.getAttribute("data-phase"), 10);
        var vis = [];
        var showscale = [];
        for (var j = 0; j < n; j++) {
          vis.push(j === i);
          showscale.push(j === i);
        }
        Plotly.restyle(plotDiv, { visible: vis, showscale: showscale });
        document.querySelectorAll(BAR_SEL).forEach(function (b) {
          b.classList.toggle("active", b === btn);
        });
      });
    });
    return true;
  }
  if (!wirePhaseBar()) {
    var tries = 0;
    var t = setInterval(function () {
      if (wirePhaseBar() || ++tries > 60) clearInterval(t);
    }, 50);
  }
})();
</script>"""


def _equalize_phase_button_labels(labels):
    """Zeilenbreite angleichen (Monospace in Plotly-Buttons → gleiche Buttonbreite)."""
    rows = [str(label).split("\n") for label in labels]
    n_lines = max(len(r) for r in rows)
    for r in rows:
        while len(r) < n_lines:
            r.append("")
    widths = [max(len(r[i]) for r in rows) for i in range(n_lines)]
    return [
        "\n".join(r[i].center(widths[i]) for i in range(n_lines))
        for r in rows
    ]


def _phase_bar_buttons_html(labels):
    import html as html_module

    parts = []
    for i, label in enumerate(labels):
        text = html_module.escape(label).replace("\n", "<br>")
        active = " active" if i == 0 else ""
        parts.append(
            f'<button type="button" class="phase-btn{active}" data-phase="{i}">{text}</button>'
        )
    return "".join(parts)


PLOTLY_HEATMAP_X_DOMAIN_END = 0.97
PLOTLY_GEOMAP_X_DOMAIN_END = 0.97


def _sync_geomap_colorbar(fig, x_domain_end=PLOTLY_GEOMAP_X_DOMAIN_END):
    for trace in fig.data:
        cb = trace.colorbar
        if cb is None:
            continue
        cb.len = 0.92
        cb.lenmode = "fraction"
        cb.y = 0.5
        cb.yref = "paper"
        cb.yanchor = "middle"
        cb.x = min(x_domain_end + 0.018, 0.995)
        cb.xanchor = "left"
        cb.xpad = 0
        cb.thickness = 8


def _expand_geomap_for_html_export(fig, x_domain_end=PLOTLY_GEOMAP_X_DOMAIN_END):
    """Karte auf volle Breite (wie Heatmap), Colorbar daneben."""
    fig.update_layout(
        geo=dict(
            domain=dict(x=[0, x_domain_end], y=[0, 1]),
            fitbounds="geojson",
            bgcolor=PLOTLY_BG_TRANSPARENT,
            showland=False,
            showcountries=False,
            showcoastlines=False,
            showocean=False,
            showlakes=False,
        ),
        margin=dict(t=4, b=4, l=0, r=4, pad=0),
    )
    _sync_geomap_colorbar(fig, x_domain_end)


def _sync_heatmap_colorbar(fig, plot_top, x_domain_end=PLOTLY_HEATMAP_X_DOMAIN_END):
    """Colorbar-Höhe und -Position an Heatmap-Domain koppeln."""
    for trace in fig.data:
        cb = trace.colorbar
        if cb is None:
            continue
        cb.len = plot_top
        cb.y = plot_top / 2
        cb.yref = "paper"
        cb.x = min(x_domain_end + 0.018, 0.995)
        cb.xanchor = "left"
        cb.xpad = 0
        cb.thickness = 8


def _expand_phase_plot_for_html_export(fig, plot_top=1.0, x_domain_end=PLOTLY_HEATMAP_X_DOMAIN_END):
    """HTML-Buttons liegen außerhalb → Heatmap darf volle Plot-Höhe nutzen."""
    m = fig.layout.margin
    fig.update_layout(
        yaxis=dict(domain=[0, plot_top]),
        xaxis=dict(domain=[0, x_domain_end]),
        margin=dict(
            t=28,
            b=32,
            l=int(m.l) if m.l is not None else 0,
            r=4,
            pad=0,
        ),
    )
    _sync_heatmap_colorbar(fig, plot_top, x_domain_end)


def _phase_bar_height_css(total_height, plot_height):
    return f"""<style>
html, body {{
  margin: 0;
  padding: 0;
  width: 100%;
  height: {total_height}px;
  overflow: hidden;
}}
.phase-heatmap-embed {{
  height: {total_height}px;
}}
.phase-heatmap-embed .plotly-graph-div {{
  height: {plot_height}px !important;
  flex: 0 0 {plot_height}px;
  overflow: hidden;
}}
</style>"""


def write_plotly_html_responsive(
    fig,
    path,
    height=None,
    include_plotlyjs="inline",
    full_html=True,
    phase_bar_labels=None,
    phase_bar_layout="heatmap",
):
    """Plotly-HTML für iframe mit width=100% (füllt die Content-Spalte).

    phase_bar_labels: Phasen-Labels → HTML-Zeile mit gleicher Buttonbreite und Abstand.
    height: Bei phase_bar_labels Gesamthöhe inkl. Buttonzeile (px), sonst Plot-Höhe.
    phase_bar_layout: "heatmap" passt Domain/Margin für Heatmaps an, "generic" für Karten.
    """
    import copy
    import re
    from pathlib import Path

    export_fig = fig
    total_height = height
    plot_height = height
    if phase_bar_labels:
        export_fig = copy.deepcopy(fig)
        export_fig.layout.updatemenus = ()
        if phase_bar_layout == "heatmap":
            _expand_phase_plot_for_html_export(export_fig)
        elif phase_bar_layout == "generic":
            _expand_geomap_for_html_export(export_fig)
        total_height = height if height is not None else 400
        plot_height = total_height - PLOTLY_PHASE_BAR_HEIGHT_PX

    m = export_fig.layout.margin
    if phase_bar_labels:
        top = int(m.t) if m.t is not None else (28 if phase_bar_layout == "heatmap" else 8)
    else:
        top = max(88, int(m.t)) if m.t is not None else 88
    layout = {
        "autosize": True,
        "width": None,
        "margin": dict(
            l=int(m.l) if m.l is not None else 0,
            r=int(m.r) if m.r is not None else 0,
            t=top,
            b=int(m.b) if m.b is not None else (32 if phase_bar_labels and phase_bar_layout == "heatmap" else 8),
            pad=0,
        ),
    }
    if plot_height is not None:
        layout["height"] = plot_height
    export_fig.update_layout(**layout)

    config = {"responsive": True, "displayModeBar": False}
    html = export_fig.to_html(
        include_plotlyjs=include_plotlyjs,
        full_html=full_html,
        config=config,
    )
    head_css = PLOTLY_EMBED_CSS
    if phase_bar_labels:
        head_css += PLOTLY_PHASE_BAR_CSS
        head_css += _phase_bar_height_css(total_height, plot_height)
    html = html.replace("</head>", head_css + "</head>", 1)

    if phase_bar_labels:
        bar_html = _phase_bar_buttons_html(phase_bar_labels)
        html = re.sub(
            r'(<div id="[^"]+" class="plotly-graph-div")',
            r'<div class="phase-heatmap-embed"><div class="phase-btn-bar">'
            + bar_html
            + r"</div>\1",
            html,
            count=1,
        )
        html = html.replace("</body>", PLOTLY_PHASE_BAR_JS + "</body>", 1)

    if phase_bar_labels:
        plot_style = f'class="plotly-graph-div" style="width:100%;height:{plot_height}px;"'
    else:
        plot_style = 'class="plotly-graph-div" style="width:100%;height:100%;"'
    html = re.sub(
        r'class="plotly-graph-div" style="[^"]*"',
        plot_style,
        html,
        count=1,
    )
    Path(path).write_text(html, encoding="utf-8")


def _transparent(fig, ax=None):
    # Hintergrund transparent – sonst sieht es im Blog komisch aus
    fig.patch.set_facecolor("none")
    if ax is None:
        return
    # Klappt auch wenn ax eine einzelne Axes ist
    for a in np.atleast_1d(ax).ravel():
        a.set_facecolor("none")


def _baue_zeitwahl_buttons(zeit_spalten, n_traces_pro_label, anzahl_dummy_traces=0):
    # Erstellt die Zeitwahl-Buttons – Dummy-Traces am Ende bleiben immer sichtbar
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
# 5. HEATMAP
# ══════════════════════════════════════════════════════════════

def heatmap(pivot, xlabel="", ylabel="", vmax=0.5, vmin=-0.5,
            cmap=None, figsize=(6, 7), fmt=".2f",
            xlabels=None, ylabels=None, rotation=0):
    if cmap is None:
        cmap = CMAP_HEATMAP

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=figsize)
    _transparent(fig, ax)
    sns.heatmap(
        pivot, cmap=cmap,
        vmin=vmin, vmax=vmax,
        linewidths=0.1,
        annot=True, fmt=fmt,
        annot_kws={"size": FONTSIZE_KLEIN},
        ax=ax)
    # Beschriftung oben, wie in einer Kreuztabelle
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
# 5b. INTERAKTIVE HEATMAP MIT PHASEN-/ZEITSLOT-AUSWAHL
# ══════════════════════════════════════════════════════════════

def heatmap_interaktiv_phasen(
    phasen,
    vmin=-0.5,
    vmax=0.5,
    titel="",
    xlabel=None,
    ylabel=None,
    xlabels=None,
    ylabels=None,
    text_fmt=".2f",
    colorscale=None,
    width=None,
    height=360,
    default_index=0,
):
    """
    Plotly-Heatmap mit Phasen-Buttons (einzeilig nebeneinander, Label mit \\n zweizeilig).

    phasen: Liste von (Button-Label, Pivot-DataFrame), z. B. aus df_phase pro phase.
    Der Pivot sollte Zeilen = Akteure, Spalten = Kantone, Werte bereits in Plot-Skala sein.
    """
    if not phasen:
        raise ValueError("phasen ist leer")

    if colorscale is None:
        colorscale = "RdBu"

    fig = go.Figure()
    default_index = min(default_index, len(phasen) - 1)

    # Reservierter Streifen für Plotly-Phasen-Buttons (Notebook); Blog nutzt HTML-Leiste.
    button_strip = 0.16
    plot_top = 1.0 - button_strip

    colorbar = dict(
        thickness=8,
        len=plot_top,
        lenmode="fraction",
        y=plot_top / 2,
        yanchor="middle",
        yref="paper",
        x=min(PLOTLY_HEATMAP_X_DOMAIN_END + 0.018, 0.995),
        xanchor="left",
        xpad=0,
        outlinewidth=0,
        tickfont=dict(size=PLOTLY_FONT_SIZE - 2),
    )

    for i, (label, pivot) in enumerate(phasen):
        x = list(xlabels) if xlabels is not None else [str(c) for c in pivot.columns]
        y = list(ylabels) if ylabels is not None else [str(r) for r in pivot.index]
        z = pivot.values.astype(float)
        text = np.where(
            np.isnan(z),
            "",
            np.char.mod(f"%{text_fmt}", z),
        )

        fig.add_trace(
            go.Heatmap(
                z=z,
                x=x,
                y=y,
                zmin=vmin,
                zmax=vmax,
                zmid=0 if vmin < 0 < vmax else None,
                colorscale=colorscale,
                text=text,
                texttemplate="%{text}",
                textfont=dict(size=PLOTLY_HEATMAP_CELL_FONT),
                hoverinfo="skip",
                colorbar=colorbar,
                showscale=True,
                visible=(i == default_index),
                xgap=1,
                ygap=1,
            )
        )

    n_traces = len(phasen)
    raw_labels = [label for label, _ in phasen]
    eq_labels = _equalize_phase_button_labels(raw_labels)
    btn_font = dict(
        family="Courier New, Courier, monospace",
        size=9,
        color="#333333",
    )
    phase_buttons = []
    for i, (_, _) in enumerate(phasen):
        visible = [j == i for j in range(n_traces)]
        phase_buttons.append(
            dict(
                label=eq_labels[i],
                method="update",
                args=[{"visible": visible}],
            )
        )

    grid_axis = dict(
        showgrid=True,
        gridcolor=PLOTLY_GRID_COLOR,
        gridwidth=1,
        zeroline=False,
    )
    # button_strip / plot_top: siehe oben (Colorbar-Ausrichtung)
    layout_kwargs = dict(
        xaxis=dict(
            title=xlabel,
            side="top",
            tickangle=-90,
            type="category",
            automargin=True,
            domain=[0, PLOTLY_HEATMAP_X_DOMAIN_END],
            **grid_axis,
        ),
        yaxis=dict(
            title=ylabel,
            autorange="reversed",
            type="category",
            automargin=True,
            domain=[0, plot_top],
            **grid_axis,
        ),
        template=PLOTLY_TEMPLATE,
        font=dict(family=PLOTLY_FONT_FAMILY, size=PLOTLY_FONT_SIZE),
        paper_bgcolor=PLOTLY_BG_TRANSPARENT,
        plot_bgcolor=PLOTLY_PLOT_BG,
        hovermode=False,
        autosize=True,
        margin=dict(t=16, b=40, l=0, r=0, pad=0),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=default_index,
                x=0.5,
                xanchor="center",
                y=0.99,
                yanchor="top",
                buttons=phase_buttons,
                showactive=True,
                bgcolor=PLOTLY_DROPDOWN_BG,
                bordercolor=PLOTLY_DROPDOWN_BORDER,
                borderwidth=1,
                font=btn_font,
            )
        ],
    )
    if width is not None:
        layout_kwargs["width"] = width
    if height is not None:
        layout_kwargs["height"] = height
    if titel:
        layout_kwargs["title"] = titel
    fig.update_layout(**layout_kwargs)

    return fig


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


def _load_ch_geojson_dict(geojson_pfad=None):
    import json

    path = Path(geojson_pfad) if geojson_pfad is not None else _DEFAULT_CH_GEOJSON
    if not path.is_file():
        raise FileNotFoundError(f"GeoJSON nicht gefunden: {path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def phase_kantons_row_to_map_df(row, wert_spalte="kongruenz", id_col="id"):
    """
    Eine Zeile aus df_heatmap_by_phase (Kantons-Spalten …-japroz) → DataFrame id + Wert.
    Skala wie Heatmap: (ja_proz − 50) in pp → −0.5 … +0.5.
    """
    canton_cols = [c for c in row.index if str(c).endswith("-japroz")]
    values = pd.to_numeric(row[canton_cols], errors="coerce").astype(float)
    if values.abs().max() > 1:
        values = values / 100
    values = values.clip(-0.5, 0.5)
    return pd.DataFrame(
        {
            id_col: ["CH" + str(c).split("-")[0].upper() for c in canton_cols],
            wert_spalte: values.values,
        }
    )


def schweiz_karte_interaktiv_phasen(
    phasen,
    wert_spalte="kongruenz",
    join_col="id",
    vmin=-0.5,
    vmax=0.5,
    titel="",
    colorscale=None,
    geojson_pfad=None,
    featureidkey="properties.id",
    width=None,
    height=360,
    default_index=0,
):
    """
    Plotly-Choropleth Schweiz mit Phasen-Umschaltung (wie heatmap_interaktiv_phasen).

    phasen: Liste (Button-Label, DataFrame mit join_col + wert_spalte), z. B. aus phase_kantons_row_to_map_df.
    """
    if not phasen:
        raise ValueError("phasen ist leer")

    if colorscale is None:
        colorscale = "RdBu"

    geojson = _load_ch_geojson_dict(geojson_pfad)
    fig = go.Figure()
    default_index = min(default_index, len(phasen) - 1)

    colorbar = dict(
        thickness=8,
        len=0.92,
        lenmode="fraction",
        y=0.5,
        yanchor="middle",
        yref="paper",
        x=min(PLOTLY_GEOMAP_X_DOMAIN_END + 0.018, 0.995),
        xanchor="left",
        xpad=0,
        outlinewidth=0,
        tickfont=dict(size=PLOTLY_FONT_SIZE - 2),
    )

    for i, (_, df_map) in enumerate(phasen):
        if join_col not in df_map.columns or wert_spalte not in df_map.columns:
            raise ValueError(f"DataFrame braucht Spalten {join_col!r} und {wert_spalte!r}")
        fig.add_trace(
            go.Choropleth(
                geojson=geojson,
                locations=df_map[join_col],
                z=df_map[wert_spalte],
                featureidkey=featureidkey,
                zmin=vmin,
                zmax=vmax,
                zmid=0 if vmin < 0 < vmax else None,
                colorscale=colorscale,
                marker_line_width=0.4,
                marker_line_color="#333333",
                colorbar=colorbar,
                showscale=(i == default_index),
                visible=(i == default_index),
                hovertemplate="%{location}<br>Kongruenz: %{z:.2f}<extra></extra>",
            )
        )

    n_traces = len(phasen)
    raw_labels = [label for label, _ in phasen]
    eq_labels = _equalize_phase_button_labels(raw_labels)
    btn_font = dict(
        family="Courier New, Courier, monospace",
        size=9,
        color="#333333",
    )
    phase_buttons = []
    for i, (_, _) in enumerate(phasen):
        visible = [j == i for j in range(n_traces)]
        showscale = [j == i for j in range(n_traces)]
        phase_buttons.append(
            dict(
                label=eq_labels[i],
                method="update",
                args=[
                    {"visible": visible, "showscale": showscale},
                ],
            )
        )

    layout_kwargs = dict(
        template=PLOTLY_TEMPLATE,
        font=dict(family=PLOTLY_FONT_FAMILY, size=PLOTLY_FONT_SIZE),
        paper_bgcolor=PLOTLY_BG_TRANSPARENT,
        plot_bgcolor=PLOTLY_BG_TRANSPARENT,
        hovermode=False,
        autosize=True,
        margin=dict(t=16, b=4, l=0, r=4, pad=0),
        geo=dict(
            domain=dict(x=[0, PLOTLY_GEOMAP_X_DOMAIN_END], y=[0, 1]),
            bgcolor=PLOTLY_BG_TRANSPARENT,
            lakecolor=PLOTLY_BG_TRANSPARENT,
            showcountries=False,
            showcoastlines=False,
            showland=False,
            showocean=False,
            showlakes=False,
            fitbounds="geojson",
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=default_index,
                x=0.5,
                xanchor="center",
                y=1.08,
                yanchor="bottom",
                buttons=phase_buttons,
                showactive=True,
                bgcolor=PLOTLY_DROPDOWN_BG,
                bordercolor=PLOTLY_DROPDOWN_BORDER,
                borderwidth=1,
                font=btn_font,
            )
        ],
    )
    if width is not None:
        layout_kwargs["width"] = width
    if height is not None:
        layout_kwargs["height"] = height
    if titel:
        layout_kwargs["title"] = titel
    fig.update_layout(**layout_kwargs)
    return fig


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

    # Dummy-Punkte für stabile Legende, echte Traces haben showlegend=False
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