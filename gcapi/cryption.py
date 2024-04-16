from datetime import (
    datetime, 
    timezone
)
import os
import gnupg
import string
import random
from dotenv import load_dotenv
load_dotenv()

BACKUP_FOLDER = os.environ.get('GCAPI_BACKUP_FOLDER')
GPG_RECIPIENT = os.environ.get('GCAPI_GPG_RECIPIENT')

class Cryption:
    def __init__(self):
        self.gpg = gnupg.GPG(gnupghome=self.get_gnupg_home())
        self.gpg.encoding = 'utf-8'

    def get_gnupg_home(self):
        # Get GNUPG_HOME from environment variable or use default value
        return os.environ.get('GCAPI_GNUPG_HOME')

    def generate_rsa_key(self, 
                     name_real: str, 
                     name_email: str,
                     key_length: int=4096,
                     expire_date: str|int=0,
                     passphrase: str=None
        ) -> str:
        """Generate new RSA key pair
        
        Params:
            name_real:  str ->  Real name
            name_email: str ->  Email address of user
            key_length:   str -> RSA key length. Default 4096.
            expire_date:    str|int -> Key expire date. Default 0(never):
            
                <n> :   int -> <n> days
                <n>w:   str -> <n> weeks
                <n>m:   str -> <n> months
                <n>y:   str -> <n> years   
        """
        # Define key parameters
        key_params = {
            'key_type': "RSA",
            'key_length': key_length,
            'name_real': name_real,
            'name_email': name_email,
            'expire_date': expire_date
        }
        
        if passphrase:
            # if we have passphares add this to key params
            key_params.update({"passphrase": passphrase})
        else:
            # if we do not have any passpharase, add no protection
            key_params.update({'no_protection': True})

        # generate key input
        key_input = self.gpg.gen_key_input(**key_params)
        
        # Generate key
        key = self.gpg.gen_key(key_input)
        return key

    def list_keys(self):
        # List keys in the keyring
        keys = self.gpg.list_keys()
        return keys

    def id_generator(self, size=24, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    
    def __safe_open_w(self, path):
        """ 
        Open "path" for writing, creating any parent directories as needed.
        """
        # if the file already exists, add additional random char
        if os.path.exists(path):
            path = f"{path}_{self.id_generator(size=3)}"
        
        # create folder and file
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return open(path, 'w')
        
    def __export(self, 
                    key,
                    passpharese: str=None
        ) -> None:
        name = datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S:%f')
        file_path = f'{self.get_gnupg_home()}/export/{name}.asc'
        
        # file exporting
        ascii_armored_public_keys = self.gpg.export_keys(keyids=key)
        if passpharese:
            # if we have passpharese use it
            ascii_armored_private_keys = self.gpg.export_keys(keyids=key,
                                                          secret=True,
                                                          passphrase=passpharese)
        else:
            # if we do not have pass
            ascii_armored_private_keys = self.gpg.export_keys(keyids=key,
                                                          secret=True,
                                                          expect_passphrase=False)
        with self.__safe_open_w(file_path) as f:
            f.write(ascii_armored_public_keys)
            f.write(ascii_armored_private_keys)
        print(f"GPG key exported to {file_path}")

    def export_key(self, 
                   key_id: str|dict|list[dict]|list[str]
        ) -> None:
        """Export GPG keys
        
        Params:
            key_id: str|dict|list   -> GPG key id
        """
        if isinstance(key_id, list):
            for key in key_id:
                if isinstance(key, dict):
                   self.__export(key.get('keyid'))
                else:
                    raise TypeError("You should provide str (keyId) or dict key object to export")
        elif isinstance(key_id, dict):
            self.__export(key_id.get('keyid'))
        elif isinstance(key_id, str):
            self.__export(key_id)

    def import_keys(self, key_path: str):
        """Import GPG key from file
        
        Params:
            key_path: str -> GPG exported file path
            
        Return:
            bool: True if import successful, False otherwise
        """
        with open(key_path, 'rb') as key_file:
            key_data = key_file.read()
            
        import_result = self.gpg.import_keys(key_data)
        return import_result


    def delete_key(self, 
                   key
        ) -> bool:
        """Import GPG key from file
        
        Params:
            key:  str  -> GPG key
        
        Return:
            status: bool -> True/False
        """
        fp = key.get('fingerprint')
        result = self.gpg.delete_keys(fp, 
                                        secret=True,
                                        expect_passphrase=False)
        return True if result == 'ok' else False

    def destory_keys(self) -> bool:
        """Delete all keys in GPG list
        
        Return:
            status: bool -> True/False
        """
        keys = self.list_keys()
        status = False
        for key in keys:
            result = self.delete_key(key)
            status = True if result == 'ok' else False
        return status
    
    def encrypt_file(self, file: str):
        """Encrypt file with GPG key
        
        If there is a only one GPG key you do not have to set recipients,
        But if you have more than one GPG key you have to set recipients.
        
        Params:
            file: str -> file path
            fingerprint: str -> recipients list. (mail)
    
        Example:
            encrypt_file(file='./test.txt', fingerprint="ali@gmail.com, jhony@gmail.com")
        
        Return:
            status: bool -> True/False
        """
        with open(file, 'rb') as f:
            file_name = f"{os.path.basename(f.name)}.gpg"
            output = os.path.join(BACKUP_FOLDER, file_name)
            status = self.gpg.encrypt_file(
                fileobj_or_path=f,
                recipients=GPG_RECIPIENT,
                output=output
            )
            return status.ok, output
        
    def decrypt_file(self, file: str):
        """Decrypt file with GPG key"""

        with open(file, 'rb') as f:
            # remove .gpg extention of file
            file_name = self.__remove_gpg_extention(
                file_name=os.path.basename(f.name)
            )
            
            # define output path and decrypt file
            output = os.path.join(BACKUP_FOLDER, file_name)
            status = self.gpg.decrypt_file(
                f, 
                output=output
            )
            
        return status.ok, output
    
    def __remove_gpg_extention(self, file_name: str) -> str:
        """Remove .gpg extension from file name"""
        if file_name.endswith('.gpg'):
            return file_name[:-4]  # Remove the last 4 characters (".gpg")
        else:
            return file_name
        