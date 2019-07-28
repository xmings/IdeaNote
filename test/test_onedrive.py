#!/bin/python
# -*- coding: utf-8 -*-
# @File  : test_onedrive.py
# @Author: wangms
# @Date  : 2019/7/27
from common import conf
from urllib.parse import quote, unquote
import webbrowser
import requests
import json

def test_onedrive_connection():
    info =  conf.remote_connection_info
    base_url = """
        https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?
        client_id={client_id}
        &response_type={response_type}
        &redirect_uri={redirect_uri}
        &response_mode={response_mode}
        &scope={scope}
        &state={state}
    """.format(tenant=info["tenant"],
               client_id=info["client_id"],
               response_type=info["response_type"],
               redirect_uri=quote(info["redirect_uri"]),
               response_mode=info["response_mode"],
               scope=quote(info["scope"]),
               state=info["state"])
    print(base_url)
    webbrowser.open(base_url)

session = requests.Session()
token = ""
def test_fetch_onedrive_token():
    base_url = """https://login.microsoftonline.com/56bf626c-6568-4dfb-b53b-3145c8ef7618/oauth2/v2.0/token"""

    resp = session.post(base_url,data={
        "client_id": "963224c0-fdef-4c42-8ccb-6474d5a5f086",
        "scope": "https://graph.microsoft.com/.default",
        "client_secret": "4X3PslAkd.UE=21MmC-pJhnE_qASJRML",
        "grant_type": "client_credentials"
    }, headers={
        "Host": "login.microsoftonline.com",
        "Content-Type" : "application/x-www-form-urlencoded"
    })
    result = resp.json()
    print("\n")
    print(result["access_token"])
    token = result["access_token"]
    return token


def test_fetch_user_info():
    token = "eyJ0eXAiOiJKV1QiLCJub25jZSI6Im1hYlhveXVoeUR3MWZYdzRmRWVHZzlNLUpzbUF1N0k4aGZCU2NKWWpDVjgiLCJhbGciOiJSUzI1NiIsIng1dCI6InU0T2ZORlBId0VCb3NIanRyYXVPYlY4NExuWSIsImtpZCI6InU0T2ZORlBId0VCb3NIanRyYXVPYlY4NExuWSJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC81NmJmNjI2Yy02NTY4LTRkZmItYjUzYi0zMTQ1YzhlZjc2MTgvIiwiaWF0IjoxNTY0MzE2MDM2LCJuYmYiOjE1NjQzMTYwMzYsImV4cCI6MTU2NDMxOTkzNiwiYWlvIjoiNDJGZ1lQQ2FWLzdpVnpDZjZZeWZHM2RadUQzM0F3QT0iLCJhcHBfZGlzcGxheW5hbWUiOiJJZGVhTm90ZSIsImFwcGlkIjoiOTYzMjI0YzAtZmRlZi00YzQyLThjY2ItNjQ3NGQ1YTVmMDg2IiwiYXBwaWRhY3IiOiIxIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNTZiZjYyNmMtNjU2OC00ZGZiLWI1M2ItMzE0NWM4ZWY3NjE4LyIsIm9pZCI6ImMwMzU3NzJmLTg2NWMtNGU4ZS1hMDA4LTY0ZDNmNzliYWU3YiIsInJvbGVzIjpbIlVzZXIuUmVhZFdyaXRlLkFsbCIsIlNpdGVzLlJlYWQuQWxsIiwiU2l0ZXMuUmVhZFdyaXRlLkFsbCIsIkZpbGVzLlJlYWRXcml0ZS5BbGwiLCJVc2VyLlJlYWQuQWxsIiwiRmlsZXMuUmVhZC5BbGwiXSwic3ViIjoiYzAzNTc3MmYtODY1Yy00ZThlLWEwMDgtNjRkM2Y3OWJhZTdiIiwidGlkIjoiNTZiZjYyNmMtNjU2OC00ZGZiLWI1M2ItMzE0NWM4ZWY3NjE4IiwidXRpIjoiamNUdy1OQ25kRXlraDFPeGhWY3lBQSIsInZlciI6IjEuMCIsInhtc190Y2R0IjoxNTY0MjE4Mjg1fQ.Fyx5Mk6fyLzjGqJg0cov9zqIo-muh1MAsUTsH-4SbjCwvRZ2WYouqgV30RDyCcTJvsnARKPjq7AW6fpnoI8TD7xhlmIaptDNn_uiSPFpRsYJ_KLjAkd2U-CYQ9rkOaY-s5ZT_AH4IvvRZ3tlJMgK5YnYK3eJQR24mYPiTEqOqmhByTXBE__Rc_sYcfcl5UbET91QUwwLd4Snq9-6VJ4JygoFF8FQEAuIWCkspXtX86FnrS_Fj1WBnOxP7416OPiMrVLdUaaUTRHqZxL1JaYwFfdfdtAAC29UfomXOHApAIk_pootqeDjIBulBjwl29s4MGlG7JRWzhS25-QInREV9w"
    base_url = "https://graph.microsoft.com/v1.0/users/77661ab0-7626-4800-b344-ceec5ca6adc0"
    resp = session.get(base_url, headers={
        "Authorization": "Bearer {}".format(token),
        "Host": "graph.microsoft.com"
    })
    print(json.dumps(resp.json(), indent=4, ensure_ascii=False))


