from anesthetic import read_chains

samples = read_chains(
    "data/grid/klcdm/planck_2018_plik/planck_2018_plik_polychord_raw/planck_2018_plik"
)

samples.columns
samples.columns
samples[["omk", "omega_de"]]
samples.omega_de
samples.plot_2d(["omk", "omega_de"])
axes = Out[18]
axes.loc["omk", "omega_de"]
