# Generated by Django 5.1.1 on 2024-10-15 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_prediction_approximate_persistency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prediction',
            name='approximate_persistency',
            field=models.FloatField(),
        ),
    ]