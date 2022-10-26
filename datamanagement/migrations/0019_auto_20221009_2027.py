# Generated by Django 3.1.7 on 2022-10-09 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamanagement', '0018_strategy_paper'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategy',
            name='totp',
            field=models.CharField(default='NONE', max_length=50),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='angel_client_id',
            field=models.CharField(default='NONE', max_length=50),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='angel_password',
            field=models.CharField(default='NONE', max_length=50),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='stoploss',
            field=models.IntegerField(default=0),
        ),
    ]
