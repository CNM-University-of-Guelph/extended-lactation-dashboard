# Generated by Django 5.1.1 on 2024-12-13 15:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_rename_prev_lactation_length_multiparousfeatures_prev_lact_length'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='multiparousfeatures',
            name='days_to_peak',
        ),
        migrations.RemoveField(
            model_name='multiparousfeatures',
            name='persistency',
        ),
    ]
