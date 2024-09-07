from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def get_google_drive_service(service_account_file):
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials)


def find_or_create_folder(service, folder_name, parent_id="root"):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id != "root":
        query += f" and '{parent_id}' in parents"

    results = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )
    folders = results.get("files", [])

    if not folders:
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        folder = service.files().create(body=folder_metadata, fields="id").execute()
        return folder.get("id")

    return folders[0]["id"]


def upload_to_drive(service, file_path, file_name, folder_id):
    file_metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id, webViewLink")
        .execute()
    )
    return file.get("id"), file.get("webViewLink")


def set_file_permissions(service, file_id, email_list):
    for email in email_list:
        permission = {"type": "user", "role": "reader", "emailAddress": email}
        service.permissions().create(fileId=file_id, body=permission).execute()
