from azure.cosmos import CosmosClient
from config import COSMOS_DB_URL, COSMOS_DB_KEY, COSMOS_DB_DATABASE_NAME, COSMOS_DB_CONTAINER_NAME

client = CosmosClient(COSMOS_DB_URL, credential=COSMOS_DB_KEY)

def get_notas():
    database = client.get_database_client(COSMOS_DB_DATABASE_NAME)
    container = database.get_container_client(COSMOS_DB_CONTAINER_NAME)

    # Consulta para obter todas as notas do container
    query = "SELECT * FROM c"
    notas = list(container.query_items(query, enable_cross_partition_query=True))

    # Adicionar logs para verificar o retorno
    print("Notas obtidas do Cosmos DB:", notas)

    return notas
