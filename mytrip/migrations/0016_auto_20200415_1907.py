# Generated by Django 3.0.4 on 2020-04-15 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mytrip', '0015_auto_20200322_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='photo',
            field=models.ImageField(upload_to='events/'),
        ),
        migrations.DeleteModel(
            name='nearby_location',
        ),
    ]
