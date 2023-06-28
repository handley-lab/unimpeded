"""Zenodo API wrapper.

https://developers.zenodo.org/
"""
import requests
import os
import http
import json


class Zenodo(object):
    """Zenodo API wrapper.

    Parameters
    ----------
    access_token : str
        The access token for the Zenodo API.
    sandbox : bool
        Whether to use the sandbox or production API.
    """

    def __init__(self, access_token=None, sandbox=False):
        self.access_token = access_token
        self.sandbox = sandbox
        if self.sandbox:
            self.base_url = "https://sandbox.zenodo.org/api"
        else:
            self.base_url = "https://zenodo.org/api"

    def list(self, **kwargs):
        """List records."""
        r = requests.get(self._url(), params=self._params(**kwargs))
        if r.status_code != http.HTTPStatus.OK:
            r.raise_for_status()
        return r.json()

    def retrieve(self, record_id):
        """Retrieve a record."""
        r = requests.get(self._url(record_id), params=self._params())
        if r.status_code != http.HTTPStatus.OK:
            r.raise_for_status()
        return r.json()

    def delete(self, record_id):
        """Delete a record."""
        r = requests.delete(self._url(record_id), params=self._params())
        if r.status_code != http.HTTPStatus.NO_CONTENT:
            r.raise_for_status()

    @property
    def depositions(self):
        """Depositions API."""
        return ZenodoDepositions(self.access_token, self.sandbox)

    @property
    def records(self):
        """Records API."""
        return ZenodoRecords(self.access_token, self.sandbox)

    @property
    def licenses(self):
        """Licenses API."""
        return ZenodoLicenses(self.access_token, self.sandbox)

    def depositionactions(self, record_id):
        """Deposition actions API."""
        return ZenodoDepositionActions(record_id, self.access_token,
                                       self.sandbox)

    def depositionfiles(self, record_id):
        """Deposition files API."""
        return ZenodoDepositionFiles(record_id, self.access_token,
                                     self.sandbox)

    def _params(self, **kwargs):
        params = {'access_token': self.access_token}
        params.update(kwargs)
        return params

    def _url(self, record_id=None):
        if record_id is not None:
            return os.path.join(self.base_url, str(record_id))
        else:
            return self.base_url


class ZenodoDepositions(Zenodo):
    """Depositions API.

    https://developers.zenodo.org/#depositions
    """

    def __init__(self, access_token=None, sandbox=False):
        super().__init__(access_token, sandbox)
        self.base_url = os.path.join(self.base_url, "deposit/depositions")

    def create(self, title, description, upload_type="dataset", **kwargs):
        """Create a new deposition."""
        return self.update(None, title, description,
                           upload_type=upload_type, **kwargs)

    def update(self, record_id, title, description,
               upload_type="dataset", **kwargs):
        """Update a deposition."""
        metadata = {"title": title,
                    "description": description,
                    "upload_type": upload_type}
        metadata.update(kwargs)
        json = {"metadata": metadata}
        r = requests.post(self._url(record_id), params=self._params(),
                          json=json)
        if r.status_code != http.HTTPStatus.CREATED:
            r.raise_for_status()
        return r.json()


class ZenodoDepositionFiles(Zenodo):
    """Deposition files API.

    https://developers.zenodo.org/#deposition-files
    """

    def __init__(self, record_id, access_token=None, sandbox=False):
        super().__init__(access_token, sandbox)
        self.record_id = record_id
        self.base_url = os.path.join(self.base_url, "deposit/depositions",
                                     str(self.record_id), "files")

    def create(self, name, filepath, new_api=True):
        """Create a file for a record."""
        with open(filepath, "rb") as fp:
            if new_api:
                record = self.depositions.retrieve(self.record_id)
                bucket_url = os.path.join(record["links"]["bucket"], name)
                r = requests.put(bucket_url, params=self._params(), data=fp)
            else:
                data = {"name": name}
                files = {'file': fp}
                r = requests.post(self._url(), params=self._params(),
                                  data=data, files=files)
            if r.status_code != http.HTTPStatus.CREATED:
                r.raise_for_status()
            return r.json()

    def sort(self, id_order):
        """Sort the files for a record."""
        data = json.dumps([{"id": i} for i in id_order])
        r = requests.put(self._url(), params=self._params(), data=data)
        if r.status_code != http.HTTPStatus.OK:
            r.raise_for_status()
        return r.json()


class ZenodoDepositionActions(Zenodo):
    """Deposition actions API.

    https://developers.zenodo.org/#deposition-actions
    """

    def __init__(self, record_id, access_token=None, sandbox=False):
        super().__init__(access_token, sandbox)
        self.base_url = os.path.join(self.base_url, "deposit/depositions",
                                     str(record_id), "actions")

    def publish(self):
        """Publish a record."""
        r = requests.post(self._url("publish"), params=self._params())
        if r.status_code != http.HTTPStatus.ACCEPTED:
            r.raise_for_status()
        return r.json()

    def edit(self):
        """Unlock a record for editing."""
        r = requests.post(self._url("edit"), params=self._params())
        if r.status_code != http.HTTPStatus.CREATED:
            r.raise_for_status()
        return r.json()

    def discard(self):
        """Discard a record."""
        r = requests.post(self._url("discard"), params=self._params())
        if r.status_code != http.HTTPStatus.CREATED:
            r.raise_for_status()
        return r.json()

    def newversion(self):
        """Create a new version of a record."""
        r = requests.post(self._url("newversion"), params=self._params())
        if r.status_code != http.HTTPStatus.CREATED:
            r.raise_for_status()
        new_id = r.json()["links"]["latest_draft"]
        new_id = os.path.basename(new_id)
        r = ZenodoDepositions(self.access_token, self.sandbox).retrieve(new_id)
        return r


class ZenodoRecords(Zenodo):
    """Records API.

    https://developers.zenodo.org/#records
    """

    def __init__(self, access_token=None, sandbox=False):
        super().__init__(access_token, sandbox)
        self.base_url = os.path.join(self.base_url, "records")


class ZenodoLicenses(Zenodo):
    """Licenses API.

    https://developers.zenodo.org/#licenses
    """

    def __init__(self, access_token=None, sandbox=False):
        super().__init__(access_token, sandbox)
        self.base_url = os.path.join(self.base_url, "licenses")
