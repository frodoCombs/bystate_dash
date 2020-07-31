# https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/

from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


#url = 'https://raw.githubusercontent.com/frodoCombs/covid_dash/master/covid.csv'
cases = pd.read_csv('covid.csv',sep=",")

by_state = cases.drop(columns=['County Name','stateFIPS','countyFIPS'])
by_state = by_state.groupby(by_state['State'],as_index=False).sum()

states = by_state.State.unique()
states.sort()
	
#button color
wh = {'font-size':'18px','background-color':'white','height':'40px','width': '110px','border-width':'1px','border-style':'solid','border-radius':'2px',
'border-color':'Gainsboro','font-weight':'bold','margin-left':'30px'}
rd = {'font-size':'18px','background-color': 'blue','height':'40px','width': '110px','border-width':'1px','border-radius':'2px','border-style':'solid',
'border-color':'Gainsboro','font-weight':'bold','color':'white','margin-left':'30px'}


app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children = [
	html.H1("Confirmed Covid-19 Cases - by state"),
	html.H4("Choose which states to visualize"),
	html.Div([dcc.Checklist(id='state-select', 
			options=[{'label': i, 'value': i} for i in states],
			value=['NY','TX'], labelStyle={'display':'inline-block'},
			style={'width':'70%','margin':'auto'})]),
	html.Button('All States',id='button',n_clicks=0,style=wh),
	html.H4("Choose the date range"),
	dcc.DatePickerRange(
		id='my-date-picker-range',
		min_date_allowed=dt(2020, 1, 22), max_date_allowed=dt(2020, 7, 30),
		initial_visible_month=dt(2020, 2, 1), start_date=dt(2020,1,22).date(),
		end_date=dt(2020,7,29).date(),style={'margin-left':'30px'}),
	dcc.Graph('lines', config={'displayModeBar': False}),
	html.Hr(),
	html.P(["This interactive graph was created by ",dcc.Link('Ford Combs',href="https://medium.com/@fordcombs",refresh=True), " using the ",dcc.Link('Dash framework.',href="https://dash.plotly.com/introduction",refresh=True), " The data can be downloaded ",dcc.Link('here',href="https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/",refresh=True),'.'])
	])

@app.callback(
	[Output('lines', 'figure'),Output('button', 'style')],
	[Input('state-select', 'value'),
	Input('button','n_clicks'),
	Input('my-date-picker-range', 'start_date'),
	Input('my-date-picker-range', 'end_date'),]
)
def update_graph(grpnames,clicks,start_date,end_date):
	if clicks%2 > 0:
		style = rd
	else:
		style = wh
		
	# format date to use as range
	start_date = start_date.split('-')
	end_date = end_date.split('-')
	start_date = dt(int(start_date[0]),int(start_date[1]),int(start_date[2])).date().strftime("%m/%d/%y")
	end_date = dt(int(end_date[0]),int(end_date[1]),int(end_date[2])).date().strftime("%m/%d/%y")
	start = dt.strptime(start_date, "%m/%d/%y")
	end = dt.strptime(end_date, "%m/%d/%y")
	date_range = [start + timedelta(days=x) for x in range(0, (end-start).days)]
	date_range = [d.strftime("%-m/%-d/%y")for d in date_range]
	
	# Plot the data
	df = by_state.copy()
	df = pd.melt(df,id_vars='State')
	if style == rd:
		pass
	else:
		df = df[df['State'].isin(grpnames)]
	df = df[df['variable'].isin(date_range)]

	
	import plotly.express as px
	plot = px.line(
	data_frame=df,x='variable',y='value',color='State',
	labels ={'variable':'Date','value':'# of Confirmed Cases'}
	)


	return plot, style
	

if __name__ == '__main__':
    app.run_server(debug=False)
