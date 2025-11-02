#!/bin/bash

# Run Django shell command to delete inactive customers
deleted_count=$(python3 manage.py shell << END
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(order__isnull=True, created_at__lt=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
END
)

# Log the result with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt
