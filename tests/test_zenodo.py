from unimpeded.zenodo import Zenodo
import pytest
from requests.exceptions import HTTPError
import os
import datetime
import numpy as np
import requests
import time


def test_access_token():
    access_token = os.environ['ZENODO_SANDBOX_TOKEN']
    z = Zenodo(access_token)
    with pytest.raises(HTTPError, match='401 Client Error'):
        z.depositions.list()

    z = Zenodo(access_token, sandbox=True)
    r = z.depositions.list()
    assert isinstance(r, list)


def test_bad_token():
    z = Zenodo(access_token='foodbar')
    with pytest.raises(HTTPError, match='401 Client Error'):
        z.depositions.list()


def test_base_urls():
    z = Zenodo()
    assert (z.depositions.base_url ==
            'https://zenodo.org/api/deposit/depositions')
    assert z.records.base_url == 'https://zenodo.org/api/records'
    assert z.licenses.base_url == 'https://zenodo.org/api/licenses'
    assert (z.depositionactions(1234).base_url ==
            'https://zenodo.org/api/deposit/depositions/1234/actions')
    assert (z.depositionfiles(1234).base_url ==
            'https://zenodo.org/api/deposit/depositions/1234/files')

    z = Zenodo(sandbox=True)
    assert (z.depositions.base_url ==
            'https://sandbox.zenodo.org/api/deposit/depositions')
    assert z.records.base_url == 'https://sandbox.zenodo.org/api/records'
    assert z.licenses.base_url == 'https://sandbox.zenodo.org/api/licenses'
    assert (z.depositionactions(1234).base_url ==
            'https://sandbox.zenodo.org/api/deposit/depositions/1234/actions')
    assert (z.depositionfiles(1234).base_url ==
            'https://sandbox.zenodo.org/api/deposit/depositions/1234/files')


def test_depositions():
    z = Zenodo(os.environ['ZENODO_SANDBOX_TOKEN'], sandbox=True)

    dt = datetime.datetime.now()
    pr = os.environ['PR_NUMBER']
    title = "Unimpeded Test Deposition: %s" % dt
    description = f"""
    Automatically generated by the unimpeded test suite on {dt}
    as part of pull request {pr}:
    https://github.com/handley-lab/unimpeded/pull/{pr}
    """
    creators = [{"name": "Github Actions"}]

    with pytest.raises(HTTPError, match='400 Client Error'):
        r = z.depositions.create(
                title=title,
                description=description,
                creators=creators,
                upload_type='foobar'
                )

    r = z.depositions.create(
            title=title,
            description=description,
            creators=creators
            )
    time.sleep(1)

    assert r['id'] in [d['id'] for d in z.depositions.list()]
    assert z.depositions.retrieve(r['id'])

    z.depositions.delete(r['id'])
    time.sleep(1)

    assert r['id'] not in [d['id'] for d in z.depositions.list()]
    with pytest.raises(HTTPError, match='410 Client Error'):
        z.depositions.retrieve(r['id'])

    r = z.depositions.create(
            title=title,
            description=description,
            creators=creators
            )

    datafile_1 = dt.strftime('1-%Y%m%d%H%M%S%f.txt')
    data_1 = np.random.rand(10)
    np.savetxt(datafile_1, data_1)
    z.depositionfiles(r['id']).create(f'file1 on {dt}', datafile_1)
    os.remove(datafile_1)

    datafile_2 = dt.strftime('2-%Y%m%d%H%M%S%f.txt')
    data_2 = np.random.rand(10)
    np.savetxt(datafile_2, data_2)
    z.depositionfiles(r['id']).create(f'file2 on {dt}', datafile_2,
                                      new_api=False)
    os.remove(datafile_2)

    datafile_3 = dt.strftime('3-%Y%m%d%H%M%S%f.txt')
    data_3 = np.random.rand(10)
    np.savetxt(datafile_3, data_3)
    z.depositionfiles(r['id']).create(f'file3 on {dt}', datafile_3)

    f3 = z.depositionfiles(r['id']).list()[-1]
    assert f3['filename'] == f'file3 on {dt}'
    assert z.depositionfiles(r['id']).retrieve(f3['id'])
    time.sleep(1)
    z.depositionfiles(r['id']).delete(f3['id'])
    with pytest.raises(HTTPError, match='404 Client Error'):
        z.depositionfiles(r['id']).retrieve(f3['id'])
    with pytest.raises(HTTPError, match='404 Client Error'):
        z.depositionfiles(r['id']).delete(f3['id'])

    ids = [f['id'] for f in z.depositionfiles(r['id']).list()]
    with pytest.raises(HTTPError, match='404 Client Error'):
        z.depositionfiles(r['id']).delete(f3['id'])

    reversed(ids)
    z.depositionfiles(r['id']).sort(reversed(ids))
    with pytest.raises(HTTPError, match='500 Server Error'):
        z.depositionfiles(r['id']).sort(['foo', 'bar'])
    ids_reversed = [f['id'] for f in z.depositionfiles(r['id']).list()]
    assert list(reversed(ids)) == ids_reversed

    assert r['submitted'] is False
    r = z.depositionactions(r['id']).publish()
    assert r['submitted'] is True

    with pytest.raises(HTTPError, match='403 Client Error'):
        r = z.depositionactions(r['id']).publish()

    assert r['state'] == 'done'

    with pytest.raises(HTTPError, match='403 Client Error'):
        z.depositionfiles(r['id']).create(f'file3 on {dt}', datafile_3)

    r = z.depositionactions(r['id']).edit()
    assert r['state'] == 'inprogress'
    with pytest.raises(HTTPError, match='403 Client Error'):
        r = z.depositionactions(r['id']).edit()
    z.depositionactions(r['id']).discard()
    time.sleep(1)
    with pytest.raises(HTTPError, match='403 Client Error'):
        z.depositionactions(r['id']).discard()

    r = z.depositionactions(r['id']).newversion()
    with pytest.raises(HTTPError, match='403 Client Error'):
        r = z.depositionactions(r['id']).newversion()
    z.depositionfiles(r['id']).create(f'file3 on {dt}', datafile_3)
    os.remove(datafile_3)

    r = z.depositionactions(r['id']).publish()

    rid = r['id']
    fn = f'file1 on {dt}?download=1'.replace(' ', '%20')
    url = f'https://sandbox.zenodo.org/record/{rid}/files/{fn}'
    rr = requests.get(url)
    open(datafile_1, 'wb').write(rr.content)
    assert np.allclose(np.loadtxt(datafile_1), data_1)
    os.remove(datafile_1)

    fn = f'file2 on {dt}?download=1'.replace(' ', '_').replace(':', '')
    url = f'https://sandbox.zenodo.org/record/{rid}/files/{fn}'
    rr = requests.get(url)
    open(datafile_2, 'wb').write(rr.content)
    assert np.allclose(np.loadtxt(datafile_2), data_2)
    os.remove(datafile_2)

    fn = f'file3 on {dt}?download=1'.replace(' ', '%20')
    url = f'https://sandbox.zenodo.org/record/{rid}/files/{fn}'
    rr = requests.get(url)
    open(datafile_3, 'wb').write(rr.content)
    assert np.allclose(np.loadtxt(datafile_3), data_3)
    os.remove(datafile_3)
