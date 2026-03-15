from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0002_chatmessage_sender_key_chatmessage_sender_name_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatConnection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key_one", models.CharField(db_index=True, max_length=255)),
                ("key_two", models.CharField(db_index=True, max_length=255)),
                ("key_one_name", models.CharField(blank=True, default="", max_length=255)),
                ("key_two_name", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "constraints": [
                    models.UniqueConstraint(fields=("key_one", "key_two"), name="uniq_chat_connection_pair")
                ],
            },
        ),
        migrations.CreateModel(
            name="ChatConnectionRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("from_key", models.CharField(db_index=True, max_length=255)),
                ("to_key", models.CharField(db_index=True, max_length=255)),
                ("from_name", models.CharField(blank=True, default="", max_length=255)),
                ("to_name", models.CharField(blank=True, default="", max_length=255)),
                ("reason", models.CharField(blank=True, default="", max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")],
                        db_index=True,
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("responded_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
