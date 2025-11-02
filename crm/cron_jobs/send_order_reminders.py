import datetime
import requests
import json

# Define GraphQL query
query = """
query {
  orders(orderDate_Gte: "%s") {
    id
    customer {
      email
    }
  }
}
""" % (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')

# Send request to GraphQL endpoint
response = requests.post(
    "http://localhost:8000/graphql",
    json={"query": query},
    headers={"Content-Type": "application/json"}
)

# Parse response
orders = response.json().get("data", {}).get("orders", [])

# Log results
with open("/tmp/order_reminders_log.txt", "a") as log_file:
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for order in orders:
        log_file.write(f"{timestamp} - Order ID: {order['id']}, Email: {order['customer']['email']}\n")

print("Order reminders processed!")
