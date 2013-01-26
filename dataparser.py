import json
import yummly

yummly.api_id = '5dd6a908'
yummly.api_key = '1144f281d7ac2e4d2f08ba7883bdc396'

results = yummly.search('banana bread', maxResults=10)
