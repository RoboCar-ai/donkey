from paho.mqtt.client import Client
from json import dumps as to_json
from donkeycar.messaging.models.image_pb2 import Image as ImageModel
from PIL import Image
from io import BytesIO
import numpy as np

client = None

def get_client(cfg):
    '''
    client factory that gets the wrapped client where the underling client
    object is a singleton to not disconnect other components
    and an internal bridge is not required.

    This enables a singe TCP socket to the telemetry hub.

    TODO: use a interal hub for inter part comm or something like ROS.
    :param cfg: configuration object
    :return: Client to pub/sub
    '''
    global client
    if not client:
        client = Client(client_id=cfg.TELEMETRY_CLIENT_ID, clean_session=cfg.TELEMETRY_CLEAN_SESSION)

    return client

class StatusClient:
    def __init__(self, cfg, message_client):
        self.client = message_client
        self.cfg = cfg
        self.status_topic = 'robocars/{}/status'.format(self.cfg.TELEMETRY_CLIENT_ID)
        self.disconnect_message = to_json({'status': 'disconnected'})
        self.connected_message = to_json({'status': 'connected'})

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




