# Generated by Django 5.0.2 on 2024-02-29 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0003_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, upload_to='productimage'),
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, upload_to='productimage'),
        ),
    ]
