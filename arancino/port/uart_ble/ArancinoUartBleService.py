from adafruit_ble.characteristics.stream import StreamIn, StreamOut
from adafruit_ble.uuid import VendorUUID
from adafruit_ble.services.nordic import UARTService
from arancino.utils.ArancinoUtils import ArancinoConfig

CONF = ArancinoConfig.Instance()

class ArancinoUartBleService(UARTService):
    _server_tx = StreamOut(
        uuid=VendorUUID(CONF.get_port_uart_ble_vendor_tx_uuid()),
        timeout=CONF.get_port_uart_ble_timeout(),
        buffer_size=CONF.get_port_uart_ble_buffer_size(), #64
    )
    _server_rx = StreamIn(
        uuid=VendorUUID(CONF.get_port_uart_ble_vendor_rx_uuid()),
        timeout=CONF.get_port_uart_ble_timeout(),
        buffer_size=CONF.get_port_uart_ble_buffer_size(),
    )