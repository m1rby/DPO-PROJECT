from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0008_merge_20250511_1207'),
    ]

    operations = [
        migrations.CreateModel(
            name='WithdrawalRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_rejected', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdrawal_requests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ] 