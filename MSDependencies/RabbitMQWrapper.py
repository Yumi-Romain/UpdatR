import pika
import json
import requests
import os
from ReportHandler.ChecksDependencies import ChecksDependencies

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im5vbmUiLCJhZG1pbiI6dHJ1ZSwiaWF0IjoxNTc5MDc4Njk1LCJleHAiOjE2NTY4Mzg2OTV9.s4g9C3TRTkSpS-c-VUrpNbF_xw0PtV4YYjnRCTxtQv8"

class RabbitMQWrapper:

    def __init__(self, url):
        self.connection = pika.BlockingConnection(pika.connection.URLParameters(url=url))
        self.connection.process_data_events(time_limit=1)
        self.channel = None
        self.id = {}

    def send(self, queue, durable, body, routing_key):
        channel = self.connection.channel()
        channel.queue_declare(queue=queue, durable=durable)
        channel.basic_publish(body=body, exchange='', routing_key=routing_key)

    def listen(self, queue):
        def callback(ch, method, properties, body): #Body: json en str
            resp = json.loads(body.decode('utf8'))
            if resp["git_url"] is None:
                # resp["git_url"] = 'https://github.com/BaptisteMagoni/app-questionnaire-vue.git'
                return
            print(resp['git_url'])
            try:
                check = ChecksDependencies(resp["git_url"])
                check.start()
                reports = {
                    "git_url": resp['git_url'],
                    "rapportInfo": check.getReport(),
                    "DiscordAlert": resp['Discord_alert'],
                    "SlackAlert": resp['Slack_alert']
                }
                print('envoie du rapport dans "rapport"')
                url = "http://127.0.0.1:8000/api/rapport/"
                requests.post(url, data=reports, headers={'Authorization': TOKEN})
                if check.report.hasOutdatedPackage():
                    print('envoie du rapport dans "alert"')
                    self.send(queue='alert', durable=True, body=json.dumps(reports), routing_key='alert')  # Envoie le rapport dans la queue rapport
                    os.system("rm -rf repos/{}".format(check.path_git))
            except ValueError:
                pass

        channel = self.connection.channel()
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()