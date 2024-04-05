from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
from gcapi.drive import GCDrive
from gcapi.cryption import Cryption
from gcapi.compress import extract_folder
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
        
    def __protect_old_media(self):
        """
        Protect old media folder before changing new media folder
        """
        media_root = settings.MEDIA_ROOT
        compress_folder(media_root, 'old_media')
        print("<----- media folder protected -------->")    
        return True
        
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
        is_decrypt = options['decrypt']
        temp_files = []
        
        # first protect old media folder
        is_protected = self.__protect_old_media()
        if is_protected:
            temp_files.append(f"{media_root}.zip") # protected folder
            # find latest media backup and download it
            latest_media = _drive.get_latest_media()
            media_id = latest_media.get('id')
            media_name = latest_media.get('name')
            status, media_file = _drive.download(
                file_id=media_id,
                file_name=media_name
            )
            temp_files.append(media_file)  # add new downloaded file
        
            #! every time file do not have to .zip.gpg, so after control it
            #! but for now I make it just this one.
            
            # decrypt file
            status, decrypt_file = _cryption.decrypt_file(file=media_file)
            if not status:
                self.__error_output("Fail: Decryption error! Check credentials.json!")
                return
            
            temp_files.append(decrypt_file)
            
            # extract folder to media root
            is_extract = extract_folder(
                zip_filename=decrypt_file,
                extract_path=media_root
            )
            
            if is_extract:
                for file in temp_files:
                    os.remove(file) # remove all not useful files
                self.__success_output("Success: Media data's successfully restored")
            else:
                # if there is a problem, back to old data
                extract_folder(f"{media_root}.zip",
                               extract_path=media_root)
                self.__error_output("Fail: Extract error!")
                
            
        
        
