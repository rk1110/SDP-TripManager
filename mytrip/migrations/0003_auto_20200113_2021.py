# Generated by Django 3.0.1 on 2020-01-13 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mytrip', '0002_auto_20200113_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='contact',
            field=models.DecimalField(decimal_places=0, max_digits=10),
        ),
    ]
