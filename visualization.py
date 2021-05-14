from locale import normalize
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from functions import validate, maxlen, aspace
from configurating import enter

folder = ''
def main(f):
    sns.set_style('ticks')
    sns.set_palette('tab10')
    sns.set_context('paper')
    sns.set_style({'font.family': 'Segoe UI'})

    global folder
    folder = f + '\\plots'

def savefig(type, x, groups=''):
    if groups == '': groups = 'Tất cả'
    path = folder + '\\' + type + '_' + maxlen(validate(x), 20) + '_' + maxlen(validate(groups), 20) + '.jpg'
    plt.savefig(path, dpi=200)
    plt.clf()
    return path

def kde(df, x, groups=''):
    if groups != enter:
        if groups == '':
            sns.histplot(df.loc[:, x], color='#217346', kde=True, bins=10, legend=None)
        else:
            for g in df[groups].unique():
                sns.kdeplot(df.loc[df[groups] == g, x], shade=True, linewidth=1, alpha=.45, bw_adjust=.8, thresh=0)

            plt.legend(labels=df[groups].unique(), edgecolor='#000000', fancybox=False)
        
        plt.title(x)

        return savefig('kde', x, groups)

def bar(df, name):
    if 'Tất cả' not in df.index:
        df.plot(kind='barh', stacked=True)
        plt.legend(edgecolor='#000000', fancybox=False)
    else:
        df.plot(kind='barh', legend=None)

    plt.title(name)

    plt.ylabel(name)
    plt.xlabel('Count')

    plt.tight_layout()
    return savefig('bar', name)

def pie(df, x, y, name):#explode=(df.loc[:, y] == df.loc[:, y].max()).apply(float) / 12
    patches, _, autopcts = plt.pie(df.loc[df[y] != 0, y], autopct=lambda p: '{:.0f}%'.format(round(p)) if p >= 6 else '',
        pctdistance=0.85, startangle=90, counterclock=False, explode=(df.loc[:, y] == df.loc[:, y].max()).apply(float) / 20, normalize=True, colors=['#dc3e32', '#f75b57', '#fc9803', '#f7bd46', '#33a752', '#61d667', '#548dd4', '#66b3ff', '#7a4add', '#bc74ed', '#000000'])
    
    labels=df.loc[df[y] != 0, x]

    plt.legend(patches, labels, edgecolor='#000000', fancybox=False, loc="center left", borderaxespad=0)
    plt.subplots_adjust(right=1.5)

    plt.setp(autopcts, **{'color':'white', 'weight':'bold', 'fontsize': 12, 'fontname': 'DejaVu Sans'})

    # Draw circle
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    plt.axis('equal') 
    plt.title(name)

    plt.tight_layout(rect=[0,0,1.3,1])
    return savefig('pie', name)