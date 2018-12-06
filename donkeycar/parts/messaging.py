from paho.mqtt.client import Client
from json import dumps as to_json
from donkeycar.messaging.models.image_pb2 import Image as ImageModel
from donkeycar.utils import CancellationToken
from PIL import Image
from io import BytesIO
import numpy as np
import json


class StatusClient:
    def __init__(self, cfg, message_client):
        self.client = message_client
        self.cfg = cfg
        self.status_topic = 'robocars/{}/status'.format(self.cfg.TELEMETRY_CLIENT_ID)
        self.disconnect_message = to_json({'connectionStatus': 'disconnected'})
        self.connected_message = to_json({'connectionStatus': 'connected'})

    def send_good_status(self):
        self.client.publish(self.status_topic, self.connected_message)

    def send_disconnect_status(self):
        self.client.publish(self.status_topic, self.disconnect_message)

class ImageTelemetryClient:
    def __init__(self, cfg, message_client):
        self.cfg = cfg
        self.client = message_client
        self.session_id = None

    def gen_topic(self):
        # if not self.session_id:
        #     raise ValueError('session_id is None')
        return 'robocars/{}/image-telemetry'\
            .format(self.cfg.TELEMETRY_CLIENT_ID)

    def publish_telemetry(self, telemetry):
        self.client.publish(self.gen_topic(), telemetry)


class SessionClient:
    def __init__(self, cfg, message_client):
        self.client = message_client
        self.cfg = cfg
        self.topic = 'robocars/{}/session'.format(self.cfg.TELEMETRY_CLIENT_ID)

    def init(self):
        self.client.subscribe(self.topic, 0)
        self.client.message_callback_add(self.topic, self.session_callback)

    def session_callback(self, client, userdata, msg):
        import donkeycar.templates.donkey2 as manage
        from threading import Thread
        print(str(msg.payload))
        message = json.loads(msg.payload.decode("utf-8"))
        name = message['name']
        status = message['status']

        if status == 'active':
            print('TelemetryClient: starting drive')
            self.cancellation = CancellationToken()
            Thread(target=manage.drive, args=(self.cfg,),
                   kwargs={'cancellation': self.cancellation, 'model_path': 'd2/models/imitation.h5',
                           'model_type': 'linear'}).start()
        elif status == 'inactive':
            print('TelemetryClient: stopping drive')
            self.cancellation.stopping = True


class ImagePublisher:
    def __init__(self, inputs, cfg, client_):
        self.client = ImageTelemetryClient(cfg, client_)
        self.count = 0

        self.steering_index = inputs.index('user/angle')
        self.mode_index = inputs.index('user/mode')
        self.throttle_index = inputs.index('user/throttle')
        self.image_index = inputs.index('cam/image_array')

    def run(self, *data):
        self.count += 1
        if self.count % 100 == 0:
            print('records captured: {}'.format(self.count))

        self.put_record(data)

    def put_record(self, data):
        """
        Publishes Images and Telemetry to telemetry hub storage.
        Uses Lightweight messaging with protocol buffers for light and compact serialization.
        """
        img_data = Image.fromarray(np.uint8(data[self.image_index]))
        raw = BytesIO()
        img_data.save(raw, format='JPEG')

        image = ImageModel()
        image.data = raw.getvalue()
        image.name = '{}.jpg'.format(self.count)
        image.telemetry.mode = data[self.mode_index]
        image.telemetry.steering_angle = float(data[self.steering_index])
        image.telemetry.throttle = data[self.throttle_index]
        image.telemetry.image_id = self.count
        self.client.publish_telemetry(image.SerializeToString())

    def shutdown(self):
        pass


class TelemetryClient:
    def __init__(self, cfg):
        self.client = None
        self.cfg = cfg
        self.status_client = None
        self.session_client = None

    def connect(self):
        self.client = Client(client_id=self.cfg.TELEMETRY_CLIENT_ID, clean_session=self.cfg.TELEMETRY_CLEAN_SESSION)
        self.status_client = StatusClient(self.cfg, self.client)
        self.session_client = SessionClient(self.cfg, self.client)
        self.client.on_subscribe = TelemetryClient.on_subscribe
        self.client.on_connect = self.on_connect
        self.client.will_set('robocars/{}/lwt'.format(self.cfg.TELEMETRY_CLIENT_ID), self.status_client.disconnect_message)

        print('connecting to telemetry host:', self.cfg.TELEMETRY_HUB_HOST)
        self.client.connect(self.cfg.TELEMETRY_HUB_HOST)

        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print('\nclient stopping...')
            self.status_client.send_disconnect_status()
            self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.session_client.init()
        print('Sending status message:', self.status_client.connected_message)
        self.status_client.send_good_status()

    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        print('subscribed to:', mid)









