from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail


class Command(BaseCommand):
    help = "Send a test email using the current Django email backend settings."

    def add_arguments(self, parser):
        parser.add_argument("recipient", help="Email address to receive the test message")

    def handle(self, *args, **options):
        recipient = options["recipient"].strip()
        if not recipient:
            raise CommandError("Recipient email is required.")

        sent = send_mail(
            subject="EduBond SMTP Test",
            message="This is a test email from EduBond. If you received it, Gmail SMTP is working.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )

        if sent != 1:
            raise CommandError("Email backend did not confirm delivery.")

        self.stdout.write(self.style.SUCCESS(f"Test email sent to {recipient}"))
