from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0003_chatconnection_chatconnectionrequest"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatmessage",
            name="delivered_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="chatmessage",
            name="read_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
