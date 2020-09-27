# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_table as dt
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', "https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"]
external_scripts = ["https://unpkg.com/leaflet@1.7.1/dist/leaflet.js", "./mapcode.js"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
server = app.server

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

choleraDeaths = pd.read_csv("./Data/choleraDeaths.tsv", sep="\t")
choleraDeaths["Total"] = choleraDeaths.apply(lambda row: row.Death + row.Attack, axis = 1)

choleraDeathForLine = pd.read_csv("./Data/choleraDeaths.tsv", sep="\t")
sumDeaths = choleraDeathForLine["Death"].to_numpy(copy=True)
sumAttacks = choleraDeathForLine["Attack"].to_numpy(copy=True)
for i in range(sumDeaths.size):
    if i != 0:
        sumDeaths[i] = sumDeaths[i - 1] + sumDeaths[i]
        sumAttacks[i] = sumAttacks[i - 1] + sumAttacks[i]
choleraDeathForLine["Total Attacks"] = sumAttacks
choleraDeathForLine["Total Deaths"] = sumDeaths



choleraTable = dt.DataTable(
    id='choleratable',
    columns=[{"name": "Date", "id": "Date"}, {"name": "Attacks", "id": "Attack"}, {"name": "Deaths", "id": "Death"}, {"name": "Total", "id": "Total"}],
    data=choleraDeaths.to_dict('Records')
)

choleraLineFig = go.Figure()
choleraLineFig.add_scatter(x=choleraDeathForLine["Date"], y=choleraDeathForLine["Attack"], name="Attacks", line=dict(color="#ffa600"))
choleraLineFig.add_scatter(x=choleraDeathForLine["Date"], y=choleraDeathForLine["Death"], name="Deaths", line=dict(color="#0388fc"))
choleraLineFig.add_scatter(x=choleraDeathForLine["Date"], y=choleraDeathForLine["Total Attacks"], name="Total Attacks", line=dict(color="#ef5675"))
choleraLineFig.add_scatter(x=choleraDeathForLine["Date"], y=choleraDeathForLine["Total Deaths"], name="Total Deaths", line=dict(color="#003f5c"))

#fig = px.bar(choleraDeaths, x="Date", y=["Death", "Attack"])

naplesData = pd.read_csv("./Data/naplesCholeraAgeSexData.tsv", sep="\t", header = 5)

naplesTable = dt.DataTable(
    id='naplestable',
    columns=[{"name": "Age range", "id":"age"}, {"name": "Male deaths per 10k", "id":"male"}, {"name": "Female deaths per 10k", "id":"female"}],
    data=naplesData.to_dict('Records')
)
naplesMaleFigure = px.bar(naplesData, x="age", y="male", labels={ "age": "Age range (men)", "male": "Deaths per 10,000"}) #, color="male", color_continuous_scale='Plotly3_r'
naplesFemaleFigure = px.bar(naplesData, x="age", y="female", labels={ "age": "Age range (women)", "female": "Deaths per 10,000"})

ukData = pd.read_csv("./Data/UKcensus1851.csv", header = 2)
ukTable = dt.DataTable(
    id='uktable',
    columns=[{"name": "Age range", "id":"age"}, {"name": "Male population", "id":"male"}, {"name": "Female population", "id":"female"}],
    data=ukData.to_dict('Records')
)
ukPieFigMale = px.pie(ukData, values='male', names='age', title='Male population in the UK by age range', labels={"age": "Age range (men)"}, color_discrete_sequence=px.colors.sequential.Plasma)
ukPieFigFemale = px.pie(ukData, values='female', names='age', title='Female population in the UK by age range', labels={"age": "Age range (women)"}, color_discrete_sequence=px.colors.sequential.Plasma)
ukBarMaleFigure = px.bar(ukData, x="age", y="male", labels={ "age": "Age range (men)", "male": "Population"}, color_discrete_sequence=px.colors.sequential.Plasma, color="age")
ukBarFemaleFigure = px.bar(ukData, x="age", y="female", labels={ "age": "Age range (women)", "female": "Population"}, color_discrete_sequence=px.colors.sequential.Plasma, color="age")

ukMaleSum = 0
ukFemaleSum = 0
for i in ukData["male"]:
    ukMaleSum += i
for i in ukData["female"]:
    ukFemaleSum += i
print(ukMaleSum)
print(ukFemaleSum)
sumLabels = ["Men", "Women"]
sumData = [ukMaleSum, ukFemaleSum]

ukPieFigContest = go.Figure(data=[go.Pie(labels=sumLabels, values=sumData)])

pumpData = pd.read_csv("./Data/choleraPumpLocations.csv", header = None, names = ["Long", "Lat"])
deathData = pd.read_csv("./Data/choleraDeathLocations.csv", header = None, names = ["Deaths", "Long", "Lat"])

deathsFig = px.scatter_mapbox(deathData, lat="Lat", lon="Long", size="Deaths", zoom=15, height=600)

deathsFig.add_scattermapbox(lat=pumpData["Lat"], lon=pumpData["Long"], name="Pump location", marker={"color": "#d90441", "size": 16})
deathsFig.update_layout(mapbox_style="carto-positron")
deathsFig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})



app.layout = html.Div(children=[
    html.H1(children='1854 London Cholera Outbreak'),

    html.Div(children='''
        The below table shows the number of cholera attacks & deaths on each day from the 19th of August to the 29th of September, 1854.
    '''),


    html.Div(children=choleraTable, style={'marginBottom': 50, 'marginTop': 25, 'width': 500}),

    html.Div(children='''
    The below graph shows the number of daily cholera attacks & deaths, as well as the total attacks & deaths up to that point, on a day-by-day basis.
'''),
    dcc.Graph(
        id='cholera-graph',
        figure=choleraLineFig
    ),

    html.Div(children='''
    The below table and the following two graphs show the number of deaths per 10,000 inhabitants of Naples, separated by age group and gender.
'''),
    html.Div(children=naplesTable, style={'marginBottom': 50, 'marginTop': 25, 'width': 500}),
    dcc.Graph(
        id='naples-male-graph',
        figure=naplesMaleFigure
    ),
    dcc.Graph(
        id='naples-female-graph',
        figure=naplesFemaleFigure
    ),
    html.Div(children='''
    The below table, and the following 4 graphs, show the breakdown of population by age range in the UK, at around the same time period.
'''),
    html.Div(children=ukTable, style={'marginBottom': 50, 'marginTop': 25, 'width': 500}),
    dcc.Graph(
        id='uk-male-pie',
        figure=ukPieFigMale
    ),
    dcc.Graph(
        id='uk-female-pie',
        figure=ukPieFigFemale
    ),
    dcc.Graph(
        id='uk-male-bar',
        figure=ukBarMaleFigure
    ),
    dcc.Graph(
        id='uk-female-bar',
        figure=ukBarFemaleFigure
    ),
    html.Div(children='''
    Population breakdown of the UK by gender:
'''),
    dcc.Graph(
        id='uk-cont-bar',
        figure=ukPieFigContest
    ),
    html.Div(children='''
    Deaths from cholera near the infamous Broad Street pump, and other nearby pumps
'''),
    dcc.Graph(
        id='uk-map',
        figure=deathsFig
    ),
])

if __name__ == '__main__':
    app.run_server(debug=False)
