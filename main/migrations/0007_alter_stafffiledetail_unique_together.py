# Generated by Django 4.2.16 on 2024-12-04 09:02

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0006_rename_created_at_uploadedpdf_date_uploaded_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stafffiledetail',
            unique_together={('user', 'pdf_file')},
        ),
    ]
