import json
from pprint import pprint
json_data=open('../tmp/google_json').read()

#data = json.dumps(eval(json_data))
data = eval(json_data)
print type(data)
pprint(data)
print "num_company_results = " + data['num_company_results']

# one stock
stock_data = data['searchresults'][0]
print "ticker = " + stock_data['ticker']
print "title = " + stock_data['title']
print "exchange =" + stock_data['exchange']

field_data = stock_data['columns'][0]
print "field = " + field_data['field'] 
print "val = " + field_data['value']

#json_data.close()
