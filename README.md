# HA和风天气插件

## 使用方法：

- 在HA中建立以下路径`home assistant\custom_components\sensor`

![路径图片](https://cdn2.hachina.io/wp-content/uploads/2018/01/BAD9E1C8521A9967023402224ADAB112.jpg)
如果HA中不存在以上路径，请参照图示自行建立即可。

- 在sensor文件夹下放入HeWeather.py文件，此版本文件支持0.63以上HA。
- 由于部分城市没有AQI监测站，所以如果填入你所在的城市导致报错，请使用你的上级城市名称，配置城市名称支持中英文及拼音。

## 配置内容如下

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
      - wind_dir
```