from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
from gcapi.cryption import Cryption
from gcapi.drive import GCDrive
from gcapi.compress import compress_folder
import os 

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
            
    
    def handle(self, *args, **options):
        _drive = GCDrive() 
        _cryption = Cryption()
        media_root = settings.MEDIA_ROOT
        is_encrypt = options['encrypt']
        is_compress = options['compress']
        temp_files = []
        
        
        if is_compress:
            # compress media folder
            c_status, c_file = compress_folder(
                folder_path=media_root, 
                tar_path='media.tar'
            )
            if not c_status:
                self.__error_output("Fail: Compress error!")
            temp_files.append(c_file)  # append zipped file to temp_file list
            media_root = c_file  # change media root as zipped file
        
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
