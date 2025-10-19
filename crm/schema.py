import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import datetime
import re

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise ValidationError("Email already exists")
        if input.phone and not re.match(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$', input.phone):
            raise ValidationError("Invalid phone format")
        customer = Customer.objects.create(**input)
        return CreateCustomer(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created = []
        errors = []
        with transaction.atomic():
            for entry in input:
                try:
                    if Customer.objects.filter(email=entry.email).exists():
                        raise ValidationError(f"Email {entry.email} already exists")
                    if entry.phone and not re.match(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$', entry.phone):
                        raise ValidationError(f"Invalid phone format for {entry.name}")
                    customer = Customer.objects.create(**entry)
                    created.append(customer)
                except Exception as e:
                    errors.append(str(e))
        return BulkCreateCustomers(customers=created, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise ValidationError("Price must be positive")
        if input.stock is not None and input.stock < 0:
            raise ValidationError("Stock cannot be negative")
        product = Product.objects.create(**input)
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID")

        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            raise ValidationError("Invalid product IDs")
        if len(products) == 0:
            raise ValidationError("At least one product must be selected")

        total = sum(p.price for p in products)
        order = Order.objects.create(
            customer=customer,
            total_amount=total,
            order_date=order_date or datetime.now()
        )
        order.products.set(products)
        return CreateOrder(order=order)

# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

# Query placeholder
class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)

    def resolve_all_customers(self, info):
        return Customer.objects.all()
