import streamlit as st
import pandas as pd
import altair as alt
import os
import pprint
from vega_datasets import data
import pycountry

st.title('Responsibility and Impact of Climate Change') 
st.header('Clark Kaminsky') 
st.markdown('Every year, humans continue to produce more greenhouse gas emissions as a result of industrialization, travel, and food production. Global warming has been shown to be directly proportional to the amount of carbon dioxide in the atmosphere, which is one of the primary products of burning coal, natural gas, and other fossil fuels. For every 10 parts per million increase in atmospheric carbon dioxide, the mean global temperature has been shown to rise by a tenth of a Celsius degree. In the following chart, we can explore how the levels of carbon dioxide have changed over time. The jagged fluctuations in the graph reflect the decomposition and growth of vegetation, casuing a natural rise and fall each year, but see that the general trend is that carbon dioxide is rising, and the rate of this increase is getting higher each year. The current level of atmospheric carbon dioxide is the highest it has been in anthropogenic history. Feel free to zoom and pan to find specific data.')

# Create dataframes:
coastline_df = pd.read_csv('./data/coastline_lengths.csv', header=1, thousands=',')
ghg_df = pd.read_csv('./data/ghg_EDGAR_country.csv')
co2_df = pd.read_csv('./data/mean_co2_ppm.csv')
# sea_level_df = pd.read_csv('./data/mean_sea_level_global.csv')
sea_level_df = pd.read_csv('./data/sea_level.csv')

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

st.markdown('Atmospheric greenhouse gases have been produced from industrial emissions for many years, but are reaching unprecendented levels in recent years. The EPA measures the United States\'s greenhouse gas emissions by sector, where transportation produces 28%, electricity generation 25%, industry 23%, and agriculture 10% of the country\'s emissions. Naturally, not every country produces the same amount -- in fact, less than 25 countries are responsible for more than half of all historical greenhouse gas emissions. Using the graph below, we can see how drasticly emissions have increased throughout the past half of a century. Additionally, we can see that the emissions are predominantly produced by the same select few nations during this time frame, typically either oil producing nations or developed, wealthy countries.')



def name_to_numeric(country_name):
    try:
        # print(country_name)
        return pycountry.countries.search_fuzzy(country_name)[0].numeric
    except LookupError:
        return -1

# second plot:
ghg_df_cleaned = ghg_df[ghg_df['Country'] != 'GLOBAL TOTAL']
ghg_df_cleaned = ghg_df_cleaned.dropna(subset=['Country'])
ghg_df_cleaned = ghg_df_cleaned[ghg_df_cleaned['Country'] != 'EU27']
ghg_df_cleaned = ghg_df_cleaned[ghg_df_cleaned['Country'] != 'International Shipping']
ghg_df_cleaned = ghg_df_cleaned[ghg_df_cleaned['Country'] != 'International Aviation']
ghg_df_cleaned['Country'] = ghg_df_cleaned['Country'].replace('Italy, San Marino and the Holy See', 'Italy')
ghg_df_cleaned['Country'] = ghg_df_cleaned['Country'].replace('Spain and Andorra', 'Spain')
ghg_df_cleaned['Country'] = ghg_df_cleaned['Country'].replace('France and Monaco', 'France')
ghg_df_cleaned['numeric_code'] = ghg_df_cleaned['Country'].apply(lambda x: name_to_numeric(x))

ghg_melted = ghg_df_cleaned.melt(id_vars=["EDGAR Country Code", "Country", "numeric_code"],var_name="Year",value_name="Emissions")
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


st.markdown('Furthermore, as our carbon dioxide and methane emissions are warming the planet, the global sea level is increasing accordingly. First of all, a warming earth causes water trapped in ice at the poles or in glaciers to melt, directly adding to the sea level, but increased temperature simultaneously causes water to expand, further increasing sea level. This trend can also cause a positive feedback loop: as glacier ice melts, the albedo of the earth is increased, causing the planet to reflect less sunlight and absorb more heat. In the following display, we can see how global mean sea level has risen over the past few decades, already reaching a peak of over 70 mm above the 20 year mean reference.')



sea_level_df.rename(columns={"fld3": "decimal_year", "fld6": "GMSL_mm"}, inplace=True)
zoom2 = alt.selection_interval(bind='scales', encodings=['x'])
nearest2 = alt.selection_point(on='mouseover', nearest=True, empty=False, encodings=['x'])

sea_level_chart = alt.Chart(sea_level_df).mark_line().encode(
    y = alt.Y('GMSL_mm:Q', title='Global Mean Sea Level Variation (mm)'),
    x = alt.X('decimal_year:Q', title='Year', axis=alt.Axis(format='d', title=None), scale=alt.Scale(domain=[1995, 2023])),
    # tooltip=['decimal_year:Q', 'GMSL_mm:Q']
    tooltip=alt.value(None),
).add_params(
    zoom2
)
# sea_level_chart
line = alt.Chart(sea_level_df).mark_rule(size=4, color='lightgray').encode(
    x='decimal_year:Q',
    opacity=alt.condition(nearest2, alt.value(0.7), alt.value(0)),
    tooltip=alt.value(None),
).add_params(
    nearest2
)

