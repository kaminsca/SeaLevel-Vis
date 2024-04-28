import streamlit as st
import pandas as pd
import altair as alt
import os
import pprint
from vega_datasets import data
import pycountry

st.title('Who Does Climate Change Really Affect?') 
st.header('Clark Kaminsky') 
st.subheader('4/28/2024')
st.markdown('This is where I write my text.')

# Create dataframes:
coastline_df = pd.read_csv('./data/coastline_lengths.csv', header=1, thousands=',')
ghg_df = pd.read_csv('./data/ghg_EDGAR_country.csv')
co2_df = pd.read_csv('./data/mean_co2_ppm.csv')
sea_level_df = pd.read_csv('./data/mean_sea_level_global.csv')

# vis 1
co2_df.rename(columns={'Year': 'Year'}, inplace=True)
zoom = alt.selection_interval(bind='scales', encodings=['x'])
nearest = alt.selection_point(on='mouseover', nearest=True, empty=False, encodings=['x'])

co2_chart = alt.Chart(co2_df).mark_line().encode(
    y = alt.Y('monthly_average:Q', title='CO2 (ppm)'),
    x = alt.X('Year:Q', title='Year', axis=alt.Axis(format='d', title=None), scale=alt.Scale(domain=[1961, 2023]))
).add_params(
    zoom
)

vertical_line = alt.Chart(co2_df).mark_rule(size=4, color='lightgray').encode(
    x='Year:Q',
    opacity=alt.condition(nearest, alt.value(0.7), alt.value(0)),
).add_params(
    nearest
)

interaction_dots = co2_chart.mark_point(size=90, color='firebrick').transform_filter(
    nearest
).encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

text_labels = co2_chart.mark_text(align='left', dx=-40, dy=-15).encode(
    text=alt.condition(nearest, alt.Text('monthly_average:Q', format='.2f'), alt.value(' '))
).transform_filter(
    nearest
)

interactive_co2 = alt.layer(
    co2_chart,
    vertical_line,
    interaction_dots,
    text_labels
).configure_axis(
    labelFontSize=12,
    labelFont='Roboto',
)
# interactive_co2

st.altair_chart(interactive_co2, use_container_width=True)