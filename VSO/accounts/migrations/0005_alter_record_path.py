# Generated by Django 4.2.4 on 2023-08-15 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_record_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='path',
            field=models.FilePathField(path='C:\\Users\\moa\\Documents\\tests\\dj_p'),
        ),
    ]