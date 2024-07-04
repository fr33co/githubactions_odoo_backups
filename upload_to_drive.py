from __future__ import print_function
import os
import json
import glob
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

# Define los alcances necesarios para la API de Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def authenticate(credentials_json):
    """Authenticate with Google Drive."""
    credentials = Credentials.from_service_account_info(
        credentials_json, scopes=SCOPES)
    return credentials


def upload_to_drive(file_path, folder_id=None):
    """Upload a file to Google Drive."""
    # Read the credentials from the environment variable
    credentials_json = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
    creds = authenticate(credentials_json)
    service = build('drive', 'v3', credentials=creds)

    # Create metadata for new file
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, mimetype='application/zip', resumable=True)

    # Upload file to Drive
    try:
        file_to_upload = service.files().create(
            body=file_metadata, media_body=media, fields='id').execute()
        print(f'File ID: {file_to_upload.get("id")}')
    except Exception as e:
        print(f'An error occurred: {e}')


def delete_old_zip_files_from_drive(folder_id, days=8):
    """Delete .zip files older than `days` from Google Drive."""
    now = datetime.now()
    cutoff_date = now - timedelta(days=days)
    cutoff_date_str = cutoff_date.isoformat() + 'Z'
    # Authenticate and build the service
    creds = authenticate(json.loads(credentials_json))
    service = build('drive', 'v3', credentials=creds)

    # Search for .zip files in the specified folder
    query = (f"'{folder_id}' in parents and mimeType='application/zip' "
             f"and createdTime < '{cutoff_date_str}'")
    results = service.files().list(
        q=query,
        spaces='drive', fields='files(id, name, createdTime)').execute()
    items = results.get('files', [])

    if not items:
        print('No .zip files found to delete.')
    else:
        for item in items:
            print(
                f"Deleting file: {item['name']} (ID: {item['id']}, "
                f"Created: {item['createdTime']})"
            )
            service.files().delete(fileId=item['id']).execute()


if __name__ == '__main__':
    # Verify environment variables
    credentials_json = os.getenv('GOOGLE_CREDENTIALS')
    folder_id = os.getenv('GOOGLE_FOLDER')
    if not credentials_json:
        raise ValueError("The secret 'GOOGLE_CREDENTIALS' is not defined")
    if not folder_id:
        raise ValueError("The secret 'GOOGLE_FOLDER' is not defined")

    # Delete old .zip files from Google Drive
    delete_old_zip_files_from_drive(folder_id, days=8)

    # Debug prints
    print(f'Folder ID: {folder_id}')

    zip_files = glob.glob('*.zip', recursive=False)
    if not zip_files:
        print("There are no files to upload.")
    else:
        for file_path in zip_files:
            upload_to_drive(file_path, folder_id)
