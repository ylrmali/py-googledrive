from django.conf import settings
from django.core.management.base import BaseCommand
from gcapi.drive import GCDrive
from gcapi.cryption import Cryption
import subprocess
import datetime
import os 

class Command(BaseCommand):
    help = "Backup database"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--encrypt',
            action='store_true',
            help='Encrypt dump file'
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
        db = settings.DATABASES['default']
        db_name = db.get('NAME')
        db_user = db.get('USER')
        
        output_dir = settings.BASE_DIR
        is_encrypt = options['encrypt']
        
        # Create a timestamp for the backup file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        
        # Define the backup file name
        backup_filename = f"default_{db_name}_{timestamp}.dump"

        # Define the full path to the backup file
        backup_filepath = os.path.join(output_dir, backup_filename)

        try:
            # Call pg_dump command to perform the backup
            cmd = f"pg_dump -U {db_user} -d {db_name} -Fc -f {backup_filepath}"
            subprocess.run(cmd, shell=True, check=True)
            
            if is_encrypt:
                status, encrypted_file = Cryption().encrypt_file(file=f"{backup_filepath}")
                self.__success_output("<------ Dump file successfully encrypted ------>") if status \
                else self.__error_output("<------ Dump file could not be encrypted ------>")
                backup_filepath = encrypted_file
            
            response = GCDrive().upload(file=backup_filepath)
            
            # Remove backup dump files 
            os.remove(backup_filepath)
            
            self.__success_output(text=response)    

        except Exception as e:
            self.__error_output(f"Backup failed: {e}")
