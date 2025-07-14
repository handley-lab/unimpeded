import matplotlib.pyplot as plt
from anesthetic import read_chains

samples = read_chains(
    "data/grid/lcdm/planck_2018_plik/planck_2018_plik_polychord_raw/planck_2018_plik"
)
# samples = read_chains('data/mcmc/lcdm/planck_2018_plik/planck_2018_plik')
# samples.set_labels()
samples.iloc[:, :27].plot_1d()
fig = plt.gcf()
fig.set_size_inches(3, 3)
for ax in fig.get_axes():
    ax.set_xticks([])
    ax.xaxis.label.set_size(8)

fig.tight_layout()
fig.savefig("/home/will/documents/talks/figures/planck_2018_plik.pdf")
plt.gcf().tight_layout()
