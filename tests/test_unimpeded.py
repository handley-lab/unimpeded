from unimpeded.unimpeded import unimpeded

# These locations will be changed to Zenodo links in the future.
loc = 'local'
if loc == 'local':
    location = '/Users/ongdily/Documents/Cambridge/project2/codes/'
elif loc == 'hpc':
    location = '/home/dlo26/rds/rds-dirac-dp192-63QXlf5HuFo/dlo26/'


def test_get():
    database = unimpeded(location=location)
    samples = database.get(model='klcdm', dataset='bao.sdss_dr16', method='ns')
    return samples


samples = test_get()
