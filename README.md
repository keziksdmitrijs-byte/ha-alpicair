# AlpicAir Ventilation Unit — Home Assistant Integration

Custom HACS-integration for controlling **AlpicAir** heat recovery ventilation
units (OEM-manufactured by SALDA, MCB 1.27 controller) over Modbus TCP.

## v0.3.0 — modes as dropdown, temperatures, filters, diagnostics

- Operating modes (Building protection / Economy / Comfort / Intensive boost)
  are now a single **select** dropdown instead of separate buttons.
- **Off (Standby)** stays a dedicated **button** for a clear, single-purpose action.
- Added temperature sensors: supply, extract, exhaust, outdoor, required supply setpoint.
- Added filter/diagnostics sensors: days left until filter replacement, supply/extract
  filter pressure (Pa), heat exchanger pressure, heat transfer efficiency (%).
- Added **number** entities (config category) to tune the 4 fixed fan speed presets
  for both supply and extract air (registers 450-459).
- Added error/alarm visibility: active alarm count, decoded alarm/warning text list
  (from the full MCB 1.27 alarm table), critical alarm / warning boolean flags.
- pymodbus 3.10+ compatibility fix retained (`device_id=` vs `slave=` auto-detection).

## Installation via HACS

1. HACS → Integrations → three-dot menu → **Custom repositories**.
2. Add `https://github.com/keziksdmitrijs-byte/ha-alpicair`, category **Integration**.
3. Install **AlpicAir Ventilation Unit**, restart Home Assistant.
4. Settings → Devices & Services → **Add Integration** → search "AlpicAir".
5. Enter gateway IP, Modbus TCP port (default 502), slave ID (default 1).

## Entities created

| Platform | Entity | Notes |
|---|---|---|
| select | Режим вентиляции | Building protection / Economy / Comfort / Intensive boost |
| button | Выключить (Standby) | Dedicated Off action |
| button | Вернуться в предыдущий режим | Coil 53 |
| number | Целевая температура | Comfort setpoint slider, 15-25°C |
| number | Расход приток/вытяжка, ступень 1-4 | Fan speed presets, 0-100% |
| sensor | Режим системы / Детальное состояние | Text + full state machine (incl. Boost, Preparing, Change filters...) |
| sensor | Температура притока/вытяжки/выброса/наружного воздуха | °C |
| sensor | Осталось дней до замены фильтров | days |
| sensor | Давление приточного/вытяжного фильтра, теплообменника | Pa |
| sensor | КПД теплообменника | % |
| sensor | Количество активных ошибок / Текущие ошибки вентиляции | full list in attributes |
| switch | Защита от сухости, ночное охлаждение, рециркуляция, контроль по влажности | boolean coils |

## Register map (key addresses)

| Function | Address | Register type |
|---|---|---|
| System mode | Holding 1 | R/W |
| Comfort setpoint | Holding 2 | R/W (x0.1 °C) |
| Fan speed presets 1-4 (supply/extract) | Holding 450-459 | R/W (x0.1 %) |
| Intensive air flow boost | Coil 5 | R/W |
| Go back to previous mode | Coil 53 | R/W |
| Supply/extract/exhaust/outdoor temperature | Input 18-21 | R (x0.1 °C, signed) |
| Active alarms count | Input 28 | R |
| Filters days left | Input 30 | R |
| Supply/extract filter pressure | Input 112 / 115 | R (Pa) |
| Heat exchanger pressure | Input 118 | R (Pa) |
| Heat transfer efficiency | Input 125 | R (%) |
| Any critical alarm / any warning | Discrete 188 / 189 | R |
| Individual alarm/warning bits | Discrete 1-72 | R (decoded to Russian text) |

## Disclaimer

Not affiliated with or endorsed by AlpicAir or SALDA. Verify register
addresses against your unit's documentation before use.
