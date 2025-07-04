from homeassistant import config_entries
import voluptuous as vol

DOMAIN = "israel_bus"


class IsraelBusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=f"קווי {user_input['מס׳ קו']} - תחנה {user_input['מס׳ תחנה']}", data=user_input)

        schema = vol.Schema({
            vol.Required("מס׳ קו"): str,
            vol.Required("מס׳ תחנה"): str,
            vol.Required("חברת אוטובוסים"): str,
            vol.Optional("שם סנסור קליט"): str

        })

        return self.async_show_form(step_id="user", data_schema=schema)