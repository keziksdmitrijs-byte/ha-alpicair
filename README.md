# AlpicAir Ventilation Unit — Home Assistant Integration

Custom HACS-integration for controlling **AlpicAir** heat recovery ventilation
units (OEM-manufactured by SALDA on the MCB 1.27 controller platform) over
Modbus TCP.

## Features

- Full HACS installation, no YAML editing required — configuration is done
  through the Home Assistant UI (Config Flow).
- Operating mode buttons: **Standby (Off)**, **Building protection**,
  **Economy**, **Comfort**.
- Target (Comfort) temperature slider, 15–25 °C, step 0.5 °C.
- Intensive air flow boost button.
- "Go back to previous mode" button.
- Read-only sensors: current mode, comfort setpoint, air flow %, intensive
  boost time remaining.
- Auxiliary switches: dryness protection, night cooling, recirculation modes,
  air flow control by relative humidity.

## Installation via HACS

1. HACS → Integrations → the three-dot menu → **Custom repositories**.
2. Add this repository URL, category **Integration**.
3. Find **AlpicAir Ventilation Unit** in the list and install.
4. Restart Home Assistant.
5. Settings → Devices & Services → **Add Integration** → search "AlpicAir".
6. Enter the gateway IP address, Modbus TCP port (default 502) and slave ID
   (default 1).

## Register map

This integration targets the register map filtered for domestic units with
an electrical heater (no DX cooling coil, no hydronic coil), matching the
MCB 1.27 Modbus table:

| Function | Address | Type | Notes |
|---|---|---|---|
| System mode | 1 | Holding, R/W | 0=Standby, 1=Building protection, 2=Economy, 3=Comfort |
| Comfort setpoint | 2 | Holding, R/W | 160–300 → 16.0–30.0 °C (×0.1) |
| Air flow by percent | 3 | Holding, R/W | 0–100 % |
| Intensive boost time left | 107 | Holding, R | seconds |
| Dryness protection | Coil 3 | R/W | boolean |
| Night cooling | Coil 4 | R/W | boolean |
| Intensive air flow boost | Coil 5 | R/W | 1 = activate |
| Full recirculation (building protection) | Coil 6 | R/W | boolean |
| Full recirculation (economy) | Coil 7 | R/W | boolean |
| Air flow control by RH | Coil 8 | R/W | boolean |
| Go back to previous mode | Coil 53 | R/W | 1 = activate |

## Rebranding note

AlpicAir units are OEM-manufactured by SALDA and share the same MCB 1.27
Modbus register map. This integration uses the "AlpicAir" name and icons for
manufacturer/model metadata, but the underlying protocol is identical to the
SALDA Smarty 3R S VER (electrical heater) home unit family.

## Disclaimer

Not affiliated with or endorsed by AlpicAir or SALDA. Use at your own risk;
verify register addresses against your unit's specific Modbus documentation
before use, especially if your unit has DX cooling or a hydronic coil, which
are not covered by this integration.
