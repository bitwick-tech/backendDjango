from django.shortcuts import render
import pymongo
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


def transform_res(res):
    ret = {}
    ret["coinData"] = []
    for key, values in res.items():
        if key == "koinex":
            ret["coinData"] = ret["coinData"] + (transform_koinex_data(values["prices"]))
        elif key == "unocoin":
            ret["coinData"].append(transform_unocoin_data(values))
        elif key == "zebpay":
            ret["coinData"].append(transform_zebpay_data(values))

    ret["ts"] = res["ts"]
    return ret


def index(request):
    res = get_data_from_mongo()
    res = transform_res(res)
    return JsonResponse((res))
    # ({'foo': 'bar'})

# def index(request):
#    return HttpResponse("Hello, world. You're at the polls index.")


def transform_koinex_data(res):
    ret = []
    for key, val in res.items():
        tmp = {}
        newkey = (key.lower() + "__koinex")
        tmp[newkey] = {}
        tmp[newkey]["cp"] = str(val)
        tmp[newkey]["currency"] = "INR"
        ret.append(tmp)
    return ret


def transform_unocoin_data(res):
    ret = {}
    ret["btc__unocoin"] = {}
    ret["btc__unocoin"]["cp"] = str(res["buybtc"])
    ret["btc__unocoin"]["currency"] = "INR"
    return ret


def transform_zebpay_data(res):
    ret = {}
    ret["btc__zebpay"] = {}
    ret["btc__zebpay"]["cp"] = str(res["buy"])
    ret["btc__zebpay"]["currency"] = "INR"
    return ret
