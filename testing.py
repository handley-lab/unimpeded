import requests
import os

r = requests.get("https://zenodo.org/api/deposit/depositions")
r.status_code
r.json()


# Everything
ACCESS_TOKEN = "0YGEh7H7AR5cqwQ6O84B9iXG6dte0SPBuzI71FDws7eHNmbVsC4M3qiqD0b2 "


class Zenodo(object):
    base_url = "https://zenodo.org/api"

    def __init__(self, access_token):
        self.ACCESS_TOKEN = ACCESS_TOKEN

    @property
    def deposit_url(self):
        return os.path.join(self.base_url, "deposit/depositions")

    @property
    def params(self):
        return {"access_token": self.ACCESS_TOKEN}

    def get(self):
        """Get the a list of uploaded records."""
        r = requests.get(self.deposit_url, params=self.params)
        if r.status_code != 200:
            raise Exception("Error: {}".format(r.status_code), r)
        return r

    def post(self, title, description, json, upload_type="dataset", **kwargs):
        """Create a zenodo record."""
        metadata = {
            "title": title,
            "description": description,
            "upload_type": upload_type,
        }
        metadata.update(kwargs)
        json = {"metadata": metadata}
        r = requests.post(self.deposit_url, params=self.params, json=json)
        if r.status_code != 201:
            raise Exception("Error: {}".format(r.status_code), r)

    def delete(self, record_id):
        """Delete a record."""
        url = os.path.join(self.deposit_url, str(record_id))
        r = requests.delete(url, params=self.params)
        if r.status_code != 204:
            raise Exception("Error: {}".format(r.status_code), r)
        return r


class SandboxZenodo(Zenodo):
    base_url = "https://sandbox.zenodo.org/api"


zenodo = SandboxZenodo(ACCESS_TOKEN)

# Sandbox everything
ACCESS_TOKEN = "BxxUGkBsmoiYXoHqW8QQmWqfoz5FczxWVg6lmHVf4cjOCUYYtX6CA97w2kQf"
zenodo = SandboxZenodo(ACCESS_TOKEN)

zenodo.post(title="My title", description="Test description", json={})

for i in zenodo.get().json():
    zenodo.delete(i["record_id"])

zenodo.delete(zenodo.get().json()[0]["record_id"])
len(zenodo.get().json())

zenodo.base_url

r = requests.get(
    "https://sandbox.zenodo.org/api/deposit/depositions",
    params={"access_token": ACCESS_TOKEN},
)

params = {"access_token": ACCESS_TOKEN}
r = requests.post(
    "https://sandbox.zenodo.org/api/deposit/depositions", params=params, json={}
)
r.status_code
r.json()["record_id"]
