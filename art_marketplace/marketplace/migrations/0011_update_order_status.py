from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0010_withdrawalrequest_method_and_payment_details'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[('completed', 'Completed'), ('cancelled', 'Cancelled')],
                default='completed',
                max_length=20
            ),
        ),
        migrations.RunSQL(
            "UPDATE marketplace_order SET status = 'completed' WHERE status = 'pending'",
            reverse_sql="UPDATE marketplace_order SET status = 'pending' WHERE status = 'completed'"
        ),
    ] 