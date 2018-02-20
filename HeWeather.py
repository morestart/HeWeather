import logging
from datetime import timedelta
import voluptuous as vol
import requests
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION, ATTR_FRIENDLY_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity import generate_entity_id
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import track_time_interval
import homeassistant.util.dt as dt_util

_LOGGER = logging.getLogger(__name__)

TIME_BETWEEN_UPDATES = timedelta(seconds=600)

CONF_OPTIONS = "options"
CONF_CITY = "city"
CONF_AQI_CITY = "aqi_city"
CONF_APPKEY = "appkey"

OPTIONS = {
    "fl": ["HeWeather_fl", "体感温度", "mdi:temperature-celsius", "℃"],
    "tmp": ["HeWeather_tmp", "室外温度", "mdi:thermometer", "℃"],
    "hum": ["HeWeather_hum", "室外湿度", "mdi:water-percent", "%Rh"],
    "pcpn": ["HeWeather_pcpn", "降水量", "mdi:weather-rainy", "mm"],
    "pres": ["HeWeather_pres", "大气压", "mdi:debug-step-over", "hPa"],
    "vis": ["HeWeather_vis", "能见度", "mdi:eye", "km"],
    "wind_spd": ["HeWeather_wind_spd", "风速", "mdi:speedometer", "km/h"],
    "wind_sc": ["HeWeather_wind_sc", "风力", "mdi:flag-variant", None],
    "wind_dir": ["HeWeather_wind_dir", "风向", "mdi:weather-windy", None],
    "cond_txt": ["HeWeather_cond_txt", "天气状态", "mdi:presentation", None],
    "qlty": ["HeWeather_qlty", "空气质量", "mdi:beach", None],
    "main": ["HeWeather_main", "主要污染物", "mdi:chart-bar-stacked", None],
    "aqi": ["HeWeather_aqi", "空气质量指数", "mdi:poll", None],
    "pm10": ["HeWeather_pm10", "PM10", "mdi:blur", "μg/m³"],
    "pm25": ["HeWeather_pm25", "PM2.5", "mdi:blur", "μg/m³"],
    "comf": ["HeWeather_comf", "舒适度指数", "mdi:chart-bubble", None],
    "cw": ["HeWeather_cw", "洗车指数", "mdi:car-wash", None],
    "drsg": ["HeWeather_drsg", "穿衣指数", "mdi:tie", None],
    "flu": ["HeWeather_flu", "感冒指数", "mdi:seat-individual-suite", None],
    "sport": ["HeWeather_sport", "运动指数", "mdi:bike", None],
    "uv": ["HeWeather_uv", "紫外线指数", "mdi:sunglasses", None],
    "trav": ["HeWeather_trav", "出行指数", "mdi:bus", None]
}

ATTR_UPDATE_TIME = "更新时间"
ATTRIBUTION = "Powered by He Weather"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CITY): cv.string,
        vol.Required(CONF_APPKEY): cv.string,
        vol.Required(CONF_OPTIONS, default=[]): vol.All(cv.ensure_list, [vol.In(OPTIONS)]),
    }
)


