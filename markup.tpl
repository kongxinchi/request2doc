{{ url }}
METHOD: {{ method }}
{%- if request_get_dict %}
GET参数:
||Name||Type||Description||
{%- for k, v in request_get_dict.items() %}
| {{ k }} | {{ v }} | |
{%- endfor %}
{%- endif %}

{%- if request_post_dict %}
POST参数:
||Name||Type||Description||
{%- for k, v in request_post_dict.items() %}
| {{ k }} | {{ v }} | |
{%- endfor %}
{%- endif %}

{%- if response_item_list %}
返回字段说明:
||Name||Type||Description||
{%- for item in response_item_list %}
| {{ item.name }} | {{ item.type }} | {{ item.description }} |
{%- endfor %}
{%- endif %}

{code:title=返回JSON样例|collapse=true}
{{ response_body }}
{code}