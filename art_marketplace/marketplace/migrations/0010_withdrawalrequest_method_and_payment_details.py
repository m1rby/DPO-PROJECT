from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0009_withdrawalrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawalrequest',
            name='method',
            field=models.CharField(choices=[('card', 'Card'), ('paypal', 'PayPal')], default='card', max_length=10),
        ),
        migrations.AddField(
            model_name='withdrawalrequest',
            name='payment_details',
            field=models.CharField(default='', max_length=255),
        ),
    ] 