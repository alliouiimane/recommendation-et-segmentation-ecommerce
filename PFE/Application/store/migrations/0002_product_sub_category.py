# Generated by Django 4.0.10 on 2024-04-30 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sub_category',
            field=models.CharField(default='', max_length=100),
        ),
    ]
