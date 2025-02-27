# Generated by Django 5.0.6 on 2024-09-28 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_remove_trainingprogram_payment_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingprogram',
            name='payment_status',
            field=models.CharField(choices=[('Not Enroll', 'Not Enroll'), ('Enroll Pending', 'Enroll Pending'), ('Enrolled', 'Enrolled')], default='Not Enroll', max_length=15),
        ),
        migrations.AddField(
            model_name='trainingprogram',
            name='time_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