points = sea_level_chart.mark_point(size=90, color='firebrick').transform_filter(
    nearest2
).encode(
    opacity=alt.condition(nearest2, alt.value(1), alt.value(0))
)

labels = sea_level_chart.mark_text(align='left', dx=-40, dy=-15).encode(
    text=alt.condition(nearest2, alt.Text('GMSL_mm:Q', format='.2f'), alt.value(' '))
).transform_filter(
    nearest2
)

interactive_sea_level = alt.layer(
    sea_level_chart,
    line,
    points,
    labels
)

st.altair_chart(interactive_sea_level, use_container_width=True)


st.markdown('Sea level rise can increase the rate of extreme weather event occurrences, which has huge impacts on communities, infrastructure, and land. With warmer atmospheres and higher ocean levels, hurricanes, floods, and storm surges will continue to become more common, which all have more impact on coastal countries than those with more landlocked regions. As more than 40% of all humans live within 100 kilometers of the coast, societies will continue to be strongly damaged by the sideeffects of sea level rise and climate change. The following two maps can give a clear idea of which countries have the highest coastline lengths, and which have a higher amount of coastline compared to their area.')


coasts = pd.read_csv('./data/coasts_countries.csv')
world = data.world_110m.url
countries = alt.topo_feature(world, 'countries')
# selection = alt.selection_point(fields=['Country'], empty=False, value=840)

choro = alt.Chart(countries).mark_geoshape(
    stroke='#aaa', strokeWidth=0.25
).transform_lookup(
    # lookup='id', from_=alt.LookupData(data=coasts, key='id', fields=['Country','Coastline Length'])
    lookup='id',from_=alt.LookupData(data=coasts, key='numeric_code', fields=['Country', 'Coastline Length'])
).encode(
    alt.Color('Coastline Length:Q', scale=alt.Scale(type='sqrt',scheme='yellowgreenblue'), legend=alt.Legend(title='Coastline Length (km)')),
    # opacity=alt.condition(selection, alt.value(1), alt.value(0.5)),
    tooltip=['Country:N','Coastline Length:Q']
).project(
    type='equalEarth'
).properties(
    width=600,
    height=450
)

coast_per_area = alt.Chart(countries).mark_geoshape(
    stroke='#aaa', strokeWidth=0.25
).transform_lookup(
    # lookup='id', from_=alt.LookupData(data=coasts, key='id', fields=['Country','Coastline Length'])
    lookup='id',from_=alt.LookupData(data=coasts, key='numeric_code', fields=['Country', 'Coast/area (m/km2)'])
).encode(
    alt.Color('Coast/area (m/km2):Q', scale=alt.Scale(type='sqrt',scheme='yellowgreenblue'), legend=alt.Legend(title='Coast/area ratio (m/km2)')),
    tooltip=['Country:N','Coast/area (m/km2):Q']
).project(
    type='equalEarth'
).properties(
    width=600,
    height=450
)

vertical = (choro & coast_per_area).resolve_scale(
    color='independent'
)
st.altair_chart(vertical, use_container_width=True)

st.markdown('Comparing these maps to the list of countries that have produced the most significant amounts of greenhouse gas emissions, we find very little overlap. Nations like China, the United States, India, and Russia have consistently been top emitters, but small island countries will be disproportionately damaged compared to their contributions to climate change, especially since they are often less affluent, developing nations.')

st.markdown('In conclusion, we have seen that human activities—specifically industrial practices, transportation, and agriculture—have led to a significant and alarming increase in greenhouse gas emissions, intensifying global warming. The correlation between rising carbon dioxide levels and rising global temperatures has now become a clear signal of the accelerating impact humans are having on our planet. As industrialized and wealthy nations continue to dominate the production of greenhouse gas emissions, contributing disproportionately to this existential threat, we approach a difficult and evolving climate justice dilemma. Smaller, less developed nations, particularly island states with extensive coastlines, face devastating repercussions from the rising sea levels and extreme weather events that arise from global warming—disasters to which they have contributed the least. Commitment to sustainable practices, reformed industrial processes, and efforts to protect those most at risk is essential as we as a planet reach the point of no return.')

st.markdown('Data sources: 1. https://edgar.jrc.ec.europa.eu/report_2023 2. https://climate.nasa.gov/vital-signs/carbon-dioxide/?intent=121 3. https://en.wikipedia.org/wiki/List_of_countries_by_length_of_coastline 4.  https://climate.nasa.gov/vital-signs/sea-level/?intent=121')