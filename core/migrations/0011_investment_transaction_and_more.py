# Generated by Django 4.1.6 on 2023-03-14 12:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_notification_options_deposit_transaction_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='investment',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.transaction'),
        ),
        migrations.AlterField(
            model_name='investmentpackage',
            name='capital',
            field=models.IntegerField(help_text='Investment amount required'),
        ),
        migrations.AlterField(
            model_name='investmentpackage',
            name='duration',
            field=models.IntegerField(help_text='Duration of payout in days'),
        ),
        migrations.AlterField(
            model_name='investmentpackage',
            name='name',
            field=models.CharField(help_text='Package name. eg Bronze Starter', max_length=200),
        ),
        migrations.AlterField(
            model_name='investmentpackage',
            name='roi',
            field=models.DecimalField(decimal_places=2, help_text='Return on Investment in Percentage', max_digits=20000),
        ),
    ]
