<h1 style='text-align: center; '>py-googledrive</h1>


## Instalation

```bash
pip install git+https://github.com/ylrmali/py-googledrive.git
```

* PyPip installation will come!


## Configuration

* You have to provide your google drivce service credentails to use library. So you can give your `credentials.json` file path in your `.env` as `CREDENTIALS_PATH`.

* **You can download file from your drive with `GCDrive().dowload()` method, by default it save your file to `.\backups` folder. You can create `backups` folder out of your current folder or you can define a path of folder in your `.env` as `BACKUP_FOLDER`**

* Finally you can change default(10) list file size in your `.env` as `PAGE_LIST_SIZE`.

## Usage
* Import `GCDrive` class where you want to use.

    ``` python
    from gcapi.drive import GCDrive

    ...
    gcdrive = GCDrive()
    gcdrive.execute_credentials()  # setup credentials
    ...
    ```


## Methods

> `GCDrive().execute_credentials()` \
 Set google credentials and service.
You should call this method before all the other methods

> `GCDrive().list()` \
List Google Drive files

> `GCDrive().get(file_id: str, shared_drive: bool=None)` \
Get specific file with file.

> `GCDrive().upload(file: str, folder_id: str=None)` \
Upload new file to your Google Drive \
***file** : string  => your file path \
**folder_id**: string => your google drive specific folder's id (copy from end of the url)

> `GCDrive().delete(file_id: str)` \
Delete specific file 

> `GCDrive().bulk_delete(file_list: list)` \
Delete multiple file

> `GCDrive().download(file_id: str)` \
Download a specific file on your Google Drive to default folder (backups).
>
> 


     

