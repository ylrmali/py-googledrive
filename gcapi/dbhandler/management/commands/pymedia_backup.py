from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
from gcapi.cryption import Cryption
from gcapi.drive import GCDrive
from gcapi.compress import compress_folder
import os 
import tarfile
import datetime

class Command(BaseCommand):
    help = "Restore database"

    
    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '--encrypt',
            action='store_true',
            help='Encrypt media folder'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help="Compress media folder"
        )   
        
    def __success_output(self, text):
        """
        Success output
        """
        return self.stdout.write(self.style.SUCCESS(str(text)))
    
    def __error_output(self, text):
        """
        Success output
        """
        return self.stdout.write(self.style.ERROR(str(text)))
    
    def __remove_temp(self, temp_list: list):
        """
        Remove temprary used files
        """
        for file in temp_list:
            os.remove(file)
            
    
    def _create_media_tar(media_folder: str):
        # Create a timestamp for the media folder
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        tarname = f'media_{timestamp}.tar.gz'
        
        try:
            # Create a tar file
            with tarfile.open(tarname, 'w:gz') as tar:
                # Walk through the media folder and add each file to the tar archive
                for root, dirs, files in os.walk(media_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Add the file to the tar archive with the relative path
                        tar.add(file_path, arcname=os.path.relpath(file_path, media_folder))
            return True, tarname
        except Exception as exc:
            return False, exc
    
    def handle(self, *args, **options):
        _drive = GCDrive() 
        _cryption = Cryption()
        media_root = settings.MEDIA_ROOT
        is_encrypt = options['encrypt']
        is_compress = options['compress']
        temp_files = []
        
        c_status, c_output =  self._create_media_tar(media_root=media_root)
        if c_status:
            temp_files.append(c_output)
            media_root = c_output
        else:
            self.__remove_temp(temp_files)
            return self.__error_output(f"Fail: Compress error!: {c_output}")
        
        if is_encrypt:
            # encrypt media.zip folder
            status, encrypted_file = _cryption.encrypt_file(file=media_root)

            if not status:
                self.__error_output("Fail: Encryption error!. Check credentials.json !")
            temp_files.append(encrypted_file)
            media_root = encrypted_file
            
        # send to drive
        
        try:
            response = _drive.upload(file=media_root)
            if response:
                self.__success_output(f"Success: Media backup successfully upload to Google Drive\n Message: {response}")
            self.__remove_temp(temp_files)

        except Exception as e:
            self.__error_output(f"Media backup failed: {e}")
