from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
import uuid
from config import BLOB_CONNECTION_STRING, BLOB_CONTAINER_NAME, COSMOS_DB_URL, COSMOS_DB_KEY, COSMOS_DB_DATABASE_NAME, COSMOS_DB_CONTAINER_NAME
from io import BytesIO

# Inicialização do Cosmos DB e Blob Service Client
cosmos_client = CosmosClient(COSMOS_DB_URL, COSMOS_DB_KEY)
database = cosmos_client.create_database_if_not_exists(id=COSMOS_DB_DATABASE_NAME)
container = database.create_container_if_not_exists(
    id=COSMOS_DB_CONTAINER_NAME,
    partition_key=PartitionKey(path="/IdNota"),
    offer_throughput=400
)

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
blob_container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

def get_next_id():
    database = cosmos_client.get_database_client(COSMOS_DB_DATABASE_NAME)
    container = database.get_container_client(COSMOS_DB_CONTAINER_NAME)

    # Consulta para obter o maior ID atual
    query = "SELECT VALUE MAX(c.id) FROM c"
    max_id = list(container.query_items(query, enable_cross_partition_query=True))

    if max_id and max_id[0] is not None:
        return int(max_id[0]) + 1
    else:
        return 1


def process_upload(texto, imagem):
    # Upload da imagem para o blob
    blob_name = str(uuid.uuid4()) + '-' + imagem.filename
    blob_client = blob_container_client.get_blob_client(blob_name)

    # Lendo a imagem como bytes e enviando para o blob
    with BytesIO() as stream:
        stream.write(imagem.stream.read())
        stream.seek(0)
        blob_client.upload_blob(stream)

    # Buscar o URL da imagem
    blob_url = blob_client.url

    # Preparar os dados para enviar para o Cosmos DB
    nota_id = get_next_id()
    item = {
        "id": str(nota_id),   # Adicione a propriedade 'id'
        "IdNota": str(nota_id),
        "texto": texto,
        "imgURL": blob_url
    }

    # Upload de tudo para o Cosmos DB
    try:
        container.create_item(body=item)
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error uploading to Cosmos DB: {e}")