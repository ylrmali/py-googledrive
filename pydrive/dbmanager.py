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
        self._dbname = None
        self._output_dir = None
        
    def get_django_setting(self, setting_name, default=None):
        """
        Function to retrieve a Django setting by name.
        If the setting doesn't exist, it returns the default value.
        """
        from django.conf import settings
        return getattr(settings, setting_name, default)
        
    def is_django_installed(self):
        try:
            import django
            django.setup()
            return True
        except ImportError:
            return False
        
    def __get_db_name(self):
        return self.get_django_setting('DATABASES')['default']['NAME']
    
    def __get_output_dir(self):
        return self.get_django_setting('BACKUP_DIR')
        
        
    def backup_database(self, 
                        database_name: str=None, 
                        output_dir: str=None
        ):
        if not self.is_django_installed():
            print("Django is not installed.")
            return None
        
        if not self._dbname:
            self._dbname = self.__get_db_name()
        if not self._output_dir:
            self._output_dir = self.__get_output_dir()
       
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
            from django.core.management import call_command
            call_command('dumpdata', f'--output={backup_filepath}')
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
            from django.core.management import call_command
            call_command('loaddata', backup_filepath)
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
