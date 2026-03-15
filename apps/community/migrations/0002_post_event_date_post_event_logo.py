from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("community", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="event_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="post",
            name="event_logo",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
    ]
