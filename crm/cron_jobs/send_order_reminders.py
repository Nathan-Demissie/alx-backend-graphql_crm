from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import datetime

# Set up GraphQL transport
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Define query
seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
query = gql(f"""
query {{
  orders(orderDate_Gte: "{seven_days_ago}") {{
    id
    customer {{
      email
    }}
  }}
}}
""")

# Execute query
result = client.execute(query)
orders = result.get("orders", [])

# Log results
with open("/tmp/order_reminders_log.txt", "a") as log_file:
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for order in orders:
        log_file.write(f"{timestamp} - Order ID: {order['id']}, Email: {order['customer']['email']}\n")

print("Order reminders processed!")
