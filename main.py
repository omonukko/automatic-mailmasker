from utils import get_logger, C, Fore
from faker import Faker
from nextcaptcha import NextCaptchaAPI
import time
import tls_client
import random
import uuid
import re
import requests



solver = NextCaptchaAPI(client_key="nextcaptcha key", open_log=False)
proxy = "proxy"

class PaichaCloud(requests.Session):
    def __init__(self):
        super().__init__()
    def getmail(self, id: str):
        return f"{id}@miffyboost.live"
    def inbox(self, id: str):
        response = self.get(f"https://mail.paicha.cloud/api/{id}%40miffyboost.live").json()
        return response
    def body(self, id: str, code: str):
        response = self.get(f"https://mail.paicha.cloud/api/mailbox/{id}%40miffyboost.live/mail/{code}").json()
        return response

class MailMaskerException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class MailMasker(tls_client.Session):
    def __init__(self, client_identifier = "chrome_120", ja3_string = None, h2_settings = None, h2_settings_order = None, supported_signature_algorithms = None, supported_delegated_credentials_algorithms = None, supported_versions = None, key_share_curves = None, cert_compression_algo = None, additional_decode = None, pseudo_header_order = None, connection_flow = None, priority_frames = None, header_order = None, header_priority = None, random_tls_extension_order = False, force_http1 = False, catch_panics = False, debug = False, certificate_pinning = None):
        super().__init__(client_identifier, ja3_string, h2_settings, h2_settings_order, supported_signature_algorithms, supported_delegated_credentials_algorithms, supported_versions, key_share_curves, cert_compression_algo, additional_decode, pseudo_header_order, connection_flow, priority_frames, header_order, header_priority, random_tls_extension_order, force_http1, catch_panics, debug, certificate_pinning)
        self.headers = {
            'accept': '*/*',
            'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
            'connection': 'keep-alive',
            'content-type': 'application/json',
            'host': 'api.mailmasker.com',
            'origin': 'https://app.mailmasker.com',
            'referer': 'https://app.mailmasker.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        }
        self.proxies = {
            "https": f"{proxy}",
            "http": f"{proxy}"
        }
        self.faker = Faker()
    def is_available(self, mail: str=None):
        if mail == None:
            mail = self.faker.last_name()+str(random.randint(1, 9999)).zfill(4)
        response = self.post("https://api.mailmasker.com/graphql",
            params={
                "name": "IsEmailMaskAvailable"
            },
            json={
                'operationName': 'IsEmailMaskAvailable',
                'variables': {
                    'email': f'{mail}@mailmasker.com',
                },
                'query': 'query IsEmailMaskAvailable($email: String!) {\n  isEmailMaskAvailable(email: $email)\n}\n',
            }
        )
        if response.json()["data"]["isEmailMaskAvailable"] == True:
            return True
        else:
            return False
    def create_record(self):
        response = self.post("https://mail-masker-analytics.netlify.app/api",
            json={
                "query": "\n\t\t\tmutation createRecord($domainId: ID!, $input: CreateRecordInput!) {\n\t\t\t\tcreateRecord(domainId: $domainId, input: $input) {\n\t\t\t\t\tpayload {\n\t\t\t\t\t\tid\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}\n\t\t",
                "variables": {
                    "domainId": "b79f0d27-bb42-4711-a8f2-58a666975d7e",
                    "input": {
                        "siteLocation": "https://www.mailmasker.com/",
                        "siteReferrer": "",
                        "siteLanguage": "ja",
                        "screenWidth": 1920,
                        "screenHeight": 1080,
                        "screenColorDepth": 24,
                        "deviceName": None,
                        "deviceManufacturer": None,
                        "osName": "Windows",
                        "osVersion": "10",
                        "browserName": "Chrome",
                        "browserVersion": "137.0.0.0",
                        "browserWidth": 1920,
                        "browserHeight": 1080
                    }
                }
            }
        )
        if response.status_code == 200 and response.json()["data"]["createRecord"]["payload"]["id"]:
            return response.json()["data"]["createRecord"]["payload"]["id"]
        return None
    def create_user(self, username:str, forward_email: str, password: str, mask_mail: str):
        print(f"Creating: {username}:{forward_email}:{password}:{mask_mail}")
        self.uuid = uuid.uuid4()
        solve = solver.recaptchav2hs_enterprise(
            "https://www.mailmasker.com",
            "6LcQ83cpAAAAACu0XWJTZ8zFKlV9fPyllJyoAUO8",
            page_action="submit",
            is_invisible=True
        )["solution"]["gRecaptchaResponse"]
        response = self.post(
            "https://api.mailmasker.com/graphql",
            params={
                "name": "CreateUser"
            },
            json={
                'operationName': 'CreateUser',
                'variables': {
                    'username': f'{username}',
                    'password': f'{password}',
                    'uuid': f"{self.uuid}",
                    'persistent': True,
                    'emailMask': f'{mask_mail}@mailmasker.com',
                    'verifiedEmail': f'{forward_email}',
                    'reCAPTCHAToken': f"{solve}"
                },
                'query': 'mutation CreateUser($username: String!, $password: String!, $uuid: String!, $persistent: Boolean!, $verifiedEmail: String!, $emailMask: String!, $reCAPTCHAToken: String!) {\n  createUser(username: $username, password: $password, uuid: $uuid, persistent: $persistent, verifiedEmail: $verifiedEmail, emailMask: $emailMask, reCAPTCHAToken: $reCAPTCHAToken) {\n    userID\n    __typename\n  }\n}\n',
            }
        )
        if response.status_code == 200 and response.cookies.get("jwt"):
            self.cookies.set("jwt", response.cookies.get("jwt"))
            return response.json()
        else:
            raise MailMaskerException("Failed to account generation: "+ response.text)
    def verify(self, code: str, forward_email: str):
        response = self.post(
            "https://api.mailmasker.com/graphql",
            params={
                "name": "VerifyEmailWithCodeMutation"
            },
            json={
                "operationName": "VerifyEmailWithCodeMutation",
                "variables": {
                    "email": f"{forward_email}",
                    "code": f"{code}"
                },
                "query": "mutation VerifyEmailWithCodeMutation($email: String!, $code: String!) {\n  verifyEmailWithCode(email: $email, code: $code) {\n    id\n    email\n    verified\n    __typename\n  }\n}\n"
            }
        )
        if response.status_code == 200 and response.json()["data"]["verifyEmailWithCode"]["verified"] == True:
            self.emailId = response.json()["data"]["verifyEmailWithCode"]["id"]
            return response.json()
        else:
            raise MailMaskerException("Failed to verifying account: "+response.text)
    def add_mail(self, name: str):
        if not self.is_available(name):
            raise MailMaskerException("The Name is already taken.")
        response = self.post(
            "https://api.mailmasker.com/graphql",
            params={
                "name": "CreateEmailMask"
            },
            json={
                "operationName": "CreateEmailMask",
                "variables": {
                    "email": f"{name}@mailmasker.com"
                },
                "query": "mutation CreateEmailMask($email: String!) {\n  createEmailMask(raw: $email) {\n    id\n    domain\n    alias\n    parentEmailMaskID\n    __typename\n  }\n}\n"
            }
        )
        if response.status_code == 200 and response.json()["data"]["createEmailMask"]["id"]:
            create_route = self.post(
                "https://api.mailmasker.com/graphql",
                params={
                    "name": "CreateRoute"
                },
                json={
                    "operationName": "CreateRoute",
                    "variables": {
                        "redirectToVerifiedEmailID": f"{self.emailId}",
                        "emailMaskID": f"{response.json()["data"]["createEmailMask"]["id"]}"
                    },
                    "query": "mutation CreateRoute($redirectToVerifiedEmailID: ID!, $emailMaskID: ID!) {\n  createRoute(redirectToVerifiedEmailID: $redirectToVerifiedEmailID, emailMaskID: $emailMaskID) {\n    id\n    redirectToVerifiedEmail {\n      id\n      email\n      verified\n      __typename\n    }\n    emailMask {\n      id\n      domain\n      alias\n      parentEmailMaskID\n      __typename\n    }\n    expiresISO\n    __typename\n  }\n}\n"
                }
            )
            if create_route.status_code == 200 and create_route.json()["data"]["createRoute"]["id"]:
                return create_route.json()
            else:
                raise MailMaskerException("Failed to add mail and route: "+create_route.text)
        else:
            raise MailMaskerException("Failed to add mail: "+response.text)


if __name__ == "__main__":
    masker = MailMasker()
    p = PaichaCloud()
    mail = p.getmail(str(random.randint(1, 999999)).zfill(4))
    print(mail)
    c = masker.create_user(f"teammiffy{str(random.randint(1, 9999)).zfill(4)}", f"{mail}", "MiffyAlts@2025", f"teammiffy{str(random.randint(1, 9999)).zfill(4)}")
    print(c)
    time.sleep(5)
    inbox = p.inbox(mail.split("@")[0])
    for b in inbox:
        if not b["subject"] == "[Mail Masker] Verify your email address":
            continue
        body = p.body(mail.split("@")[0], b["id"])
        match = re.search(r"https://app\.mailmasker\.com/verify-email/[^/]+/code/[a-zA-Z0-9\-]+", body["html_body"])
        if match:
            url = match.group()
            print(f"{b["subject"]} - {url}")
            print(masker.verify(f"{url.split(f"https://app.mailmasker.com/verify-email/{mail}/code/")[1]}", f"{mail}"))
            print(masker.add_mail("miffyalts"+str(random.randint(1, 9999))))