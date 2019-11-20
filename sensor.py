import logging
from datetime import timedelta
import voluptuous as vol
import requests
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from requests.exceptions import (
    ConnectionError as ConnectError, HTTPError, Timeout)

_LOGGER = logging.getLogger(__name__)

TIME_BETWEEN_UPDATES = timedelta(minutes=30)

CONF_OPTIONS = "options"
CONF_CITY = "city"
# CONF_AQI_CITY = "aqi_city"
CONF_APPKEY = "appkey"

life_index_list = {"comf_txt": None, "drsg_txt": None, "flu_txt": None,
                   "sport_txt": None, "trav_txt": None, "uv_txt": None, "cw_txt": None}

OPTIONS = dict(fl=["HeWeather_fl", "实时体感温度", "mdi:temperature-celsius", "℃"],
               tmp=["HeWeather_tmp", "实时室外温度", "mdi:thermometer", "℃"],
               hum=["HeWeather_hum", "实时室外湿度", "mdi:water-percent", "%Rh"],
               pcpn=["HeWeather_pcpn", "降水量", "mdi:weather-rainy", "mm"],
               pres=["HeWeather_pres", "大气压", "mdi:debug-step-over", "hPa"],
               vis=["HeWeather_vis", "能见度", "mdi:eye", "km"],
               wind_spd=["HeWeather_wind_spd", "风速", "mdi:speedometer", "km/h"],
               wind_sc=["HeWeather_wind_sc", "风力", "mdi:flag-variant", None],
               wind_dir=["HeWeather_wind_dir", "风向", "mdi:apple-safari", None],
               cond_txt=["HeWeather_cond_txt", "天气状态", "mdi:counter", None],
               qlty=["HeWeather_qlty", "空气质量", "mdi:beach", None],
               main=["HeWeather_main", "主要污染物", "mdi:chart-bar-stacked", None],
               aqi=["HeWeather_aqi", "空气质量指数", "mdi:poll", "AQI"],
               pm10=["HeWeather_pm10", "PM10", "mdi:blur", "μg/m³"],
               pm25=["HeWeather_pm25", "PM2.5", "mdi:blur", "μg/m³"],
               comf=["HeWeather_comf", "舒适度指数", "mdi:chart-bubble", None],
               cw=["HeWeather_cw", "洗车指数", "mdi:car-wash", None],
               drsg=["HeWeather_drsg", "穿衣指数", "mdi:tie", None],
               flu=["HeWeather_flu", "感冒指数", "mdi:seat-individual-suite", None],
               sport=["HeWeather_sport", "运动指数", "mdi:bike", None],
               uv=["HeWeather_uv", "紫外线指数", "mdi:sunglasses", None],
               trav=["HeWeather_trav", "出行指数", "mdi:bus", None],
               tmp_max=["HeWeather_tmp_max", "今日最高温度", "mdi:mdi:thermometer", "℃"],
               tmp_min=["HeWeather_tmp_min", "今日最低温度", "mdi:mdi:thermometer", "℃"],
               pop=["HeWeather_pop", "降水概率", "mdi:weather-rainy", "%"],
               cond_code=[])

ATTR_UPDATE_TIME = "更新时间"
ATTRIBUTION = "Powered by He Weather"
ATTRIBUTION_SUGGESTION = "生活建议"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CITY): cv.string,
        vol.Required(CONF_APPKEY): cv.string,
        vol.Required(CONF_OPTIONS, default=[]): vol.All(cv.ensure_list, [vol.In(OPTIONS)]),
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.info("Setup platform sensor.HeWeather")
    city = config.get(CONF_CITY)
    appkey = config.get(CONF_APPKEY)
    # aqi_city = config.get(CONF_AQI_CITY)
    data = WeatherData(city, appkey)

    dev = []
    for option in config[CONF_OPTIONS]:
        dev.append(HeWeatherSensor(data, option))
    add_entities(dev, True)


class HeWeatherSensor(Entity):
    def __init__(self, data, option):
        self._data = data
        self._object_id = OPTIONS[option][0]
        self._friendly_name = OPTIONS[option][1]
        self._icon = OPTIONS[option][2]
        self._unit_of_measurement = OPTIONS[option][3]
        self._type = option
        self._state = None
        self._updatetime = None

    @property
    def unique_id(self):
        return self._object_id

    @property
    def name(self):
        return self._friendly_name

    # @property
    # def registry_name(self):
    #     return self._friendly_name

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
        global ATTRIBUTION

        if self._friendly_name == "舒适度指数":
            ATTRIBUTION = life_index_list['comf_txt']
        elif self._friendly_name == "穿衣指数":
            ATTRIBUTION = life_index_list["drsg_txt"]
        elif self._friendly_name == "感冒指数":
            ATTRIBUTION = life_index_list["flu_txt"]
        elif self._friendly_name == "运动指数":
            ATTRIBUTION = life_index_list["sport_txt"]
        elif self._friendly_name == "出行指数":
            ATTRIBUTION = life_index_list["trav_txt"]
        elif self._friendly_name == "紫外线指数":
            ATTRIBUTION = life_index_list["uv_txt"]
        elif self._friendly_name == "洗车指数":
            ATTRIBUTION = life_index_list["cw_txt"]
        else:
            ATTRIBUTION = "Powered by HeWeather"

        return {
            ATTR_UPDATE_TIME: self._updatetime,
            ATTRIBUTION_SUGGESTION: ATTRIBUTION,
        }

    def update(self):
        self._data.update()
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
        elif self._type == "tmp_max":
            self._state = self._data.tmp_max
        elif self._type == "tmp_min":
            self._state = self._data.tmp_min
        elif self._type == "pop":
            self._state = self._data.pop


