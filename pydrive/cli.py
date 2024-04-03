import click
from pydrive.cryption import Cryption
from pydrive.drive import GCDrive


__cls = GCDrive()
__cryption = Cryption()

@click.group()
def main():
    pass


@main.command()
@click.option("-e", "--encrypt", is_flag=True , help="Encrypt file with GPG")
@click.option("-f", "--file", type=str, help="Specific file path")
def backup(encrypt, file=None):
    if file:
        response = __cls.upload(file=file,
                         folder_id="13Gi_wHTYIvUppxL3iMD4GhSfVJljnEbe",
                         encrypt=encrypt)
        click.echo(response)
    
@main.command()
@click.option("-d", "--decrypt", is_flag=True, help="Decrypt downloaded file")
@click.option("-f", "--file", type=str, help="Specific file path")
def restore(decrypt, file_name=None):
    if file_name:
        # get file id according to file name from google drive
        file_id = __cls.get_by_name(
            file_name=file_name).get('id')
        
        # download file
        status, file = __cls.download(file_id=file_id)
        if status:
            click.echo(f"File save to {file} path")
        else:
            click.echo("There is a problem while downloding file from google drive")
            
        
        
        
        
    