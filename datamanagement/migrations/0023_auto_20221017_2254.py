# Generated by Django 3.1.7 on 2022-10-17 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamanagement', '0022_auto_20221017_2250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stop_symboll',
            name='symbol',
            field=models.CharField(default='NONE', max_length=25),
        ),
    ]
