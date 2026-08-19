# AlpicAir Ventilation Unit — Home Assistant Integration

Custom HACS-integration for controlling **AlpicAir** heat recovery ventilation
units (OEM-manufactured by SALDA, MCB 1.27 controller) over Modbus TCP.

## v0.4.0 — measured flow per speed step, night cooling settings

- Added **measured air flow sensors** (m3/h) for all 4 fixed speed steps, both
  supply and extract, read from Input registers 77-80 (supply) and 83-86
  (extract): step 1 = Building protection, step 2 = Economy, step 3 = Comfort,
  step 4 = Boost/Intensive.
- Added full **Night Cooling** configuration as `number` entities: start/stop
  time (hours+minutes), extract air temperature thresholds for start/stop,
  outdoor temperature threshold for stop, and supply air setpoint (Holding
  registers 25-32).
- Added "Ночное охлаждение сейчас" sensor (from discrete input 209) showing
  whether the function is currently running.
- Kept the existing Night cooling enable/disable switch (Coil 4).

## v0.3.0 — modes as dropdown, temperatures, filters, diagnostics

- Operating modes (Building protection / Economy / Comfort / Intensive boost)
  are a single **select** dropdown; **Off (Standby)** stays a dedicated button.
- Temperature sensors: supply, extract, exhaust, outdoor, required supply setpoint.
- Filter/diagnostics sensors: days left, supply/extract filter pressure, HX
  pressure, heat transfer efficiency.
- Configurable 4-speed fan presets (% of nominal) for supply and extract.
- Alarm/error visibility: active alarm count, decoded text list, critical/warning flags.
- pymodbus 3.10+ compatibility fix (`device_id=` vs `slave=` auto-detection).

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
| button | Выключить (Standby) / Вернуться в предыдущий режим | |
| number | Целевая температура | Comfort setpoint slider, 15-25°C |
| number | Расход приток/вытяжка, ступень 1-4 | Fan speed % presets (config category) |
| number | Ночное охлаждение: время начала/окончания, пороги t, уставка притока | 8 entities (config category) |
| sensor | Режим системы / Детальное состояние | |
| sensor | Температура притока/вытяжки/выброса/наружного воздуха | °C |
| sensor | Расход приток/вытяжка, факт. ступень 1-4 | m³/h, measured, read-only |
| sensor | Осталось дней до замены фильтров / давление фильтров / КПД | |
| sensor | Количество активных ошибок / Текущие ошибки вентиляции | full list in attributes |
| sensor | Ночное охлаждение сейчас | Активно / Не активно |
| switch | Защита от сухости, ночное охлаждение (вкл/выкл), рециркуляция, контроль по влажности | |

## Register map (key addresses)

| Function | Address | Register type |
|---|---|---|
| System mode | Holding 1 | R/W |
| Comfort setpoint | Holding 2 | R/W (x0.1 °C) |
| Night cooling settings | Holding 25-32 | R/W |
| Fan speed presets 1-4 (supply/extract) | Holding 450-459 | R/W (x0.1 %) |
| Intensive air flow boost | Coil 5 | R/W |
| Night cooling enable | Coil 4 | R/W |
| Supply/extract/exhaust/outdoor temperature | Input 18-21 | R (x0.1 °C, signed) |
| Measured air flow per speed step (supply) | Input 77-80 | R (m3/h) |
| Measured air flow per speed step (extract) | Input 83-86 | R (m3/h) |
| Active alarms count / Filters days left | Input 28 / 30 | R |
| Supply/extract filter pressure / HX pressure | Input 112 / 115 / 118 | R (Pa) |
| Heat transfer efficiency | Input 125 | R (%) |
| Any critical alarm / any warning / night cooling active | Discrete 188 / 189 / 209 | R |
| Individual alarm/warning bits | Discrete 1-72 | R (decoded to Russian text) |

## Disclaimer

Not affiliated with or endorsed by AlpicAir or SALDA. Verify register
addresses against your unit's documentation before use.