class WeatherData(object):
    def __init__(self, city, appkey):
        self._url = "https://free-api.heweather.com/s6/weather/now"
        self._air_url = "https://free-api.heweather.com/s6/air/now"
        self._life_index_url = "https://free-api.heweather.com/s6/weather/lifestyle"
        self._long_weather_forcasting_url = "https://free-api.heweather.com/s6/weather/forecast"
        self._params = {"location": city, "key": appkey}
        # self._aqi_params = {"location": aqi_city, "key": appkey}
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
        self._tmp_max = None
        self._tmp_min = None
        self._pop = None

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
    def tmp_max(self):
        return self._tmp_max

    @property
    def tmp_min(self):
        return self._tmp_min

    @property
    def pop(self):
        return self._pop

    @property
    def updatetime(self):
        return self._updatetime
    
    def now(self):
        now_weather = requests.post(self._url, self._params)
        con = now_weather.json()
        return con

    def air(self):
        r_air = requests.post(self._air_url, self._params)
        con_air = r_air.json()
        return con_air

    def life(self):
        life_index = requests.post(self._life_index_url, self._params)
        con_life_index = life_index.json()
        return con_life_index

    def today(self):
        today_weather = requests.post(self._long_weather_forcasting_url, self._params)
        con_today_weather = today_weather.json()
        return con_today_weather

    @Throttle(TIME_BETWEEN_UPDATES)
    def update(self):
        import time
        try:
            con = self.now()
        except (ConnectError, HTTPError, Timeout, ValueError) as error:
            time.sleep(0.01)
            con = self.now()
            _LOGGER.error("Unable to connect to HeWeather. %s", error)
        try:
            con_air = self.air()
        except (ConnectError, HTTPError, Timeout, ValueError) as error:
            time.sleep(0.01)
            con_air = self.air()
            _LOGGER.error("Unable to connect to HeWeather. %s", error)
        try:
            con_life_index = self.life()
        except (ConnectError, HTTPError, Timeout, ValueError) as error:
            time.sleep(0.01)
            con_life_index = self.life()
            _LOGGER.error("Unable to connect to HeWeather. %s", error)
        try:
            today_weather = self.today()
        except (ConnectError, HTTPError, Timeout, ValueError) as error:
            time.sleep(0.01)
            today_weather = self.today()
            _LOGGER.error("Unable to connect to HeWeather. %s", error)

        _LOGGER.info("Update from HeWeather...")
        try:
            self._fl = con.get("HeWeather6")[0].get("now").get("fl")
            self._cond_txt = con.get("HeWeather6")[0].get("now").get("cond_txt")
            self._hum = con.get("HeWeather6")[0].get("now").get("hum")
            self._pcpn = con.get("HeWeather6")[0].get("now").get("pcpn")
            self._pres = con.get("HeWeather6")[0].get("now").get("pres")
            self._tmp = con.get("HeWeather6")[0].get("now").get("tmp")
            self._vis = con.get("HeWeather6")[0].get("now").get("vis")
            self._wind_spd = con.get("HeWeather6")[0].get("now").get("wind_spd")
            self._wind_dir = con.get("HeWeather6")[0].get("now").get("wind_dir")

            self._cond_code = con.get("HeWeather6")[0].get("now").get("cond_code")

            self._qlty = con_air.get("HeWeather6")[0].get("air_now_city").get("qlty")
            self._aqi = con_air.get("HeWeather6")[0].get("air_now_city").get("aqi")
            self._pm10 = con_air.get("HeWeather6")[0].get("air_now_city").get("pm10")
            self._pm25 = con_air.get("HeWeather6")[0].get("air_now_city").get("pm25")
            if con_air.get("HeWeather6")[0].get("air_now_city").get("main") == "-":
                if int(self._pm10) > int(self._pm25):
                    self._main = "PM10"
                elif int(self._pm10) < int(self._pm25):
                    self._main = "PM25"
                else:
                    self._main = "-"
            else:
                self._main = con_air.get("HeWeather6")[0].get("air_now_city").get("main")

            self._comf = con_life_index.get("HeWeather6")[0].get("lifestyle")[0].get("brf")
            self._drsg = con_life_index.get("HeWeather6")[0].get("lifestyle")[1].get("brf")
            self._flu = con_life_index.get("HeWeather6")[0].get("lifestyle")[2].get("brf")
            self._sport = con_life_index.get("HeWeather6")[0].get("lifestyle")[3].get("brf")
            self._trav = con_life_index.get("HeWeather6")[0].get("lifestyle")[4].get("brf")
            self._uv = con_life_index.get("HeWeather6")[0].get("lifestyle")[5].get("brf")
            self._cw = con_life_index.get("HeWeather6")[0].get("lifestyle")[6].get("brf")
            life = ["comf_txt", "drsg_txt", "flu_txt", "sport_txt", "trav_txt", "uv_txt", "cw_txt"]
            for i, index in enumerate(life):
                life_index_list[index] = con_life_index["HeWeather6"][0]["lifestyle"][i]["txt"]

            self._tmp_max = today_weather.get("HeWeather6")[0].get("daily_forecast")[0].get("tmp_max")
            self._tmp_min = today_weather.get("HeWeather6")[0].get("daily_forecast")[0].get("tmp_min")
            self._pop = today_weather.get("HeWeather6")[0].get("daily_forecast")[0].get("pop")
            self._wind_sc = today_weather.get("HeWeather6")[0].get("daily_forecast")[0].get("wind_sc")
        except Exception as e:
            logging.info(e)

        import time
        self._updatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
