import seaborn as sns
import matplotlib.pyplot as plt

from functions import validate, max_len
from configurating import skip_string

folder = None


def main(f):
    sns.set_style("ticks", {"font.family": "Segoe UI"})
    sns.set_palette("tab10")
    sns.set_context("paper")

    global folder
    folder = f + "\\plots"


def save_figure(plot_type, x, groups=None):
    if groups is None:
        groups = "Tất cả"
    path = "{}\\{}_{}_{}.jpg".format(folder, plot_type, max_len(validate(x), 20), max_len(validate(groups), 20))
    plt.savefig(path, dpi=200)
    plt.clf()
    return path


# ---------------------------------------- Plotting data ---------------------------------------- #
def kde(df, x, groups=None):
    if groups != skip_string:
        if groups is None:
            sns.histplot(df.loc[:, x], color="#217346", kde=True, bins=10, legend=None)
        else:
            for g in df[groups].unique():
                sns.kdeplot(df.loc[df[groups] == g, x], shade=True, linewidth=1, alpha=.45, bw_adjust=.8, thresh=0)

            plt.legend(labels=df[groups].unique(), edgecolor="#000000", fancybox=False)
        
        plt.title(x)

        return save_figure("kde", x, groups)


def bar(df, name):
    if "Tất cả" not in df.index:
        df.plot(kind="barh", stacked=True)
        plt.legend(edgecolor="#000000", fancybox=False)
    else:
        df.plot(kind="barh", legend=None)

    plt.title(name)

    plt.ylabel(name)
    plt.xlabel("Count")

    plt.tight_layout()
    return save_figure("bar", name)


def pie(df, x, y, name):
    patches, _, auto_pcts = plt.pie(df.loc[df[y] != 0, y],
                                    autopct=lambda p: "{:.0f}%".format(round(p)) if p >= 6 else None,
                                    pctdistance=0.85, startangle=90, counterclock=False,
                                    explode=(df.loc[:, y] == df.loc[:, y].max()).apply(float) / 20, normalize=True,
                                    colors=["#dc3e32", "#f75b57", "#fc9803", "#f7bd46", "#33a752", "#61d667",
                                            "#548dd4", "#66b3ff", "#7a4add", "#bc74ed", "#000000"])
    
    labels = df.loc[df[y] != 0, x]

    plt.legend(patches, labels, edgecolor="#000000", fancybox=False, loc="center left", borderaxespad=0)
    plt.subplots_adjust(right=1.5)

    plt.setp(auto_pcts, **{"color": "white", "weight": "bold", "fontsize": 12, "fontname": "DejaVu Sans"})

    # Draw circle
    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    plt.axis("equal") 
    plt.title(name)

    plt.tight_layout(rect=[0.0, 0.0, 1.3, 1.0])
    return save_figure("pie", name)