def test_fetch_onedrive_data():
    token="eyJ0eXAiOiJKV1QiLCJub25jZSI6ImN1QVJMT1l3TzRsZkVXMjFuN21PMUpoSHViRnBLTjVKckgwcEhELUNvNmciLCJhbGciOiJSUzI1NiIsIng1dCI6InU0T2ZORlBId0VCb3NIanRyYXVPYlY4NExuWSIsImtpZCI6InU0T2ZORlBId0VCb3NIanRyYXVPYlY4NExuWSJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC81NmJmNjI2Yy02NTY4LTRkZmItYjUzYi0zMTQ1YzhlZjc2MTgvIiwiaWF0IjoxNTY0MzE2OTM3LCJuYmYiOjE1NjQzMTY5MzcsImV4cCI6MTU2NDMyMDgzNywiYWlvIjoiNDJGZ1lHZ0pteVo5YitITkI1eFQ0eElXemowL0F3QT0iLCJhcHBfZGlzcGxheW5hbWUiOiJJZGVhTm90ZSIsImFwcGlkIjoiOTYzMjI0YzAtZmRlZi00YzQyLThjY2ItNjQ3NGQ1YTVmMDg2IiwiYXBwaWRhY3IiOiIxIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNTZiZjYyNmMtNjU2OC00ZGZiLWI1M2ItMzE0NWM4ZWY3NjE4LyIsIm9pZCI6ImMwMzU3NzJmLTg2NWMtNGU4ZS1hMDA4LTY0ZDNmNzliYWU3YiIsInJvbGVzIjpbIlVzZXIuUmVhZFdyaXRlLkFsbCIsIlNpdGVzLlJlYWQuQWxsIiwiU2l0ZXMuUmVhZFdyaXRlLkFsbCIsIkZpbGVzLlJlYWRXcml0ZS5BbGwiLCJVc2VyLlJlYWQuQWxsIiwiRmlsZXMuUmVhZC5BbGwiXSwic3ViIjoiYzAzNTc3MmYtODY1Yy00ZThlLWEwMDgtNjRkM2Y3OWJhZTdiIiwidGlkIjoiNTZiZjYyNmMtNjU2OC00ZGZiLWI1M2ItMzE0NWM4ZWY3NjE4IiwidXRpIjoiS21PcVRCYTVSRTZtRzF6R2thTXJBQSIsInZlciI6IjEuMCIsInhtc190Y2R0IjoxNTY0MjE4Mjg1fQ.U8pefQNSm3P9u0CYJCY_gORe77zcWJEl87BL_8cjumy-eSUmUhWtrNY99fYO-gD-oMlCPTsw7QdZIgN_uuSS5tB8iLnP3wDna0l71jdOUCWcx-9eYmcGMJgnU3cv4ghjcMQniEqgoqT9sjCwq1wuFUqZhwcWyFJeFVjttUIwnSPH94WQvvFvJlACXGq5Uw6ZedS3PFBEIh-P9E7jvItq0ILwp1h86XPWcRRvAAGUImBMwgK5kCWga3GCMX9Zy5SX410Xuu01lIAEUg3M8Slyx51kX1J1NuPC6hp8lTRqHIxh8SDG6eqqw51rC-rkQNSoqUi37MGYBTfoJ1TKPKp1KQ"
    base_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
    resp = session.get(base_url, headers={
        "Authorization": "Bearer {}".format(token),
        "Host": "graph.microsoft.com"
    })
    print(json.dumps(resp.json(), indent=4, ensure_ascii=False))