import ssl
from async_base_animations import _loadnpxy
from aioclass import Service
import aioctl
from async_mqtt import MQTTClient
import uasyncio as asyncio
import json
import random


class MQTTService(Service):
    def __init__(self, name):
        super().__init__(name)
        self.info = "Async MQTT client v1.0"
        self.type = "runtime.service"  # continuous running, other types are
        self.enabled = True
        self.docs = "https://github.com/Carglglz/mpy-wpa_supplicant/blob/main/README.md"
        self.args = ["async_mqtt_client"]
        self.kwargs = {
            "server": "0.0.0.0",
            "port": 1883,
            "keepalive": 300,
            "debug": True,
            "on_stop": self.on_stop,
            "on_error": self.on_error,
        }
        self.anm = _loadnpxy(18, 71, timing=(400, 850, 850, 400))

        self.sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.sslctx.load_cert_chain(
            "SSL_certificate7c9ebd3d9df4.der", "SSL_key7c9ebd3d9df4.pem"
        )
        self.client = None
        self.n_msg = 0
        self.n_pub = 0

        # if "pulse" in aioctl.group().tasks:
        #     aioctl.delete("pulse")
        # aioctl.add(pulse, (R, G, B), 1, loops=2, log=request.app.log)
        # return (
        #     htmldoc_color.format(str((R, G, B))),
        #     200,
        #     {"Content-Type": "text/html"},
        # )

    def show(self):
        return (
            "Stats",
            f"   Messages: Received: {self.n_msg}, Published: " + f"{self.n_pub}",
        )

    def on_stop(self, *args, **kwargs):  # same args and kwargs as self.task
        # self.app awaits self.app.server.wait_closed which
        # consumes Cancelled error so this does not run
        if self.log:
            self.log.info(f"[{self.name}.service] stopped")
            # aioctl.add(self.app.shutdown)
        return

    def on_error(self, e, *args, **kwargs):
        if self.log:
            self.log.error(f"[{self.name}.service] Error callback {e}")
        return e

    def on_receive(self, topic, msg):
        try:
            self.n_msg += 1
            if self.log:
                self.log.info(
                    f"[{self.name}.service] @ [{topic.decode()}]:" + f" {msg.decode()}"
                )
            if topic == b"homeassistant/sensor/esphome/pulse":
                color = json.loads(msg.decode())
                R, G, B = color["R"], color["G"], color["B"]
                if "pulse" in aioctl.group().tasks:
                    aioctl.delete("pulse")
                aioctl.add(self.pulse, self, (R, G, B), 1, loops=2)
        except Exception as e:
            if self.log:
                self.log.error(f"[{self.name}.service] {e}")

    @aioctl.aiotask
    async def task(
        self,
        client_id,
        server="0.0.0.0",
        port=1883,
        keepalive=300,
        debug=True,
        log=None,
    ):
        self.log = log
        self.client = MQTTClient(client_id, server, port, keepalive=keepalive)
        self.client.set_callback(self.on_receive)
        await self.client.connect()
        await self.client.subscribe(b"homeassistant/sensor/esphome/state")
        await self.client.subscribe(b"homeassistant/sensor/esphome/pulse")
        # Add subtask

        if "as_mqtt.service.sense" in aioctl.group().tasks:
            aioctl.delete("as_mqtt.service.sense")
        aioctl.add(
            self.sense,
            self,
            42,
            sense_param="low",
            name="as_mqtt.service.sense",
            _id="as_mqtt.service.sense",
        )
        # Wait for messages
        while True:
            await self.client.wait_msg()
            await asyncio.sleep(1)

    @aioctl.aiotask
    async def pulse(self, *args, **kwargs):
        if self.log:
            self.log.info(f"[pulse] {args} {kwargs} pulse")
        await self.anm.pulse(*args, **kwargs)

    @aioctl.aiotask
    async def sense(self, *args, **kwargs):
        while True:
            val = random.random()
            if self.log:
                self.log.info(
                    f"[{self.name}.service.sense] {args} {kwargs} " + f"@ sensor: {val}"
                )
            await self.client.publish(
                b"homeassistant/sensor/esphome/state", f"{val}".encode()
            )
            self.n_pub += 1
            await asyncio.sleep(30)


service = MQTTService("as_mqtt")
