"""
Author: 
    Ali Yıldırım <ali.yildirim@tarsierteknoloji.com>


This class provide to get database backup.
For now just work in postgresql database.
This backup handler class designed for Django Framework.
"""

import os
import datetime

class DBManager:
    def __init__(self) -> None:
        if self.is_django_installed():
            from django.core.management import call_command
            from django.conf import settings
            self._settings = settings
            self._dbname = self.__get_db_name()
            self._output_dir = self.__get_output_dir()
    
    def is_django_installed(self):
        try:
            import django
            return True
        except ImportError:
            return False
        
    def __get_db_name(self):
        return self._settings.DATABASES['default']['NAME']
    
    def __get_output_dir(self):
        return self._settings.BACKUP_DIR
        
        
    def backup_database(self, 
                        database_name: str=None, 
                        output_dir: str=None
        ):
        if not self.is_django_installed():
            print("Django is not installed.")
            return None
       
        # If database_name and output_dir are not provided, use default settings from Django settings.py
        database_name = database_name or self._dbname
        output_dir = output_dir or self._output_dir
        
        # Create a timestamp for the backup file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Define the backup file name
        backup_filename = f"{database_name}_backup_{timestamp}.dump"

        # Define the full path to the backup file
        backup_filepath = os.path.join(output_dir, backup_filename)

        try:
            # Call Django management command to perform the backup
            call_command('dumpdata', '--output', backup_filepath, f'--format=json')
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
        
    def restore_backup(self, backup_filepath: str, **kwargs):
        if not self.is_django_installed():
            print("Django is not installed.")
            return False
        
        try:
            # Call Django management command to perform the backup
            call_command('loaddata', '--format=json', backup_filepath)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
        