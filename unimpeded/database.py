"""Create, publish and retrieve unimpeded chain deposits on Zenodo.

Provides :class:`Database` with the naming scheme shared by both halves,
:class:`DatabaseCreator` for archiving a grid to Zenodo, and
:class:`DatabaseExplorer` for downloading it back without credentials.
"""

import datetime
import os
from io import BytesIO

import requests
import yaml
from anesthetic import read_chains, read_csv

#: Base directory holding the chain grid that ``DatabaseCreator`` uploads from.
#: Defaults to the DiRAC allocation the public grid was produced on; override
#: with the ``UNIMPEDED_GRID_ROOT`` environment variable, or per call with the
#: ``root`` argument of the path helpers, to upload from anywhere else.
DEFAULT_GRID_ROOT = os.environ.get(
    "UNIMPEDED_GRID_ROOT",
    "/home/dlo26/rds/rds-dirac-dp192-63QXlf5HuFo/dlo26",
)


class Database:
    """Shared filename conventions for the Zenodo deposit classes.

    This class in inherited by class DatabaseCreator and DatabaseExplorer.
    """

    def __init__(self, sandbox=False):
        """Initialise the instance and fetch what is available from Zenodo.

        Parameters
        ----------
        sandbox : bool, optional
            Whether to use the Zenodo sandbox environment. Defaults to False.
        """
        self.sandbox = sandbox
        if sandbox:
            self.records_url = "https://sandbox.zenodo.org/api/records"
        else:
            self.records_url = "https://zenodo.org/api/records"

        # Fetch available combinations from Zenodo
        self.combinations = self._fetch_combinations()

    @property
    def models(self):
        """Sorted list of all unique model names available on Zenodo."""
        return sorted({model for model, _ in self.combinations})

    @property
    def datasets(self):
        """Sorted list of all unique dataset names available on Zenodo."""
        return sorted({dataset for _, dataset in self.combinations})

    def datasets_for(self, model):
        """Return a sorted list of datasets available for a given model.

        Parameters
        ----------
        model : str
            The cosmological model name (e.g. 'lcdm').

        Returns
        -------
        list
            A sorted list of dataset names available for the model.
        """
        return sorted({dataset for m, dataset in self.combinations if m == model})

    def models_for(self, dataset):
        """Return a sorted list of models available for a given dataset.

        Parameters
        ----------
        dataset : str
            The dataset identifier (e.g. 'planck_2018_plik').

        Returns
        -------
        list
            A sorted list of model names available for the dataset.
        """
        return sorted({model for model, d in self.combinations if d == dataset})

    def is_available(self, model, dataset):
        """Check whether a specific model-dataset combination exists on Zenodo.

        Parameters
        ----------
        model : str
            The cosmological model name.
        dataset : str
            The dataset identifier.

        Returns
        -------
        bool
            True if the combination exists, False otherwise.
        """
        return (model, dataset) in self.combinations

    def _fetch_combinations(self):
        """Extract every (model, dataset) pair from the Zenodo deposits.

        Returns
        -------
        set
            A set of (model, dataset) tuples representing available combinations.
        """
        combinations = set()
        page = 1
        size = 25  # Maximum results per page allowed by Zenodo API

        try:
            while True:
                params = {
                    "q": 'title:"unimpeded:"',
                    "size": size,
                    "page": page,
                }

                response = requests.get(self.records_url, params=params)
                response.raise_for_status()
                data = response.json()

                hits = data.get("hits", {}).get("hits", [])
                if not hits:
                    break

                for hit in hits:
                    title = hit.get("metadata", {}).get("title", "")
                    # Expected format: "unimpeded: model dataset"
                    if title.startswith("unimpeded: "):
                        parts = (
                            title.replace("unimpeded: ", "").strip().split(maxsplit=1)
                        )
                        if len(parts) == 2:
                            combinations.add((parts[0], parts[1]))

                # Check if there are more pages
                total = data.get("hits", {}).get("total", 0)
                if page * size >= total:
                    break
                page += 1

        except requests.RequestException as e:
            print(f"Error fetching deposits: {e}")

        return combinations

    def get_filename(self, method, model, dataset, filestype):
        """Generate a filename from the method, model, dataset and file type.

        Parameters
        ----------
        method : str
            The method used by the HPC to obtain the chains ('ns' for Nested Sampling or
            'mcmc' for Metropolis-Hastings).
        model : str
            The cosmological model name (e.g. 'klcdm').
        dataset : str
            The dataset identifier (e.g. 'bao.sdss_dr16+des_y1.joint).
        filestype : str
            The type of file. Must be one of 'samples', 'info', or 'prior_info'.

        Returns
        -------
        str
            The generated filename.

        Raises
        ------
        ValueError
            If the filestype is not one of the expected types.
        """
        if filestype == "samples":
            filename = f"{method}_{model}_{dataset}.csv"
        elif filestype == "info":
            filename = f"{method}_{model}_{dataset}.yaml"
        elif filestype == "prior_info":
            filename = f"{method}_{model}_{dataset}.prior_info"
        else:
            raise ValueError(
                f"Invalid file type: {filestype}. "
                "Expected 'samples', 'info' or 'prior_info'."
            )
        return filename


