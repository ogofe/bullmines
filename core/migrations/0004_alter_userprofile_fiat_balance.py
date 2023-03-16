# Generated by Django 4.1.6 on 2023-02-17 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rename_date_created_account_date_joined'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='fiat_balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=1000),
        ),
    ]