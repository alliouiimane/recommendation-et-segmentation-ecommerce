# Generated by Django 4.0.10 on 2024-04-30 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=370, unique=True),
        ),
    ]