class DatabaseCreator(Database):
    """A class for creating and managing deposits on Zenodo.

    Inherits from Database to utilise filename generation. ACCESS_TOEKN is required for
    authentication and is intended to be used only by the authors of unimpeded.
    """

    def __init__(
        self, sandbox=True, ACCESS_TOKEN=None, base_url=None, records_url=None
    ):
        """Initialise the DatabaseCreator instance.

        Parameters
        ----------
        sandbox : bool, optional
            Whether to use the Zenodo sandbox environment. Defaults to True.
        ACCESS_TOKEN : str, optional
            The access token for authentication.
        base_url : str, optional
            The base URL for deposit endpoints.
        records_url : str, optional
            The URL for records endpoints.
        """
        self.ACCESS_TOKEN = ACCESS_TOKEN
        if sandbox:
            self.base_url = "https://sandbox.zenodo.org/api/deposit/depositions"
        else:
            self.base_url = "https://zenodo.org/api/deposit/depositions"
        super().__init__(sandbox)

    def create_deposit(self):
        """Create a new empty deposit on Zenodo.

        Returns
        -------
        int
            The deposit_id of the new deposit on Zenodo.
        """
        r = requests.post(
            self.base_url, params={"access_token": self.ACCESS_TOKEN}, json={}
        )
        r.raise_for_status()
        deposit_id = r.json()["id"]
        return deposit_id

    def create_description(self, model, dataset):
        """Create a description string for the deposit based on model and dataset.

        Parameters
        ----------
        model : str
            The cosmological model name.
        dataset : str
            The dataset name.

        Returns
        -------
        str
            The description string.
        """
        description = f"cosmological model:{model}, dataset:{dataset}"
        return description

    def create_metadata(self, model, dataset):
        """Create metadata for a deposit on Zenodo.

        Parameters
        ----------
        model : str
            The cosmological model name.
        dataset : str
            The dataset name.

        Returns
        -------
        dict
            The metadata dictionary for the deposit.
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        metadata = {
            "metadata": {
                "title": f"unimpeded: {model} {dataset}",
                "upload_type": "dataset",
                "description": self.create_description(model, dataset),
                "creators": [
                    {"name": "Ong, Dily", "affiliation": "University of Cambridge"}
                ],
                "dates": [
                    {
                        "start": today,  # Custom date in YYYY-MM-DD format
                        # Date type, e.g. Collected, Valid, etc.
                        "type": "Created",
                    }
                ],
            }
        }
        return metadata

    def update_metadata(self, deposit_id, metadata):
        """Update the metadata of an existing zenodo deposit.

        Parameters
        ----------
        deposit_id : int
            The deposit ID of the deposit to be updated.
        metadata : dict
            The metadata to be updated.

        Returns
        -------
        Response
            The requests response object.
        """
        r = requests.put(
            f"{self.base_url}/{deposit_id}",
            params={"access_token": self.ACCESS_TOKEN},
            json=metadata,
        )
        r.raise_for_status()
        return r

    def _grid_stem(self, method, model, dataset, grid="new_grid", root=None):
        """Build the directory holding one (method, model, dataset) run in the grid.

        The layout below the base directory is identical wherever the grid is stored, so
        only the base varies between machines.

        Parameters
        ----------
        method : str
            The sampling method ('ns' or 'mcmc').
        model : str
            The cosmological model name.
        dataset : str
            The dataset name.
        grid : str, optional
            Which grid the chains live in. Defaults to 'new_grid'.
        root : str, optional
            Base directory containing the grid. Defaults to :data:`DEFAULT_GRID_ROOT`.

        Returns
        -------
        str
            The directory containing that run's files.
        """
        base = DEFAULT_GRID_ROOT if root is None else root
        return f"{base}/{grid}/{method}/{model}/{dataset}"

    def get_samples(
        self, method, model, dataset, loc="hpc", grid="new_grid", root=None
    ):
        """Retrieve samples for one method, model and dataset from the grid.

        Parameters
        ----------
        method : str
            The sampling method ('ns' for Nested Sampling and 'mcmc' for Metropolis-
            Hastings).
        model : str
            The cosmological model name.
        dataset : str
            The dataset name.
        loc : str, optional
            Retained for backwards compatibility; the grid location is now determined by
            ``root``. Defaults to 'hpc'.
        grid : str, optional
            Which grid the chains live in. 'grid' for datasets in paper 2511.04661;
            'new_grid' for datasets in paper 2603.05472. Defaults to 'new_grid'.
        root : str, optional
            Base directory containing the grid. Defaults to :data:`DEFAULT_GRID_ROOT`.

        Returns
        -------
        DataFrame
            The samples loaded via the anesthetic's read_chains function.

        Raises
        ------
        ValueError
            If the method is not 'ns' or 'mcmc'.
        """
        stem = self._grid_stem(method, model, dataset, grid=grid, root=root)
        if method == "ns":
            return read_chains(f"{stem}/{dataset}_polychord_raw/{dataset}")
        elif method == "mcmc":
            return read_chains(f"{stem}/{dataset}")
        raise ValueError(f"Invalid method: {method}. Expected 'ns' or 'mcmc'.")

    def upload_samples(
        self, deposit_id, method, model, dataset, loc="hpc", grid="new_grid", root=None
    ):
        """Upload samples from a local or HPC location to a Zenodo deposit.

        Parameters
        ----------
        deposit_id : int
            The deposit ID of the deposit.
        method : str
            The sampling method ('ns' for Nested Sampling or 'mcmc' for Metropolis-
            Hastings).
        model : str
            The cosmological model name.
        dataset : str
            The dataset name.
        loc : str
            The location of the samples ('hpc' for the HPC or 'local' for the local
            computer).
        grid : str, optional
            Which grid the chains live in. 'grid' for datasets in paper 2511.04661;
            'new_grid' for datasets in paper 2603.05472. Defaults to 'new_grid'.

        Returns
        -------
        Response
            The requests response object after uploading.
        """
        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(deposit_url)
        r.raise_for_status()
        bucket_url = r.json().get("links", {}).get("bucket")
        params = {"access_token": self.ACCESS_TOKEN}

        samples = self.get_samples(method, model, dataset, loc, grid=grid, root=root)
        filename = self.get_filename(method, model, dataset, filestype="samples")

        samples.to_csv(filename)
        path = f"./{filename}"
        headers = {"Content-Type": "application/octet-stream"}
        with open(path, "rb") as fp:
            r = requests.put(
                f"{bucket_url}/{filename}", data=fp, params=params, headers=headers
            )
            r.raise_for_status()
            if r.status_code == 201:
                print(
                    f"Uploaded {filename} to Zenodo deposit {deposit_id} successfully"
                )
            else:
                print(f"Error uploading {filename} to {deposit_id}:", r.status_code)
        os.remove(f"./{filename}")
        return r

    def get_yaml_path(
        self, method, model, dataset, loc="hpc", grid="new_grid", root=None
    ):
        """Generate the file path for the YAML file based on method, model, and dataset.

        Parameters
        ----------
        method : str
            The sampling method ('ns' for Nested Sampling and 'mcmc' for Metropolis-
            Hastings).
        model : str
            The cosmological model name.
        dataset : str
            The dataset name.
        loc : str, optional
            Retained for backwards compatibility; the grid location is now determined by
            ``root``. Defaults to 'hpc'.
        grid : str, optional
            Which grid the chains live in. 'grid' for datasets in paper 2511.04661;
            'new_grid' for datasets in paper 2603.05472. Defaults to 'new_grid'.
        root : str, optional
            Base directory containing the grid. Defaults to :data:`DEFAULT_GRID_ROOT`.

        Returns
        -------
        str
            The full path to the YAML file.
        """
        stem = self._grid_stem(method, model, dataset, grid=grid, root=root)
        return f"{stem}/{dataset}.updated.yaml"

    def upload_yaml(
        self, deposit_id, method, model, dataset, loc="hpc", grid="new_grid", root=None
    ):
        """Upload the YAML run-settings file to a Zenodo deposit.

        Parameters
        ----------
        deposit_id : int
            The deposit ID of the deposit.
        method : str
            The sampling method ('ns' for Nested Sampling or 'mcmc' for Metropolis-
            Hastings).
        model : str
            The cosmological model name.
        dataset : str
            The dataset name.
        loc : str
            The location of the samples ('hpc' for the HPC or 'local' for the local
            computer).
        grid : str, optional
            Which grid the chains live in. 'grid' for datasets in paper 2511.04661;
            'new_grid' for datasets in paper 2603.05472. Defaults to 'new_grid'.

        Returns
        -------
        Response
            The requests response object after uploading.
        """
        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(deposit_url)
        r.raise_for_status()
        bucket_url = r.json().get("links", {}).get("bucket")
        params = {"access_token": self.ACCESS_TOKEN}

        filename = self.get_filename(method, model, dataset, filestype="info")
        yaml_file_path = self.get_yaml_path(
            method, model, dataset, loc, grid=grid, root=root
        )
        with open(yaml_file_path, "rb") as fp:
            r = requests.put(f"{bucket_url}/{filename}", data=fp, params=params)
            r.raise_for_status()
            if r.status_code == 201:
                print(
                    f"Uploaded {filename} to Zenodo deposit {deposit_id} successfully"
                )
            else:
                print(f"Error uploading {filename} to {deposit_id}:", r.status_code)

        return r

    def get_prior_info_path(
        self, method, model, dataset, loc="hpc", grid="new_grid", root=None
    ):
        """Generate the PRIOR_INFO path for a method, model and dataset.

        Parameters
        ----------
        method : str
            The sampling method ('ns' for Nested Sampling and 'mcmc' for Metropolis-
            Hastings).
        model : str
            The cosmological model name.
        dataset : str
            The dataset name.
        loc : str, optional
            Retained for backwards compatibility; the grid location is now determined by
            ``root``. Defaults to 'hpc'.
        grid : str, optional
            Which grid the chains live in. 'grid' for datasets in paper 2511.04661;
            'new_grid' for datasets in paper 2603.05472. Defaults to 'new_grid'.
        root : str, optional
            Base directory containing the grid. Defaults to :data:`DEFAULT_GRID_ROOT`.

        Returns
        -------
        str
            The full path to the PRIOR_INFO file.
        """
        stem = self._grid_stem(method, model, dataset, grid=grid, root=root)
        return f"{stem}/{dataset}_polychord_raw/{dataset}.prior_info"

    def upload_prior_info(
        self, deposit_id, method, model, dataset, loc="hpc", grid="new_grid", root=None
    ):
        """Upload the PRIOR_INFO file to a Zenodo deposit.

        Parameters
        ----------
        deposit_id : int
            The deposit ID of the deposit.
        method : str
            The sampling method ('ns' for Nested Sampling or 'mcmc' for Metropolis-
            Hastings).
        model : str
            The cosmological model name.
        dataset : str
            The dataset name.
        loc : str
            The location of the samples ('hpc' for the HPC or 'local' for the local
            computer).
        grid : str, optional
            Which grid the chains live in. 'grid' for datasets in paper 2511.04661;
            'new_grid' for datasets in paper 2603.05472. Defaults to 'new_grid'.

        Returns
        -------
        Response
            The requests response object after uploading.
        """
        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        r = requests.get(deposit_url)
        r.raise_for_status()
        bucket_url = r.json().get("links", {}).get("bucket")
        params = {"access_token": self.ACCESS_TOKEN}

        filename = self.get_filename(method, model, dataset, filestype="prior_info")
        prior_info_file_path = self.get_prior_info_path(
            method, model, dataset, loc, grid=grid, root=root
        )
        with open(prior_info_file_path, "rb") as fp:
            r = requests.put(f"{bucket_url}/{filename}", data=fp, params=params)
            r.raise_for_status()
            if r.status_code == 201:
                print(
                    f"Uploaded {filename} to Zenodo deposit {deposit_id} successfully"
                )
            else:
                print(f"Error uploading {filename} to {deposit_id}:", r.status_code)

        return r

    def get_deposit_ids_by_title(self, title, size=25):
        """Search and retrieve deposit IDs that match a given title from Zenodo.

        Can search for both published and unpublished deposits.

        Parameters
        ----------
        title : str
            The deposit title to search for.
        size : int, optional
            Page size for the Zenodo deposit listing endpoint. Pagination is followed
            automatically via the response's `next` link, so the total number of results
            is not limited by this value. Zenodo's deposit API rejects size > 25 with a
            400 validation error, so the default is 25.

        Returns
        -------
        dict
            A dictionary with two keys 'published' and 'unpublished' containing lists of
            published and unpublished deposit IDs respectively.
        """
        deposit_ids = {"published": [], "unpublished": []}
        page = 1

        try:
            while True:
                params = {
                    "q": f'title:"{title}"',
                    "all_versions": True,
                    "status": "all",
                    "access_token": self.ACCESS_TOKEN,
                    "size": size,
                    "page": page,
                }
                r = requests.get(self.base_url, params=params)
                r.raise_for_status()
                response_data = r.json()

                # Normalise response shape: both list and {"hits": {"hits": [...]}}
                # dicts have been observed on Zenodo's deposit endpoint.
                if isinstance(response_data, list):
                    items = response_data
                elif isinstance(response_data, dict):
                    items = response_data.get("hits", {}).get("hits", [])
                else:
                    print("Unexpected response structure.")
                    break

                if not items:
                    break  # empty page = no more results

                for record in items:
                    deposit_id = record.get("id")
                    is_published = record.get("submitted", False)
                    if deposit_id:
                        if is_published:
                            deposit_ids["published"].append(deposit_id)
                        else:
                            deposit_ids["unpublished"].append(deposit_id)

                if len(items) < size:
                    break  # partial page = last page

                page += 1

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching deposit IDs: {e}")

        # Print published and unpublished deposit IDs
        print(f"Published deposit IDs: {deposit_ids['published']}")
        print(f"Unpublished deposit IDs: {deposit_ids['unpublished']}")

        return deposit_ids

    def delete_unpublished_deposit_by_id(self, deposit_ids):
        """Delete unpublished deposits by ID, after checking each one exists.

        Parameters
        ----------
        deposit_ids : int or list
            A single deposit ID (int) or a list of deposit IDs to delete.

        Returns
        -------
        list
            A list of dictionaries, each containing the deposit ID and the status of the
            operation.
        """
        if isinstance(deposit_ids, int):
            deposit_ids = [deposit_ids]

        if not deposit_ids:
            print("No existing deposits match the given description.")
            return []

        results = []

        for deposit_id in deposit_ids:
            try:
                # Check if the deposit exists
                check_url = f"{self.base_url}/{deposit_id}"
                check_response = requests.get(
                    check_url, params={"access_token": self.ACCESS_TOKEN}
                )

                if check_response.status_code == 404:
                    results.append({"deposit_id": deposit_id, "status": "Not Found"})
                    continue
                elif check_response.status_code != 200:
                    results.append(
                        {
                            "deposit_id": deposit_id,
                            "status": f"Check Failed ({check_response.status_code})",
                        }
                    )
                    continue

                # Attempt to delete the deposit
                delete_url = f"{self.base_url}/{deposit_id}"
                delete_response = requests.delete(
                    delete_url, params={"access_token": self.ACCESS_TOKEN}
                )

                if delete_response.status_code == 204:
                    results.append({"deposit_id": deposit_id, "status": "Deleted"})
                else:
                    results.append(
                        {
                            "deposit_id": deposit_id,
                            "status": f"Delete Failed ({delete_response.status_code})",
                        }
                    )
            except requests.exceptions.RequestException as e:
                print(
                    f"An error occurred while processing deposit ID {deposit_id}: {e}"
                )
                results.append({"deposit_id": deposit_id, "status": "Error"})

        return results

    def get_metadata(self, deposit_id):
        """Retrieve metadata for an existing deposit, given the deposit ID.

        Parameters
        ----------
        deposit_id : int
            The deposit ID of the deposit.

        Returns
        -------
        dict or None: The metadata dictionary if successful, otherwise None.
        """
        metadata_url = f"{self.base_url}/{deposit_id}"
        try:
            response = requests.get(
                metadata_url, params={"access_token": self.ACCESS_TOKEN}
            )
            response.raise_for_status()
            deposit_data = response.json()
            return deposit_data.get("metadata", {})
        except requests.exceptions.HTTPError as http_err:
            print(
                f"Failed to fetch metadata for deposit ID {deposit_id}. "
                f"Error: {http_err}"
            )
            return None

    def publish(self, deposit_id, metadata):
        """Publish a deposit on Zenodo with the provided metadata.

        Parameters
        ----------
        deposit_id : int
            The deposit ID of the deposit.
        metadata : dict
            The metadata for the deposit.

        Returns
        -------
        bool
            True if the deposit was published successfully, False otherwise.
        """
        publish_url = f"{self.base_url}/{deposit_id}/actions/publish"

        try:
            response = requests.post(
                publish_url, params={"access_token": self.ACCESS_TOKEN}, json=metadata
            )
            response.raise_for_status()

            result = response.json()
            title = metadata.get("title", "Unknown Title")
            concept_doi = result.get("conceptdoi", "N/A")

            print(
                f"{title} (Deposit ID: {deposit_id}) is published "
                f"successfully. Concept DOI: {concept_doi}"
            )
            return True

        except requests.exceptions.HTTPError as http_err:
            error_code = response.status_code if "response" in locals() else "N/A"
            title = metadata.get("title", "Unknown Title")
            print(
                f"{title} (Deposit ID: {deposit_id}) publishing failed. "
                f"Error code: {error_code}"
            )
            print(f"Error details: {http_err}")
            return False
        except Exception as err:
            print(f"An unexpected error occurred: {err}")
            return False

    def newversion(self, deposit_id):
        """Create a new version of a published deposit so it can be edited.

        Each new version is assigned a new deposit ID.

        Parameters
        ----------
        deposit_id : int
            The deposit ID of the published deposit.

        Returns
        -------
        int or None: The new deposit ID of the new version if successful; otherwise,
        None.
        """
        try:
            # Retrieve deposit information
            deposit_url = (
                f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
            )
            r = requests.get(deposit_url)
            r.raise_for_status()
            deposit_data = r.json()

            if deposit_data.get("state") == "done":
                print("Deposit is published. Proceeding to create a new version.")

                # Create a new version
                new_version_response = requests.post(
                    f"{self.base_url}/{deposit_id}/actions/newversion",
                    params={"access_token": self.ACCESS_TOKEN},
                )
                new_version_response.raise_for_status()
                new_version_data = new_version_response.json()

                print(f"New version created. New deposit ID: {new_version_data['id']}")
                return new_version_data["id"]
            else:
                print(
                    "The deposit is not yet published or cannot be unlocked directly."
                )
                return None

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_concept_doi(self, deposit_id):
        """Retrieve the concept DOI for a published deposit.

        Concept DOI is only available for previously published deposits, and it remains
        unchanged regardless of different versions, which have different deposit IDs.

        Parameters
        ----------
        deposit_id : int
            The deposit ID of the deposit.

        Returns
        -------
        str or None: The concept DOI if available; otherwise, None.
        """
        deposit_url = f"{self.base_url}/{deposit_id}?access_token={self.ACCESS_TOKEN}"
        response = requests.get(deposit_url)
        response.raise_for_status()

        deposit = response.json()
        concept_doi = deposit.get("conceptdoi")

        if concept_doi:
            print(f"Concept DOI: {concept_doi}")
            return concept_doi
        else:
            print("Concept DOI not found. Ensure the deposit is published.")
            return None


class DatabaseExplorer(Database):
    """A class for exploring and downloading deposits from Zenodo.

    Inherits from Database to utilise filename generation.
    """

    def __init__(self, sandbox=False, base_url=None, records_url=None):
        """Initialise the DatabaseExplorer instance.

        Parameters
        ----------
        sandbox : bool, optional
            Whether to use the Zenodo sandbox environment. Defaults to False.
        base_url : str, optional
            The base URL for deposit endpoints.
        records_url : str, optional
            The URL for records endpoints.
        """
        if sandbox:
            self.base_url = "https://sandbox.zenodo.org/api/deposit/depositions"
        else:
            self.base_url = "https://zenodo.org/api/deposit/depositions"
        super().__init__(sandbox)

    def download(self, deposit_id, filename):
        """Download a specific file from a deposit, given the deposit ID and filename.

        Parameters
        ----------
        deposit_id : int
            The deposit ID of the deposit.
        filename : str
            The name of the file to download.

        Returns
        -------
        DataFrame, dict, or None: The downloaded data depending on the file type; a
        DataFrame for NS and MCMC chains, a dict for info and prior_info.
        """
        deposit_url = f"{self.records_url}/{deposit_id}"
        r = requests.get(deposit_url)
        r.raise_for_status()

        if r.status_code == 200:
            deposit_info = r.json()
            files = deposit_info["files"]

            for file in files:
                if file["key"] == filename:
                    download_url = file["links"]["self"]
                    file_r = requests.get(download_url)
                    file_r.raise_for_status()

                    if file_r.status_code == 200:
                        if filename.endswith(".csv"):
                            data = read_csv(BytesIO(file_r.content))
                            print(f"{filename} file loaded successfully.")
                        elif filename.endswith((".yaml", ".yml")):
                            data = yaml.safe_load(file_r.content.decode("utf-8"))
                            print(f"{filename} file loaded successfully.")
                        elif filename.endswith(".prior_info"):
                            try:
                                raw_data = file_r.content.decode("utf-8-sig").strip()
                                if raw_data:
                                    data = {}
                                    for line in raw_data.splitlines():
                                        key, value = line.split("=")
                                        data[key.strip()] = int(value.strip())
                                    print(f"{filename} file loaded successfully.")
                                else:
                                    print(
                                        f"Warning: {filename} PRIOR_INFO file is empty."
                                    )
                                    data = {}
                            except (UnicodeDecodeError, ValueError) as e:
                                print(f"Error processing {filename}: {e}")
                                data = None
                        else:
                            print(f"Unsupported file type: {filename}")
                            data = None
                    else:
                        print(f"Error downloading {filename}:", file_r.status_code)
                        data = None
                    return data
        else:
            print("Error retrieving deposit metadata:", r.status_code, r.json())

    def download_samples(self, method, model, dataset):
        """Download samples for a given method, model, and dataset.

        Parameters
        ----------
        method : str
            The sampling method ('ns' for Nested Sampling or 'mcmc' for Metropolis-
            Hastings).
        model : str
            The cosmological model name.
        dataset : str
            The dataset name.

        Returns
        -------
        DataFrame or None: The downloaded sample data.
        """
        filename = self.get_filename(method, model, dataset, "samples")
        deposit_id = self.get_deposit_id_by_title_users(model, dataset)
        return self.download(deposit_id, filename)

    def download_info(self, method, model, dataset):
        """Download the YAML info file for a given method, model, and dataset.

        Parameters
        ----------
        method : str
            The sampling method ('ns' for Nested Sampling or 'mcmc' for Metropolis-
            Hastings).
        model : str
            The cosmological model name.
        dataset : str
            The dataset name..

        Returns
        -------
        dict or None: The contents of the info file.
        """
        filename = self.get_filename(method, model, dataset, "info")
        deposit_id = self.get_deposit_id_by_title_users(model, dataset)
        return self.download(deposit_id, filename)

    def download_prior_info(self, model, dataset, method="ns"):
        """Download the PRIOR_INFO file for a given method, model, and dataset.

        Parameters
        ----------
        model : str
            The cosmological model name.
        dataset : str
            The dataset name.
        method : str
            'ns' for Nested Sampling by default.

        Returns
        -------
        dict or None: A dictionary containing the value of 'nprior' and 'ndiscarded'.
        """
        filename = self.get_filename(method, model, dataset, "prior_info")
        deposit_id = self.get_deposit_id_by_title_users(model, dataset)
        return self.download(deposit_id, filename)

    def get_deposit_id_by_title_users(self, model, dataset):
        """Search for a single deposit by title without requiring an access token.

        Parameters
        ----------
        model : str
            The cosmological model name.
        dataset : str
            The dataset name.

        Returns
        -------
        str or None: The deposit ID of the matching result, or None if not found.
        """
        params = {
            "q": f'title:"unimpeded: {model} {dataset}"',
            "size": 1,
        }

        try:
            response = requests.get(self.records_url, params=params)
            response.raise_for_status()
            data = response.json()

            hits = data.get("hits", {}).get("hits", [])
            if hits:
                return hits[0].get("id")
            else:
                print("No deposit found with the given title.")
                return None

        except requests.RequestException as e:
            print(f"Error fetching deposit: {e}")
            return None
