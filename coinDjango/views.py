from django.shortcuts import render
from django.conf import settings
import pymongo
import pytz
# Create your views here.
# from django.http import HttpResponse

from django.http import JsonResponse

from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

coinMapping = {}
coinMapping["btc"]="Bitcoin"
coinMapping["bch"]="Bitcoin Cash/BCC"
coinMapping["xrp"]="Ripple"
coinMapping["eth"]="Ether"
coinMapping["ltc"]="Litecoin"
coinMapping["omg"]="Omisego"
coinMapping["gnt"]="Golem"
coinMapping["miota"]="IOTA"
coinMapping["btc__zebpay"]="Bitcoin  ZEBPAY"
coinMapping["btc__unocoin"]="Bitcoin  UNOCOIN"
coinMapping["btc__koinex"]="Bitcoin  KOINEX"
coinMapping["xrp__koinex"]="Ripple  KOINEX"
coinMapping["bch__koinex"]="Bitcoin Cash/BCC  KOINEX"
coinMapping["eth__koinex"]="Ether  KOINEX"
coinMapping["ltc__koinex"]="Litecoin  KOINEX"
coinMapping["omg__koinex"]="Omisego  KOINEX"
coinMapping["miota__koinex"]="IOTA  KOINEX"
coinMapping["gnt__koinex"]="GOLEM  KOINEX"


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


def fill_coin_data(id):
    res = {}
    res["id"] = id
    res["name"] = coinMapping[id]
    res["currency"] = "INR"
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


@cache_page(CACHE_TTL)
def index(request):

    paramsString = request.GET.get('q', '')
    if not paramsString:
        params = []
    else:
        params = paramsString.split(",")
    res = get_data_from_mongo()
    res = transform_res(res)
    if len(params) > 0:
        res["coinData"] = trim_result_for_request(res["coinData"], params)
    return JsonResponse((res))
    # ({'foo': 'bar'})

# def index(request):
#    return HttpResponse("Hello, world. You're at the polls index.")


def transform_koinex_data(res):
    ret = []
    for key, val in res.items():
        tmp = {}
        newkey = (key.lower() + "__koinex")
        tmp = {}
        tmp = fill_coin_data(newkey)
        tmp["cp"] = str(val)
        ret.append(tmp)
    return ret


def transform_unocoin_data(res):
    ret = {}
    ret = fill_coin_data("btc__unocoin")
    ret["cp"] = str(res["buybtc"])
    return ret


def transform_zebpay_data(res):
    ret = {}
    ret = fill_coin_data("btc__zebpay")
    ret["cp"] = str(res["buy"])
    return ret


def trim_result_for_request(res, params):
    ret = []
    for coin in res:
        if coin["id"] in params:
            ret.append(coin)
    return ret
