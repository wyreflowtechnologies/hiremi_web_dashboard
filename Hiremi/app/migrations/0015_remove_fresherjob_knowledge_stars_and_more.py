# Generated by Django 5.0.6 on 2024-07-30 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_alter_fresherjob_upload_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fresherjob',
            name='knowledge_stars',
        ),
        migrations.RemoveField(
            model_name='internship',
            name='knowledge_stars',
        ),
        migrations.AlterField(
            model_name='fresherjob',
            name='about_company',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='internship',
            name='about_company',
            field=models.TextField(),
        ),
    ]
