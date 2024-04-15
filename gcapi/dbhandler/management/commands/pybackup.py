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
    
    def __create_uri(self, 
                     user: str, 
                     password: str, 
                     host: str, 
                     port: int|str, 
                     name: str
        ) -> str:
        """
        Create postgresql connection url with user settings
        
        Params:
            username: str -> database user 
            password: str -> database user's password 
            host: str -> database host 
            port: int|str -> database port
            name: str -> database name
            
        Return:
            postgreqsl connection url
            
        Example: 
            postgresql://postgresql:password@localhost:5432/dbname
        """
        uri = 'postgresql://'
        if user and password:
            uri += f'{uri}{user}:{password}@'
        if host and port:
            uri += f'{host}:{port}'
        if name:
            uri += f'/{name}'
        return uri
        
        
    
    def handle(self, *args, **options):
        db = settings.DATABASES['default']
        db_name = db.get('NAME')
        db_user = db.get('USER')
        db_host = db.get('HOST')
        db_port = db.get('PORT')
        db_pass = db.get('PASSWORD')
        
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
            pg_url = self.__create_uri(
                user=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                name=db_name
            )
            cmd = f"pg_dump {pg_url} -Fc -f {backup_filepath}"
            subprocess.run(cmd, shell=True, check=True)
            
            if is_encrypt:
                status, encrypted_file = Cryption().encrypt_file(file=f"{backup_filepath}")
                if not status:
                    self.__error_output("<------ Dump file could not be encrypted ------>")
                
                os.remove(backup_filepath) # remove old file
                backup_filepath = encrypted_file
            
            response = GCDrive().upload(file=backup_filepath)
            
            # Remove backup dump files 
            os.remove(backup_filepath)
            
            self.__success_output(text="<------ Backup file uploaded to Google drive -------->")    

        except Exception as e:
            self.__error_output(f"Backup failed: {e}")
