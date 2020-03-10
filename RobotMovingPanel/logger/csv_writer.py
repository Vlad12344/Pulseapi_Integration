import os

from csv import writer

def create_empty_csv(path: str) -> None:
    with open(path, 'w'):
        pass

def file_existing_check(path: str) -> None:
    """
    """
    if os.path.exists(path):
        os.remove(path)
        create_empty_csv(path)
    else:
        create_empty_csv(path)

def append_list_as_row(file_name: str, list_of_elem: list) -> None:
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)