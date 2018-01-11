from django.shortcuts import render
import pymongo
import json
import pytz
# Create your views here.
# from django.http import HttpResponse

from django.http import JsonResponse


def get_data_from_mongo():
    client = pymongo.MongoClient()
    db = client.coinExchangeDB
    collection = db.coinInfo
    # res = collection.find().sort({_id: -1}).limit(1)
    for d in collection.find():
        res = d
    res.pop('_id')
    res["ts"] = res["ts"].replace(tzinfo=pytz.utc).timestamp()
    return res


def index(request):
    res = get_data_from_mongo()
    return JsonResponse((res))
    # ({'foo': 'bar'})

# def index(request):
#    return HttpResponse("Hello, world. You're at the polls index.")
