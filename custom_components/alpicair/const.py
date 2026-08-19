"""Constants for the AlpicAir ventilation unit integration."""

DOMAIN = "alpicair"

DEFAULT_PORT = 502
DEFAULT_SLAVE = 1
DEFAULT_NAME = "AlpicAir"

CONF_SLAVE = "slave"

# ---------------------------------------------------------------------------
# Modbus register map (SALDA / AlpicAir OEM controller, MCB 1.27 protocol)
# Filtered for domestic units with electrical heater (no DX, no hydronic).
# ---------------------------------------------------------------------------

# --- Holding registers (0x03/0x06/0x10), Read/Write ---
REG_SYSTEM_MODE = 1                    # 0:Standby 1:BuildingProtection 2:Economy 3:Comfort
REG_COMFORT_SETPOINT = 2               # 160..300 (x0.1 C)
REG_AIR_FLOW_PERCENT = 3               # 0..100 %
REG_ECONOMY_SETPOINT = 4               # 0:EnergySaving, 160..300 (x0.1 C)
REG_BUILDING_PROTECTION_SETPOINT = 6   # 0:EnergySaving, 160..300 (x0.1 C)
REG_INTENSIVE_TIME_SET = 14            # 0-18000 s, intensive boost duration
REG_INTENSIVE_TIME_LEFT = 107          # seconds, read-only via holding

# Night cooling settings, Holding registers (User level)
REG_NIGHT_COOLING_START_HOURS = 25      # 0-23
REG_NIGHT_COOLING_START_MINS = 26       # 0-59
REG_NIGHT_COOLING_STOP_HOURS = 27       # 0-23
REG_NIGHT_COOLING_STOP_MINS = 28        # 0-59
REG_NIGHT_COOLING_START_EXTRACT = 29    # 130-300 (x0.1 C) extract temp to start
REG_NIGHT_COOLING_STOP_EXTRACT = 30     # 130-300 (x0.1 C) extract temp to stop
REG_NIGHT_COOLING_START_OUTDOOR = 31    # 0-300 (x0.1 C) outdoor temp to stop
REG_NIGHT_COOLING_SETPOINT = 32         # 0-300 (x0.1 C) supply air setpoint

# Air flow adjustment (4-speed presets, % of nominal), Adjuster level
REG_AIR_FLOW_1_SUPPLY = 450   # Building protection
REG_AIR_FLOW_2_SUPPLY = 451   # Economy
REG_AIR_FLOW_3_SUPPLY = 452   # Comfort
REG_AIR_FLOW_4_SUPPLY = 453   # Boost / Intensive
REG_AIR_FLOW_1_EXTRACT = 456  # Building protection
REG_AIR_FLOW_2_EXTRACT = 457  # Economy
REG_AIR_FLOW_3_EXTRACT = 458  # Comfort
REG_AIR_FLOW_4_EXTRACT = 459  # Boost / Intensive

# --- Coils (0x01/0x05), Read/Write ---
COIL_DRYNESS_PROTECTION = 3
COIL_NIGHT_COOLING_FUNCTION = 4
COIL_INTENSIVE_AIR_FLOW_BOOST = 5
COIL_FULL_RECIRC_BUILDING_PROTECTION = 6
COIL_FULL_RECIRC_ECONOMY = 7
COIL_AIR_FLOW_CONTROL_BY_RH = 8
COIL_GO_BACK_PREVIOUS_MODE = 53

# --- Input registers (0x04), Read only ---
IR_CURRENT_SYSTEM_STATE = 1        # 0-255, detailed state (see SYSTEM_STATE_MAP)
IR_INTENSIVE_TIME_LEFT = 13        # seconds
IR_CURRENT_SYSTEM_MODE = 15        # 0-4
IR_CURRENT_AIR_FLOW = 16           # 0..100 %
IR_REQUIRED_SUPPLY_TEMPERATURE = 17    # x0.1 C
IR_SUPPLY_AIR_TEMPERATURE = 18         # T1, x0.1 C
IR_EXTRACT_AIR_TEMPERATURE = 19        # T2, x0.1 C
IR_EXHAUST_AIR_TEMPERATURE = 20        # T3, x0.1 C
IR_OUTDOOR_AIR_TEMPERATURE = 21        # T4, x0.1 C
IR_SUPPLY_AIR_RH = 22               # x0.1 %
IR_SUPPLY_AIR_CO2 = 23              # ppm
IR_EXTRACT_AIR_RH = 24              # x0.1 %
IR_EXTRACT_AIR_CO2 = 25             # ppm
IR_ACTIVE_ALARMS_COUNT = 28         # 0-100
IR_FILTERS_TIMER_DAYS_LEFT = 30     # 1-365 days

# Measured air flow per fixed speed step (m3/h), read-only
IR_1_SUPPLY_AIR_FLOW = 77    # Building protection
IR_2_SUPPLY_AIR_FLOW = 78    # Economy
IR_3_SUPPLY_AIR_FLOW = 79    # Comfort
IR_4_SUPPLY_AIR_FLOW = 80    # Boost / Intensive
IR_1_EXTRACT_AIR_FLOW = 83   # Building protection
IR_2_EXTRACT_AIR_FLOW = 84   # Economy
IR_3_EXTRACT_AIR_FLOW = 85   # Comfort
IR_4_EXTRACT_AIR_FLOW = 86   # Boost / Intensive

IR_SUPPLY_FILTER_PRESSURE = 112     # Pa
IR_EXTRACT_FILTER_PRESSURE = 115    # Pa
IR_HEAT_EXCHANGER_PRESSURE = 118    # Pa
IR_AFTER_HX_TEMPERATURE = 124       # x0.1 C
IR_HEAT_TRANSFER_EFFICIENCY = 125   # 0-100 %

