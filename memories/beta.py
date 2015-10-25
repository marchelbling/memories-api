# -*- coding: utf-8 -*-
import smtplib
import json
import datetime


def load_json(path):
    with open(path, 'r') as data:
        return json.load(data)


class GMailSender(object):
    def __init__(self, username="", password=""):
        self.username = username
        self.password = password

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, type, value, traceback):
        self.server.quit()

    def _connect(self):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(self.username, self.password)

    def send(self, content, recipients, **kwargs):
        subject = kwargs.get("subject", "(automatic email)")
        headers = u"\r\n".join([u"subject: {}".format(subject),
                                u"to: {}".format(";".join(recipients))])

        content = headers + u"\r\n\n" + content
        sent = self.server.sendmail(from_addr=self.username,
                                    to_addrs=recipients,
                                    msg=content.encode('utf8'))
        if not sent:
            print("email sent to {}".format(recipients))
        else:
            print("sendmail returned: {}".format(sent))


class Beta:
    @staticmethod
    def load():
        try:
            return load_json("/data/memories/beta.json")
        except:
            return {'users': []}

    @staticmethod
    def get_users():
        return Beta.load()['users']

    @staticmethod
    def add_user(user):
        beta = Beta.load()
        beta['users'].append(user)
        with open('/data/memories/beta.json', 'w') as output:
            json.dump(beta, output)

    @staticmethod
    def register(email, message, interest):
        user = filter(lambda user: user['email'] == email, Beta.get_users())

        if user:
            result = {"status": "Vous avez bien été enregistré le {}. "
                                "Vous devriez prochainement recevoir un email".format(user[0]['timestamp'])}
        else:
            Beta.send_mail_for_registration(email=email, message=message, interest=interest)
            Beta.add_user({'email': email, 'message': message, 'interest': interest,
                           'timestamp': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')})
            result = {"status": "Vous avez bien été enregistré à la beta de memories. "
                                "Vous devriez prochainement recevoir un email vous permettant d'installer "
                                "l'application. Merci de votre intérêt !"}
        return json.dumps(result)

    @staticmethod
    def send_mail_for_registration(**kwargs):
        credentials = load_json("/data/memories/.mail.json")
        with GMailSender(username=credentials["username"], password=credentials["password"]) as gmail:
            gmail.send(content="\n".join("* {key}: {value}".format(key=key, value=value)
                                         for key, value in kwargs.items() if value),
                       recipients=["cedric.soubrie@gmail.com", "marc@helbling.fr"],
                       subject="Inscription a la beta de memories")
