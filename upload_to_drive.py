from __future__ import print_function
import os
import glob
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

# Define los alcances necesarios para la API de Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate(credentials_path):
    """Autentica la cuenta de servicio y devuelve las credenciales."""
    credentials = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    return credentials

def upload_to_drive(file_path, folder_id=None):
    """Sube un archivo a Google Drive."""
    # Ruta al archivo de credenciales JSON
    credentials_path = 'credentials.json'  # Cambia esto por la ruta a tu archivo JSON

    creds = authenticate(credentials_path)
    service = build('drive', 'v3', credentials=creds)
    
    # Crear metadatos del archivo
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, mimetype='application/zip', resumable=True)
    
    # Subir el archivo
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'File ID: {file.get("id")}')


if __name__ == '__main__':
    # Directorio actual
    current_directory = os.getcwd()
    
    # Ruta al archivo de credenciales JSON
    credentials_path = 'credentials.json'  # Cambia esto por la ruta a tu archivo JSON
    
    # Autenticar y construir el servicio
    creds = authenticate(credentials_path)
    service = build('drive', 'v3', credentials=creds)
    
    # ID de la carpeta en Google Drive
    folder_id = '1vzf78cSOJptCWUBrVTvvpOP6_mDE3xll'  # Reemplaza con el ID de tu carpeta
    
    # Buscar archivos .zip en el directorio actual
    zip_files = glob.glob('*.zip')
    
    if not zip_files:
        print("No se encontraron archivos .zip para subir.")
    else:
        for file_path in zip_files:
            upload_to_drive(file_path, folder_id)
