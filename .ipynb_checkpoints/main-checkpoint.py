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
st.markdown('Every year, humans continue to produce more greenhouse gas emissions as a result of industrialization, travel, and food production. Global warming has been shown to be directly proportional to the amount of carbon dioxide in the atmosphere -- carbon dioxide is one of the primary products of burning coal, natural gas, and other fossil fuels. For every 10 parts per million increase in atmospheric carbon dioxide, the mean global temperature has been shown to rise by a tenth of a Celsius degree. In the following chart, we can explore how the levels of carbon dioxide have changed over time. The jagged fluctuations in the graph reflect the decomposition and growth of vegetation, casuing a natural rise and fall each year, but see that the general trend is that carbon dioxide is rising, and the rate of this increase is getting higher each year. Feel free to zoom and pan to find specific data.')

# Create dataframes:
coastline_df = pd.read_csv('./data/coastline_lengths.csv', header=1, thousands=',')
ghg_df = pd.read_csv('./data/ghg_EDGAR_country.csv')
co2_df = pd.read_csv('./data/mean_co2_ppm.csv')
sea_level_df = pd.read_csv('./data/mean_sea_level_global.csv')

# vis 1
co2_df.rename(columns={'decimal_year': 'Year'}, inplace=True)
zoom = alt.selection_interval(bind='scales', encodings=['x'])
nearest = alt.selection_point(on='mouseover', nearest=True, empty=False, encodings=['x'])

co2_chart = alt.Chart(co2_df).mark_line().encode(
    y = alt.Y('monthly_average:Q', title='CO2 (ppm)'),
    x = alt.X('Year:Q', title='Year', axis=alt.Axis(format='d', title=None), scale=alt.Scale(domain=[1961, 2023])),
    tooltip=alt.value(None),
).add_params(
    zoom
)

vertical_line = alt.Chart(co2_df).mark_rule(size=4, color='lightgray').encode(
    x='Year:Q',
    opacity=alt.condition(nearest, alt.value(0.7), alt.value(0)),
    tooltip=alt.value(None),
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







# second plot:
ghg_df_cleaned = ghg_df[ghg_df['Country'] != 'GLOBAL TOTAL']
ghg_df_cleaned = ghg_df_cleaned[ghg_df_cleaned['Country'] != 'EU27']
ghg_df_cleaned = ghg_df_cleaned[ghg_df_cleaned['Country'] != 'International Shipping']
ghg_df_cleaned = ghg_df_cleaned[ghg_df_cleaned['Country'] != 'International Aviation']
ghg_df_cleaned['Country'] = ghg_df_cleaned['Country'].replace('Italy, San Marino and the Holy See', 'Italy')
ghg_df_cleaned['Country'] = ghg_df_cleaned['Country'].replace('Spain and Andorra', 'Spain')
ghg_df_cleaned['Country'] = ghg_df_cleaned['Country'].replace('France and Monaco', 'France')
ghg_melted = ghg_df_cleaned.melt(id_vars=["EDGAR Country Code", "Country"],var_name="Year",value_name="Emissions")
ghg_melted['Year'] = ghg_melted['Year'].astype(int)

alt.data_transformers.disable_max_rows()
max_emissions = max(ghg_melted.Emissions)
year_slider = alt.binding_range(min=1970, max=2022, step=1)
slider_selection = alt.selection_point(bind=year_slider, fields=['Year'], name="Select", value=2022)

ghg_country_chart = alt.Chart(ghg_melted).mark_bar().add_params(
    slider_selection
).transform_filter(
    slider_selection
).transform_window(
    rank='rank(Emissions)',
    sort=[alt.SortField('Emissions', order='descending')],
    groupby=['Year']
).transform_filter(
    alt.datum.rank <= 15
).encode(
    y=alt.Y('Country:N', sort=alt.EncodingSortField(field='Emissions', order='descending'), axis=alt.Axis(title=None)),
    x=alt.X(
        'Emissions:Q',
        title='Mton CO2 equivalent',
        scale=alt.Scale(domain=(0, max_emissions))
    ),
    color=alt.Color('Emissions:Q', legend=alt.Legend(title="Emissions (Mton CO2 eq)"), scale=alt.Scale(domain=(0, max_emissions), scheme='reds')),
    tooltip=['Country', 'Year', 'Emissions']
)

st.altair_chart(ghg_country_chart, use_container_width=True)




