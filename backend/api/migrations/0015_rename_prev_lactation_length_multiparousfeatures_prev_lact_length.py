# Generated by Django 5.1.1 on 2024-12-13 15:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_multiparousfeatures_current_a_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='multiparousfeatures',
            old_name='prev_lactation_length',
            new_name='prev_lact_length',
        ),
    ]
