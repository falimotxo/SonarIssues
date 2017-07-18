import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SendEmail:

    def __init__(self, address_email, port_email, user_email, password_email, email_to, email_cc):
        self.address_email = address_email
        self.port_email = port_email
        self.user_email = user_email
        self.password_email = password_email
        self.email_to = email_to
        self.email_cc = email_cc

    def sendEmail(self, titleEmail, messageHtml):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = titleEmail
        msg['From'] = self.user_email
        msg['To'] = self.email_to
        msg['Cc'] = self.email_cc

        html = "<html><head></head><body>" + messageHtml + "</body></html>"

        part1 = MIMEText(messageHtml, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        try:
            server = smtplib.SMTP(self.address_email, self.port_email)
            print('INFO - {} : Conectado a servidor de correo'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
            server.starttls()
            server.login(self.user_email, self.password_email)
            print('INFO - {} : Logado a servidor de correo'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))
            server.sendmail(self.user_email, [self.email_to, self.email_cc], msg.as_string())
            print('INFO - {} : Correo enviado a {} correctamente'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y'), self.email_to))
            server.quit()
        except Exception as e:
            print('ERROR - {} : Se ha producido un error al enviar correo a la dirección: {}'.format(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y'), self.email_to))