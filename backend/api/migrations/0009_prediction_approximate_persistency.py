# Generated by Django 5.1.1 on 2024-10-15 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_primiparousfeatures'),
    ]

    operations = [
        migrations.AddField(
            model_name='prediction',
            name='approximate_persistency',
            field=models.FloatField(default=None),
            preserve_default=False,
        ),
    ]