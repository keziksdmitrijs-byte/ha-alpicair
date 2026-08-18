# AlpicAir Ventilation Unit — Home Assistant Integration

Custom HACS-integration for controlling **AlpicAir** heat recovery ventilation
units (OEM-manufactured by SALDA, MCB 1.27 controller) over Modbus TCP.

## v0.2.0 — pymodbus compatibility fix

Fixed: `Modbus read failed: ModbusClientMixin.read_holding_registers() got an
unexpected keyword argument 'slave'`.

pymodbus 3.10.0 renamed the `slave=` keyword argument to `device_id=` on all
client calls. This integration now detects the installed pymodbus version at
runtime and uses the correct keyword automatically (`device_id` on
pymodbus >= 3.10.0, `slave` on older releases), so it keeps working across
Home Assistant/pymodbus upgrades.

## Installation via HACS

1. HACS → Integrations → three-dot menu → **Custom repositories**.
2. Add `https://github.com/keziksdmitrijs-byte/ha-alpicair`, category **Integration**.
3. Install **AlpicAir Ventilation Unit**, restart Home Assistant.
4. Settings → Devices & Services → **Add Integration** → search "AlpicAir".
5. Enter gateway IP, Modbus TCP port (default 502), slave ID (default 1).

## Features

- Config Flow setup through the UI, no YAML editing required.
- Mode buttons: Standby (Off), Building protection, Economy, Comfort.
- Target (Comfort) temperature slider, 15-25 °C, step 0.5 °C.
- Intensive air flow boost button + "go back to previous mode" button.
- Read-only sensors: current mode, comfort setpoint, air flow %, boost time left.
- Auxiliary switches: dryness protection, night cooling, recirculation modes,
  air flow control by relative humidity.

## Register map

| Function | Address | Type |
|---|---|---|
| System mode | 1 | Holding, R/W |
| Comfort setpoint | 2 | Holding, R/W (x0.1 °C) |
| Air flow % | 3 | Holding, R/W |
| Intensive boost time left | 107 | Holding, R |
| Dryness protection | Coil 3 | R/W |
| Night cooling | Coil 4 | R/W |
| Intensive air flow boost | Coil 5 | R/W |
| Full recirculation (building protection) | Coil 6 | R/W |
| Full recirculation (economy) | Coil 7 | R/W |
| Air flow control by RH | Coil 8 | R/W |
| Go back to previous mode | Coil 53 | R/W |

## Disclaimer

Not affiliated with or endorsed by AlpicAir or SALDA. Verify register
addresses against your unit's documentation before use.
