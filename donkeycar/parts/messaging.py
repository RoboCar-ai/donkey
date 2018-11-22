from paho.mqtt.client import Client
from json import dumps as to_json

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
        if not self.session_id:
            raise ValueError('session_id is None')
        return 'robocars/{}/image-telemetry/{}'\
            .format(self.cfg.TELEMETRY_CLIENT_ID, self.session_id)

    def publish_telemetry(self):
        pass
