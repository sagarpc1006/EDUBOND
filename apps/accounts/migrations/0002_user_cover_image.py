from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="cover_image",
            field=models.FileField(blank=True, null=True, upload_to="covers/"),
        ),
    ]
