import gzip
import shutil
import tarfile
import os

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


def compress_folder(folder_path, tar_path):
    """
    Compresses a folder into a tar archive asynchronously.
    
    Args:
        folder_path (str): Path to the folder to compress.
        tar_path (str): Path to save the compressed tar archive.
        
    Returns:
        tuple: A tuple containing a boolean indicating success or failure and the path to the compressed tar archive.
    """
    try:
        with tarfile.open(tar_path, 'w') as tar:
            tar.add(folder_path, os.path.basename(folder_path))
        return True, tar_path
    except Exception as e:
        return False, str(e)

def uncompress_folder(tar_path, extract_dir):
    """
    Uncompresses a tar archive into a directory.
    
    Args:
        tar_path (str): Path to the tar archive to uncompress.
        extract_dir (str): Directory to extract the contents into.
    """
    try:
        with tarfile.open(tar_path, 'r') as tar:
            tar.extractall(path=extract_dir)
        return True, extract_dir
    except Exception as e:
        return False, str(e)

