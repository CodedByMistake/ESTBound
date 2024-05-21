import uuid
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from config import BLOB_CONNECTION_STRING, BLOB_CONTAINER_NAME, COSMOS_DB_URL, COSMOS_DB_KEY, COSMOS_DB_DATABASE_NAME, COSMOS_DB_CONTAINER_NAME

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
blob_container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

cosmos_client = CosmosClient(COSMOS_DB_URL, COSMOS_DB_KEY)
database = cosmos_client.create_database_if_not_exists(id=COSMOS_DB_DATABASE_NAME)
container = database.create_container_if_not_exists(
    id=COSMOS_DB_CONTAINER_NAME,
    partition_key=PartitionKey(path="/IdNota"),
    offer_throughput=400
)

def get_next_id():
    try:
        query = "SELECT VALUE MAX(c.IdNota) FROM c"
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        max_id = items[0] if items else 0
        return max_id + 1
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error querying Cosmos DB: {e}")
        return 1

def process_upload(texto, imagem):
    # Upload da imagem para o blob
    blob_name = str(uuid.uuid4()) + '-' + imagem.filename
    blob_client = blob_container_client.get_blob_client(blob_name)
    blob_client.upload_blob(imagem)

    # Buscar o URL da imagem
    blob_url = blob_client.url

    # Preparar os dados para enviar para o cosmoDB
    nota_id = get_next_id()
    item = {
        "IdNota": str(nota_id),
        "texto": texto,
        "imgURL": blob_url
    }

    # Upload de tudo para o cosmoDB
    try:
        container.create_item(body=item)
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error uploading to Cosmos DB: {e}")