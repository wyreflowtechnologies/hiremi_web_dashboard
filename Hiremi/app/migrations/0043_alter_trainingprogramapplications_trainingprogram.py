# Generated by Django 5.0.6 on 2024-09-30 06:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0042_remove_trainingprogramapplications_fresherjob_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingprogramapplications',
            name='TrainingProgram',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='training_program_details', to='app.trainingprogram'),
        ),
    ]
