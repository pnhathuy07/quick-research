import seaborn as sns
import matplotlib.pyplot as plt

from functions import validate, max_len
from configurations import skip_string

folder = None
title_font_size = 12


def main(f):
    sns.set_style("ticks", {"font.family": "Segoe UI"})
    sns.set_palette("tab10")
    sns.set_context("paper")

    global folder
    folder = f + "\\plots"


def save_figure(plot_type, x, groups="__All"):
    if groups == "__All":
        groups = "Tất cả"
    path = "{}\\{} - {} ({}).jpg".format(folder, plot_type, max_len(validate(x), 80), max_len(validate(groups), 50))
    plt.savefig(path, dpi=200)
    plt.clf()
    return path


# ---------------------------------------- Plotting data ---------------------------------------- #
def kde(df, x, groups="__All"):
    if groups is not None:
        if groups == "__All":
            sns.histplot(df.loc[:, x], color="#217346", kde=True, bins=10, legend=None)
        else:
            for g in df[groups].unique():
                sns.kdeplot(df.loc[df[groups] == g, x], shade=True, linewidth=1, alpha=.5, bw_adjust=.8, thresh=0)

            plt.legend(labels=df[groups].unique(), edgecolor="#000000", fancybox=False)

        plt.title(x, fontdict={"fontsize": title_font_size})

        return save_figure("KDE", x, groups)


def bar(df, name):
    if "Tất cả" not in df.index:
        df.plot(kind="barh", stacked=True)
        plt.legend(edgecolor="#000000", fancybox=False)
    else:
        df.plot(kind="barh", legend=None)

    plt.title(name, fontdict={"fontsize": title_font_size})

    plt.ylabel(None)
    plt.xlabel("Count")

    plt.tight_layout()
    return save_figure("BAR", name)


def pie(df, x, y, name):
    patches, _, auto_pcts = plt.pie(df.loc[df[y] != 0, y],
                                    autopct=lambda p: "{:.0f}%".format(round(p)) if p >= 6 else None,
                                    pctdistance=0.85, startangle=90, counterclock=False,
                                    explode=(df.loc[:, y] == df.loc[:, y].max()).apply(float) / 20, normalize=True,
                                    colors=["#dc3e32", "#f75b57", "#fc9803", "#f7bd46", "#33a752", "#61d667",
                                            "#548dd4", "#66b3ff", "#7a4add", "#bc74ed", "#000000"])
    
    labels = df.loc[df[y] != 0, x]

    plt.legend(patches, labels, edgecolor="#000000", fancybox=False, loc="center left", borderaxespad=0)
    plt.subplots_adjust(right=2.5)

    plt.setp(auto_pcts, **{"color": "white", "weight": "bold", "fontsize": 12, "fontname": "DejaVu Sans"})

    # Draw circle
    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    plt.axis("equal")
    plt.title(name, fontdict={"fontsize": title_font_size})

    plt.tight_layout(rect=[0.0, 0.0, 1.2, 1.0])
    return save_figure("PIE", name)
