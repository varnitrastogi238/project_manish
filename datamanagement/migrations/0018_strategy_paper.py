# Generated by Django 3.1.7 on 2022-10-08 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamanagement', '0017_auto_20221008_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategy',
            name='paper',
            field=models.CharField(default='off', max_length=4),
        ),
    ]
