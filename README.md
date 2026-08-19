# AlpicAir Ventilation Unit — v0.6.0

Added editable airflow presets and Night Cooling configuration.

## Editable airflow presets

The existing read-only measured flow sensors (Input Registers 77-86) remain unchanged. New slider entities write to the actual configurable Holding Registers 450-459:

- Supply 1-4: Building protection, Economy, Comfort, Boost — 450-453.
- Extract 1-4: Building protection, Economy, Comfort, Boost — 456-459.

The registers use a 0.1% scale: 300 = 30%, 500 = 50%, 1000 = 100%. The sliders display 0-100% and convert automatically on write [file:16].

## Editable Night Cooling

Night Cooling is now fully configurable through `number` entities:

- Start hour/minute — Holding 25/26.
- Stop hour/minute — Holding 27/28.
- Extract temperature for start/stop — Holding 29/30, x0.1°C.
- Outdoor temperature threshold — Holding 31, x0.1°C.
- Supply temperature setpoint — Holding 32, x0.1°C.

The existing switch controls function enable/disable through Coil 4; the sensor shows whether Night Cooling is currently active via Discrete Input 209 [file:16].

## Other functionality

Mode selection, Standby button, target Comfort temperature, air temperatures, measured flow sensors, filter pressure/days, efficiency and decoded alarms remain available.

## Installation

Install through HACS from `https://github.com/keziksdmitrijs-byte/ha-alpicair`, then restart Home Assistant and add AlpicAir from Settings → Devices & Services.
