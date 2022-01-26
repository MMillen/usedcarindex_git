from plotly.offline import plot
from plotly.graph_objs import Scatter
import plotly.graph_objects as go
import numpy as np
import MySQLdb 
import pandas.io.sql as psql 
import pandas as pd 
import plotly.express as px
from datetime import date


'''

def getPrice(year,month):
    year = year
    month = month
    startyear = year - 7
    endyear = year - 4
    
    db = MySQLdb.connect(host="*", user="*", passwd="*",db="autofin")
    query = "SELECT round(avg(price), 2) price, count(price) count FROM autofin.listingsbeta where price < 60000 and price > 400 and year >= "+ str(startyear) +" and year <= " + str(endyear) + " and postyear = " + str(year) +" and postmonth = " + str(month) +" and ( (make like '%honda%' and model like '%pilot%') or (make like '%nissan%' and model like '%altima%') or (make like '%chevrolet%' and model like '%traverse%' ) or (make like '%honda%' and model like '%civic%' ) or (make like '%honda%' and model like '%accord%' ) or (make like '%toyota%' and model like '%camry%' ) or (make like '%ford%' and model like '%f150%' ) or (make like '%dodge%' and model like '%ram%' ) or (make like '%chevrolet%' and model like '%silverado%' ) or (make like '%ford%' and model like '%mustang%' ) or (make like '%jeep%' and model like '%wrangler%' ) or (make like '%toyota%' and model like '%tacoma%' ) or (make like '%toyota%' and model like '%corolla%' ) or (make like '%toyota%' and model like '%prius%' ) or (make like '%bmw%' and model like '%3 series%' ) or (make like '%volkswagen%' and model like '%jetta%' ) or (make like '%nissan%' and model like '%sentra%' ) or (make like '%hyundai%' and model like '%sonata%' ) or (make like '%ford%' and model like '%fusion%' ) or (make like '%hyundai%' and model like '%elantra%' ) or (make like '%ford%' and model like '%fusion%' ) or (make like '%toyota%' and model like '%rav4%' ) or (make like '%chevrolet%' and model like '%malibu%' ) or (make like '%nissan%' and model like '%rogue%' ) or (make like '%mazda%' and model like '%3%' ) or (make like '%volkswagen%' and model like '%passat%' ) or (make like '%volkswagen%' and model like '%beetle%' ))"
    data = psql.read_sql(query,con=db)
    price = data.price[0]
    count = data['count'][0]
    
    output = [price,count]
    return output
    

index = pd.DataFrame(columns=['date','year','month','price','count'])
todays_date = date.today()
curyear = todays_date.year
curmonth = todays_date.month
totalyears = curyear - 2008



for i in range(totalyears+1):
    year = 2008 + i
    monthstop = 12
    for x in range(12):
        x += 1
        if year == 2008:
            x += 8

        if year == curyear:
            monthstop = curmonth

        if x <= monthstop:
            print x
            result = getPrice(year,x)
            price = result[0]
            count = result[1]
            dt = date(year=year,month=x, day=28)
            index = index.append({'date':dt,'year':year,'month':x,'price':price,'count':count}, ignore_index=True)


index = index[index['price'].notna()]
index =index[index['count'] >= 20]



index = index.reset_index(drop=True)

		
index['change'] = 0.0 
index['mark'] = 100
for i in range(len(index.price)):
    if i > 0:
        change = ((index.price[i] - index.price[0]) / index.price[0]) 
        mark = index.mark[i] + (index.mark[i] * change)
        index.change.iloc[i] = change
        index.mark.iloc[i] = mark 

		

index['priceupper'] = index['mark'] + (index['mark'] * .05)
index['pricelower'] = index['mark'] - (index['mark'] * .05)

index.to_csv('data.csv', index=False)
index = pd.read_csv('data.csv')	


'''
 

 
 
 
 
 
#Generate Plotly Graph
 
 

x = index['date'].tolist()
x_rev = x[::-1]

# Line 1
y1 = index['mark'].tolist()
y1_upper = index['priceupper'].tolist()
y1_lower = index['pricelower'].tolist()
y1_lower = y1_lower[::-1]


fig = go.Figure(layout=go.Layout(title=go.layout.Title(text="")))

fig.add_trace(go.Scatter(
    x=x+x_rev,
    y=y1_upper+y1_lower,
    fill='toself',
    fillcolor='rgba(0,100,80,0.4)',
    line_color='rgba(255,255,255,0)',
    showlegend=False,
    name='Average Price',
	line_smoothing=1.3,
))

fig.add_trace(go.Scatter(
    x=x, y=y1,
    line_color='rgb(0,100,80)',
    name='',
	showlegend=False,
	line_smoothing=1.3,
))


fig.update_traces(mode='lines')
fig.update_layout(template="plotly_dark")
fig.update_layout(paper_bgcolor="rgb(0,0,0)")
fig.update_layout(plot_bgcolor="rgb(0,0,0)")
fig.update_layout(margin=dict(l=20, r=20, t=20, b=0))



fig.update_xaxes(
    rangeslider_visible=False,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ]),
		
        bgcolor = '#000000',
        bordercolor = '#FFFFFF',
        font = dict( size=11 )
    ),
)


fig.write_html("index.html", config= {'displaylogo': False, 'displayModeBar':False, 'staticPlot': True})
#fig.show(id='the_graph', config= {'displaylogo': False})










#Push aggregated data to database

db = MySQLdb.connect(host="*", user="*", passwd="*",db="autofin",autocommit=True)



current_math = index.mark.iloc[-1]
current = current_math.astype(int)
query = "update autofin.indexstats set current="+str(current)+" where indexname='usedcarindex' "
db.query(query) 


month = index.mark.iloc[-2] 
monthchange = round( ((current_math - month) / month) * 100, 2)
month = month.astype(int) 
query = "update autofin.indexstats set month="+str(month)+" where indexname='usedcarindex' "
db.query(query) 
query = "update autofin.indexstats set monthchange="+str(monthchange)+" where indexname='usedcarindex' "
db.query(query)



thisyear = index.year.iloc[-1]
lookupyear = index[index['year'] == (thisyear - 1)]
year = lookupyear.mark.iloc[0] 
yearchange = round( ((current_math - year) / year) * 100, 2)
year = year.astype(int)
query = "update autofin.indexstats set year="+str(year)+" where indexname='usedcarindex' "
db.query(query) 
query = "update autofin.indexstats set yearchange="+str(yearchange)+" where indexname='usedcarindex' "
db.query(query)


thisyear = index.year.iloc[-1]
lookupfive = index[index['year'] == (thisyear - 5)]
fiveyear = lookupfive.mark.iloc[0] 
fiveyearchange = round( ((current_math - fiveyear) / fiveyear) * 100, 2)
fiveyear = fiveyear.astype(int) 
query = "update autofin.indexstats set fiveyear="+str(fiveyear)+" where indexname='usedcarindex' "
db.query(query) 
query = "update autofin.indexstats set fiveyearchange="+str(fiveyearchange)+" where indexname='usedcarindex' "
db.query(query)











