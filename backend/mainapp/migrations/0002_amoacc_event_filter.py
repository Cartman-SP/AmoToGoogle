# Generated by Django 5.0.6 on 2024-08-03 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='amoacc',
            name='event_filter',
            field=models.CharField(default='123', max_length=1000),
            preserve_default=False,
        ),
    ]
