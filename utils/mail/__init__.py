import requests
from pydantic import BaseModel
from typing import Literal



class AddressResponse(BaseModel):
    status: Literal["success", "error"]
    address: str=None

class GmailNator(requests.Session):
    def __init__(self, apikey: str):
        super().__init__()
        self.headers = {
            "x-rapidapi-key": f"{apikey}",
	        "x-rapidapi-host": "gmailnator.p.rapidapi.com",
        }
    def address(self):
        response = self.post("https://gmailnator.p.rapidapi.com/generate-email", json={"options": [1, 2, 3]}).json()
        if response.get("email", None):
            return AddressResponse(
                status="success",
                address=response["email"]
            )
        else:
            return AddressResponse(
                status="error"
            )
    def inbox(self, email: str, limit: int=10) -> list:
        response = self.post("https://gmailnator.p.rapidapi.com/inbox", json={"email": email, "limit": limit}).json()
        return response
    def get_body(self, id: str):
        response = self.get("https://gmailnator.p.rapidapi.com/messageid", params={"id": id})
        return response.json()