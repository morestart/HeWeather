# HA和风天气插件

## 使用方法：

- 在HA中建立以下路径
    - `home assistant\custom_components\HeWeather\sensor.py`
    - `home assistant\custom_components\HeWeather\manifest.json`
- 或者使用以下命令下载 
    - `curl -O https://raw.githubusercontent.com/morestart/HeWeather/More-than-0.63/sensor.py`
    - `curl -O https://raw.githubusercontent.com/morestart/HeWeather/More-than-0.63/manifest.json`

如果HA中不存在以上路径，请参照图示自行建立即可。

- 在sensor文件夹下放入HeWeather.py文件，此版本文件支持0.63以上HA。
- 由于部分城市没有AQI监测站，所以报错，请使用你的上级城市名称，配置城市名称支持中英文IP及拼音。

## 配置内容如下

``` yaml
sensor:
  - platform: HeWeather
    city: auto_ip 或者 填写城市名称 eg（北京，beijing）
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
      - tmp_max
      - tmp_min
      - pop
```