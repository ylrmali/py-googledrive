import click
from pydrive.cryption import Cryption
from pydrive.drive import GCDrive
from pydrive.dbmanager import DBManager


__cls = GCDrive()
__cryption = Cryption()
__dbmanager = DBManager()

@click.group()
def main():
    pass


@main.command()
@click.option("-e", "--encrypt", is_flag=True , help="Encrypt file with GPG")
@click.option("-f", "--file", type=str, help="Specific file path")
@click.option("-d", "--database", is_flag=True, help="Database backup")
def backup(encrypt, database, file=None):
    if file:
        response = __cls.upload(file=file,
                         folder_id="13Gi_wHTYIvUppxL3iMD4GhSfVJljnEbe",
                         encrypt=encrypt)
        click.echo(response)
    if database:
        # get database backup and encrpyt that, then upload this to google drive
        backup_file = __dbmanager.backup_database()
        
        if backup_file:
            response = __cls.upload(
                        file=backup_file,
                        folder_id="13Gi_wHTYIvUppxL3iMD4GhSfVJljnEbe",
                        encrypt=encrypt
            )
            click.echo(response)
        else:
                click.echo("Encryption failed.")
    
@main.command()
@click.option("-d", "--decrypt", is_flag=True, help="Decrypt downloaded file")
@click.option("-f", "--file", type=str, help="Specific file path")
@click.option("-db", "--database", is_flag=True, help="Database backup")
def restore(decrypt, database, file_name=None):
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
    if database:
        lastest_backup = __cls.get_latest_backup() # get last database backup from google drive
        if lastest_backup:
            file_id = lastest_backup.get('id')  # get file id
            file_name = lastest_backup.get('name')  # get file name
            status, file = __cls.download(file_id=file_id)  # download file from google drive
            if status:
                decrpypt_status, decrypt_file = __cryption.decrypt_file(file=file)  # decrypt
                if decrpypt_status:
                    result = __dbmanager.restore_backup(backup_filepath=decrypt_file)
                    if result:
                        click.echo("Database restored succesfully")
                    else:
                        click.echo("Database could not restored")
            
        
        
        
        
    