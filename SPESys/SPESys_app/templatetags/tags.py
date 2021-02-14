from django import template
import pandas as pd

register = template.Library()

@register.filter
def lower_(value):
    return value.lower().replace(" ","_")

@register.filter
def get_csv(value,average):
    html = pd.DataFrame(value)
    if average:
        return html.to_html()
    for i in html.columns:
        html.loc['Total',i] = sum(html[i].dropna())
    return html.to_html()
