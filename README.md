# request2doc

Auto generate doc file by request parameter and response body. 
自动根据发送的请求生成API说明文档.

## Usage

usage: request2doc.py [-h] [-d [DATA]] [-t [TEMPLATE]] [-o [OUTPUT]]
                      [-s [SLICE_STARTSWITH]] [-b [COOKIE_JAR]]
                      [url]

positional arguments:
  url                   URL

optional arguments:
  -h, --help            show this help message and exit
  -d [DATA], --data [DATA]
                        POST数据键值对, e.g. key1=value&key2=value
  -t [TEMPLATE], --template [TEMPLATE]
                        模板文件路径，默认为markup.tpl
  -o [OUTPUT], --output [OUTPUT]
                        将文件输出到指定文件，默认为打印到屏幕
  -s [SLICE_STARTSWITH], --slice-startswith [SLICE_STARTSWITH]
                        只打印返回数据中指定域的数据, e.g. data.results
  -b [COOKIE_JAR], --cookie-jar [COOKIE_JAR]
                        cookie-jar文件路径

## Example:
  
   python request2doc.py http://domain/one-method-get-url?key1=value1&key2=value2
   python request2doc.py -d"key1=value1&key2=value2" http://domain/one-method-post-url
   
