# Generated by Django 5.0.4 on 2024-08-08 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('care', '0002_alter_benefactor_ben_email_alter_benefactor_ben_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='is_read',
            field=models.CharField(db_column='is_read', max_length=255),
        ),
    ]
