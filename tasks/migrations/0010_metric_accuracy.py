# Generated by Django 5.2.4 on 2025-07-09 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_poselandmarktype_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='metric',
            name='accuracy',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]
