# Generated by Django 5.1.3 on 2024-11-29 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stafffiledetail',
            old_name='pdf',
            new_name='pdf_file',
        ),
    ]
