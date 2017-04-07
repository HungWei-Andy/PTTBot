import json

request = {'function':'find_board','board':'gossip','title':None,'author':None,'content':None,'comment':{'state':None,'message':None,'id':None,'date':None},'push':{'all':None,'score':50,'good':None,'bad':None,'none':None},'date':None,'ip':None}

list_req = []

for i in range(5):
	list_req.append(request)

with open('dumpjson.json','w') as f:
	json.dump(list_req,f)
	
