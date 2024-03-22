"""Loading datasets."""
from anesthetic import read_chains


class unimpeded:
    """Loading datasets.

    **kwargs
    ----------
    location : str
        The location where the datasets are stored.

    """
    def __init__(self, **kwargs):
        self.location = kwargs.pop('location', None)

    def get(self, model, dataset, method):
        """Get the samples from the dataset.

        Parameters
        ----------
        method : str
            The chosen method, ns or mcmc.
        model : str
            The chosen model, e.g. klcdm.
        dataset : str
            The chosen dataset, e.g. bao.sdss_dr16.
        """
        samples = read_chains(
            self.location + f"{method}/{model}/{dataset}/"
            f"{dataset}_polychord_raw/{dataset}")
        return samples
