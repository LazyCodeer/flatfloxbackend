# Generated by Django 5.0.1 on 2024-05-20 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flatflox', '0007_workingcities'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pgpicture',
            name='pg',
        ),
    ]
