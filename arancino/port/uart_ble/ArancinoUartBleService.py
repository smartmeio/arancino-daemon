from adafruit_ble.characteristics.stream import StreamIn, StreamOut
from adafruit_ble.uuid import VendorUUID
from adafruit_ble.services.nordic import UARTService, Service
from arancino.utils.ArancinoUtils import ArancinoConfig

CONF = ArancinoConfig.Instance().cfg

class ArancinoUartBleService(UARTService):
    uuid = VendorUUID(CONF.get("port").get("uart_ble").get("services").get("vendor_communication_uuid"))

    _server_tx = StreamOut(
        uuid=VendorUUID(CONF.get("port").get("uart_ble").get("services").get("vendor_tx_uuid")),
        timeout=CONF.get("port").get("uart_ble").get("timeout"),
        buffer_size=CONF.get("port").get("uart_ble").get("buffer_size"), # default was 64
    )
    _server_rx = StreamIn(
        uuid=VendorUUID(CONF.get("port").get("uart_ble").get("services").get("vendor_rx_uuid")),
        timeout=CONF.get("port").get("uart_ble").get("timeout"),
        buffer_size=CONF.get("port").get("uart_ble").get("buffer_size"), # default was 64
    )

class ArancinoResetBleService(UARTService):
    uuid = VendorUUID(CONF.get("port").get("uart_ble").get("services").get("vendor_service_uuid"))

    _server_tx = StreamOut(
        uuid=VendorUUID(CONF.get("port").get("uart_ble").get("services").get("vendor_service_tx_uuid")),
        timeout=1.0,
        buffer_size=64, #64
    )

    _server_rx = StreamIn(
        uuid=VendorUUID(CONF.get("port").get("uart_ble").get("services").get("vendor_service_rx_uuid")),
        timeout=1.0,
        buffer_size=64, #64
    )

    def reset(self):
        self._tx.write(bytes("reset", "UTF-8"))