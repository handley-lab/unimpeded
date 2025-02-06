import requests
from anesthetic import read_chains
import os
import datetime
import pandas as pd
import yaml
from io import BytesIO

class Database:
    def get_filename(self, method, model, dataset, filestype): # a standalone function used by both DatabaseCreator and DatabaseExplorer
        if filestype == 'samples':
            filename = f"{method}_{model}_{dataset}.csv"
        elif filestype == 'info':
            filename = f"{method}_{model}_{dataset}.yaml"
        elif filestype == 'prior_info':
            filename = f"{method}_{model}_{dataset}.prior_info"
        else:
            raise ValueError(f"Invalid file type: {filestype}. Expected 'samples' or 'info'.")
        return filename
    
class DatabaseCreator(Database):
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
        r = requests.post(self.base_url,
                   params={'access_token': self.ACCESS_TOKEN},
                   json={})
        r.raise_for_status()           
        deposit_id = r.json()['id']
        #bucket_url = r.json()['links']['bucket']
        return deposit_id


    def create_description(self, model, dataset):
        description = f"cosmological model:{model}, dataset:{dataset}"
        return description


    def create_metadata(self, model, dataset):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        metadata = {
            "metadata": {
                "title": f"unimpeded: {model} {dataset}",
                "upload_type": "dataset",  # e.g., dataset, publication, image, software
                "description": self.create_description(model, dataset),
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
    

    def get_samples(self, method, model, dataset, loc):
        if loc == 'hpc':
            if method == "ns":
                samples = read_chains(f"/home/dlo26/rds/rds-dirac-dp192-63QXlf5HuFo/dlo26/{method}/{model}/{dataset}/{dataset}_polychord_raw/{dataset}") 
            elif method == "mcmc":
                samples = read_chains(f"/home/dlo26/rds/rds-dirac-dp192-63QXlf5HuFo/dlo26/{method}/{model}/{dataset}/{dataset}") 
        elif loc == 'local':
            if method == "ns":
                samples = read_chains(f"../{method}/{model}/{dataset}/{dataset}_polychord_raw/{dataset}")
            elif method == "mcmc":
                samples = read_chains(f"../{method}/{model}/{dataset}/{dataset}")
        return samples

    def upload_samples(self, deposit_id, method, model, dataset, loc):
        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(deposit_url)
        r.raise_for_status()
        bucket_url = r.json().get("links", {}).get("bucket") # retrieve bucket_url from deposit_id
        params = {'access_token': self.ACCESS_TOKEN}

        samples = self.get_samples(method, model, dataset, loc)
        filename = get_filename(method, model, dataset, filestype='samples')

        samples.to_csv(filename) 
        path = f"./{filename}"
        headers = {
            "Content-Type": "application/octet-stream"
        }        
        with open(path, "rb") as fp:
            r = requests.put(
                f"{bucket_url}/{filename}",
                data=fp,
                params=params,
                headers=headers
            )
            r.raise_for_status()
            if r.status_code == 201:
                print(f"Uploaded {filename} to Zenodo deposit {deposit_id} successfully")
            else:
                print(f"Error uploading {filename} to {deposit_id}:", r.status_code)
        os.remove(f"./{filename}")
        return r

    
    def get_yaml_path(self, method, model, dataset, loc):
        if loc == 'hpc':
            yaml_file_path = f'/home/dlo26/rds/rds-dirac-dp192-63QXlf5HuFo/dlo26/{method}/{model}/{dataset}/{dataset}.updated.yaml' # for the hpc
        elif loc == 'local':
            yaml_file_path = f'/Users/ongdily/Documents/Cambridge/project2/codes/{method}/{model}/{dataset}/{dataset}.updated.yaml' # for local computer
        return yaml_file_path
    

    def upload_yaml(self, deposit_id, method, model, dataset, loc):
        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(deposit_url)
        r.raise_for_status()
        bucket_url = r.json().get("links", {}).get("bucket") 
        params = {'access_token': self.ACCESS_TOKEN}

        filename = get_filename(method, model, dataset, filestype='info')
        
        yaml_file_path = self.get_yaml_path(method, model, dataset, loc)
        with open(yaml_file_path, "rb") as fp:
            r = requests.put(
                f"{bucket_url}/{filename}", 
                data=fp,
                params=params
            )
            r.raise_for_status()
            if r.status_code == 201:
                print(f"Uploaded {filename} to Zenodo deposit {deposit_id} successfully")
            else:
                print(f"Error uploading {filename} to {deposit_id}:", r.status_code)
        
        return r


    def get_prior_info_path(self, method, model, dataset, loc):
        if loc == 'hpc':
            path = f'/home/dlo26/rds/rds-dirac-dp192-63QXlf5HuFo/dlo26/{method}/{model}/{dataset}/{dataset}_polychord_raw/{dataset}.prior_info' # for the hpc
        elif loc == 'local':
            path = f'/Users/ongdily/Documents/Cambridge/project2/codes/{method}/{model}/{dataset}/{dataset}_polychord_raw/{dataset}.prior_info' # for local computer
        return path 
    

    def upload_prior_info(self, deposit_id, method, model, dataset, loc):
        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(deposit_url)
        r.raise_for_status()
        bucket_url = r.json().get("links", {}).get("bucket") 
        params = {'access_token': self.ACCESS_TOKEN}

        filename = get_filename(method, model, dataset, filestype='prior_info')
        
        prior_info_file_path = self.get_prior_info_path(method, model, dataset, loc)
        with open(prior_info_file_path, "rb") as fp:
            r = requests.put(
                f"{bucket_url}/{filename}", 
                data=fp,
                params=params
            )
            r.raise_for_status()
            if r.status_code == 201:
                print(f"Uploaded {filename} to Zenodo deposit {deposit_id} successfully")
            else:
                print(f"Error uploading {filename} to {deposit_id}:", r.status_code)
        
        return r

    def get_deposit_ids_by_title(self, title):
        """
        Note: this codes is suppose to find all deposits with the given title, page by page until the last record, but somehow it just return the first 100 records. Not sure why and need to fix this later.
        Retrieves first 100 deposit IDs that match the given title, 
        and separates them into published and unpublished categories. Handles full pagination.

        Args:
            title (str): The title to search for.

        Returns:
            dict: A dictionary with two keys:
                - "published": List of published deposit IDs
                - "unpublished": List of unpublished deposit IDs
        """
        deposit_ids = {"published": [], "unpublished": []}
        url = self.base_url  # Base URL for the API
        params = {
            'q': f'title:"{title}"',
            'all_versions': True,  # Include all versions (published and unpublished)
            'status': 'all',       # Ensure drafts/unpublished deposits are included
            'access_token': self.ACCESS_TOKEN,
            'size': 100  # Max results per page
        }

        try:
            while url:
                # Debugging statement to show the current URL being fetched
                print(f"Fetching data from URL: {url}")
                
                # Fetch the data
                r = requests.get(url, params=params if url == self.base_url else None)  # Use params only for the first request
                r.raise_for_status()  # Raise an error if the request fails
                response_data = r.json()

                # Debugging: Log the response structure
                print(f"Response structure: {response_data}")

                # Process dictionary-based response with pagination
                if isinstance(response_data, dict):
                    for hit in response_data.get('hits', {}).get('hits', []):
                        deposit_id = hit.get('id')
                        is_published = hit.get('submitted', False)  # Check the "submitted" field
                        if deposit_id:
                            if is_published:
                                deposit_ids["published"].append(deposit_id)
                            else:
                                deposit_ids["unpublished"].append(deposit_id)

                    # Follow the next page URL if it exists
                    url = response_data.get('links', {}).get('next')
                    params = None  # Clear params after the first request since `url` includes them
                
                # Handle list-based responses (if applicable)
                elif isinstance(response_data, list):
                    for record in response_data:
                        deposit_id = record.get('id')
                        is_published = record.get('submitted', False)  # Check the "submitted" field
                        if deposit_id:
                            if is_published:
                                deposit_ids["published"].append(deposit_id)
                            else:
                                deposit_ids["unpublished"].append(deposit_id)
                    
                    # Stop if no pagination is available for list-based responses
                    url = None
                
                else:
                    print("Unexpected response structure.")
                    break

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching deposit IDs: {e}")

        # Print published and unpublished deposit IDs
        print(f"Published deposit IDs: {deposit_ids['published']}")
        print(f"Unpublished deposit IDs: {deposit_ids['unpublished']}")

        return deposit_ids

    def delete_unpublished_deposit_by_id(self, deposit_ids):
        """
        Deletes one or more deposits by their ID(s), but first checks if the deposit exists.

        Args:
            deposit_ids (int or list): A single deposit ID (int) or a list of deposit IDs to delete.

        Returns:
            list: A list of dictionaries, each containing the deposit ID and the status of the operation.
        """
        if isinstance(deposit_ids, int):
            # Convert single integer deposit ID into a list for uniform processing
            deposit_ids = [deposit_ids]

        # Check if the list is empty
        if not deposit_ids:
            print("No existing deposits match the given description.")
            return []

        results = []

        for deposit_id in deposit_ids:
            try:
                # Step 1: Check if the deposit exists
                check_url = f"{self.base_url}/{deposit_id}"
                check_response = requests.get(
                    check_url,
                    params={'access_token': self.ACCESS_TOKEN}
                )

                if check_response.status_code == 404:  # Deposit does not exist
                    results.append({'deposit_id': deposit_id, 'status': 'Not Found'})
                    continue
                elif check_response.status_code != 200:  # Some other error while checking
                    results.append({'deposit_id': deposit_id, 'status': f"Check Failed ({check_response.status_code})"})
                    continue

                # Step 2: Attempt to delete the deposit if it exists
                delete_url = f"{self.base_url}/{deposit_id}"
                delete_response = requests.delete(
                    delete_url,
                    params={'access_token': self.ACCESS_TOKEN}
                )
                
                # Check if the deletion was successful
                if delete_response.status_code == 204:  # HTTP 204 means No Content (successful deletion)
                    results.append({'deposit_id': deposit_id, 'status': 'Deleted'})
                else:
                    results.append({'deposit_id': deposit_id, 'status': f"Delete Failed ({delete_response.status_code})"})
            except requests.exceptions.RequestException as e:
                print(f"An error occurred while processing deposit ID {deposit_id}: {e}")
                results.append({'deposit_id': deposit_id, 'status': 'Error'})

        return results
    

    def publish(self, deposit_id, metadata):
        # Ask for metadata as compulsory input because it is required for secondary publishing, even if metadata is identical
        publish_url = f"{self.base_url}/{deposit_id}/actions/publish"   
        # Publish the deposit
        r = requests.post(publish_url,
                    params={'access_token': self.ACCESS_TOKEN},
                    json=metadata
                    )
        r.json()
        r.raise_for_status()
        return r.json()
    
    def newversion(self, deposit_id):
        """
         Used to create a new version of an already published Zenodo deposit.
        """
        try:
            # Step 1: Retrieve deposit information
            deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
            r = requests.get(deposit_url)
            r.raise_for_status()
            deposit_data = r.json()
            
            if deposit_data.get('state') == 'done':  # Ensure it's published
                print("Deposit is published. Proceeding to create a new version.")
                
                # Step 2: Create a new version
                new_version_response = requests.post(
                    f"{self.base_url}/{deposit_id}/actions/newversion",
                    params={'access_token': self.ACCESS_TOKEN}
                )
            	#r = requests.post(f'{self.base_url}/{deposit_id}/actions/edit',
                  #params={'access_token': ACCESS_TOKEN}

                new_version_response.raise_for_status()
                new_version_data = new_version_response.json()
                
                print(f"New draft version created. Draft deposit ID: {new_version_data['id']}")
                return new_version_data['id']
            else:
                print("The deposit is not yet published or cannot be unlocked directly.")
                return None

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
####################### A new class? #######################
class DatabaseExplorer(Database):
    def __init__(self, sandbox=True, ACCESS_TOKEN=None, base_url=None, records_url=None):
        self.sandbox = sandbox
        self.ACCESS_TOKEN = ACCESS_TOKEN
        if sandbox == True:
            self.base_url = "https://sandbox.zenodo.org/api/deposit/depositions"
            self.records_url = "https://sandbox.zenodo.org/api/records"
        elif sandbox == False:
            self.base_url = "https://zenodo.org/api/deposit/depositions"
            self.records_url = "https://zenodo.org/api/records"

    def download(self, deposit_id, filename):
        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(deposit_url)
        r.raise_for_status()
        
        if r.status_code == 200:
            deposit_info = r.json()
            files = deposit_info['files']
            print("files:", files)
            
            for file in files:
                if file['filename'] == filename:  # Check for your specific file
                    download_url = file['links']['download']  # Direct download link
                    print("Download url:", download_url)
                    headers = {"Authorization": f"Bearer {self.ACCESS_TOKEN}"}
                    
                    file_r = requests.get(download_url, headers=headers)
                    file_r.raise_for_status()
                    
                    if file_r.status_code == 200:
                        # Handle CSV files
                        if filename.endswith('.csv'):
                            data = pd.read_csv(BytesIO(file_r.content))
                            print(f"{filename} CSV file loaded successfully.")
                        # Handle YAML files
                        elif filename.endswith(('.yaml', '.yml')):
                            data = yaml.safe_load(file_r.content.decode('utf-8'))
                            print(f"{filename} YAML file loaded successfully.")
                        # Handle PRIOR_INFO files
                        elif filename.endswith('.prior_info'):
                            try:
                                # Decode the content and strip any leading/trailing whitespace
                                raw_data = file_r.content.decode('utf-8-sig').strip()
                                
                                if raw_data:
                                    # Parse the content into key-value pairs
                                    data = {}
                                    for line in raw_data.splitlines():
                                        key, value = line.split('=')
                                        data[key.strip()] = int(value.strip())
                                    
                                    print(f"{filename} PRIOR_INFO file loaded successfully.")
                                else:
                                    print(f"Warning: {filename} PRIOR_INFO file is empty.")
                            except (UnicodeDecodeError, ValueError) as e:
                                print(f"Error processing {filename}: {e}")
                        else:
                            print(f"Unsupported file type: {filename}")
                            data = None
                        
                    else:
                        print(f"Error downloading {filename}:", file_r.status_code)
            return data
        else:
            print("Error retrieving deposit metadata:", r.status_code, r.json())


    def download_samples(self, deposit_id, method, model, dataset):
        filename = self.get_filename(method, model, dataset, 'samples')
        return self.download(deposit_id, filename)
    
    def download_info(self, deposit_id, method, model, dataset):
        filename = self.get_filename(method, model, dataset, 'info')
        return self.download(deposit_id, filename)

    def download_prior_info(self, deposit_id, method, model, dataset):
        filename = self.get_filename(method, model, dataset, 'prior_info')
        return self.download(deposit_id, filename)


    def get_deposit_ids_by_title(self, title):
        """
        Note: this codes is suppose to find all deposits with the given title, page by page until the last record, but somehow it just return the first 100 records. Not sure why and need to fix this later.
        Retrieves first 100 deposit IDs that match the given title, 
        and separates them into published and unpublished categories. Handles full pagination.

        Args:
            title (str): The title to search for.

        Returns:
            dict: A dictionary with two keys:
                - "published": List of published deposit IDs
                - "unpublished": List of unpublished deposit IDs
        """
        deposit_ids = {"published": [], "unpublished": []}
        url = self.base_url  # Base URL for the API
        params = {
            'q': f'title:"{title}"',
            'all_versions': True,  # Include all versions (published and unpublished)
            'status': 'all',       # Ensure drafts/unpublished deposits are included
            'access_token': self.ACCESS_TOKEN,
            'size': 100  # Max results per page
        }

        try:
            while url:
                # Debugging statement to show the current URL being fetched
                print(f"Fetching data from URL: {url}")
                
                # Fetch the data
                r = requests.get(url, params=params if url == self.base_url else None)  # Use params only for the first request
                r.raise_for_status()  # Raise an error if the request fails
                response_data = r.json()

                # Debugging: Log the response structure
                print(f"Response structure: {response_data}")

                # Process dictionary-based response with pagination
                if isinstance(response_data, dict):
                    for hit in response_data.get('hits', {}).get('hits', []):
                        deposit_id = hit.get('id')
                        is_published = hit.get('submitted', False)  # Check the "submitted" field
                        if deposit_id:
                            if is_published:
                                deposit_ids["published"].append(deposit_id)
                            else:
                                deposit_ids["unpublished"].append(deposit_id)

                    # Follow the next page URL if it exists
                    url = response_data.get('links', {}).get('next')
                    params = None  # Clear params after the first request since `url` includes them
                
                # Handle list-based responses (if applicable)
                elif isinstance(response_data, list):
                    for record in response_data:
                        deposit_id = record.get('id')
                        is_published = record.get('submitted', False)  # Check the "submitted" field
                        if deposit_id:
                            if is_published:
                                deposit_ids["published"].append(deposit_id)
                            else:
                                deposit_ids["unpublished"].append(deposit_id)
                    
                    # Stop if no pagination is available for list-based responses
                    url = None
                
                else:
                    print("Unexpected response structure.")
                    break

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching deposit IDs: {e}")

        # Print published and unpublished deposit IDs
        print(f"Published deposit IDs: {deposit_ids['published']}")
        print(f"Unpublished deposit IDs: {deposit_ids['unpublished']}")

        return deposit_ids       


    def get_published_deposit_ids_by_description(self, description):
        """
        Retrieves all deposit IDs that match the given description, including unpublished deposits,
        and separates them into published and unpublished categories.

        Args:
            description (str): The description to search for.

        Returns:
            dict: A dictionary with two keys:
                - "published": List of published deposit IDs
                - "unpublished": List of unpublished deposit IDs
        """
        deposit_ids = {"published": [], "unpublished": []}
        try:
            # Include drafts/unpublished records by adding `status=all`
            r = requests.get(
                self.base_url,
                params={
                    'q': f'description:"{description}"',
                    'all_versions': True,  # Include all versions (published and unpublished)
                    'status': 'all',       # Ensure drafts/unpublished deposits are included
                    'access_token': self.ACCESS_TOKEN
                }
            )
            r.raise_for_status()
            response_data = r.json()

            # Handle response if it is a list
            if isinstance(response_data, list):
                for record in response_data:
                    deposit_id = record.get('id')
                    is_published = record.get('submitted', False)  # Check the "submitted" field
                    if deposit_id:
                        if is_published:
                            deposit_ids["published"].append(deposit_id)
                        else:
                            deposit_ids["unpublished"].append(deposit_id)

            # Handle response if it is a dictionary with nested structure
            elif isinstance(response_data, dict):
                for hit in response_data.get('hits', {}).get('hits', []):
                    deposit_id = hit.get('id')
                    is_published = hit.get('submitted', False)  # Check the "submitted" field
                    if deposit_id:
                        if is_published:
                            deposit_ids["published"].append(deposit_id)
                        else:
                            deposit_ids["unpublished"].append(deposit_id)
                        
            else:
                print("Unexpected response structure.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching deposit IDs: {e}")

        # Print published and unpublished deposit IDs
        print(f"Published deposit IDs: {deposit_ids['published']}")
        print(f"Unpublished deposit IDs: {deposit_ids['unpublished']}")

        return deposit_ids



    def get_concept_doi(self, deposit_id):
        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        
        # Fetch deposit details
        response = requests.get(deposit_url)
        response.raise_for_status()
        
        deposit = response.json()
        concept_doi = deposit.get('conceptdoi')
        
        if concept_doi:
            print(f"Concept DOI: {concept_doi}")
            return concept_doi
        else:
            print("Concept DOI not found. Ensure the deposit is published.")
            return None  
