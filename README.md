# AlpicAir Ventilation Unit — Home Assistant Integration

Custom HACS-integration for controlling **AlpicAir** heat recovery ventilation
units (OEM-manufactured by SALDA, MCB 1.27 controller) over Modbus TCP.

## v0.5.0 — fix "Modbus device returned an error response"

**Root cause:** the discrete inputs read in v0.4.0 spanned addresses 188-209
in a single request (critical alarm, warning, ... night cooling active). The
MCB 1.27 register table shows that 190-199 is only partially defined ("Test
mode" block, not a clean "Reserved" fill), and this SALDA controller returns
a Modbus exception for the *entire* request when it includes those undefined
addresses — which is exactly the "Failed setup, will retry: Modbus device
returned an error response" error reported after install.

**Fix:** the discrete input reads are now split into three independent, tightly
scoped requests:
- Address 188-189 (critical alarm, warning) — 2 registers.
- Address 209 (night cooling active) — 1 register, read separately.
- Address 1-72 (full alarm list) — unchanged, this range has no gaps.

No entities or functionality were removed; only the underlying Modbus read
strategy changed.

## v0.4.0 — measured flow per speed step, night cooling settings

- Measured air flow sensors (m3/h) for all 4 fixed speed steps, supply
  (Input 77-80) and extract (Input 83-86): step 1 = Building protection,
  step 2 = Economy, step 3 = Comfort, step 4 = Boost/Intensive.
- Full Night Cooling configuration as `number` entities (Holding 25-32):
  start/stop time, extract/outdoor temperature thresholds, supply setpoint.
- "Ночное охлаждение сейчас" sensor (Discrete 209).

## v0.3.0 — modes as dropdown, temperatures, filters, diagnostics

- Operating modes as a single **select** dropdown; **Off** as a dedicated button.
- Temperature sensors, filter/diagnostics sensors, configurable 4-speed fan presets.
- Alarm/error visibility with decoded Russian text.
- pymodbus 3.10+ compatibility fix (`device_id=` vs `slave=` auto-detection).

## Installation via HACS

1. HACS → Integrations → three-dot menu → **Custom repositories**.
2. Add `https://github.com/keziksdmitrijs-byte/ha-alpicair`, category **Integration**.
3. Install **AlpicAir Ventilation Unit**, restart Home Assistant.
4. Settings → Devices & Services → **Add Integration** → search "AlpicAir".
5. Enter gateway IP, Modbus TCP port (default 502), slave ID (default 1).

If you already have the integration installed and are hitting the "Modbus
device returned an error response" error, update to this version via HACS,
restart Home Assistant, and the config entry will retry automatically.

## Disclaimer

Not affiliated with or endorsed by AlpicAir or SALDA. Verify register
addresses against your unit's documentation before use.
