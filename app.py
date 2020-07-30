# https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/

from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

url = 'https://raw.githubusercontent.com/frodoCombs/covid_dash/master/covid.csv'
cases = pd.read_csv(url,sep=",")
print(cases.head(5))
by_state = cases.drop(columns=['County Name','stateFIPS','countyFIPS'])
by_state = by_state.groupby(by_state['State'],as_index=False).sum()
by_state = pd.melt(by_state,id_vars='State')

states = by_state.State.unique()
states.sort()
	
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
	html.H3("Choose which states to visualize"),
	html.Div([dcc.Checklist(id='state-select', options=[{'label': i, 'value': i} for i in states],
						   value=states, style={'width': '75%'})]),
	html.H3("Choose the date range"),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=dt(2020, 1, 22),
        max_date_allowed=dt(2020, 7, 27),
        initial_visible_month=dt(2020, 2, 1),
		start_date=dt(2020,1,22).date(),
        end_date=dt(2020,7,27).date()
    ),
	dcc.Graph('lines', config={'displayModeBar': False})])

@app.callback(
	Output('lines', 'figure'),
	[Input('state-select', 'value'),
	Input('my-date-picker-range', 'start_date'),
	Input('my-date-picker-range', 'end_date')]
)
def update_graph(grpnames,start_date,end_date):
	# format date to use as range
	start_date = start_date.split('-')
	end_date = end_date.split('-')
	start_date = dt(int(start_date[0]),int(start_date[1]),int(start_date[2])).date().strftime("%m/%d/%y")
	end_date = dt(int(end_date[0]),int(end_date[1]),int(end_date[2])).date().strftime("%m/%d/%y")
	start = dt.strptime(start_date, "%m/%d/%y")
	end = dt.strptime(end_date, "%m/%d/%y")
	date_range = [start + timedelta(days=x) for x in range(0, (end-start).days)]
	date_range = [d.strftime("%#m/%#d/%y")for d in date_range]

	# Plot the data
	df = by_state.copy()
	df = df[df['State'].isin(grpnames)]
	df = df[df['variable'].isin(date_range)]
	import plotly.express as px
	return px.line(
	data_frame=df,x='variable',y='value',color='State',
	labels ={'variable':'Date','value':'# of Confirmed Cases'}
	)

if __name__ == '__main__':
    app.run_server(debug=False)
