import logging
from datetime import datetime, timedelta, timezone
import requests
from dateutil import parser
import pytz

from homeassistant.components.sensor import SensorEntity

DOMAIN = "israel_bus"
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    config = hass.data[DOMAIN][config_entry.entry_id]
    line = config["מס׳ קו"]
    stop = config["מס׳ תחנה"]
    agency = config["חברת אוטובוסים"]
    sensor_friendly_name = config.get("שם סנסור קליט", "") or ""
    async_add_entities([BusSensor(line, stop, agency, sensor_friendly_name)], update_before_add=True)

class BusSensor(SensorEntity):
    def __init__(self, line, stop, agency, sensor_friendly_name):
        self._line = line
        self._stop = stop
        self._agency = agency
        self.sensor_friendly_name = sensor_friendly_name
        self._attr_name = f"Bus {line} at stop {stop}"
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}
        self._attr_device_class = "timestamp"

    def update(self):
        try:
            # נחשב את טווח הזמנים ב-UTC כפי שנדרש על ידי ה-API
            now_utc = datetime.now(timezone.utc)
            arrival_from = now_utc.isoformat(timespec="seconds")
            arrival_to = (now_utc + timedelta(minutes=30)).isoformat(timespec="seconds")

            url = "https://open-bus-stride-api.hasadna.org.il/gtfs_ride_stops/list"
            params = {
                "get_count": "false",
                "arrival_time_from": arrival_from,
                "arrival_time_to": arrival_to,
                "gtfs_stop__code": self._stop,
                "gtfs_route__route_short_name": self._line,
                "gtfs_route__agency_name": self._agency,
                "order_by": "id asc"
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                self._attr_native_value = None
                self._attr_extra_state_attributes = {"next_buses": []}
                return

            # המרה לשעון ישראל
            israel_tz = pytz.timezone("Asia/Jerusalem")
            arrival_times = []
            for item in data:
                utc_time = parser.isoparse(item["arrival_time"])
                local_time = utc_time.astimezone(israel_tz)
                arrival_times.append(local_time)

            self._attr_native_value = arrival_times[0]
            self._attr_extra_state_attributes = {
                "next_buses": arrival_times[1:],
                "line_number": self._line,
                "sensor_friendly_name": self.sensor_friendly_name,
                "stop_name": data[0].get("gtfs_stop__name", "Unknown")
            }

        except Exception as e:
            _LOGGER.error("Error fetching bus data: %s", e)
            self._attr_native_value = None
            self._attr_extra_state_attributes = {"next_buses": []}
