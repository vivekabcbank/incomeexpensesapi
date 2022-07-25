from django.core.mail import EmailMessage

class Utils:

    @staticmethod
    def send_email(data):
        print(data["email_subject"],data["email_body"],[data["to_email"]])
        email = EmailMessage(subject=data["email_subject"], body=data["email_body"],to=[data["to_email"]])
        email.send()

