# Generated by Django 5.0.4 on 2024-05-10 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_remove_product_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='title',
            field=models.CharField(default='title', max_length=600),
        ),
    ]
