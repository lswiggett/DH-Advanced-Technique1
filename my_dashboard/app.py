# My dashboard: the trans-Atlantic slave trade to the Americas, 1520–1866
# (exported from notebook 06). Run locally with:  python app.py   — on Render: gunicorn app:server

import os
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

# --- Data (cleaned in notebook 06) ---
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voyages.csv")
voyages = pd.read_csv(csv_path)

min_year = int(voyages['year_of_arrival'].min())
max_year = int(voyages['year_of_arrival'].max())

# dropdown options for the pie charts: column name -> label
pie_options = {
    'flag': 'Flag of vessel',
    'place_of_purchase': 'Place of purchase (Africa)',
    'place_of_landing': 'Place of landing (Americas)',
    'demographics': 'Women / children / men',
    'resistance_label': 'Resistance',
}

# --- App instance ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA])
server = app.server

# --- Frontend ---
def pie_column(dropdown_id, graph_id, default):
    return dbc.Col([
        dbc.Label("Show the make-up by:", className="fw-bold"),
        dcc.Dropdown(id=dropdown_id,
                     options=[{'label': label, 'value': col} for col, label in pie_options.items()],
                     value=default, clearable=False),
        dcc.Graph(id=graph_id)
    ], xs=12, md=6)

app.layout = dbc.Container(
    [   dbc.Row([ # row 1: title and intro
        dbc.Col([html.H1('The Trans-Atlantic Slave Trade to the Americas, 1520–1866'),
                 html.P('Captives embarked in Africa and disembarked in the Americas, by year of arrival. '
                        'Each record is a slaving voyage; behind every number are enslaved people.')],
        className="text-center mt-3 mb-3")
    ]),
        dbc.Row([ # row 2: year range selector (filters every chart)
            dbc.Label("Select a range of years:", className="fw-bold"),
            dcc.RangeSlider(
                id='year-range',
                min=min_year, max=max_year, step=1,
                value=[min_year, max_year],
                marks={y: str(y) for y in [min_year] + list(range(1550, max_year, 50)) + [max_year]},
                tooltip={"placement": "bottom", "always_visible": True}
            )
    ], className="mb-3"),

        dbc.Row([ # row 3: line chart
            dbc.Col(dcc.Graph(id='line-graph'))
    ]),

        dbc.Row([ # row 4: two pie charts with their own dropdowns
            pie_column('pie-left-var', 'pie-left', 'flag'),
            pie_column('pie-right-var', 'pie-right', 'place_of_landing')
    ]),

        dbc.Row([ # row 5: source
            dbc.Col(html.P(['Source: Trans-Atlantic Slave Trade Database, ',
                            html.A('SlaveVoyages.org', href='https://www.slavevoyages.org/')],
                           className="text-muted small text-center mt-3"))
    ])
    ])

# --- Backend ---
# Backend: chart functions, then the callback that redraws all three charts
def make_line(dff):
    yearly = dff.groupby('year_of_arrival')[['total_embarked', 'total_disembarked']].sum().reset_index()
    yearly = yearly.rename(columns={'total_embarked': 'Embarked', 'total_disembarked': 'Disembarked'})
    yearly = yearly.melt(id_vars='year_of_arrival', var_name='Series', value_name='People')
    fig = px.line(yearly, x='year_of_arrival', y='People', color='Series',
                  title='People embarked in Africa vs. disembarked in the Americas')
    fig.update_layout(xaxis_title='Year of arrival', yaxis_title='Number of people')
    return fig

def short_label(name, max_len=20):
    # shorten long place names so the legend doesn't crowd the chart
    name = name.replace(', port unspecified', ' ')
    return name if len(name) <= max_len else name[:max_len - 1] + '…'

def make_pie(dff, variable):
    label = pie_options[variable]
    if variable == 'demographics':
        # only some voyages recorded the make-up of captives; estimate people from those
        known = dff.dropna(subset=['percent_women', 'percent_children', 'percent_men'])
        df_pie = pd.DataFrame({
            'Group': ['Women', 'Children', 'Men'],
            'People': [(known['percent_women'] * known['total_embarked']).sum(),
                       (known['percent_children'] * known['total_embarked']).sum(),
                       (known['percent_men'] * known['total_embarked']).sum()]
        })
        title = f"{label} (from {len(known):,} voyages with records)"
        names, values = 'Group', 'People'
    elif variable == 'resistance_label':
        # count voyages, only where resistance was recorded
        df_pie = dff['resistance_label'].value_counts().reset_index()
        df_pie.columns = ['Resistance', 'Voyages']
        title = f"{label} (voyages with resistance recorded: {df_pie['Voyages'].sum():,})"
        names, values = 'Resistance', 'Voyages'
    else:
        # share of people embarked; top 10 plus "Others"
        totals = dff.groupby(variable)['total_embarked'].sum().sort_values(ascending=False)
        df_pie = totals.head(10).reset_index()
        df_pie.columns = [label, 'People embarked']
        if len(totals) > 10:
            df_pie.loc[len(df_pie)] = ['Others', totals.iloc[10:].sum()]
        title = f"{label} (share of people embarked)"
        names, values = label, 'People embarked'

    if df_pie[values].sum() == 0:
        fig = px.pie(title=f"{label}: no records in these years")
        return fig
     # short names in the legend; the full name still shows on hover
    df_pie['Full name'] = df_pie[names]
    df_pie[names] = df_pie[names].map(short_label)
    fig = px.pie(df_pie, values=values, names=names, hole=.6, title=title,
                 hover_name='Full name',
                 color_discrete_sequence=px.colors.sequential.RdBu)
    # legend underneath the chart instead of beside it
    return fig

# callback decorator
@app.callback(
    Output('line-graph', 'figure'),
    Output('pie-left', 'figure'),
    Output('pie-right', 'figure'),
    Input('year-range', 'value'),
    Input('pie-left-var', 'value'),
    Input('pie-right-var', 'value')
)

# callback function
def update_output(year_range, left_var, right_var):
    # filter voyages to the selected years
    start_year, end_year = year_range
    mask = (voyages['year_of_arrival'] >= start_year) & (voyages['year_of_arrival'] <= end_year)
    dff = voyages.loc[mask]

    return make_line(dff), make_pie(dff, left_var), make_pie(dff, right_var)

# callback decorator
@app.callback(
    Output('line-graph', 'figure'),
    Output('pie-left', 'figure'),
    Output('pie-right', 'figure'),
    Input('year-range', 'value'),
    Input('pie-left-var', 'value'),
    Input('pie-right-var', 'value')
)

# callback function
def update_output(year_range, left_var, right_var):
    # filter voyages to the selected years
    start_year, end_year = year_range
    mask = (voyages['year_of_arrival'] >= start_year) & (voyages['year_of_arrival'] <= end_year)
    dff = voyages.loc[mask]

    return make_line(dff), make_pie(dff, left_var), make_pie(dff, right_var)

if __name__ == '__main__':
    app.run(debug=True)
