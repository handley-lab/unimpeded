import requests
from anesthetic import read_chains
import os
import datetime
import pandas as pd

class database:
    def __init__(self, sandbox=True, ACCESS_TOKEN=None, base_url=None, records_url=None):
        self.sandbox = sandbox
        self.ACCESS_TOKEN = ACCESS_TOKEN
        if sandbox == True:
            self.base_url = "https://sandbox.zenodo.org/api/deposit/depositions"
            self.records_url = "https://sandbox.zenodo.org/api/records"
        elif sandbox == False:
            self.base_url = "https://zenodo.org/api/deposit/depositions"
            self.records_url = "https://zenodo.org/api/records"


        #self.bucket_url = bucket_url

    def create_deposit(self):
        """Create a new empty deposit on Zenodo

        Returns:
        deposit_id (int): The ID of the new deposit on Zenodo
        """ 
        #base_url = 'https://sandbox.zenodo.org/api/deposit/depositions'
        r = requests.post(self.base_url,
                   params={'access_token': self.ACCESS_TOKEN},
                   json={})
        r.raise_for_status()           
        deposit_id = r.json()['id']
        #bucket_url = r.json()['links']['bucket']
        return deposit_id


    def get_filename_samples(self, method, model, dataset, loc):
        filename = f"{method}_{model}_{dataset}.csv"
        if loc == 'hpc':
            samples = read_chains(f"/home/dlo26/rds/rds-dirac-dp192-63QXlf5HuFo/dlo26/{method}/{model}/{dataset}/{dataset}_polychord_raw/{dataset}") # for hpc
        elif loc == 'local':
            samples = read_chains(f"../{method}/{model}/{dataset}/{dataset}_polychord_raw/{dataset}")
        return filename, samples
    
    def get_metadata(self, method, model, dataset):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        metadata = {
            "metadata": {
                "title": f"{method}_{model}_{dataset}",
                "upload_type": "dataset",  # e.g., dataset, publication, image, software
                "description": self.get_description(method, model, dataset),
                "creators": [
                    {"name": "Ong, Dily", "affiliation": "University of Cambridge"}
                ],
                "dates": [
                    {
                        "start": today,  # Custom date in YYYY-MM-DD format
                        "type": "Created"    # Type of date (e.g., Collected, Valid, etc.)
                    }
                ]
            }
        }    
        return metadata

    def update_metadata(self, deposit_id, metadata):
        r = requests.put(f"{self.base_url}/{deposit_id}",
                         params={'access_token': self.ACCESS_TOKEN},
                         json=metadata)
        r.raise_for_status()
        return r.json()    
    

    def upload(self, filename, samples, deposit_id):
        deposit_url = f"https://sandbox.zenodo.org/api/deposit/depositions/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(deposit_url)
        r.raise_for_status()
        bucket_url = r.json().get("links", {}).get("bucket") # retrieve bucket_url from deposit_id

        samples.to_csv(filename) # saving samples as csv, but is it necessary?
        path = f"./{filename}"
        print(path)
        params = {'access_token': self.ACCESS_TOKEN}
        with open(path, "rb") as fp:
            print(path)
            r = requests.put(
                f"{bucket_url}/{filename}",
                data=fp,
                params=params
            )
            r.raise_for_status()
        os.remove(f"./{filename}")
        return r.json()

    def download(self, ID, filename): #filename=method_model_dataset
        metadata_url = f"https://sandbox.zenodo.org/api/deposit/depositions/{ID}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(metadata_url)
        r.raise_for_status()
        if r.status_code == 200:
            deposit_info = r.json()
            files = deposit_info['files'] # list of files in the deposit

            downloads = []
            for file in files:
                if file['filename'] == f'{filename}':  # Check for your specific CSV file
                    download_url = file['links']['download']  # Direct download link
                    print("Download url:", download_url)
                    headers = {"Authorization": f"Bearer {self.ACCESS_TOKEN}"}
            
                
                    csv_r = requests.get(download_url, headers=headers)
                    csv_r.raise_for_status()
                
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


    def publish(self, deposit_id):
        publish_url = f"{self.base_url}/{deposit_id}/actions/publish"   
        # Publish the deposit
        r = requests.post(publish_url,
                    params={'access_token': self.ACCESS_TOKEN},
                    json={}
                    )
        r.raise_for_status()
        return r.json()
        
    def get_description(self, method, model, dataset):
        description = f"Method:{method}, cosmological model:{model}, dataset:{dataset}"
        return description

    def retrieve_records(self, description):
        print(f'description:{description}')
        r = requests.get(self.records_url, params={'q':f'description:"{description}"','access_token':self.ACCESS_TOKEN})
        r.raise_for_status()
        return r.json()