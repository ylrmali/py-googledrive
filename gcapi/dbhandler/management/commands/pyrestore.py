from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
from gcapi.cryption import Cryption
from gcapi.drive import GCDrive
import subprocess
import os 

class Command(BaseCommand):
    help = "Restore database"
    
    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '--decrypt',
            action='store_true',
            help='Decrypt database dump file'
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
        db_name = settings.DATABASES['default']['NAME'] 
        is_decrypt = options['decrypt']
        
        # Get the latest backup file from Google Drive
        latest_backup = _drive.get_latest_backup(db_name=db_name)
        file_id = latest_backup.get('id')
        file_name = latest_backup.get('name')
        # Download the backup file
        download_status, file = _drive.download(file_id=file_id,
                                                file_name=file_name)
        if not download_status:
            self.__error_output("<------ Fail: Downloading issue. Check credentials.json! ------->")
            return
        
        if is_decrypt:
            # Decrypt the downloaded file if requested
            status, decrypted_file = Cryption().decrypt_file(file=file)
            if not status:
                os.remove(file)
                self.__error_output("<------ Fail: Decryption issue. Check credentials.json! ------->")
                return

            # If decryption process is successful, use the decrypted file
            os.remove(file)  # Remove the original downloaded file
            file = decrypted_file
        
        try:
            # Perform the restore using pg_restore command
            cmd = f"pg_restore --clean --dbname={db_name} {file}"
            subprocess.run(cmd, shell=True, check=True)
            os.remove(file)  # remove file
            self.__success_output("Success: Database data's successfully loaded from backup file")

        except Exception as e:
            self.__error_output(f"Restore failed: {e}")
