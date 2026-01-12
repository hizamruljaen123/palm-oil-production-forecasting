import os.path
import io
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from utils.config_loader import get_google_drive_config

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_credentials(session_credentials=None):
    """
    Get valid credentials from session dictionary or file.
    Use session_credentials if provided (preferred for Web context).
    Otherwise falls back to token.json if available.
    """
    creds = None
    config = get_google_drive_config()
    token_pickle = config.get('token_pickle', 'token.json') # Legacy fallback

    if session_credentials:
        creds = Credentials.from_authorized_user_info(session_credentials, SCOPES)
    
    # Fallback to local file if no session (e.g. CLI or singleton server auth)
    if not creds and os.path.exists(token_pickle):
        try:
            creds = Credentials.from_authorized_user_file(token_pickle, SCOPES)
        except Exception:
            creds = None
            
    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"Error refreshing token: {e}")
            creds = None
            
    return creds

def create_flow(redirect_uri):
    """Create an OAuth2 Flow instance."""
    config = get_google_drive_config()
    client_secrets_file = config.get('credentials_json', 'client_secret.json')
    
    if not os.path.exists(client_secrets_file):
        raise FileNotFoundError(f"Client secrets file not found: {client_secrets_file}")
        
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    return flow

def get_drive_service(session_credentials=None):
    """Build the Drive service using provided session credentials or fallback."""
    config = get_google_drive_config()
    if not config.get('enabled', False):
        return None
    
    creds = get_credentials(session_credentials)
    
    if not creds or not creds.valid:
        return None

    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building Drive service: {e}")
        return None

def list_csv_files_from_google_drive(session_credentials=None):
    """Lists CSV files from Google Drive."""
    files_result = []
    try:
        service = get_drive_service(session_credentials)
        if not service:
            return []

        query = "name contains '.csv' and trashed = false"
        results = service.files().list(
            q=query,
            pageSize=50, 
            fields="nextPageToken, files(id, name, modifiedTime, size)").execute()
        items = results.get('files', [])

        for item in items:
            files_result.append({
                'id': item['id'],
                'name': item['name'],
                'modifiedTime': item.get('modifiedTime'),
                'size': int(item.get('size', 0))
            })
            
    except Exception as e:
        print(f"Error listing Google Drive files: {e}")
    
    return files_result

def download_csv_from_google_drive(file_id, session_credentials=None):
    """Download CSV and return as DataFrame."""
    try:
        service = get_drive_service(session_credentials)
        if not service:
            return None

        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        df = pd.read_csv(fh)
        return df

    except Exception as e:
        print(f"Error downloading from Google Drive: {e}")
        return None

def get_file_info_google_drive(file_id, session_credentials=None):
    """Get file metadata."""
    try:
        service = get_drive_service(session_credentials)
        if not service:
            return None
            
        file = service.files().get(fileId=file_id, fields="id, name, modifiedTime, size").execute()
        return {
            'id': file['id'],
            'name': file['name'],
            'modifiedTime': file.get('modifiedTime'),
            'size': int(file.get('size', 0))
        }
    except Exception as e:
        print(f"Error getting file info from Google Drive: {e}")
        return None

def check_google_drive_connection(session_credentials=None):
    """Check if Google Drive connection is valid."""
    try:
        service = get_drive_service(session_credentials)
        return service is not None
    except Exception:
        return False
