import logging
import aiohttp
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.util.dt import parse_datetime
from .const import DOMAIN, CONF_BUS_LINE, CONF_STATION_NUMBER

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=3)
API_KEY = "YL17615191"

async def async_setup_entry(hass, entry, async_add_entities):
    bus_line = entry.data[CONF_BUS_LINE]
    station = entry.data[CONF_STATION_NUMBER]

    async def async_update_data():
        try:
            url = f"http://moran.mot.gov.il:110/Channels/HTTPChannel/SmQuery/2.8/json?Key={API_KEY}&MonitoringRef={station}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()

            visits = data.get("Siri", {}).get("ServiceDelivery", {}).get("StopMonitoringDelivery", [])[0].get("MonitoredStopVisit", [])
            results = []

            for v in visits:
                journey = v.get("MonitoredVehicleJourney", {})
                if journey.get("PublishedLineName") != bus_line:
                    continue

                monitored_call = journey.get("MonitoredCall", {})
                results.append({
                    "expected": monitored_call.get("ExpectedArrivalTime"),
                    "aimed": monitored_call.get("AimedArrivalTime"),
                    "confidence": journey.get("ConfidenceLevel", "unknown")
                })

                if len(results) >= 2:
                    break

            return results

        except Exception as e:
            _LOGGER.error(f"Error fetching or parsing bus data: {e}")
            return []

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="israel_bus",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    sensors = [
        BusArrivalSensor(coordinator, entry.entry_id, bus_line, station, 0),
        BusArrivalSensor(coordinator, entry.entry_id, bus_line, station, 1),
    ]

    async_add_entities(sensors)


class BusArrivalSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, config_entry_id, bus_line, station, index):
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry_id}_{index}"
        self._attr_name = f"Bus {bus_line}-{station}-{index + 1}"
        self._attr_device_class = "timestamp"
        self.index = index
        self._attr_extra_state_attributes = {}

    @property
    def native_value(self):
        try:
            record = self.coordinator.data[self.index]
            is_live = record.get("confidence") == "probablyReliable"
            self._attr_extra_state_attributes["is_live"] = is_live

            raw_time = record.get("expected" if is_live else "aimed")
            return parse_datetime(raw_time)
        except (IndexError, TypeError, ValueError):
            self._attr_extra_state_attributes["is_live"] = False
            return None

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and len(self.coordinator.data) > self.index
        )
