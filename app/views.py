from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from .models import Session
from web3 import Web3
from json import load, loads, dumps
from auth.settings import PRIVATE_KEY
import urllib

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
with open("../server/artifacts/contracts/OAuth3.sol/OAuth3.json", "r") as f:
    abi = load(f)["abi"]

with open("../server/cache/address.json", "r") as f:
    address = Web3.to_checksum_address(load(f)["oauth3"])

contract = web3.eth.contract(address=address, abi=abi)
owner = web3.eth.account.from_key(PRIVATE_KEY)

print(urllib.parse.quote("http://127.0.0.1:8545"))


def base_render(request, filename, context={}):
    if (request.POST.get("session_id", None) is not None):
        context["session_id"] = request.POST.get("session_id")
    return render(request, filename + ".html", context)

# Views
@require_GET
def connect(request):
    client_id = request.GET.get("client_id", None)
    req_scope = request.GET.get("req_scopes", None)
    session_id = request.GET.get("session_id", None)
    print(client_id, req_scope)
    session = Session(session_id=session_id)
    session.client_id = client_id
    session.req_scopes = req_scope
    session.save()
    session.delete_incomplete_session
    return base_render(request, "connect", context={"session_id": session.pk})


@require_POST
def selectAccount(request):
    session = Session.objects.filter(session_id=request.POST.get("session_id", None))
    addresses = loads(request.POST.get("addresses"))
    print(addresses)
    print(session)

    if (len(session) == 0):
        redirect("error")

    accounts = []

    for i in addresses:
        detail = contract.functions.getUser(Web3.to_checksum_address(i)).call({
            "from": owner.address})
        if detail[0] != "":
            aadhaar_detail = contract.functions.readAadhaar(
                Web3.to_checksum_address(i)).call({"from": owner.address})
            if (aadhaar_detail[1] != ""):
                accounts.append(
                    {"address": Web3.to_checksum_address(i), "uid": detail[0], "name": aadhaar_detail[3]})
        else:
            accounts.append(
                {"address": Web3.to_checksum_address(i), "uid": detail[0], "name": None})
        print(accounts)

    return base_render(request, "selectAccount", context={"accounts": accounts})


@require_POST
def scope(request):
    session = Session.objects.filter(session_id=request.POST.get("session_id", None))
    address = request.POST.get("accountAddress", None)
    print(session)
    print(address)

    if (len(session) == 0):
        redirect("error")

    uid = contract.functions.getUser(
        Web3.to_checksum_address(address)).call({"from": owner.address})

    session = session.first()
    session.uid = uid[0]
    session.save()

    return base_render(request, "scope")


@require_POST
def selectScope(request):
    session = Session.objects.filter(session_id=request.POST.get("session_id", None))
    allowed_scopes = request.POST.get("allowed_scopes", None)

    if (len(session) == 0):
        redirect("error")

    session = session.first()
    session.allowed_scope = allowed_scopes
    session.save()

    return HttpResponse("<script>window.close()</script>")


@csrf_exempt
@require_POST
def getAuthToken(request):
    """
    request.GET: client_id
    response: Page for authentication
    Generates authtication token for client_id with required_scopes by different steps
    and sends it by making post request to callback_url
    """
    session = Session.objects.filter(
        session_id=request.POST.get("session_id")).first()
    print(session.session_id)
    while session:
        if session.allowed_scope != "":
            return HttpResponse(session.authentication_token)


@csrf_exempt
@require_POST
def getAccessToken(request):
    """
    request.POST: authentication_token
    response: access_token, uid
    Access Token is returned as response if Authentication Code and Client Secret is correct
    """
    auth_token = request.POST.get("auth_token", None)
    client_secret = request.POST.get("")
    print(auth_token)
    session = Session.objects.filter(authentication_token=auth_token)

    if (len(session) == 0):
        return HttpResponse("error")

    session = session.first()
    res = {"access_token": session.access_token, "uid": session.uid}
    return HttpResponse(dumps(res))


@csrf_exempt
@require_POST
def getDetails(request):
    """
    request.POST: access_token, uid, client_id
    response: Details in json format
    Returns details for correct access_token and uid for client
    """
    access_token = request.POST.get("access_token", None)
    uid = request.POST.get("uid", None)
    client_id = request.POST.get("client_id", None)

    if not (access_token and uid and client_id):
        return redirect("error")

    contract.functions.getUser(Web3.to_checksum_address()).call({
        "from": owner.address})
