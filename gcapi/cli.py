from gcapi.cryption import Cryption
from gcapi.drive import GCDrive
import click
import os


__cls = GCDrive()
__cryption = Cryption()

FOLDER_ID = os.environ.get('GCAPI_FOLDER_ID', None)

@click.group()
def main():
    pass


@main.command()
@click.option("-e", "--encrypt", is_flag=True , help="Encrypt file with GPG")
@click.option("-f", "--file", type=str, help="Specific file path")
def upload(encrypt, file=None):
    if file:
        if encrypt:
            status, encrypt_file = __cryption.encrypt_file(
                file=file
            )
            return ... if status else click.echo("Fail: Encryption error!")
        
        response = __cls.upload(
            file=encrypt_file if status else file,
            folder_id=FOLDER_ID)
        
        click.echo(response)
    
@main.command()
@click.option("-d", "--decrypt", is_flag=True, help="Decrypt downloaded file")
@click.option("-f", "--file", type=str, help="File name")
def download(decrypt, file_name=None):
    if file_name:
        # get file id according to file name from google drive
        file_id = __cls.get_by_name(
            file_name=file_name).get('id')
        
        # download file
        status, file = __cls.download(file_id=file_id)
        if status:
            if decrypt:
                decrypt_status, decrypt_file = __cryption.decrypt_file(file=file)
                # remove .gpg file if decrypt proccess success
                os.remove(file) if decrypt_status else ...
                
            click.echo(f"File save to {decrypt_file if decrypt else file} path")
        else:
            click.echo("There is a problem while downloding file from google drive")
             