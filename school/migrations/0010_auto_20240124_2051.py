# Generated by Django 3.0.5 on 2024-01-24 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0009_auto_20240124_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parent',
            name='phone_no',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
    ]
