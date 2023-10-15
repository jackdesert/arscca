from contextlib import contextmanager
from pathlib import Path


@contextmanager
def file_based_singleton(tempdir:str):
    """
    This context manager is a singleton

    It is useful when you only want one instance of a process running
    at a time (to prevent resource overflow)

    It creates a temporary directory for the duration of the block.
    If the temporary directory already exists, it assumes that
    there is already a process running, so it raises an exception.
    """
    tempdir = Path(tempdir)

    # This will raise an exception if the directory already exists
    tempdir.mkdir()

    try:
        yield
    finally:
        # Remove the temporary directory if it exists
        try:
            tempdir.rmdir()
        except FileNotFoundError:
            pass



if __name__ == '__main__':
    """
    To test manually, run this from two different consoles
    at about the same time.

    $ python arscca/models/singleton.py some_label
    """

    import sys
    try:
        label = sys.argv[1]
    except IndexError:
        label = 'Unlabeled'

    from time import sleep
    fname_ = '/tmp/singleton-test'

    with file_based_singleton(fname_):
        print(f'{label}: Starting long task')
        sleep(5)
        print(f'{label}: Ending long task')

