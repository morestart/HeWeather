# HomeAssistant和风天气插件

## 使用说明

在HomeAssistant建立以下路径
home assistant\custom_components\sensor

在sensor文件夹下放入HeWeather.py文件

## Conf文件配置如下

由于部分城市没有AQI监测站，如果填上你的城市导致报错，请将AQI城市换成你的上级城市

``` yaml
sensor:
  - platform: HeWeather
    city: 你所在的城市
    aqi_city: 最近的有监测站的城市（比如你的上级城市或者你的城市）
    appkey: 你的密钥
    options:
      - fl
      - tmp
      - cond_txt
      - wind_spd
      - hum
      - pcpn
      - pres
      - vis
      - wind_sc
      - aqi
      - main
      - qlty
      - pm10
      - pm25
      - comf
      - cw
      - drsg
      - flu
      - sport
      - trav
      - uv
```