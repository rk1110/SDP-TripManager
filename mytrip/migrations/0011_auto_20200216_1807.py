# Generated by Django 3.0.1 on 2020-02-16 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mytrip', '0010_nearby_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event_registration',
            name='mobileno',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='events',
            name='contact',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='users',
            name='mobileno',
            field=models.CharField(max_length=10),
        ),
    ]
