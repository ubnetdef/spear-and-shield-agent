from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

transport = AIOHTTPTransport(url="https://spearandshield.ubnetdef.org/graphql")

client = Client(transport=transport, fetch_schema_from_transport=True)

def get_ip_address():
    query = gql(
    """
    query MyQuery {
      hello
    }
    """
    )

    result = client.execute(query)
    return result