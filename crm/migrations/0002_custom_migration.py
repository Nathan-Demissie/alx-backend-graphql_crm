from django.db import migrations, models

def set_default_stock(apps, schema_editor):
    Product = apps.get_model('crm', 'Product')
    for product in Product.objects.all():
        if product.stock is None:
            product.stock = 0
            product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(set_default_stock),
    ]
