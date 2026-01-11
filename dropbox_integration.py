import dropbox
import pandas as pd
import io

# Konfigurasi Dropbox
APP_KEY = 'vm03f7eq8mbwt2g'
APP_SECRET = 'm6t6wlnss3sru2e'
ACCESS_TOKEN = 'sl.u.AGNBt_D8sFw3O0k93ey7blxUwEgmmmOuEWuJehGJWRO_jxl42o7uIQKH7Y8SjPVWVvUQ4GewOVOKZzFOlgGfL_rEJoR5eSUdBKmGJWrwBKTUJAUA83Zj7H4Eo19AwadiITwXDUaquxf6kvUA8ICk5jVa03u5C4499uqQAqqdsIe4wqXzXxR84IuZq-tj0N1EKeLAWZdbNnwM6C5b460j5eeYR3Pt7x65KnAYAZu8ZVqlzGHFr4xIJPwkTxKZFXtveBkb4n4KZi79_ESgtgC6Q2862dt-tdeLFHQeYkFG4sJ4h7j7baiROJ4u3vojhnYhavTmpq0Mq2A9w9ib44Bl8hfolv0T5hAJXin2wVcZ2_q9J_501vy4LuYM-D0mp1rw9vKPI8QKw4GUuaxtq8lggek3UmE-9Rxgp6xEUAzQ9n8B70AF6cNdF6qjfhj9BAuNIz0rsWWTdQ_nMtHrMv2dKeoGRefZdSrAo6DavoG7fzBbyhe8ilguMw4_T7Vc-f75InXbGG_-h1ZodI1dq6nYRl4_ein8IOBHcpNqx6i3HSMonepox9YhbJgxhekBeyX3DRS8T4o0d1ydN-FMPet7L--gFltkrwy-GdrS6998w7GaMTt0oVqL0tqhgOJ3uWrarANGTUOkl69zlzMP9ZdfO6U6iPbybBMW4LtpnlNtW9jm2F6-GtEOrW0pj0ID8GCYyHoxelZwyjEnbUSB6-1xBOc44Csswv5sm-SiCfpEGRmsA8pcHOVjfwIkL2qvqt1uGA7MueTfwh95rWm-EWje7-GIoCx4nGiy6606a1J3iu-wXujbqL_SpwNHur1FLZ5Vsdr2C88Z5V88MqbMPjYnAPUQcoeCDH1S727J-lAV1YAGvTelS_mQDKVqSojyWNYVD2O4eKuzGxDHsb0Q-Bqvi6ksDzGOEHrDxYK4a7tZHYAgLU176pvF16ujNBNd6BDfFKxvtWV84lql48FBgvA7zFlxd70W7V2m508uKS0jF-rlYsKV3GerA0-3agwGEr3S0eSAV6JTCnKKh-ETAaeJcunS2oZ4JBHPM7YIgy4JsHGn7f2jyCuAGLAsKhB_71OFH0aDxFaeOGU9F3ZjwduEzHhTDpO2XTFy48w4HH4DXqY-Bed8WYHjtcGc5sb8LglH71Cg9haVKEMTjD5DgyHHaFu7D4JMcvu81KGg7li_2Nz8ecgwidGVOhdtEMSrgcroVPH-bUt7XIZBQJEPlBLQrjharR-_u-gQkaSmH74W68yEsD8HcK0wo35Q0miSULG91NhJZSqi9tHOXbsWZArz0H4wk2oxayHlRNSL8YhZ1SGvmritiDGBp9dd9yygQfDLC89VbpeCILPt-3e1fK2mM0rwfIA1yEgKSLJPKWQIeBaNeVS6kuRUfIHZWjLY09P4izQYqvPcVwMtatjxwE-oZ15Brp88Qpt5c3JljU6pLyvo5w'

def get_dropbox_client():
    """Membuat koneksi ke Dropbox."""
    try:
        dbx = dropbox.Dropbox(ACCESS_TOKEN)
        return dbx
    except Exception as e:
        print(f"Error connecting to Dropbox: {e}")
        return None

def list_csv_files_from_dropbox(folder_path=''):
    """
    Listing file CSV dari Dropbox.
    Karena menggunakan token spesifik app folder, path biasanya relatif terhadap root folder aplikasi.
    """
    files = []
    try:
        dbx = get_dropbox_client()
        if not dbx:
            return []

        # List folder. Jika folder_path kosong, list root.
        # Note: Untuk App Folder, root adl '/'
        res = dbx.files_list_folder(folder_path)
        
        while True:
            for entry in res.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    if entry.name.lower().endswith('.csv'):
                        files.append({
                            'id': entry.path_lower, # Gunakan path sebagai ID untuk download
                            'name': entry.name,
                            'modifiedTime': entry.client_modified.isoformat(),
                            'size': entry.size
                        })
            
            # Pagination
            if not res.has_more:
                break
            res = dbx.files_list_folder_continue(res.cursor)
            
    except Exception as e:
        print(f"Error listing Dropbox files: {e}")
    
    return files

def download_csv_from_dropbox(file_path):
    """Download CSV dan return sebagai DataFrame."""
    try:
        dbx = get_dropbox_client()
        if not dbx:
            return None
            
        metadata, res = dbx.files_download(file_path)
        
        # Baca content
        content = res.content
        s = io.BytesIO(content)
        df = pd.read_csv(s)
        return df
        
    except Exception as e:
        print(f"Error downloading from Dropbox: {e}")
        return None

def get_file_info_dropbox(file_path):
    """Mendapatkan metadata file."""
    try:
        dbx = get_dropbox_client()
        if not dbx:
            return None
            
        metadata = dbx.files_get_metadata(file_path)
        return {
            'id': metadata.path_lower,
            'name': metadata.name,
            'modifiedTime': metadata.client_modified,
            'size': metadata.size
        }
        return None
    except Exception as e:
        print(f"Error getting file info: {e}")
        return None

def upload_file_to_dropbox(file_content, filename):
    """Upload file content (bytes) to Dropbox. Returns Metadata on success, None on failure."""
    try:
        dbx = get_dropbox_client()
        if not dbx:
            return None
        
        # Dropbox API expects a slash at the start for the path
        # For App Folder, '/' is the root of the app folder
        destination_path = f"/{filename}"
        
        # Determine write mode (overwrite if exists)
        mode = dropbox.files.WriteMode.overwrite
        
        try:
            res = dbx.files_upload(file_content, destination_path, mode=mode, mute=True)
            return res
        except dropbox.exceptions.ApiError as err:
            print(f"Dropbox API upload error: {err}")
            return None
            
    except Exception as e:
        print(f"Error uploading to Dropbox: {e}")
        return None

def check_dropbox_connection():
    """Memeriksa apakah koneksi Dropbox valid menggunakan token saat ini."""
    try:
        dbx = get_dropbox_client()
        if not dbx:
            return False
        # Mencoba operasi ringan untuk memverifikasi token
        dbx.users_get_current_account()
        return True
    except Exception as e:
        print(f"Dropbox connection check failed: {e}")
        return False
