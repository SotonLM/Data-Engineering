import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

def store_to_azure(file_name: str, container_name: str, data_type: str = "raw") -> str:
    """
    Upload a file to Azure Blob Storage container, organized by data type.
    
    Args:
        file_name (str): Path to the local file to upload
        container_name (str): Name of the Azure container
        data_type (str): "clean" or "raw" - determines directory structure


    Returns: path of the file stored in the azure blob
    """
    # Load environment variables
    load_dotenv()
    
    # Get connection string from .env
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("AZURE_CONNECTION_STRING not found in .env file")
    
    # Create BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Get container client
    container_client = blob_service_client.get_container_client(container_name)
    
    # Create container if it doesn't exist
    if not container_client.exists():
        container_client.create_container()
    
    # Extract blob name from file path and prepend data_type directory
    blob_name = os.path.basename(file_name)
    blob_path = f"{data_type}/{blob_name}"
    
    # Upload file to the appropriate directory
    with open(file_name, "rb") as data:
        blob_client = container_client.get_blob_client(blob_path)
        blob_client.upload_blob(data, overwrite=True)
    
    print(f"File {file_name} uploaded to {container_name}/{blob_path}")
    return f"https://sotonlmdeng.blob.core.windows.net/{container_name}/{blob_path}"


# Example usage:
# store_to_azure("sacrifice.txt", "conversational-social", "raw")
# store_to_azure("cleaned_data.json", "conversational-social", "clean")