import os
import io
import base64
from azure.storage.blob import BlobServiceClient


class StorageAccount:
    def __init__(self, connection_string, container_name):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)
        if not self.container_client.exists():
            self.container_client.create_container()

    def download_blob(self, file_name):
        blob_client = self.container_client.get_blob_client(file_name)
        content = blob_client.download_blob().readall()
        return content

    def get_files_from_directory(self, directory_name: str) -> list[dict]:
        """
        Obtiene una lista de archivos desde un directorio específico en el contenedor de Azure Blob Storage.
        Args:
            directory_name (str): Nombre del directorio dentro del contenedor desde el cual se desean listar y obtener los archivos.
        Returns:
            list[dict]: Una lista de diccionarios
        Nota:
            Este método descarga cada archivo encontrado en el directorio especificado y lo almacena en memoria como un flujo bufferizado.
        """
        blobs = self.container_client.list_blobs(name_starts_with=directory_name)

        file_list = []
        for blob in blobs:
            blob_name = blob.name
            blob_client = self.container_client.get_blob_client(blob)

            stream = io.BytesIO()
            download_stream = blob_client.download_blob()
            download_stream.readinto(stream)
            stream.seek(0)
            
            buffered_stream = io.BufferedReader(stream)
            relative_name = blob_name[len(directory_name):]

            file_list.append({
                'filename': relative_name,
                'file': buffered_stream,
            })
                
        return file_list
    
    def get_files_strings(self, filter_name):
        blobs = self.container_client.list_blobs(name_starts_with=filter_name)

        file_list = []
        for blob in blobs:
            blob_content = self.download_blob(blob.name)
            encoded_content = base64.b64encode(blob_content).decode('utf-8')
            file_list.append({
                'file_name': blob.name,
                'content_base64': encoded_content
            })

        return file_list