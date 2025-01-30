import requests
from anesthetic import read_chains
import os
import datetime
import pandas as pd
import yaml
from io import BytesIO
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
    
    def get_metadata(self, method, model, dataset, job_no):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        metadata = {
            "metadata": {
                "title": f"unimpeded: arrayjob_{job_no}_{model}_{dataset}",
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
        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(deposit_url)
        r.raise_for_status()
        bucket_url = r.json().get("links", {}).get("bucket") # retrieve bucket_url from deposit_id

        samples.to_csv(filename) # saving samples as csv, but is it necessary?
        path = f"./{filename}"
        print(path)
        params = {'access_token': self.ACCESS_TOKEN}
        print(filename)
        with open(path, "rb") as fp:
            r = requests.put(
                f"{bucket_url}/{filename}",
                data=fp,
                params=params
            )
            r.raise_for_status()
        os.remove(f"./{filename}")
        return r
    
    def get_yaml(self, method, model, dataset, loc):
        if loc == 'hpc':
            yaml_file_path = f'home/dlo26/rds/rds-dirac-dp192-63QXlf5HuFo/dlo26/{method}/{model}/{dataset}/{dataset}.updated.yaml' # for the hpc
        elif loc == 'local':
            yaml_file_path = f'Users/ongdily/Documents/Cambridge/project2/codes/{method}/{model}/{dataset}/{dataset}.updated.yaml' # for local computer
        with open(yaml_file_path, 'r') as file:
            # Load the YAML content into a Python data structure (usually a dictionary)
            yaml_data = yaml.safe_load(file)
        return yaml_data
    
    def get_yaml_path(self, method, model, dataset, loc):
        if loc == 'hpc':
            yaml_file_path = f'/home/dlo26/rds/rds-dirac-dp192-63QXlf5HuFo/dlo26/{method}/{model}/{dataset}/{dataset}.updated.yaml' # for the hpc
        elif loc == 'local':
            yaml_file_path = f'/Users/ongdily/Documents/Cambridge/project2/codes/{method}/{model}/{dataset}/{dataset}.updated.yaml' # for local computer
        return yaml_file_path

    def upload_yaml(self, yaml_file_path, method, model, dataset, deposit_id):
        """
        Need to rewrite this part
        Uploads a YAML file to the Zenodo sandbox.

        Args:
            self: The class instance (if this function is part of a class).
            filename: The name of the YAML file.
            deposit_id: The Zenodo deposit ID.

        Returns:
            The JSON response from the Zenodo API.
        """

        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(deposit_url)
        r.raise_for_status()
        bucket_url = r.json().get("links", {}).get("bucket") 

        #path = f"/{filename}" 
        params = {'access_token': self.ACCESS_TOKEN}
        filename = f"{method}_{model}_{dataset}.yaml"
        #filename = f"{method}_{model}_{dataset}.yaml"
        #filename = filename.strip()
        print(yaml_file_path)
        print(filename)
        with open(yaml_file_path, "rb") as fp:
            r = requests.put(
                f"{bucket_url}/{filename}", 
                data=fp,
                params=params
            )
            r.raise_for_status()
        
        return r.json()

    def download_yaml(self, deposit_id, method, model, dataset):
        """
        Downloads a YAML file from Zenodo sandbox to the local computer.

        Args:
            self: The class instance (if this function is part of a class).
            deposit_id: The Zenodo deposit ID.
            method, model, dataset: Components to form the filename.
            download_path: The local path where the file should be saved.
            
        Returns:
            None
        """
        # Build the URL to get the deposition's file metadata
        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(deposit_url)
        r.raise_for_status()
        
        # Extract the bucket URL and file information from the response
        bucket_url = r.json().get("links", {}).get("bucket")
        filename = f"{method}_{model}_{dataset}.yaml"
        
        # Form the URL to download the specific file
        file_url = f"{bucket_url}/{filename}"
        
        # Make the GET request to download the file
        file_response = requests.get(file_url, params={'access_token': self.ACCESS_TOKEN})
        file_response.raise_for_status()
        
        # Save the file locally
        with open(f'{filename}', "wb") as f:
            f.write(file_response.content)
        
        print(f"File downloaded successfully: {f'{filename}'}")


    def download(self, deposit_id, filename):
        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(deposit_url)
        r.raise_for_status()
        
        if r.status_code == 200:
            deposit_info = r.json()
            files = deposit_info['files']
            print("files:", files)
            downloads = []
            
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
                        else:
                            print(f"Unsupported file type: {filename}")
                            data = None
                        
                        if data is not None:
                            downloads.append(data)
                    else:
                        print(f"Error downloading {filename}:", file_r.status_code)
            return downloads
        else:
            print("Error retrieving deposit metadata:", r.status_code, r.json())

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
        
    def get_description(self, method, model, dataset):
        description = f"Method:{method}, cosmological model:{model}, dataset:{dataset}"
        return description

    def retrieve_records(self, description, return_latest=True):
        print(f'description:{description}')
        r = requests.get(self.records_url, params={'q':f'description:"{description}"','access_token':self.ACCESS_TOKEN})
        r.raise_for_status()
        print(r.json())
        deposit_data = r.json()
        no_records = len(deposit_data['hits']['hits']) # number of deposits with identical description on Zenodo found
        print(f"Number of deposits with identical description: {no_records}")
        if no_records==1:
            deposit_id_retrieved = deposit_data['hits']['hits'][-1]['id']
            print(f"Deposit ID: {deposit_id_retrieved}")
            return deposit_id_retrieved
        elif no_records>1:
            id_list = [] # list of deposit IDs with identical description
            for i in range(no_records):   
                id_list.append(deposit_data['hits']['hits'][i]['id'])
            print("Duplicate deposits found. Deposit IDs: ", id_list)
            if return_latest == True:
                latest_deposit_id_retrieved = id_list[-1]
                print(f"Returning the latest deposit ID: {latest_deposit_id_retrieved}")
                return latest_deposit_id_retrieved # default return the latest deposit
            else:
                return id_list

        

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

    def check_duplication(self, description): # maybe remove this function later 
        r = self.retrieve_records(description)
        print("Number of deposits with identical description: ", len(r['hits']['hits']))
        print('\n')
        for i in range(len(r['hits']['hits'])):   
            print(r['hits']['hits'][i]['metadata']['title'])
            print(r['hits']['hits'][i]['metadata']['description'])
            print(r['hits']['hits'][i]['id'])
            print('\n')

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
        
    def get_versions(self, concept_doi):
        url = f"{self.records_url}/{concept_doi}"
        response = requests.get(self.records_url, params={'q':f'conceptdoi:"{concept_doi}"','access_token':self.ACCESS_TOKEN})
        # Fetch the record for the given concept DOI
        #response = requests.get(url, params={'access_token':self.ACCESS_TOKEN})

        #headers = {"Authorization": f"Bearer {self.ACCESS_TOKEN}"}
        #response = requests.get(url, headers=headers)

        response.raise_for_status()
        
        # Extract versions from the response
        record = response.json()
        versions = record.get('versions', [])
        
        if versions:
            print("Published versions of the deposit:")
            for version in versions:
                print(f"Version DOI: {version['doi']}")
                print(f"Version ID: {version['id']}")
                print(f"Version Title: {version.get('metadata', {}).get('title', 'No title available')}")
                print(f"Version Published: {version.get('created', 'No date available')}")
                print("-" * 40)
        else:
            print("No versions found for this concept DOI.")
        
        return versions, response
    


    def get_deposit_ids_by_description(self, description):
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
    
    def get_deposit_ids_by_title(self, title):
        """
        Retrieves all deposit IDs that match the given title, including unpublished deposits,
        and separates them into published and unpublished categories.

        Args:
            title (str): The title to search for.

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
                    'q': f'title:"{title}"',
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

    def get_deposit_ids_by_title_2(self, title):
        """
        Retrieves all deposit IDs that match the given title, including unpublished deposits,
        and separates them into published and unpublished categories. Handles pagination.

        Args:
            title (str): The title to search for.

        Returns:
            dict: A dictionary with two keys:
                - "published": List of published deposit IDs
                - "unpublished": List of unpublished deposit IDs
        """
        deposit_ids = {"published": [], "unpublished": []}
        url = self.base_url
        params = {
            'q': f'title:"{title}"',
            'all_versions': True,  # Include all versions (published and unpublished)
            'status': 'all',       # Ensure drafts/unpublished deposits are included
            'access_token': self.ACCESS_TOKEN,
            'size': 100  # Number of results per page (adjust if needed)
        }

        try:
            while url:
                print(f"Fetching data from URL: {url}")  # Debugging statement
                r = requests.get(url, params=params)
                r.raise_for_status()  # Raise an error if the request fails
                response_data = r.json()

                # Debugging: Log the response structure
                print(f"Response structure: {response_data}")  # Print response for debugging

                # Check if response_data is a dictionary with the expected "hits" structure
                if isinstance(response_data, dict):
                    hits = response_data.get('hits', {}).get('hits', [])
                    for hit in hits:
                        deposit_id = hit.get('id')
                        is_published = hit.get('submitted', False)  # Check the "submitted" field
                        if deposit_id:
                            if is_published:
                                deposit_ids["published"].append(deposit_id)
                            else:
                                deposit_ids["unpublished"].append(deposit_id)
                    
                    # Get the next page URL from the "links" section
                    url = response_data.get('links', {}).get('next')
                    # Clear params after the first request
                    params = None
                else:
                    print("Unexpected response structure.")
                    break

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching deposit IDs: {e}")

        # Print published and unpublished deposit IDs
        print(f"Published deposit IDs: {deposit_ids['published']}")
        print(f"Unpublished deposit IDs: {deposit_ids['unpublished']}")

        return deposit_ids
    
    def get_deposit_ids_by_title_3(self, title):
        """
        Retrieves all deposit IDs that match the given title, including unpublished deposits,
        and separates them into published and unpublished categories. Handles pagination.

        Args:
            title (str): The title to search for.

        Returns:
            dict: A dictionary with two keys:
                - "published": List of published deposit IDs
                - "unpublished": List of unpublished deposit IDs
        """
        deposit_ids = {"published": [], "unpublished": []}
        url = self.base_url
        params = {
            'q': f'title:"{title}"',
            'all_versions': True,  # Include all versions (published and unpublished)
            'status': 'all',       # Ensure drafts/unpublished deposits are included
            'access_token': self.ACCESS_TOKEN,
            'size': 100  # Request up to 100 results per page
        }

        try:
            while url:
                print(f"Fetching data from URL: {url}")  # Debugging statement
                r = requests.get(url, params=params)
                r.raise_for_status()  # Raise an error if the request fails
                response_data = r.json()

                # Debugging: Log the response structure
                print(f"Response structure: {response_data}")

                # Handle response if it's a list of records
                if isinstance(response_data, list):
                    for record in response_data:
                        deposit_id = record.get('id')
                        is_published = record.get('submitted', False)  # Check the "submitted" field
                        if deposit_id:
                            if is_published:
                                deposit_ids["published"].append(deposit_id)
                            else:
                                deposit_ids["unpublished"].append(deposit_id)

                    # Pagination for list-based responses
                    url = None  # No pagination links available for lists; stop here
                
                # Handle pagination for dictionary-based structure
                elif isinstance(response_data, dict):
                    for hit in response_data.get('hits', {}).get('hits', []):
                        deposit_id = hit.get('id')
                        is_published = hit.get('submitted', False)  # Check the "submitted" field
                        if deposit_id:
                            if is_published:
                                deposit_ids["published"].append(deposit_id)
                            else:
                                deposit_ids["unpublished"].append(deposit_id)

                    # Pagination: Check if there's a "next" link
                    url = response_data.get('links', {}).get('next')
                    params = None  # Clear params for subsequent requests since `url` includes them
                
                else:
                    print("Unexpected response structure.")
                    break

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching deposit IDs: {e}")

        # Print published and unpublished deposit IDs
        print(f"Published deposit IDs: {deposit_ids['published']}")
        print(f"Unpublished deposit IDs: {deposit_ids['unpublished']}")

        return deposit_ids

    def get_deposit_ids_by_title_4(self, title):
        """
        Retrieves all deposit IDs that match the given title, including unpublished deposits,
        and separates them into published and unpublished categories. Handles full pagination.

        Args:
            title (str): The title to search for.

        Returns:
            dict: A dictionary with two keys:
                - "published": List of published deposit IDs
                - "unpublished": List of unpublished deposit IDs
        """
        deposit_ids = {"published": [], "unpublished": []}
        url = self.base_url
        params = {
            'q': f'title:"{title}"',
            'all_versions': True,  # Include all versions (published and unpublished)
            'status': 'all',       # Ensure drafts/unpublished deposits are included
            'access_token': self.ACCESS_TOKEN,
            'size': 100  # Max results per page
        }

        try:
            while url:
                print(f"Fetching data from URL: {url}")  # Debugging statement
                r = requests.get(url, params=params)
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
                
                # Process list-based responses (rare, based on your API behavior)
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

    def get_deposit_ids_by_title_5(self, title):
        """
        Retrieves all deposit IDs that match the given title, including unpublished deposits,
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


    def delete_deposit_by_id_old(self, deposit_ids):
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
    
    def delete_deposit_by_id(self, deposit_ids):
        """
        Deletes one or more deposits by their ID(s), including published deposits.
        If a deposit is published, it first removes the DOI before deleting the deposit.

        Args:
            deposit_ids (int or list): A single deposit ID (int) or a list of deposit IDs to delete.

        Returns:
            list: A list of dictionaries, each containing the deposit ID and the status of the operation.
        """
        # Handle both integer and list input for deposit_ids
        if isinstance(deposit_ids, int):
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

                # Determine if the deposit is published
                deposit_data = check_response.json()
                is_published = deposit_data.get('submitted', False)

                # Step 2: If published, delete the DOI first
                if is_published:
                    doi_url = f"{self.base_url}/{deposit_id}/actions"
                    doi_response = requests.post(
                        doi_url,
                        params={'access_token': self.ACCESS_TOKEN},
                        json={'action': 'edit'}  # Unlocks the published deposit for deletion
                    )

                    if doi_response.status_code != 200:
                        results.append({'deposit_id': deposit_id, 'status': f"Failed to Unlock DOI ({doi_response.status_code})"})
                        continue

                # Step 3: Attempt to delete the deposit
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
    
    def delete_deposit_by_id2(self, deposit_ids):
        """
        Deletes one or more deposits by their ID(s), including published deposits.
        If a deposit is published, it first unlocks the DOI before deleting the deposit.

        Args:
            deposit_ids (int or list): A single deposit ID (int) or a list of deposit IDs to delete.

        Returns:
            list: A list of dictionaries, each containing the deposit ID and the status of the operation.
        """
        # Handle both integer and list input for deposit_ids
        if isinstance(deposit_ids, int):
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

                # Determine if the deposit is published
                deposit_data = check_response.json()
                is_published = deposit_data.get('submitted', False)

                # Step 2: If published, unlock the deposit for deletion
                if is_published:
                    unlock_url = f"{self.base_url}/{deposit_id}/actions/edit"
                    unlock_response = requests.post(
                        unlock_url,
                        params={'access_token': self.ACCESS_TOKEN}
                    )

                    if unlock_response.status_code == 201:
                        results.append({'deposit_id': deposit_id, 'status': 'DOI unlocked'})
                    else:
                        results.append({'deposit_id': deposit_id, 'status': f"Failed to Unlock DOI ({unlock_response.status_code})"})
                        continue

                # Step 3: Attempt to delete the deposit
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