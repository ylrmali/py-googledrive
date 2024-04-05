import gzip
import shutil

def compress_file(filepath: str) -> str:
    """
    Compress file with gzip.
    
    Params:
        filepath: str -> File path
        
    Return:
        zipped file path
    """
    newfile = f'{filepath}.gz'
    # open file which is do you want to zip
    with open(filepath, 'rb') as f_in:
        # open new file with gzip
        # and write old datas to here
        with gzip.open(newfile, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            
    return newfile


def uncompress_file(filepath: str) -> str:
    """
    Uncompress gzipped file with gzip.
    
    Params:
        filepath: str -> File path
        
    Return:
        unzipped file path
    """
    # open gzipped file
    with gzip.open(filepath, 'rb') as f_in:
        # remove .gz extantion
        extracted_file = filepath[:-3]
        # create new file and copy file
        with open(extracted_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return extracted_file


def compress_folder(folder_path, zip_filename):
    shutil.make_archive(zip_filename, 'zip', folder_path)
    return True

def extract_folder(zip_filename, extract_path):
    shutil.unpack_archive(zip_filename, extract_path)
    return True
