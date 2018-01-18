# -
HomeAssistant和风天气插件

在HomeAssistant建立以下路径
home assistant\custom_components\sensor

在sensor文件夹下放入HeWeather.py文件


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
