# Generated by Django 3.1 on 2020-08-26 00:55

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20200826_0055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='token'),
        ),
    ]
