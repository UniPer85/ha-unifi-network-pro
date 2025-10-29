"""Constants for the UniFi Network Pro integration."""

DOMAIN = "unifi_network_pro"

CONF_SITE_ID = "site_id"
DEFAULT_SITE_ID = "default"

# UniFi API endpoints
API_LOGIN = "/api/auth/login"
API_LOGOUT = "/api/auth/logout"
API_CLIENTS = "/proxy/network/api/s/{site}/stat/sta"
API_DEVICES = "/proxy/network/api/s/{site}/stat/device"
API_HEALTH = "/proxy/network/api/s/{site}/stat/health"
API_SYSTEM_INFO = "/proxy/network/api/s/{site}/stat/sysinfo"

# Device tracker attributes
ATTR_IP_ADDRESS = "ip"
ATTR_MAC_ADDRESS = "mac"
ATTR_HOSTNAME = "hostname"
ATTR_CONNECTION_TYPE = "connection_type"
ATTR_LAST_SEEN = "last_seen"
ATTR_RX_BYTES = "rx_bytes"
ATTR_TX_BYTES = "tx_bytes"
ATTR_SIGNAL = "signal"
ATTR_UPTIME = "uptime"

# Sensor types
SENSOR_CONNECTED_CLIENTS = "connected_clients"
SENSOR_WAN_DOWNLOAD = "wan_download"
SENSOR_WAN_UPLOAD = "wan_upload"
SENSOR_LAN_DOWNLOAD = "lan_download"
SENSOR_LAN_UPLOAD = "lan_upload"
SENSOR_CPU_USAGE = "cpu_usage"
SENSOR_MEMORY_USAGE = "memory_usage"
SENSOR_UPTIME = "uptime"
SENSOR_WAN_IP = "wan_ip"
