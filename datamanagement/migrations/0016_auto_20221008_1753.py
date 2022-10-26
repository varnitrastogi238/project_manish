# Generated by Django 3.1.7 on 2022-10-08 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamanagement', '0015_auto_20221008_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategy',
            name='symbol',
            field=models.CharField(default='NONE', max_length=100),
        ),
        migrations.AddField(
            model_name='strategy',
            name='token',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='position_increase',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=5),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='range',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=5),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='stoploss',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=5),
        ),
    ]