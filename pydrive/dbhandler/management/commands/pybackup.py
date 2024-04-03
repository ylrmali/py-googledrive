from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.core.management import call_command
from pydrive.drive import GCDrive
from pydrive.cryption import Cryption
from django.conf import settings
import datetime
import os 

class Command(BaseCommand):
    help = "Backup database"
    
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--encrypt',
            action='store_true',
            help='Encrypt dump file'
        )
    
    def handle(self, *args, **options):
        database_name = settings.DATABASES['default']['NAME'] 
        output_dir = settings.BASE_DIR
        is_encrypt = options['encrypt']
        
        # Create a timestamp for the backup file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        
        # Define the backup file name
        backup_filename = f"default_backup_{timestamp}.dump"

        # Define the full path to the backup file
        backup_filepath = os.path.join(output_dir, backup_filename)

        try:
            # Call Django management command to perform the backup
            
            call_command('dumpdata', f'--output={backup_filepath}')
            
            status, encrypted_file = Cryption().encrypt_file(file=f"{backup_filepath}")
            self.stdout.write(self.style.ERROR(str(status)))
            
            # encrypted_path = os.path.join(output_dir, encrypted_file)
            print(status, encrypted_file)
            
            response = GCDrive().upload(
                        file=encrypted_file,
                        folder_id="13Gi_wHTYIvUppxL3iMD4GhSfVJljnEbe",
                        encrypt=False
            )
            if response:
                os.remove(backup_filepath)
                os.remove(encrypted_file)
            else:
                os.remove(backup_filepath)
            
            self.stdout.write(self.style.SUCCESS(response))
        except Exception as e:
            print(f"Backup failed: {e}")
            return False