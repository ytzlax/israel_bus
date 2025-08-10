from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_BUS_LINE, CONF_STATION_NUMBER

class IsraelBusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=f"Bus {user_input[CONF_BUS_LINE]}-{user_input[CONF_STATION_NUMBER]}", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_BUS_LINE): str,
                vol.Required(CONF_STATION_NUMBER): str
            })
        )
