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
    
    
    def handle(self, *args, **options):
        _drive = GCDrive() 
        _cryption = Cryption()
        media_root = settings.MEDIA_ROOT
        is_encrypt = options['encrypt']
        is_compress = options['compress']
        temp_files = []
        
        
        if is_compress:
            # compress media folder
            compress_folder(
                folder_path=media_root,
                zip_filename='media'
            )
            temp_files.append(f"{media_root}.zip")
            media_root = f"{media_root}.zip"
        
        if is_encrypt:
            # encrypt media.zip folder
            status, encrypted_file = _cryption.encrypt_file(file=media_root)

            if not status:
                self.__error_output("Fail: Encryption error!. Check credentials.json !")
                return
            temp_files.append(encrypted_file)
            media_root = encrypted_file
            
        # send to drive
        
        try:
            response = _drive.upload(file=media_root)
            if response:
                for file in temp_files:
                    os.remove(file)  # remove files
                self.__success_output("Success: Database data's successfully loaded from backup file")

        except Exception as e:
            self.__error_output(f"Restore failed: {e}")
