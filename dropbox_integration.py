import dropbox
import pandas as pd
import io
from utils.config_loader import get_dropbox_config

def get_dropbox_client():
    """Membuat koneksi ke Dropbox."""
    config = get_dropbox_config()
    ACCESS_TOKEN = config.get('access_token')
    
    if not ACCESS_TOKEN:
        print("Dropbox Access Token not found in config.")
        return None
        
    try:
        dbx = dropbox.Dropbox(ACCESS_TOKEN)
        return dbx
    except Exception as e:
        print(f"Error connecting to Dropbox: {e}")
        return None
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
