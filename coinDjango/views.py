from django.shortcuts import render
from django.conf import settings
import pymongo
import pytz
# Create your views here.
# from django.http import HttpResponse

from django.http import JsonResponse
import json
import redis
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

# coinMapping = {}
# coinMapping["btc"]="Bitcoin"
# coinMapping["bch"]="Bitcoin Cash"
# coinMapping["xrp"]="Ripple"
# coinMapping["eth"]="Ether"
# coinMapping["ltc"]="Litecoin"
# coinMapping["omg"]="Omisego"
# coinMapping["gnt"]="Golem"
# coinMapping["miota"]="IOTA"
# coinMapping["btc__zebpay"]="Bitcoin  zebpay"
# coinMapping["bch__zebpay"]="Bitcoin Cash  zebpay"
# coinMapping["ltc__zebpay"]="Litecoin  zebpay"
# coinMapping["xrp__zebpay"]="Ripple  zebpay"
# coinMapping["btc__unocoin"]="Bitcoin  unocoin"
# coinMapping["btc__koinex"]="Bitcoin  koinex"
# coinMapping["xrp__koinex"]="Ripple  koinex"
# coinMapping["bch__koinex"]="Bitcoin Cash/BCC  koinex"
# coinMapping["eth__koinex"]="Ether  koinex"
# coinMapping["ltc__koinex"]="Litecoin  koinex"
# coinMapping["omg__koinex"]="Omisego  koinex"
# coinMapping["miota__koinex"]="IOTA  koinex"
# coinMapping["gnt__koinex"]="GOLEM  koinex"

# zebpayCoins = ["btc", "bch", "ltc", "xrp"]


# def get_data_from_mongo():
#     client = pymongo.MongoClient()
#     db = client.coinExchangeDB
#     collection = db.coinInfo
#     # res = collection.find().sort({_id: -1}).limit(1)
#     for d in collection.find():
#         res = d
#     res.pop('_id')
#     res["ts"] = res["ts"].replace(tzinfo=pytz.utc).timestamp()
#     return res


# def fill_coin_data(id):
#     res = {}
#     res["id"] = id
#     res["name"] = coinMapping[id]
#     res["currency"] = "inr"
#     res["op"] = "0.0"
#     return res
#
#
# def transform_res(res):
#     ret = {}
#     ret["coinData"] = []
#     for key, values in res.items():
#         if key == "koinex":
#             ret["coinData"] = ret["coinData"] + (transform_koinex_data(values["prices"]))
#         elif key == "unocoin":
#             ret["coinData"].append(transform_unocoin_data(values))
#         elif key == "zebpay":
#             ret["coinData"].append(transform_zebpay_data(values))
#
#     ret["ts"] = res["ts"]
#     return ret


def get_data_from_redis():
    r = redis.Redis(host='localhost', port=6379, db=0)
    key = "latestCoinData"
    garbage = r.get(key)
    garbage = json.loads(garbage)
    print(garbage["coinData"])
    return garbage


@cache_page(CACHE_TTL)
def coins(request):

    paramsString = request.GET.get('q', '')
    if not paramsString:
        params = []
    else:
        params = paramsString.split(",")
#    res = get_data_from_mongo()
    res = get_data_from_redis()
#    res = transform_res(res)
    if len(params) > 0:
        res["coinData"] = trim_result_for_request(res["coinData"], params)
    return JsonResponse((res))
    # ({'foo': 'bar'})


@cache_page(900)
def frequency(request):
    ret = {}
    ret["w"] = 20
    ret['a'] = 20
    return JsonResponse(ret)

@cache_page(CACHE_TTL)
def index(request):
    return JsonResponse({"hello ": "world!"})


# def index(request):
#    return HttpResponse("Hello, world. You're at the polls index.")


# def transform_koinex_data(res):
#     ret = []
#     for key, val in res.items():
#         tmp = {}
#         newkey = (key.lower() + "__koinex")
#         tmp = {}
#         tmp = fill_coin_data(newkey)
#         tmp["cp"] = str(val)
#         ret.append(tmp)
#     return ret
#
#
# def transform_unocoin_data(res):
#     ret = {}
#     ret = fill_coin_data("btc__unocoin")
#     ret["cp"] = str(res["buybtc"])
#     return ret
#
#
# def transform_zebpay_data(res):
#     ret = {}
#     ret = fill_coin_data("btc__zebpay")
#     ret["cp"] = str(res["buy"])
#     return ret
#
#
def trim_result_for_request(res, params):
    ret = []
    for coin in res:
        if coin["id"] in params:
            ret.append(coin)
    return ret
