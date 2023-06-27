import requests
import os
import http
import json


class ZenodoBase(object):
    def __init__(self, access_token, sandbox=False):
        self.ACCESS_TOKEN = ACCESS_TOKEN
        if sandbox:
            self.base_url = "https://sandbox.zenodo.org/api"
        else:
            self.base_url = "https://zenodo.org/api"

    def params(self, **kwargs):
        params = {'access_token': self.ACCESS_TOKEN}
        params.update(kwargs)
        return params

    def list(self, **kwargs):
        """Get the a list of uploaded records."""
        r = requests.get(self.url(), params=self.params(**kwargs))
        if r.status_code != http.HTTPStatus.OK:
            raise Exception(r.json())
        return r.json()

    def retrieve(self, record_id):
        """Retrieve a record."""
        r = requests.get(self.url(record_id), params=self.params())
        if r.status_code != http.HTTPStatus.OK:
            raise Exception(r.json())
        return r.json()

    def delete(self, record_id):
        """Delete a record."""
        r = requests.delete(self.url(record_id), params=self.params())
        if r.status_code != http.HTTPStatus.NO_CONTENT:
            raise Exception(r.json())

    def url(self, record_id=None):
        if record_id is not None:
            return os.path.join(self.base_url, str(record_id))
        else:
            return self.base_url


class ZenodoDepositions(ZenodoBase):
    def __init__(self, access_token, sandbox=False):
        super().__init__(access_token, sandbox=sandbox)
        self.base_url = os.path.join(self.base_url, "deposit/depositions")

    def create(self, title, description, upload_type="dataset", **kwargs):
        return self.update(None, title, description, upload_type="dataset", **kwargs)

    def update(self, record_id, title, description, upload_type="dataset", **kwargs): 
        metadata = {"title": title,
                    "description": description,
                    "upload_type": upload_type}
        metadata.update(kwargs)
        json = {"metadata": metadata}
        r = requests.post(self.url(record_id), params=self.params(), json=json)
        if r.status_code != http.HTTPStatus.CREATED:
            raise Exception(r.json())
        return r.json()


class ZenodoDepositionFiles(ZenodoBase):
    def __init__(self, record_id, access_token, sandbox=False):
        super().__init__(access_token, sandbox=sandbox)
        self.base_url = os.path.join(self.base_url, "deposit/depositions", str(record_id), "files")

    def create(self, name, file):
        """Create a file for a record."""
        data = {"name": name}
        files = {'file': file}
        r = requests.post(self.url(), params=self.params(), data=data, files=files)
        if r.status_code != http.HTTPStatus.CREATED:
            raise Exception(r.json())
        return r.json()

    def sort(self, id_order):
        """Sort the files for a record."""
        data = json.dumps([{"id": i} for i in id_order])
        r = requests.put(self.url(), params=self.params(), data=data)
        if r.status_code != http.HTTPStatus.OK:
            raise Exception(r.json())
        return r.json()

    def update(self, file_id, name):
        """Update a file name for a record."""
        data = {"name": name}
        r = requests.put(self.url(file_id), params=self.params(), data=data)
        if r.status_code != http.HTTPStatus.OK:
            raise Exception(r.json())
        return r.json()


class ZenodoDepositionActions(ZenodoBase):
    def __init__(self, record_id, access_token, sandbox=False):
        super().__init__(access_token, sandbox=sandbox)
        self.base_url = os.path.join(self.base_url, "deposit/depositions", str(record_id), "actions")

    def publish(self):
        """Publish a record."""
        r = requests.post(self.url("publish"), params=self.params())
        if r.status_code != http.HTTPStatus.ACCEPTED:
            raise Exception(r.json())
        return r.json()

    def edit(self):
        """Unlock a record for editing."""
        r = requests.post(self.url("edit"), params=self.params())
        if r.status_code != http.HTTPStatus.CREATED:
            raise Exception(r.json())
        return r.json()

    def discard(self):
        """Discard a record."""
        r = requests.post(self.url("discard"), params=self.params())
        if r.status_code != http.HTTPStatus.CREATED:
            raise Exception(r.json())
        return r.json()

    def newversion(self):
        """Create a new version of a record."""
        r = requests.post(self.url("newversion"), params=self.params())
        if r.status_code != http.HTTPStatus.CREATED:
            raise Exception(r.json())
        return r.json()


class ZenodoRecords(ZenodoBase):
    def __init__(self, access_token, sandbox=False):
        super().__init__(access_token, sandbox=sandbox)
        self.base_url = os.path.join(self.base_url, "records")


class ZenodoLicenses(ZenodoBase):
    def __init__(self, access_token, sandbox=False):
        super().__init__(access_token, sandbox=sandbox)
        self.base_url = os.path.join(self.base_url, "licenses")
