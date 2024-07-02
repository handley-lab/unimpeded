import requests
from anesthetic import read_chains

class database:
    def __init__(self, sandbox=True, ACCESS_TOKEN=None, bucket_url=None):
        self.sandbox = sandbox
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.bucket_url = bucket_url

    def upload(self, method, model, dataset, loc):
        filename = f"{method}_{model}_{dataset}.csv"
        if loc == 'hpc':
            samples = read_chains(f"/home/dlo26/rds/rds-dirac-dp192-63QXlf5HuFo/dlo26/{method}/{model}/{dataset}/{dataset}_polychord_raw/{dataset}") # for hpc
        elif loc == 'local':
            samples = read_chains(f"../{method}/{model}/{dataset}/{dataset}_polychord_raw/{dataset}")
        samples.to_csv(filename) # saving samples as csv, but is it necessary?
        path = f"./{filename}"
        with open(path, "rb") as fp:
            print(path)
            r = requests.put(
                f"{bucket_url}/{filename}",
                data=fp,
                params=params
            )
