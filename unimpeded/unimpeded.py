#%%
from anesthetic import read_chains
#%%
class unimpeded:

    # which __init__ is better?
    """
    def __init__(self, **kwargs):
        self.model = kwargs.pop('model', None)
        self.data = kwargs.pop('data', None)
        self.method = kwargs.pop('method', None)
    """
    def __init__(self, model, dataset, method, location):
        self.model = model
        self.dataset = dataset
        self.method = method
        self.location = location
    
    def get(self):
        if self.location == 'hpc':
            samples = read_chains(f"/home/dlo26/rds/rds-dirac-dp192-63QXlf5HuFo/dlo26/{self.method}/{self.model}/{self.dataset}/{self.dataset}_polychord_raw/{self.dataset}") # for hpc
        elif self.location == 'local':
            samples = read_chains(f"../../{self.method}/{self.model}/{self.dataset}/{self.dataset}_polychord_raw/{self.dataset}")
        return samples

#%%
database = unimpeded('klcdm', 'bao.sdss_dr16', 'ns', 'local')
samples = database.get()
# %%
