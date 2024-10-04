# Generated by Django 5.1.1 on 2024-09-28 14:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_cow_lactation_lactationdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultiparousFeatures',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parity', models.IntegerField()),
                ('milk_total_1_10', models.FloatField()),
                ('milk_total_11_20', models.FloatField()),
                ('milk_total_21_30', models.FloatField()),
                ('milk_total_31_40', models.FloatField()),
                ('milk_total_41_50', models.FloatField()),
                ('milk_total_51_60', models.FloatField()),
                ('month_sin', models.FloatField()),
                ('month_cos', models.FloatField()),
                ('prev_persistency', models.FloatField()),
                ('prev_lactation_length', models.IntegerField()),
                ('prev_days_to_peak', models.IntegerField()),
                ('prev_305_my', models.FloatField()),
                ('persistency', models.FloatField()),
                ('days_to_peak', models.IntegerField()),
                ('predicted_305_my', models.FloatField()),
                ('lactation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.lactation')),
            ],
        ),
    ]