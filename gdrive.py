# Helper module for Google Drive functionality
from googleapiclient.discovery import build
from apiclient import errors
from apiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io

GDRIVE_APP_FOLDER = 'UBP Ebooks'
API_NAME = 'drive'
API_VERSION = 'v3'

def build_gdrive_service(credentials):
    
    # TODO: Use singleton
    drive = build(API_NAME, API_VERSION, credentials=credentials)
    return drive

def create_app_folder(credentials):

    drive = build_gdrive_service(credentials)
    metadata = {
        'name': GDRIVE_APP_FOLDER,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    folder = drive.files().create(
        body=metadata,
        fields='id'
    ).execute()

    return folder.get('id')


def get_app_folder_id(credentials):
    """Gets the folder for storing ebooks, creating it if it doesn't exist"""

    drive = build_gdrive_service(credentials)
    resp = drive.files().list(
        q=f"name='{GDRIVE_APP_FOLDER}' and \
            'root' in parents and \
            trashed = false",
        fields='files(id, name)',
        spaces='drive'
    ).execute()

    folders = resp['files']

    if len(folders) > 0:
        return folders[0].get('id')
    
    return create_app_folder(credentials)   


def get_all_epub_file_ids(credentials, folder=None):
    """
    Fetch a list of all epub files in Drive folder. For now, only fetch epubs
    that are direct children of the app folder
    TODO: Use recursive search to fetch ALL files
    """

    drive = build_gdrive_service(credentials)
    if folder is None:
        folder = get_app_folder_id(credentials)

    file_ids = []
    page_token = None

    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token

            resp = drive.files().list(
                q=f"'{folder}' in parents and \
                    mimeType='application/epub+zip' ",
                fields='files(id)',
                **param
            ).execute()

            if resp['files']:
                file_ids.append(*[file['id'] for file in resp['files']])

            page_token = resp.get('nextPageToken')
            if not page_token:
                break

        except errors.HttpError as error:
            print(f'An error occurred: {error}')
            break
    
    return file_ids

def download_file(credentials, file_id):
    """Download file with given id, return file-like object(?)"""

    drive = build_gdrive_service(credentials)
    request = drive.files().get_media(fileId=file_id)

    file_handle = io.BytesIO()
    downloader = MediaIoBaseDownload(file_handle, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    return file_handle

def upload_file(credentials, file_handle, filename, app_folder_id, generated_file_id):
    """Upload file to Google Drive"""

    drive = build_gdrive_service(credentials)

    metadata = {
        'name': filename,
        'parents': [app_folder_id],
        'contentRestrictions': [{'readOnly':'true'}],
        'id': generated_file_id
    }
    upload = MediaIoBaseUpload(
        file_handle,
        mimetype='application/epub+zip',
        resumable=True
    )

    # TODO: Rewrite
    try:
        file = drive.files().create(
            body=metadata,
            media_body=upload,
            fields='id'
        ).execute()
        return file.get('id')
    except errors.HttpError as error:
        return False

def generate_file_id(credentials):

    drive = build_gdrive_service(credentials)
    
    try:
        resp = drive.files().generateIds(count=1, fields='ids').execute()
        return resp['ids'][0]
    except errors.HttpError as error:
        return None
