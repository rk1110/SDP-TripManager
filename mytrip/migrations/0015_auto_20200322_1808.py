# Generated by Django 3.0.4 on 2020-03-22 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mytrip', '0014_auto_20200216_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='photo',
            field=models.ImageField(default='', upload_to='events/'),
        ),
    ]
