# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0006_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artwork',
            name='likes',
        ),
    ] 