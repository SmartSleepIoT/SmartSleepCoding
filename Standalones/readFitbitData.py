import requests, csv
from SmartSleep import secrets

header = {'Authorization': f'Bearer {secrets.access_token}'}
response = requests.get(f'https://api.fitbit.com/1/user/{secrets.user_id}/activities/heart/date/2021-10-11/2021-10-12/1min/time/23:00/08:00.json', headers=header).json()
response = response['activities-heart-intraday']['dataset']

f = open('SensorsData/Heartrate.csv', 'w')
writer =  csv.writer(f)
csvHeader = ['time', 'heartrate']
writer.writerow(csvHeader)
for data in response:
    writer.writerow([data['time'], data['value']])
f.close()