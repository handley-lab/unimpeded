import requests
from anesthetic import read_chains
import os
from datetime import datetime
import pandas as pd

class database:
    def __init__(self, sandbox=True, ACCESS_TOKEN=None, bucket_url=None):
        self.sandbox = sandbox
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.bucket_url = bucket_url


    def get_filename_samples(self, method, model, dataset, loc):
        filename = f"{method}_{model}_{dataset}.csv"
        if loc == 'hpc':
            samples = read_chains(f"/home/dlo26/rds/rds-dirac-dp192-63QXlf5HuFo/dlo26/{method}/{model}/{dataset}/{dataset}_polychord_raw/{dataset}") # for hpc
        elif loc == 'local':
            samples = read_chains(f"../{method}/{model}/{dataset}/{dataset}_polychord_raw/{dataset}")
        return filename, samples
    
    def create_metadata(title='filename', upload_type="dataset",name="Dily Ong", email='dlo26@cam.ac.uk', affiliation="University of Cambridge"):
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        metadata = {"metadata": {
            "upload_type": "dataset",
            "dates": [{"start": today, "type": "Created"}]
            }
                    }
        
        metadata["metadata"]["title"] = title
        metadata["metadata"]["upload_type"] = upload_type
        metadata["metadata"]["creators"] = [{"name": name, "email": email, "affiliation": affiliation}]
        metadata["metadata"]["license"] = "INSERT LICENSE HERE"

        return metadata
    
    def upload(self, filename, samples):        
        samples.to_csv(filename) # saving samples as csv, but is it necessary?
        path = f"./{filename}"
        print(path)
        params = {'access_token': self.ACCESS_TOKEN}
        with open(path, "rb") as fp:
            print(path)
            r = requests.put(
                f"{self.bucket_url}/{filename}",
                data=fp,
                params=params
            )
        os.remove(f"./{filename}")
        return r.json()

    def download(self, ID, filename): #filename=method_model_dataset
        metadata_url = f"https://sandbox.zenodo.org/api/deposit/depositions/{ID}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(metadata_url)
        if r.status_code == 200:
            deposit_info = r.json()
            files = deposit_info['files'] # list of files in the deposit

            downloads = []
            for file in files:
                if file['filename'] == f'{filename}':  # Check for your specific CSV file
                    download_url = file['links']['download']  # Direct download link
                    print(download_url)
                    headers = {"Authorization": f"Bearer {self.ACCESS_TOKEN}"}
            
                
                    csv_r = requests.get(download_url, headers=headers)
                
                    if csv_r.status_code == 200:
                        # Save the file locally
                        with open(f'{filename}', 'wb') as f:
                            f.write(csv_r.content)
                        print(f"{filename} file downloaded successfully.")
                        downloads.append(pd.read_csv(f'{filename}', index_col=0))
                    else:
                        print(f"Error downloading CSV file:", csv_r.status_code)
            return downloads
        else:
            print("Error retrieving deposit metadata:", r.status_code, r.json())

            
