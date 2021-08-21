import seaborn as sns
import matplotlib.pyplot as plt
from functions import validate, max_len
from matplotlib.ticker import FuncFormatter
import math

folder = None
title_size = 12


def main(f):
    sns.set_style("whitegrid")
    sns.set_palette("deep")
    sns.set_context("paper")

    global folder
    folder = f + "\\plots"


def save_figure(plot_type, x, groups="__All"):
    # Set X ticks to integer values
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda i, _: int(i)))

    if groups == "__All":
        groups = "Tất cả"
    path = "{}\\{} - {} ({}).jpg".format(folder, plot_type, max_len(validate(x), 80), max_len(validate(groups), 50))
    plt.savefig(path, dpi=180)
    plt.clf()
    return path


# ---------------------------------------- Plotting data ---------------------------------------- #
def hist(df, x, groups=None):
    n_bins = math.ceil(math.log2(len(df.index)) + 1)
    if groups is None:
        sns.histplot(x=df.loc[:, x], bins=n_bins, legend=None)
        plt.ylabel("Tần suất")
    else:
        sns.histplot(x=df.loc[:, x], y=df.loc[:, groups], hue=df.loc[:, groups], legend=None)
        plt.ylabel(None)

    plt.title(x, fontdict={"fontsize": title_size})

    plt.xlabel(None)
    plt.grid(False, which='major', axis="x")

    return save_figure("HST", x)


def box(df, x, groups=None):
    if groups is None:
        sns.boxplot(x=df.loc[:, x])
    else:
        sns.boxplot(x=df.loc[:, x], y=df.loc[:, groups])

    sns.despine(left=True)

    plt.title(x, fontdict={"fontsize": title_size})

    plt.xlabel(None)
    plt.ylabel(None)

    return save_figure("BOX", x)


def bar(df, name):
    if "Tất cả" not in df.index:
        df.plot(kind="barh", stacked=True)
        plt.legend(edgecolor="#000000", fancybox=False)
    else:
        df.plot(kind="barh", legend=None)

    plt.grid(True, which='major', axis="x", color='grey', alpha=.25)
    plt.grid(False, which='major', axis="y")

    plt.title(name, fontdict={"fontsize": title_size})

    plt.ylabel(None)
    plt.xlabel("Tần suất")

    plt.tight_layout()
    return save_figure("BAR", name)


def pie(df, x, y, name):
    patches, _, auto_pcts = plt.pie(df.loc[df[y] != 0, y],
                                    autopct=lambda p: "{:.0f}%".format(round(p)) if p >= 6 else None,
                                    startangle=90, counterclock=False, normalize=True)
    
    labels = df.loc[df[y] != 0, x]

    plt.legend(patches, labels, edgecolor="#000000", fancybox=False, loc="center left", borderaxespad=0)
    plt.subplots_adjust(right=2.5)

    plt.setp(auto_pcts, **{"color": "white", "fontsize": 16})

    plt.axis("equal")
    plt.title(name, fontdict={"fontsize": title_size})

    plt.ylabel(None)
    plt.xlabel(None)

    plt.tight_layout(rect=[0.0, 0.0, 1.2, 1.0])
    return save_figure("PIE", name)
