import datetime
import requests

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=True, retries=3)
client = Client(transport=transport, fetch_schema_from_transport=True)

query = gql("{ hello }")
response = client.execute(query)


def log_crm_heartbeat():
    # Log timestamped heartbeat message
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} CRM is alive\n")

    # Optional: Check GraphQL hello field
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("GraphQL heartbeat check passed.")
        else:
            print("GraphQL heartbeat check failed.")
    except Exception as e:
        print(f"GraphQL heartbeat error: {e}")

CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
]
