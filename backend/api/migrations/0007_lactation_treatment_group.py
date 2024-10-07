# Generated by Django 5.1.1 on 2024-10-05 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_prediction_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='lactation',
            name='treatment_group',
            field=models.CharField(choices=[('No group', 'No Group'), ('Extend 1 cycle', 'Extend 1 cycle'), ('Extend 2 cycles', 'Extend 2 cycles'), ('Extend 3 cycles', 'Extend 3 cycles'), ('Do not extend', 'Do not extend')], default='No group', max_length=20),
        ),
    ]
