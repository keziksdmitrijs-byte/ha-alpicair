"""Constants for AlpicAir Ventilation Unit (SALDA MCB 1.27 OEM)."""
DOMAIN="alpicair"
DEFAULT_PORT=502
DEFAULT_SLAVE=1
DEFAULT_NAME="AlpicAir"
CONF_SLAVE="slave"

# Holding registers, R/W
REG_SYSTEM_MODE=1
REG_COMFORT_SETPOINT=2
REG_AIR_FLOW_PERCENT=3
REG_ECONOMY_SETPOINT=4
REG_BUILDING_PROTECTION_SETPOINT=6
REG_INTENSIVE_TIME_SET=14
REG_INTENSIVE_TIME_LEFT=107

# Night cooling, holding registers 25-32
REG_NC_START_HOURS=25
REG_NC_START_MINS=26
REG_NC_STOP_HOURS=27
REG_NC_STOP_MINS=28
REG_NC_START_EXTRACT=29
REG_NC_STOP_EXTRACT=30
REG_NC_START_OUTDOOR=31
REG_NC_SETPOINT=32

# Configurable fan presets, holding registers; stored as 0.1 percent
REG_FLOW_1_SUPPLY=450
REG_FLOW_2_SUPPLY=451
REG_FLOW_3_SUPPLY=452
REG_FLOW_4_SUPPLY=453
REG_FLOW_1_EXTRACT=456
REG_FLOW_2_EXTRACT=457
REG_FLOW_3_EXTRACT=458
REG_FLOW_4_EXTRACT=459

# Coils
COIL_DRYNESS=3
COIL_NIGHT_COOLING=4
COIL_INTENSIVE_BOOST=5
COIL_FULL_RECIRC_PROTECTION=6
COIL_FULL_RECIRC_ECONOMY=7
COIL_FLOW_BY_RH=8
COIL_GO_BACK=53

# Input registers, read-only
IR_STATE=1
IR_TIME_LEFT=13
IR_MODE=15
IR_CURRENT_FLOW=16
IR_REQUIRED_SUPPLY_TEMP=17
IR_SUPPLY_TEMP=18
IR_EXTRACT_TEMP=19
IR_EXHAUST_TEMP=20
IR_OUTDOOR_TEMP=21
IR_ALARMS_COUNT=28
IR_FILTER_DAYS_LEFT=30
IR_1_SUPPLY_FLOW=77
IR_2_SUPPLY_FLOW=78
IR_3_SUPPLY_FLOW=79
IR_4_SUPPLY_FLOW=80
IR_1_EXTRACT_FLOW=83
IR_2_EXTRACT_FLOW=84
IR_3_EXTRACT_FLOW=85
IR_4_EXTRACT_FLOW=86
IR_SUPPLY_FILTER_PRESSURE=112
IR_EXTRACT_FILTER_PRESSURE=115
IR_HEAT_EXCHANGER_PRESSURE=118
IR_EFFICIENCY=125

# Discrete inputs
DI_CRITICAL=188
DI_WARNING=189
DI_NIGHT_COOLING=209

SYSTEM_MODES={0:"standby",1:"building_protection",2:"economy",3:"comfort"}
MODE_LABELS={"standby":"Выключено","building_protection":"Защита здания","economy":"Эконом","comfort":"Комфорт"}
SYSTEM_STATES={0:"Ожидание",1:"Защита здания",2:"Эконом",3:"Комфорт",4:"Аварийный режим",5:"Подготовка",6:"Открытие заслонок",7:"Форсаж",8:"Охлаждение нагревателей",9:"Закрытие заслонок",10:"Ночное охлаждение",11:"Критическая авария",12:"Пожарная тревога",13:"Защита от замерзания",14:"Замена фильтров",15:"Ограничение скорости",17:"Тест заслонки"}

ALARM_MESSAGES={
1:"Предупреждение: обрыв ремня ротора",2:"Авария: защита камина",3:"Предупреждение: защита от сухости",4:"Предупреждение: защита от замерзания теплообменника",5:"Авария: защита от замерзания. Система остановлена",6:"Предупреждение: реле защиты от замерзания",8:"Предупреждение: низкая температура притока",9:"Предупреждение: высокая температура притока",10:"Авария: низкая температура притока. Система остановлена",11:"Авария: высокая температура притока. Система остановлена",12:"Предупреждение: замените приточный фильтр",13:"Предупреждение: замените вытяжной фильтр",14:"Предупреждение: истёк таймер фильтров",15:"Авария: сбой питания",16:"Предупреждение: датчик притока",17:"Предупреждение: датчик вытяжки",18:"Предупреждение: датчик выброса",19:"Предупреждение: наружный датчик",23:"Предупреждение: датчик шкафа управления",24:"Авария: датчик притока. Система остановлена",25:"Авария: датчик вытяжки. Система остановлена",26:"Авария: датчик выброса. Система остановлена",27:"Авария: наружный датчик. Система остановлена",31:"Авария: датчик шкафа. Система остановлена",33:"Предупреждение: тест противопожарной заслонки",34:"Авария: ручная защита нагревателя",35:"Предупреждение: автоматическая защита нагревателя",38:"Авария: приточный вентилятор",39:"Авария: вытяжной вентилятор",41:"Авария: пожар",42:"Авария: давление приточного вентилятора",43:"Авария: давление вытяжного вентилятора",44:"Авария: внутренняя ошибка",47:"Авария: ошибка внутренней связи",50:"Предупреждение: высокая влажность",54:"Предупреждение: высокий уровень конденсации",55:"Предупреждение: приточный вентилятор",56:"Предупреждение: вытяжной вентилятор",58:"Авария: заслонка байпаса",70:"Авария: противопожарная заслонка",71:"Предупреждение: датчик после теплообменника",72:"Авария: датчик после теплообменника"}

MIN_TEMP=15.0; MAX_TEMP=25.0; TEMP_STEP=0.5
