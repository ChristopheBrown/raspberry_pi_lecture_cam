import smtplib
import datetime
import os
from os import system as sys
from email.mime.text import MIMEText


class Uploader:
    relative_path = None
    file = None
    absolute_path = None
    keyfile = 'REDACTED'  # NOTE: If you get "permissions are too open" do "chmod 400 [pem file]" in terminal
    destination_path = 'REDACTED'
    server = 'REDACTED' + destination_path
    gmail_sender = 'REDACTED'
    gmail_password = 'REDACTED'
    gmail_recipients = []

    show_recipients = False

    def upload(self):
        if self.file is None:
            return

        # these command performs the file copy to the remote server *COPY-SEND-DELETE*
        command = 'cp {} {}'.format(self.absolute_path, self.file)
        print('Copying file to local directory.')
        print(command)
        sys(command)

        command = 'scp -i "{}" "{}" "{}"'.format(self.keyfile, self.file, self.server)
        print('Sending to EC2 server.')
        print(command)
        sys(command)

        command = 'rm {}'.format(self.file)
        print('Cleaning up.')
        print(command)
        sys(command)

        print('File {} has been uploaded to EC2 instance.'.format(self.file))

    def email(self, gmail_recipients=[]):
        if self.file is None:
            return

        for recipient in gmail_recipients:
            self.gmail_recipients.append(recipient)

        # set up email server
        smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(self.gmail_sender, self.gmail_password)
        today = datetime.date.today()

        # prepare email message body
        mail_body = 'Your file can be accessed at {}{}'.format(self.destination_path, self.file)
        msg = MIMEText(mail_body)
        msg['Subject'] = 'File ' + self.file + ' upload success %s' % today.strftime('%b %d %Y')
        msg['From'] = self.gmail_sender

        # send the success message to all recipients
        for recipient in self.gmail_recipients:
            msg['To'] = recipient
            smtpserver.sendmail(self.gmail_sender, [recipient], msg.as_string())

        smtpserver.quit()

        if self.show_recipients:
            print('The following recipients have been notified:'.format(self.file))
            for address in self.gmail_recipients:
                print(address)

    def __init__(self, filename, print_emails=False):

        # make sure PEM file and upload file exist
        try:
            f = open(self.keyfile)
        except IOError:
            print('PEM file not found. Please locate ', self.keyfile)
        finally:
            f.close()

        try:
            f = open(filename)
            self.relative_path = os.path.split(filename)[0]
            self.file = os.path.split(filename)[1]
            self.absolute_path = str(self.relative_path) + '/' + str(self.file)
            print(self.relative_path)
            print(self.file)
            print(self.absolute_path)

        except IOError:
            print('Upload file "' + filename + '" not found. Please locate it and make sure it is spelled correctly.')
        finally:
            f.close()

        if print_emails:
            self.show_recipients = True


# the code below can be used to run the program by itself, no importing needed. i.e. like so in your terminal:
# python uploader.py
# change file_to_send below to the file you want to upload, the code will check whether your file exists

if __name__ == '__main__':
    file_to_send = 'sample.txt'
    gmail_recipients = ['REDACTED']

    u = Uploader(file_to_send, print_emails=True)  # change to False to not print out emails when finished
    u.upload()
    u.email(gmail_recipients)
