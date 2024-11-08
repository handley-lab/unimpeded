#%%
import pandas as pd
import datetime
import numpy as np
from pandas.testing import assert_frame_equal
from unimpeded.database_2 import database
import time

ACCESS_TOKEN = 'Kt4ZX8YhOYDO5GJQLHQInEFjK2qvf3yTMAjgjncOsmO5OiKQTb4eZaTtF9Y9'
params = {'access_token': ACCESS_TOKEN}

bucket_url = 'https://sandbox.zenodo.org/api/files/d8292cb1-2e9f-4c94-a253-fe1fc84dc412'

def test_upload():
     # Test upload function
     samples = pd.DataFrame(np.random.randn(5, 3), columns=['A', 'B', 'C'])
     filename = 'test.csv'

     db = database(bucket_url=bucket_url, ACCESS_TOKEN=ACCESS_TOKEN)
     
     #r = db.create_metadata(metadata=metadata) 
     #ID = r.json()['id']
     ID = 128545

     #db.upload(filename, samples)
     r = db.upload(filename,samples)

     # Wait for the file to be uploaded
     time.sleep(1)

     # Download the file
     new_samples = db.download(ID, filename)

     # Check if the pandas data frames are equal
     assert_frame_equal(samples, new_samples[-1])