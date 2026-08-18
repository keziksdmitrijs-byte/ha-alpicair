"""Constants for the AlpicAir ventilation unit integration."""

DOMAIN = "alpicair"

DEFAULT_PORT = 502
DEFAULT_SLAVE = 1
DEFAULT_NAME = "AlpicAir"

CONF_SLAVE = "slave"

# ---------------------------------------------------------------------------
# Modbus register map (SALDA / AlpicAir OEM controller, MCB 1.27 protocol)
# All holding register addresses are 0-based as used by pymodbus.
# ---------------------------------------------------------------------------

REG_SYSTEM_MODE = 1              # 0:Standby 1:BuildingProtection 2:Economy 3:Comfort
REG_COMFORT_SETPOINT = 2         # 160..300 (*0.1 C)
REG_AIR_FLOW_PERCENT = 3         # 0..100 %
REG_ECONOMY_SETPOINT = 4         # 0:EnergySaving, 160..300 (*0.1 C)
REG_BUILDING_PROTECTION_SETPOINT = 6  # 0:EnergySaving, 160..300 (*0.1 C)
REG_INTENSIVE_TIME_LEFT = 107    # seconds, read-only

COIL_DRYNESS_PROTECTION = 3
COIL_NIGHT_COOLING_FUNCTION = 4
COIL_INTENSIVE_AIR_FLOW_BOOST = 5
COIL_FULL_RECIRC_BUILDING_PROTECTION = 6
COIL_FULL_RECIRC_ECONOMY = 7
COIL_AIR_FLOW_CONTROL_BY_RH = 8
COIL_GO_BACK_PREVIOUS_MODE = 53

SYSTEM_MODES = {
    0: "standby",
    1: "building_protection",
    2: "economy",
    3: "comfort",
}
SYSTEM_MODES_REVERSE = {v: k for k, v in SYSTEM_MODES.items()}

MIN_TEMP = 15.0
MAX_TEMP = 25.0
TEMP_STEP = 0.5
