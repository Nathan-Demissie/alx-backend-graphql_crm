from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import datetime

from datetime import datetime
import requests

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

response = requests.post(
    "http://localhost:8000/graphql",
    json={"query": "{ customers { id } orders { id totalamount } }"},
    headers={"Content-Type": "application/json"}
)


@shared_task
def generate_crm_report():
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
    query {
        customers { id }
        orders { id totalamount }
    }
    """)

    try:
        result = client.execute(query)
        total_customers = len(result.get("customers", []))
        orders = result.get("orders", [])
        total_orders = len(orders)
        total_revenue = sum(order["totalamount"] for order in orders)

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"

        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(report)

        print("CRM report generated.")
    except Exception as e:
        print(f"Error generating report: {e}")
