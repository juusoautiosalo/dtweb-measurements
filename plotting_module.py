"""
Functions for plotting measurement results of Digital Twin Web.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt

# Set style for figures
try:
    from distutils.spawn import find_executable
    if find_executable('latex'):
        # print("Latex installed")
        plt.style.use(['science','ieee'])
        print('Using SciencePlots IEEE style for figures: https://github.com/garrettj403/SciencePlots#faq')
        # print('If you get weird errors, you may have to install LaTeX: https://github.com/garrettj403/SciencePlots#faq')
    else:
        print('Did not find LaTeX, using manually defined styles for figures')
        print('More info: https://github.com/garrettj403/SciencePlots#faq')
        raise Exception
except:
    plt.rcParams.update({'font.size': 8})


def plot_network_fetch_times(filepath: str, folderpath: str, registry_domain: str):
    """
    Plots network measurement

    Args:
      filepath: Path to measurement log file
      folderpath: Path to folder where all measurement result files will be written.
      registry_domain: internet domain address of the DTID registry for figure title
    """

    width = 2.3 # inches
    height = 3.5 # inches
    
    df = pd.read_csv(filepath)

    print(filepath)

    # Check max depth
    df = df[df['Event'] == 'DT doc received']
    max_depth = int(df["Depth"].max())
    print('Max depth: ' + str(max_depth))

    fig, axes = plt.subplots(figsize=(width,height))

    # Prepare data
    violindata = []
    quantiles = []
    labels = []
    for depth in range(max_depth+1):
        violindata.append(df[df.Depth == str(depth)]["Time"].values.astype('float'))
        quantiles.append([0,0.5,0.99])
        labels.append(str(depth))

    # Plot
    plot = axes.violinplot(dataset = violindata,
        points=100,
        widths=0.9,
        showmeans=False, showextrema=False, showmedians=False,
        quantiles=quantiles, 
        # bw_method=0.1
        )
    plot['cquantiles'].set_linewidth(0.5)
    
    # axes.violinplot(dataset = violindata,
    #     points=100,
    #     widths=0.9,
    #     showmeans=False, showextrema=False, showmedians=False,
    #     # quantiles=quantiles,
    #     bw_method=0.05)

    # Set texts to figure
    axes.set_title('DTID registry: ' + registry_domain)
    axes.yaxis.grid(True)
    axes.set_xlabel('Depth in the network (steps from origin)')
    axes.set_ylabel('Time (s)')
    # axes.set_ylim([0, 2])
    axes.set_xticks(range(1,max_depth+2))
    axes.set_xticklabels(labels)
    # plt.xticks(rotation=90)
    plt.tight_layout()

    figurename = 'fetch_times_network_' + registry_domain + '.pdf'
    fig.savefig(os.path.join(folderpath, figurename))

    return True


def plot_registry_fetch_times(filepath, folderpath, dtids):
    """
    Plots registry comparison measurement

    Args:
      filepath: Path to measurement log file
      folderpath: Path to folder where all measurement result files will be written.
      dtids: List of DTIDs to be plotted
    """

    df = pd.read_csv(filepath)


    #### VIOLIN simple ####
    # https://stackoverflow.com/questions/43345599/process-pandas-dataframe-into-violinplot

    fig, axes = plt.subplots(figsize=(3.5,3.5))

    # Prepare data
    df = df[df['Event'] == 'DT doc received']
    violindata = []
    quantiles = []
    labels = []
    for dtid in dtids:
        violindata.append(df[df.Base == dtid]["Time"].values.astype('float'))
        # quantiles.append([0,0.025,0.5,0.975,0.99])
        quantiles.append([0,0.5,0.99])
        labels.append(dtid.split('/')[2])

    # Plot
    plot = axes.violinplot(dataset = violindata,
        points=100,
        widths=0.9,
        showmeans=False, showextrema=False, showmedians=False, \
        quantiles=quantiles,
        bw_method=0.1)
    plot['cquantiles'].set_linewidth(0.5)


    # Set texts to figure
    # axes.set_title('Fetch time')
    axes.yaxis.grid(True)
    axes.set_xlabel('Domain name of registry')
    axes.set_ylabel('Time (s)')
    axes.set_ylim([0, 2])
    axes.set_xticks(range(1,len(dtids)+1))
    axes.set_xticklabels(labels)
    plt.xticks(rotation=90)
    plt.tight_layout()

    fig.savefig(os.path.join(folderpath, "base_fetch_times_violin.png"))
    fig.savefig(os.path.join(folderpath, "base_fetch_times_violin.pdf"))


    # VIOLIN with divided base & registry ####
    # https://stackoverflow.com/questions/43345599/process-pandas-dataframe-into-violinplot

    df = pd.read_csv(filepath)
    fig, axes = plt.subplots(figsize=(3.5,3.5))

    # Prepare data
    df_dh = df[df['Event'] == 'DTID > hosturl fetch time']
    violindata_dh = []
    quantiles = []
    labels = []
    for dtid in dtids:
        violindata_dh.append(df_dh[df_dh.Base == dtid]["Time"].values.astype('float'))
        quantiles.append([0,0.5,0.99,1])
        labels.append(dtid.split('/')[2])


    # Plot
    plot_dh = axes.violinplot(dataset = violindata_dh,
        points=100,
        widths=0.9,
        showmeans=False, showextrema=False, showmedians=False, \
        quantiles=quantiles, 
        # bw_method=0.1
        )
    plot_dh['cquantiles'].set_linewidth(0.5)

    plot_dh = axes.violinplot(dataset = violindata_dh,
        points=100,
        widths=0.9,
        showmeans=False, showextrema=False, showmedians=False, \
        quantiles=quantiles, 
        bw_method=0.1
        )

    plot_dh['cquantiles'].set_linewidth(0.5)

    # Prepare data
    df_hosdoc = df[df['Event'] == 'Hosturl > DT doc fetch time']
    violindata_hosdoc = []
    quantiles = []
    labels = []
    for dtid in dtids:
        violindata_hosdoc.append(df_hosdoc[df_hosdoc.Base == dtid]["Time"].values.astype('float'))
        quantiles.append([0,0.5,0.99,1])
        labels.append(dtid.split('/')[2])
    
    # Plot
    plot_hosdoc = axes.violinplot(dataset = violindata_hosdoc, points=100, widths=0.9, showmeans=False, showextrema=False, showmedians=False, \
        quantiles=quantiles, 
        bw_method=0.1)

    # Set texts to figure
    # axes.set_title('Fetch time')
    axes.yaxis.grid(True)
    # axes.set_xlabel('Base number')
    axes.set_ylabel('Time (s)')
    axes.set_ylim([0, 2])
    axes.set_xticks(range(1,len(dtids)+1))
    axes.set_xticklabels(labels)
    plt.xticks(rotation=90)
    plt.tight_layout()
   
    plot_hosdoc['cquantiles'].set_linewidth(0.5)

    fig.savefig(os.path.join(folderpath, "base_fetch_times_violin_divided.png"))
    fig.savefig(os.path.join(folderpath, "base_fetch_times_violin_divided.pdf"))

    return True

if __name__ == '__main__':

    print('Use the "run_measurements.py file to run and plot measurements')
