"""
Author: 
    Ali Yıldırım <ali.yildirim@tarsierteknoloji.com>

Backup handler with using Google Drive Api

This class provide get, list, create, delete files.
    - get()     -> Get specific file details
    - list()    -> List all file in your drive
    - create()  -> Create new file to your drive
    - delete()  -> Delete your specific file in your drive
    - bulk_delete() -> Delete multiple file in your drive
    - execute_credentials() -> Set credentials and service
    
Sources:
    resources files -> https://developers.google.com/drive/api/reference/rest/v3/files?hl=en 
"""
import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from pydrive.cryption import Cryption
from pydrive.dbmanager import DBManager

BACKUP_FOLDER = os.environ.get('BACKUP_FOLDER','./backups/')
CREDENTIALS_PATH = os.environ.get('CREDENTIALS_PATH', 'credentials.json')
PAGE_LIST_SIZE = os.environ.get('PAGE_LIST_SIZE', 10)

class GCDrive:
    def __init__(self) -> None:
        self.__credentials = None  
        self.__service = None
        self.cryption = Cryption()
        self.dbmanager = DBManager()
        self.execute_credentials()
    
    def set_credentials(self, cred_path: str):
        self.__credentials = Credentials.from_service_account_file(cred_path)
        return self
    
    def get_credentials(self):
        return self.__credentials
    
    def set_service(self):
        self.__service = build('drive', 'v3', 
                               credentials=self.get_credentials())
        return self
    
    def get_service(self):
        return self.__service
    
    def execute_credentials(self) -> None:
        """
        Set credentials and service
        """
        self.set_credentials(cred_path=CREDENTIALS_PATH)
        self.set_service()
        return self
    
    def get(self, 
            file_id: str, 
            shared_drive: bool=None
        ) -> dict:
        """
        Get specific file or folder information
        
        Params:
            file_id:    string  ->  file id which you want to see detail of file
            shared_drive:   boolean ->  support all drives. Include shared drives 
        
        Return:
            File: id, name, createdTime, mimeType, kind, owners, size
        """
        service = self.get_service()
        result = service.files()\
            .get(fileId=file_id,
                    supportsAllDrives=shared_drive,
                    fields='id, name, createdTime, mimeType, kind, owners, size')\
            .execute()
        return result
    
    def get_by_name(self, 
                file_name: str, 
                shared_drive: bool=None
        ) -> dict:
        """
        Get information about a file by its name
        
        Params:
            file_name:      str     ->  name of the file you want to retrieve information for
            shared_drive:   bool    ->  whether to include shared drives
            
        Return:
            File: id, name, createdTime, mimeType, kind, owners, size
        """
        service = self.get_service()
        
        # Search for the file by name
        query = f"name='{file_name}'"
        # if shared_drive is not None:
        #     query += f" and '{'true' if shared_drive else 'false'}' in parents"
        
        results = service.files().list(q=query,
                                    supportsAllDrives=shared_drive,
                                    fields='files(id, name, createdTime, mimeType, kind, owners, size)')\
                                .execute()
        
        # Check if any files match the query
        files = results.get('files', [])
        if files:
            # Return information for the first matching file
            return files[0]
        else:
            # If no matching file is found, return None
            return None

    
    def list(self) -> list[dict]:
        """
        List all item on Google Drive service
        
        Return:
            Dictionary object in array list
            File: id, name ,createdTime, mimeType, fullFileExtension
        """
        service = self.get_service()  # get drive service
        results = service.files()\
            .list(pageSize=PAGE_LIST_SIZE, 
                fields="nextPageToken, \
                files(id, name, createdTime, mimeType, fullFileExtension)")\
            .execute()
        items = results.get("files", [])
        return items
    
    def list_backup_files(self):
        service = self.get_service()
        db_name = 'default' # DBManager().__get_db_name()  # get database name from setting of django 
        query = f"name contains '{db_name}_backup_'"
        
        response = service.files()\
                                .list(q=query, 
                                    fields="files(id, name, createdTime)")\
                                .execute()
        return response.get('files', [])
    
    def get_latest_backup(self):
        backup_files = self.list_backup_files()
        if backup_files:
            latest_backup = max(backup_files, key=lambda x: x['createdTime'])
            return latest_backup
        else:
            return None
    
    def upload(self, 
               file: str, 
               folder_id: str=None,
               encrypt: bool=True,
        ) -> dict:
        """Create new file
        
        Upload API to google drive
        
        Params:
            file :       string -> path of file or file name
            folder_id :  string -> your specific folder on your drive
            
        Return:
            json : proivde id of uploaded file and name of file
        """
        service = self.get_service()
        if encrypt:
            status, file_name = self.cryption.encrypt_file(file=file,
                                       fingerprint='aali@gmail.com')
            file = file_name if status else ...
            
        media_body = MediaFileUpload(filename=file,
                                    mimetype='application/octet-stream')
        body = {
            'name': file,
            'parents': [folder_id] if folder_id else None
        }
        
        response = service.files().create(body=body, 
                                          media_body=media_body, 
                                          fields='id, name').execute()
        return response
        
    def delete(self, 
               file_id: str
        ) -> bool:
        """Delete specific file
        
        Delete item on your Google Drive service
        
        Params:
            file_id :   string -> item id
        
        Return:
            True/False : boolean -> Normally it return empty response, 
            but for the control it return boolean value
        """
        service = self.get_service()
        response = service.files().delete(fileId=file_id).execute()
        return True if response == "" else False 
    
    def bulk_delete(self,
                    file_list: list
        ) -> bool:
        """Multiple delete file
        
        Allow to delete more than one file on your google drive
        
        Params:
            file_list :     list[string] -> item id as a list
            
        Return:
            True/False : boolean -> Normally it return empty response, 
            but for the control it return boolean value
        """
        service = self.get_service()
        result = False
        for file in file_list:
            response = service.files().delete(fileId=file).execute()
            if response == "":
                result = True
            else:
                raise ValueError('Could not delete file, it my cause of id')
        return result        

    def download(self,
               file_id: str
        ):
        """
        Download specific file on your Google Drive as byte
        
        Params:
            file_id:    string -> item id
            
        Return:
            status:     boolean -> download proccess status
        """
        service = self.get_service()
        request = service.files().get_media(fileId=file_id)
        with open(f'{BACKUP_FOLDER}{file_id}', 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            return done, f"{BACKUP_FOLDER}{file_id}"
        