class WeatherData(object):
    def __init__(self, hass, city, appkey, aqi_city):
        self._url = "https://free-api.heweather.com/s6/weather/now?parameters"
        self._air_url = "https://free-api.heweather.com/s6/air/now?parameters"
        self._life_index_url = "https://free-api.heweather.com/s6/weather/lifestyle?parameters"
        self._headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) '
                                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        self._params = {"location": city, "key": appkey}
        self._aqi_params = {"location": aqi_city, "key": appkey}
        self._fl = None
        self._tmp = None
        self._cond_txt = None
        self._wind_spd = None
        self._hum = None
        self._pcpn = None
        self._pres = None
        self._vis = None
        self._wind_sc = None
        self._wind_dir = None
        self._qlty = None
        self._main = None
        self._aqi = None
        self._pm10 = None
        self._pm25 = None
        self._updatetime = None
        self._comf = None
        self._cw = None
        self._drsg = None
        self._flu = None
        self._sport = None
        self._uv = None
        self._trav = None

        self.update(dt_util.now())

        track_time_interval(hass, self.update, TIME_BETWEEN_UPDATES)

    @property
    def fl(self):
        return self._fl

    @property
    def tmp(self):
        return self._tmp

    @property
    def cond_txt(self):
        return self._cond_txt

    @property
    def wind_spd(self):
        return self._wind_spd

    @property
    def wind_dir(self):
        return self._wind_dir

    @property
    def hum(self):
        return self._hum

    @property
    def pcpn(self):
        return self._pcpn

    @property
    def pres(self):
        return self._pres

    @property
    def vis(self):
        return self._vis

    @property
    def wind_sc(self):
        return self._wind_sc

    @property
    def qlty(self):
        return self._qlty

    @property
    def main(self):
        return self._main

    @property
    def aqi(self):
        return self._aqi

    @property
    def pm10(self):
        return self._pm10

    @property
    def pm25(self):
        return self._pm25

    @property
    def comf(self):
        return self._comf

    @property
    def cw(self):
        return self._cw

    @property
    def drsg(self):
        return self._drsg

    @property
    def flu(self):
        return self._flu

    @property
    def sport(self):
        return self._sport

    @property
    def uv(self):
        return self._uv

    @property
    def trav(self):
        return self._trav

    @property
    def updatetime(self):
        return self._updatetime

    def update(self, now):
        _LOGGER.info("Update from HeWeather...")
        try:
            r = requests.get(self._url, self._params, verify=True, headers=self._headers)
            con = r.json()
            self._fl = con["HeWeather6"][0]["now"]["fl"]
            self._cond_txt = con["HeWeather6"][0]["now"]["cond_txt"]
            self._hum = con["HeWeather6"][0]["now"]["hum"]
            self._pcpn = con["HeWeather6"][0]["now"]["pcpn"]
            self._pres = con["HeWeather6"][0]["now"]["pres"]
            self._tmp = con["HeWeather6"][0]["now"]["tmp"]
            self._vis = con["HeWeather6"][0]["now"]["vis"]
            self._wind_spd = con["HeWeather6"][0]["now"]["wind_spd"]
            self._wind_sc = con["HeWeather6"][0]["now"]["wind_sc"]
            self._wind_dir = con["HeWeather6"][0]["now"]["wind_dir"]
        except:
            _LOGGER.info("连接失败")
        try:
            r_air = requests.get(self._air_url, self._aqi_params, verify=True, headers=self._headers)
            con_air = r_air.json()
            self._qlty = con_air["HeWeather6"][0]["air_now_city"]["qlty"]
            self._main = con_air["HeWeather6"][0]["air_now_city"]["main"]
            self._aqi = con_air["HeWeather6"][0]["air_now_city"]["aqi"]
            self._pm10 = con_air["HeWeather6"][0]["air_now_city"]["pm10"]
            self._pm25 = con_air["HeWeather6"][0]["air_now_city"]["pm25"]
        except:
            _LOGGER.info("连接失败")
        
        try:
            life_index = requests.get(self._life_index_url, self._params, verify=True, headers=self._headers)
            con_life_index = life_index.json()
            self._comf = con_life_index["HeWeather6"][0]["lifestyle"][0]["brf"]
            self._drsg = con_life_index["HeWeather6"][0]["lifestyle"][1]["brf"]
            self._flu = con_life_index["HeWeather6"][0]["lifestyle"][2]["brf"]
            self._sport = con_life_index["HeWeather6"][0]["lifestyle"][3]["brf"]
            self._trav = con_life_index["HeWeather6"][0]["lifestyle"][4]["brf"]
            self._uv = con_life_index["HeWeather6"][0]["lifestyle"][5]["brf"]
            self._cw = con_life_index["HeWeather6"][0]["lifestyle"][6]["brf"]
        except:
            _LOGGER.info("连接失败")
        import time
        self._updatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def setup_platform(hass, config, add_devices, discovery_info=None):
    _LOGGER.info("Setup platform sensor.HeWeather")
    city = config.get(CONF_CITY)
    appkey = config.get(CONF_APPKEY)
    aqi_city = config.get(CONF_AQI_CITY)
    data = WeatherData(hass, city, appkey, aqi_city)

    dev = []
    for option in config[CONF_OPTIONS]:
        dev.append(HeWeatherSensor(data, option))
    add_devices(dev, True)


class HeWeatherSensor(Entity):
    def __init__(self, data, option):
        self._data = data
        self._object_id = OPTIONS[option][0]
        self._friendly_name = OPTIONS[option][1]
        self._icon = OPTIONS[option][2]
        self._unit_of_measurement = OPTIONS[option][3]
        self.registry_name = OPTIONS[option][1]
        self._type = option
        self._state = None
        self._updatetime = None

    @property
    def name(self):
        return self._object_id

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return self._icon

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def device_state_attributes(self):
        if self._state is not None:
            return {
                ATTR_ATTRIBUTION: ATTRIBUTION,
                ATTR_FRIENDLY_NAME: self._friendly_name,
                ATTR_UPDATE_TIME: self._updatetime
            }

    def update(self):
        self._updatetime = self._data.updatetime

        if self._type == "fl":
            self._state = self._data.fl
        elif self._type == "tmp":
            self._state = self._data.tmp
        elif self._type == "cond_txt":
            self._state = self._data.cond_txt
        elif self._type == "wind_spd":
            self._state = self._data.wind_spd
        elif self._type == "hum":
            self._state = self._data.hum
        elif self._type == "pcpn":
            self._state = self._data.pcpn
        elif self._type == "pres":
            self._state = self._data.pres
        elif self._type == "vis":
            self._state = self._data.vis
        elif self._type == "wind_sc":
            self._state = self._data.wind_sc
        elif self._type == "wind_dir":
            self._state = self._data.wind_dir
        elif self._type == "qlty":
            self._state = self._data.qlty
        elif self._type == "main":
            self._state = self._data.main
        elif self._type == "aqi":
            self._state = self._data.aqi
        elif self._type == "pm10":
            self._state = self._data.pm10
        elif self._type == "pm25":
            self._state = self._data.pm25
        elif self._type == "cw":
            self._state = self._data.cw
        elif self._type == "comf":
            self._state = self._data.comf
        elif self._type == "drsg":
            self._state = self._data.drsg
        elif self._type == "flu":
            self._state = self._data.flu
        elif self._type == "sport":
            self._state = self._data.sport
        elif self._type == "trav":
            self._state = self._data.trav
        elif self._type == "uv":
            self._state = self._data.uv
