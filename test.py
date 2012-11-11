#!/usr/bin/python
import imaplib, smtplib
from email import message_from_string
from email.header import Header, decode_header, make_header
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart

username,password = 'xxx',"xxx"

sendserver = smtplib.SMTP('smtp.gmail.com:587')
sendserver.starttls()
sendserver.login(username,password)

recieveserver = imaplib.IMAP4_SSL('imap.gmail.com', 993)
recieveserver.login(username,password)

result, data = recieveserver.select('Inbox')
print "Inbox mail count :", data

result, data = recieveserver.search(None,'UnSeen')
print "Unread mails:", data

result, data = recieveserver.uid('search', None, 'ALL')
print "Uid of all mails:", data

mail_uid = '27'
#~ result, data = recieveserver.fetch(mail_uid, "(RFC822)")
#~ print "Email data:", data

result, data = recieveserver.uid('fetch', mail_uid, '(RFC822)')
#print "Email data:", data

mail = data[0][1]
parsed_mail = message_from_string(mail)
print "--"*40
print "From:", parsed_mail.get_all('From', [])
print "To:", parsed_mail.get_all('To', [])
print "Cc:", parsed_mail.get_all('Cc', [])
print "Date:", parsed_mail['date']
print "Subject:", parsed_mail['subject']
print "Multipart:", parsed_mail.is_multipart()
print "Body:"
print "--"*40
if not parsed_mail.is_multipart():
    print parsed_mail.get_payload(decode=True)
else:
    counter = 1
    accepted_types = ['text/plain', 'text/html']
    body = {}
    filenames = []
    files = {}
    for part in parsed_mail.walk():
        # multipart/* are just containers
        if part.get_content_maintype() == 'multipart':  continue
        filename = part.get_filename()
        if not filename:
            if part.get_content_type() in accepted_types:
                if part.get_content_type() not in body:
                    body[part.get_content_type()] = []
                body[part.get_content_type()].append(part.get_payload(decode=True))
            else:
                ext = mimetypes.guess_extension(
                       part.get_content_type())
                if not ext:
                    # Use a generic bag-of-bits extension
                    ext = '.bin'
                    filename = 'part-%03d%s' % (counter, ext)
                counter += 1
        if filename:
            filename = unicode(make_header(decode_header(filename)))
            filenames.append(filename)
            files[filename] = part
    print body['text/html'][0]
    print "Attachments:", filenames
    #print files
print "--"*40
def attachment(filename):
        file_data = file(filename, "rb")
        mimetype, mimeencoding = mimetypes.guess_type(filename)
        if mimeencoding or (mimetype is None): mimetype = "application/octet-stream"
        maintype, subtype = mimetype.split("/")
        retval = MIMEBase(maintype, subtype)
        retval.set_payload(file_data.read())
        Encoders.encode_base64(retval)
        retval.add_header(
            "Content-Disposition",
            "attachment",
            filename=os.path.basename(filename)
        )
        file_data.close()
        return retval
def send(FROM, TO, SUBJECT, MESSAGE, CC, CONTENT_TYPE='text', MULTIPART=False, ATTACHMENTS=[]):
    TO      = TO.split(',')
    CC      = CC.split(',')
    SUBJECT = Header(SUBJECT, 'utf-8')
    EMAIL   = ''
    if not MULTIPART:
        EMAIL = MIMEText(MESSAGE, 'plain', 'utf-8')
        EMAIL['Content-Type'] = 'text/plain; charset="utf-8"'
    else:
        EMAIL = MIMEMultipart()
        BODY = MIMEText(MESSAGE, 'html', 'utf-8')
        EMAIL.attach(BODY)
        for FILE in list(ATTACHMENTS):
            EMAIL.attach(attachment(FILE))
    EMAIL['Subject'] = SUBJECT
    EMAIL.preamble
    EMAIL['From'] = FROM
    EMAIL['Reply-To'] = 'another@example.com'
    EMAIL['To'] = ", ".join(TO)
    EMAIL['CC'] = CC
    EMAIL = EMAIL.as_string()
    sendserver.sendmail(FROM.split(','), TO + CC.split(','), EMAIL)

