# Generated by Django 4.1.3 on 2022-11-23 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_product_interested'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status_date',
            field=models.DateField(auto_now=True),
        ),
    ]