# --- Discrete inputs (0x02), Read only ---
DI_CRITICAL_ALARM = 188   # any active critical alarm
DI_WARNING = 189          # any active warning
DI_NIGHT_COOLING_FUNCTION = 209  # night cooling currently active

# Individual alarm/warning bits (address -> human message), from Alarm list table
ALARM_MESSAGES = {
    1: "Предупреждение: обрыв ремня ротора",
    2: "Авария: сработала защита камина",
    3: "Предупреждение: активирована защита от сухости",
    4: "Предупреждение: активирована защита от замерзания пластинчатого теплообменника",
    5: "Авария: защита от замерзания теплообменника. Система остановлена.",
    6: "Предупреждение: реле давления защиты от замерзания теплообменника",
    8: "Предупреждение: слишком низкая температура притока",
    9: "Предупреждение: слишком высокая температура притока",
    10: "Авария: слишком низкая температура притока. Система остановлена.",
    11: "Авария: слишком высокая температура притока. Система остановлена.",
    12: "Предупреждение: замените приточный фильтр (реле давления)",
    13: "Предупреждение: замените вытяжной фильтр (реле давления)",
    14: "Предупреждение: истёк таймер замены фильтров",
    15: "Авария: сбой питания, проверьте предохранитель F1",
    16: "Предупреждение: неисправен датчик температуры притока. Аварийный режим.",
    17: "Предупреждение: неисправен датчик температуры вытяжки. Аварийный режим.",
    18: "Предупреждение: неисправен датчик температуры выброса. Аварийный режим.",
    19: "Предупреждение: неисправен датчик наружной температуры. Аварийный режим.",
    23: "Предупреждение: неисправен датчик температуры в шкафу управления. Аварийный режим.",
    24: "Авария: неисправен датчик температуры притока. Система остановлена.",
    25: "Авария: неисправен датчик температуры вытяжки. Система остановлена.",
    26: "Авария: неисправен датчик температуры выброса. Система остановлена.",
    27: "Авария: неисправен датчик наружной температуры. Система остановлена.",
    31: "Авария: неисправен датчик температуры в шкафу управления. Система остановлена.",
    32: "Тест противопожарной заслонки пройден успешно",
    33: "Предупреждение: тест противопожарной заслонки не пройден",
    34: "Авария: ручная защита нагревателя. Система остановлена!",
    35: "Предупреждение: автоматическая защита нагревателя",
    36: "Авария: ручная защита преднагревателя. Система остановлена!",
    37: "Предупреждение: автоматическая защита преднагревателя",
    38: "Авария: отказ приточного вентилятора",
    39: "Авария: отказ вытяжного вентилятора",
    41: "Авария: пожар",
    42: "Авария: защита по давлению приточного вентилятора. Система остановлена.",
    43: "Авария: защита по давлению вытяжного вентилятора. Система остановлена.",
    44: "Авария: внутренняя ошибка системы",
    45: "Авария: ручная защита нагревателя. Форсаж.",
    46: "Авария: ручная защита преднагревателя. Форсаж.",
    47: "Авария: ошибка внутренней связи",
    49: "Предупреждение: высокая влажность вытяжки (3 суток). Увеличение расхода.",
    50: "Предупреждение: высокая влажность вытяжки. Форсаж.",
    51: "Авария: обрыв ремня ротора. Система остановлена.",
    52: "Предупреждение: отказ газового нагревателя",
    53: "Предупреждение: отказ газового преднагревателя",
    54: "Предупреждение: высокий уровень конденсации",
    55: "Предупреждение: отказ приточного вентилятора. Аварийный режим.",
    56: "Предупреждение: отказ вытяжного вентилятора. Аварийный режим.",
    58: "Авария: отказ заслонки байпаса. Система остановлена.",
    61: "Авария: отказ удалённого нагревателя!",
    62: "Предупреждение: отказ удалённого нагревателя!",
    63: "Авария: отказ удалённого преднагревателя!",
    64: "Предупреждение: отказ удалённого преднагревателя!",
    65: "Авария: отказ удалённого охладителя!",
    66: "Предупреждение: отказ удалённого охладителя!",
    67: "Авария: срабатывание противопожарной защиты 2",
    68: "Предупреждение: отказ удалённого нагревателя! Форсаж.",
    69: "Предупреждение: отказ удалённого преднагревателя! Форсаж.",
    70: "Авария: отказ противопожарной заслонки",
    71: "Предупреждение: неисправен датчик температуры после теплообменника. Аварийный режим.",
    72: "Авария: неисправен датчик температуры после теплообменника. Система остановлена.",
}

SYSTEM_STATE_MAP = {
    0: "Ожидание (Stand-by)",
    1: "Защита здания",
    2: "Эконом",
    3: "Комфорт",
    4: "Аварийный режим",
    5: "Подготовка",
    6: "Открытие заслонок",
    7: "Форсаж",
    8: "Охлаждение нагревателей",
    9: "Закрытие заслонок",
    10: "Ночное охлаждение",
    11: "Критическая авария",
    12: "Пожарная тревога",
    13: "Защита теплообменника от замерзания",
    14: "Замена фильтров",
    15: "Ограничение скорости (низкая влажность)",
    17: "Тест противопожарной заслонки",
}

SYSTEM_MODES = {
    0: "standby",
    1: "building_protection",
    2: "economy",
    3: "comfort",
}
SYSTEM_MODES_REVERSE = {v: k for k, v in SYSTEM_MODES.items()}

MODE_LABELS_RU = {
    "standby": "Выключено",
    "building_protection": "Защита здания",
    "economy": "Эконом",
    "comfort": "Комфорт",
}

MIN_TEMP = 15.0
MAX_TEMP = 25.0
TEMP_STEP = 0.5
