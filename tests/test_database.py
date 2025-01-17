#%%
import pandas as pd
import datetime
import numpy as np
from pandas.testing import assert_frame_equal
from unimpeded.database import database
import time
import os
import pytest
import requests
#ACCESS_TOKEN = 'Kt4ZX8YhOYDO5GJQLHQInEFjK2qvf3yTMAjgjncOsmO5OiKQTb4eZaTtF9Y9'
#ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']# import ACCESS_TOKEN from Github secrets or local computer
params = {'access_token': ACCESS_TOKEN} 
#%%
#bucket_url = 'https://sandbox.zenodo.org/api/files/d8292cb1-2e9f-4c94-a253-fe1fc84dc412'

def test_upload_download():
     # Test upload function
     samples = pd.DataFrame(np.random.randn(5, 3), columns=['A', 'B', 'C'])
     filename = 'test.csv'

     db = database(ACCESS_TOKEN=ACCESS_TOKEN)
     
     #r = db.create_metadata(metadata=metadata) 
     #ID = r.json()['id']
     ID = 128545

     #db.upload(filename, samples)
     r = db.upload(filename,samples,ID)

     # Wait for the file to be uploaded
     time.sleep(10)

     # Download the file
     new_samples = db.download(ID, filename)

     # Check if the pandas data frames are equal
     assert_frame_equal(samples, new_samples[-1])
     
#%%
def test_failed_download():
    db = database(ACCESS_TOKEN=ACCESS_TOKEN)
    with pytest.raises(requests.HTTPError):
        db.download(1243,'dily')

# %%

# %%

# %%

# %%

# %%

# %%
