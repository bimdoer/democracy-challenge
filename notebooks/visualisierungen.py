"""
Verwendung im Notebook:
    %load_ext autoreload
    %autoreload 2
    from visualisierungen import *
"""

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
PALETTE_SNS = sns.color_palette(PALETTE_KATEGORIAL)
 
CMAP_HEATMAP = "mako"
CMAP_DIVERGIEREND = "coolwarm"
 
 
def palette_farben(n):
    """Gibt n Farben aus der kategorialen Palette zurück."""
    if n <= len(PALETTE_KATEGORIAL):
        return sns.color_palette(PALETTE_KATEGORIAL[:n])
    return sns.color_palette(PALETTE_KATEGORIAL, n_colors=n)
 
 
# ══════════════════════════════════════════════════════════════
# 1. BALKENDIAGRAMM
# ══════════════════════════════════════════════════════════════
 
def balkendiagramm(data, x, y, xlabel="", ylabel="", titel="",
                   ylim=None, palette=None,
                   height=6, aspect=2, rotation=0, order=None):
    if palette is None:
        palette = PALETTE_KATEGORIAL
 
    sns.set_style("whitegrid")
    sns.catplot(
        data=data, x=x, y=y,
        kind="bar", hue=x,
        palette=palette, legend=False,
        height=height, aspect=aspect, order=order)
 
    plt.title(titel, fontsize=14) if titel else None
    plt.xlabel(xlabel, fontsize=12, fontweight="bold")
    plt.ylabel(ylabel, fontsize=12, fontweight="bold")
    plt.xticks(fontsize=10, rotation=rotation)
    plt.yticks(fontsize=10)
    if ylim:
        plt.ylim(*ylim)
    plt.tight_layout()
    plt.show()
 
 
# ══════════════════════════════════════════════════════════════
# 2. BALKENDIAGRAMM SORTIERT
# ══════════════════════════════════════════════════════════════
 
def balkendiagramm_sortiert(data, x, y, xlabel="", ylabel="", titel="",
                            ylim=None, palette=None,
                            height=6, aspect=2, rotation=90):
    if palette is None:
        palette = PALETTE_KATEGORIAL
 
    sortiert = data.sort_values(y, ascending=False)
    sns.set_style("whitegrid")
    sns.catplot(
        data=data, x=x, y=y,
        order=sortiert[x], hue_order=sortiert[x],
        kind="bar", hue=x,
        palette=palette, legend=False,
        height=height, aspect=aspect)
 
    plt.title(titel, fontsize=14) if titel else None
    plt.xlabel(xlabel, fontsize=12, fontweight="bold")
    plt.ylabel(ylabel, fontsize=12, fontweight="bold")
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
                               xlabels=None):
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
                    palette=None, figsize=(8, 5), xlabels=None):
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
            xlabels=None, ylabels=None):
    if cmap is None:
        cmap = CMAP_HEATMAP
 
    sns.set_style("whitegrid")
    plt.figure(figsize=figsize)
    ax = sns.heatmap(
        pivot, cmap=cmap,
        vmin=0, vmax=vmax,
        linewidths=0.1,
        annot=True, fmt=fmt,
        annot_kws={"size": 9})
 
    if xlabels:
        ax.set_xticklabels(xlabels)
    if ylabels:
        ax.set_yticklabels(ylabels)
 
    plt.xlabel(xlabel, fontsize=12, fontweight="bold")
    plt.ylabel(ylabel, fontsize=12, fontweight="bold")
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10, rotation=0)
    plt.tight_layout()
    plt.show()
 
 
# ══════════════════════════════════════════════════════════════
# 6. BOXPLOT
# ══════════════════════════════════════════════════════════════
 
def boxplot(data, x=None, y=None, titel="", xlabel="", ylabel="",
            farbe=None, figsize=(10, 5)):
    if farbe is None:
        farbe = HAUPTFARBE
 
    sns.set_style("whitegrid")
    plt.figure(figsize=figsize)
    sns.boxplot(data=data, x=x, y=y, color=farbe, width=0.4)
 
    plt.title(titel, fontsize=14) if titel else None
    plt.xlabel(xlabel, fontsize=12) if xlabel else None
    plt.ylabel(ylabel, fontsize=12) if ylabel else None
    plt.tight_layout()
    plt.show()
 
 
# ══════════════════════════════════════════════════════════════
# 7. SCATTERPLOT
# ══════════════════════════════════════════════════════════════
 
def scatterplot(data, x, y, size=None, titel="", xlabel="", ylabel="",
                sizes=(20, 800), alpha=0.4, farbe=None):
    if farbe is None:
        farbe = HAUPTFARBE
 
    sns.set_style("whitegrid")
    sns.scatterplot(
        data=data, x=x, y=y,
        size=size, sizes=sizes,
        alpha=alpha, color=farbe)
 
    plt.title(titel, fontsize=14) if titel else None
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.tight_layout()
    plt.show()
 
 
# ══════════════════════════════════════════════════════════════
# 8. HISTOGRAMM
# ══════════════════════════════════════════════════════════════
 
def histogramm(data, spalte, bins=50, titel="", xlabel="", ylabel="Anzahl",
               farbe=None, xlim=None, figsize=(10, 5), vlines=None):
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
    plt.ylabel(ylabel, fontsize=12, fontweight="bold")
    if xlim:
        plt.xlim(*xlim)
    plt.tight_layout()
    plt.show()
 
 
# ══════════════════════════════════════════════════════════════
# 9. COUNTPLOT
# ══════════════════════════════════════════════════════════════
 
def countplot(data, x, titel="", xlabel="", ylabel="Anzahl Nennungen",
              farbe=None, rotation=0):
    if farbe is None:
        farbe = HAUPTFARBE
 
    sns.set_style("whitegrid")
    sns.countplot(data=data, x=x, color=farbe)
 
    plt.title(titel, fontsize=14) if titel else None
    plt.xlabel(xlabel, fontsize=12, fontweight="bold")
    plt.ylabel(ylabel, fontsize=12, fontweight="bold")
    plt.xticks(fontsize=10, rotation=rotation)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.show()