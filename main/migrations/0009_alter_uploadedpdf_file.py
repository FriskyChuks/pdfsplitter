# Generated by Django 4.2.16 on 2024-12-05 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_uploadedpdf_file_uploadedpdf_unique_file_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedpdf',
            name='file',
            field=models.FileField(upload_to='uploads'),
        ),
    ]
