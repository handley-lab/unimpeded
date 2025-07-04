from unimpeded.database import DatabaseExplorer

db = DatabaseExplorer()
samples = db.download_samples('ns','klcdm','planck_2018_plik')
#samples = db.download_samples('ns','klcdm','planck_2018_lensing')

samples
