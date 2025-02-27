# Generated by Django 5.0.6 on 2024-07-20 16:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_query_status_query_updated_at_alter_query_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='query',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='query',
            name='status',
        ),
        migrations.RemoveField(
            model_name='query',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='query',
            name='issue',
            field=models.CharField(choices=[('general', 'General Inquiry'), ('technical', 'Technical Issue'), ('billing', 'Billing Issue'), ('other', 'Other')], max_length=50),
        ),
        migrations.AlterField(
            model_name='query',
            name='name',
            field=models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(2, message='Name must be at least 2 characters long.')]),
        ),
        migrations.AddIndex(
            model_name='query',
            index=models.Index(fields=['email'], name='app_query_email_053c8c_idx'),
        ),
        migrations.AddIndex(
            model_name='query',
            index=models.Index(fields=['created_at'], name='app_query_created_0c55d0_idx'),
        ),
    ]
