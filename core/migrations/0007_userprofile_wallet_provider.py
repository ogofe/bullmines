# Generated by Django 4.1.6 on 2023-03-03 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_transaction_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='wallet_provider',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
