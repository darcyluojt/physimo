# Generated by Django 5.2.4 on 2025-07-09 10:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_poselandmark_presence'),
    ]

    operations = [
        migrations.CreateModel(
            name='PoseLandmarkType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_index', models.PositiveIntegerField(unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.RenameIndex(
            model_name='poselandmark',
            new_name='tasks_posel_attachm_79731c_idx',
            old_name='tasks_posel_attachm_c7526a_idx',
        ),
        migrations.AlterField(
            model_name='poselandmark',
            name='location_index',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.poselandmarktype'),
        ),
    ]
