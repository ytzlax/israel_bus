# 🚌 Home Assistant Integration: Israel Bus

**Israel Bus** is a custom [Home Assistant](https://www.home-assistant.io/) integration that provides upcoming bus arrival times in Israel using data from the [Hasadna OpenBus API](https://openbus-stride-api.hasadna.org.il/).

This integration creates timestamp-based sensors that can trigger automations, display arrival times on dashboards, and more.

---

## ✅ Features

- 🕒 Sensor shows next arrival time as a proper timestamp (for automations).
- 📋 Attributes include additional upcoming arrival times.
- 🗺️ Displays the name of the stop.
- 🧠 Supports multiple sensors for different stops and lines.
- ⚙️ Configurable via the Home Assistant UI (no YAML required).
- 🌍 Timezone-aware (Asia/Jerusalem).

---

## 📦 Installation

### Manual (ZIP)

1. [Download the latest ZIP](https://github.com/YOUR_USERNAME/israel_bus/archive/refs/heads/main.zip) and extract it.
2. Copy the folder `custom_components/israel_bus` into your Home Assistant configuration directory:
3. Restart Home Assistant.

### Add via HACS (coming soon)

---

## 🧭 Setup

1. Go to **Settings → Devices & Services → + Add Integration**.
2. Search for `Israel Bus`.
3. Enter the following:
- **Line Number** (e.g., `504`)
- **Stop Code** (e.g., `1403`)
- **Bus Operator Name** (e.g., `סופרבוס`)
- Optionally: a friendly name for the sensor
4. Click **Submit**.

---

## 🖼️ Example Lovelace Card

```yaml
type: entities
title: התחנה שלי
entities:
- entity: sensor.bus_504_at_stop_1403
 name: קו 504
 icon: mdi:bus


🙌 Contributions
Pull requests and feedback are welcome!