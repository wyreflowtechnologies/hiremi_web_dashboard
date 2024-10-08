from django.core.mail import send_mail
from django.conf import settings

def send_custom_email(subject, message, recipient_list, from_email=None, fail_silently=False):
    """
    Send an email using Django's send_mail function.

    :param subject: Subject of the email
    :param message: Body of the email
    :param recipient_list: List of recipient email addresses
    :param from_email: The sender's email address (optional)
    :param fail_silently: Boolean to specify whether to fail silently or raise an exception (optional)
    """
    if from_email is None:
        from_email = settings.EMAIL_HOST_USER

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=fail_silently,
    )


def send_password_reset_email(email):
    subject = 'Password Reset Successful'
    message = (
        "Dear User,\n\n"
        "We are writing to inform you that your password has been successfully reset.\n\n"
        "If you did not request this change, please contact us immediately for assistance.\n\n"
        "Best regards,\n"
        "Hiremi"
    )
    from_email = 'hiremiotp@gmail.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def send_ticket_creation_email(email):
    subject = 'Query Raised Successfully'
    message = (
        "Dear Customer,\n\n"
        "We have received your Query and it has been successfully raised. "
        "Our team will review your request and get back to you as soon as possible. "
        "We appreciate your patience and understanding.\n\n"
        "Thank you for reaching out to us.\n\n"
        "Best regards,\n"
        "Customer Support Team \n"
        "Hiremi"
    )
    from_email = 'hiremiotp@gmail.com'
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)




def send_payment_initiation_email(email, amount, order_id):
    subject = 'Payment Initiated Successfully'
    message = (
        "Dear Customer,\n\n"
        "We have successfully initiated the payment for your order. "
        "An amount of **{amount} INR** has been charged to your account. "
        "Your order ID is **{order_id}**.\n\n"
        "If you have any questions or concerns regarding this transaction, "
        "please feel free to contact us.\n\n"
        "Best regards,\n"
        "Hiremi"
    ).format(amount=amount, order_id=order_id)
    from_email = 'hiremiotp@gmail.com'
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)    



def send_payment_confirmation_email(email, amount, order_id):
    subject = 'Payment Successful'
    message = (
        "Dear Customer,\n\n"
        "We are writing to confirm that your payment for the order with ID **{order_id}** "
        "has been successfully processed. An amount of **{amount} INR** has been deducted from your account.\n\n"
        "Thank you for choosing us.\n\n"
        "Best regards,\n"
        "Hiremi"
    ).format(amount=amount, order_id=order_id)
    from_email = 'hiremiotp@gmail.com'
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)
    

def send_payment_failed_email(email, amount, order_id):
    subject = 'Payment Failure Notification'
    message = (
        "Dear Customer,\n\n"
        "We regret to inform you that your payment of **{amount} INR** for Order ID **{order_id}** "
        "was unsuccessful. This may have occurred due to issues with your payment method.\n\n"
        "We recommend trying again with a different bank account or payment method.\n\n"
        "If you continue to experience issues, please do not hesitate to contact our support team for further assistance.\n\n"
        "Thank you for your understanding.\n\n"
        "Best regards,\n"
        "The Hiremi Team"
    ).format(amount=amount, order_id=order_id)
    
    from_email = 'support@hiremi.com'  # Use a professional support email
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)




def send_job_application_confirmation_email(email, job_title):
    subject = 'Job Application Submitted Successfully'
    message = (
        "Dear Applicant,\n\n"
        "We are writing to confirm that your job application for the position of **{job_title}** "
        "has been successfully submitted.\n\n"
        "Our team will review your application and get back to you as soon as possible. "
        "We appreciate your interest in joining our company.\n\n"
        "Best regards,\n"
        "Your Company"
    ).format(job_title=job_title)
    from_email = 'hiremiotp@gmail.com'
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list) 

def send_internship_application_confirmation_email(email, internship_title):
    subject = 'Internship Application Submitted Successfully'
    message = (
        "Dear Applicant,\n\n"
        "We are writing to confirm that your internship application for the position of **{internship_title}** "
        "has been successfully submitted.\n\n"
        "Our team will review your application and get back to you as soon as possible. "
        "We appreciate your interest in joining our company.\n\n"
        "Best regards,\n"
        "Your Company"
    ).format(internship_title=internship_title)
    from_email = 'hiremiotp@gmail.com'
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)      





    