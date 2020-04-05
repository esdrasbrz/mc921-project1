import os
import pytest

from glob import glob

io_path = os.path.join('tests', 'io')


def read_files(ext):
    files = []

    files_list = sorted(glob(os.path.join(os.getcwd(), io_path, '*{}'.format(ext))))

    for file_path in files_list:
        with open(file_path) as f:
            files.append(f.read())

    return files


@pytest.fixture(params=list(zip(read_files('.in'), read_files('.out'))))
def tests(request):
    return request.param

