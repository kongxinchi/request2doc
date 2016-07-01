h3.{{ url.split('/')[3:]|join('/') }}
METHOD: {{ method }}
----
{%- if request_get_items %}
GET参数:
||Name||Type||Description||
{%- for item in request_get_items %}
| {{ item.name|replace('*', '\*') }} | {{ item.type|replace('|', '\|') }} | {{ item.description|replace('|', '\|') }} |
{%- endfor %}
{%- endif %}

{%- if request_post_items %}
POST参数:
||Name||Type||Description||
{%- for item in request_post_items %}
| {{ item.name|replace('*', '\*') }} | {{ item.type|replace('|', '\|') }} | {{ item.description|replace('|', '\|') }} |
{%- endfor %}
{%- endif %}

{%- if response_items %}
返回字段说明:
||Name||Type||Description||
{%- for item in response_items %}
| {{ item.name|replace('*', '\*') }} | {{ item.type|replace('|', '\|') }} | {{ item.description|replace('|', '\|') }} |
{%- endfor %}
{%- endif %}

{code:title=返回JSON样例|collapse=true}
{{ response_body }}
{code}