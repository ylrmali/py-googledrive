import os
import subprocess
from dotenv import load_dotenv
load_dotenv()

BACKUP_FOLDER = os.environ.get('GCAPI_BACKUP_FOLDER')
GPG_RECIPIENT = os.environ.get('GCAPI_GPG_RECIPIENT')

class Cryption:
    def encrypt_file(self, file: str, compress: bool=False):
        """Encrypt file with GPG key
        
        If there is only one GPG key, you do not have to set recipients.
        But if you have more than one GPG key, you have to set recipients.
        
        Params:
            file: str -> file path
            fingerprint: str -> recipients list. (mail)
    
        Example:
            encrypt_file(file='./test.txt', fingerprint="ali@gmail.com, jhony@gmail.com")
        
        Return:
            status: bool -> True/False
        """
        file_name = os.path.basename(file)
        output = os.path.join(BACKUP_FOLDER, f"{file_name}.gpg")
        
        # Construct the GPG command
        gpg_cmd = ["gpg"]
        
        # GPG options
        options = [
            "--encrypt",
            "--output", output,
            "--always-trust",
            "--recipient", GPG_RECIPIENT
        ]
        if compress:
            options.append("--compress-algo=zip")
        
        # add options to base gpg command
        gpg_cmd.extend(options)
        
        # add file
        gpg_cmd.append(file)
        
        # Run the GPG command using subprocess
        try:
            subprocess.run(gpg_cmd, check=True)
            return True, output
        except subprocess.CalledProcessError as e:
            print(f"Error encrypting file: {e}")
            return False, None
        
    def decrypt_file(self, file: str):
        """Decrypt an encrypted file with GPG
        
        Params:
            encrypted_file: str -> path to the encrypted file
            output_folder: str -> folder to save the decrypted file
        
        Return:
            status: bool -> True/False
            decrypted_file: str or None -> path to the decrypted file or None if decryption failed
        """
        # remove .gpg extention of file
        file_name = self.__remove_gpg_extention(
            file_name=os.path.basename(file)
        )
        
        # define output path and decrypt file
        output = os.path.join(BACKUP_FOLDER, file_name)
        
        # Construct the GPG command
        gpg_command = [
            "gpg",
            "--decrypt",
            "--always-trust",
            "--output", output,
            "--recipient", GPG_RECIPIENT,
            file
        ]
        
        # Run the GPG command using subprocess
        try:
            subprocess.run(gpg_command, check=True)
            return True, output
        except subprocess.CalledProcessError as e:
            print(f"Error decrypting file: {e}")
            return False, None
        
   
    def __remove_gpg_extention(self, file_name: str) -> str:
        """Remove .gpg extension from file name"""
        if file_name.endswith('.gpg'):
            return file_name[:-4]  # Remove the last 4 characters (".gpg")
        else:
            return file_name
        