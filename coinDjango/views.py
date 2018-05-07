from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
import json
import redis
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
redis_host = 'localhost'
all_coins_list = {}


def get_data_from_redis():
    r = redis.Redis(host=redis_host, port=6379, db=0)
    key = "latestCoinData"
    garbage = r.get(key)
    garbage = json.loads(garbage)
    return garbage


@cache_page(CACHE_TTL)
def coins(request):
    paramsString = request.GET.get('q', '')
    if not paramsString:
        params = []
    else:
        params = paramsString.split(",")
    res = get_data_from_redis()
    if len(params) > 0:
        res["coinData"] = trim_result_for_request(res["coinData"], params)
    return JsonResponse((res))


@cache_page(9)
def frequency(request):
    ret = {}
    ret["w"] = 12
    ret['a'] = 12
    ret["st_d_v"] = 14
    return JsonResponse(ret)

@cache_page(900)
def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render())


def trim_result_for_request(res, params):
    ret = []
    for coin in res:
        if coin["id"] in params:
            ret.append(coin)
    return ret


def get_all_coins_static_data(request):
    r = redis.Redis(host=redis_host, port=6379, db=0)
    key = "allCoinsStaticDataHash"
    garbage = r.get(key)
    garbage = json.loads(garbage)
    return JsonResponse(garbage)


@cache_page(2)
def get_coin_price_api(request):
    r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
    res = {}
    if request.method == 'GET':
        res = get_coin_price_api_get(r, request)
    # elif request.method == 'POST':
    #     res = get_coin_price_api_post(r, request)
    return JsonResponse(res)


# def get_coin_price_api_post(r, request):
#     if not paramsString:
#         params = []
#     else:
#         params = paramsString.split(",")
#     res = get_data_from_redis()
#     if len(params) > 0:
#         pipeline = r.pipeline()
#
#     return request


def get_coin_price_api_get(r, request):
    paramsString = request.GET.get('q', '')
    ret = {}
    if not paramsString:
        params = []
    else:
        params = paramsString.split(",")
    if len(params) > 0:
        pipeline = r.pipeline()
        for param in params:
            pipeline.get(param)
        ret = restructure_price_result(pipeline.execute(), params)
    return ret


def restructure_price_result(res, params):
    ret = {"coinData": {}}
    for i, coin in enumerate(res):
        if coin is not None:
            tmp = params[i].split("__")
            if tmp[0] not in ret["coinData"]:
                ret["coinData"][tmp[0]] = {}
            if tmp[1] not in ret["coinData"][tmp[0]]:
                ret["coinData"][tmp[0]][tmp[1]] = {}
            ret["coinData"][tmp[0]][tmp[1]][tmp[2]] = json.loads(coin)
    return ret
