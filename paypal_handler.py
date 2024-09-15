import asyncio
import aiohttp
from fastapi import APIRouter, status, Request
from fastapi.responses import RedirectResponse
from bot_init import config


paypal_router = APIRouter(tags=['payment'], prefix='/payment')


@paypal_router.get(path='/paypal_webhook', status_code=status.HTTP_200_OK)
async def get_webhook_handler() -> dict:
    print("Running get webhook handler...")
    return {'ok': True}


@paypal_router.post(path='/paypal_webhook', status_code=status.HTTP_200_OK)
async def post_webhook_handler(data: dict) -> dict:
    print("Running post webhook handler...")
    print(data)
    return {'ok': True}


@paypal_router.get(path='/paypal_return', status_code=status.HTTP_200_OK)
async def paypal_return_handler(paymentId: str, PayerID: str, request: Request) -> dict:
    print("Running paypal_return_handler...")
    print(paymentId, PayerID)
    token = await get_paypal_token()
    url = f'https://api-m.sandbox.paypal.com/v1/payments/payment/{paymentId}/execute'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token,
    }
    data = { "PayerID": PayerID }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data):
            return RedirectResponse(url='https://youtube.com')

@paypal_router.get(path='/paypal_cancel', status_code=status.HTTP_200_OK)
async def paypal_cancel_handler() -> dict:
    print("Running paypal_cancel_handler...")
    return RedirectResponse(url='https://google.com')


async def get_paypal_token():
    url = 'https://api-m.sandbox.paypal.com/v1/oauth2/token'
    data = {
        'grant_type': 'client_credentials',
    }
    auth = aiohttp.BasicAuth(config['client_id'], config['client_secret'])

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, auth=auth) as response:
            if response.status == 200:
                result = await response.json()
                return f"Bearer {result.get('access_token')}"
            return await response.text()


async def create_paypal_webhook():
    url = 'https://api-m.sandbox.paypal.com/v1/notifications/webhooks'
    token = await get_paypal_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token,
    }
    data = {
        "url": f"{config.get('tg_domain')}/payment/paypal_webhook",
        "event_types": [
            { "name": "*" }
        ]
    }
    print(data)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                return await response.text()


async def create_paypal_payment(amount: str, currency: str, descr: str, user_id: str):
    url = 'https://api-m.sandbox.paypal.com/v1/payments/payment'
    token = await get_paypal_token()
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    data = {
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [
            {
                "amount": {
                    "total": amount,
                    "currency": currency
                },
                "description": descr,
                "custom": user_id,
            }
        ],
        "note_to_payer": "Contact us for any questions on your order.",
        "redirect_urls": {
            "return_url": f"{config.get('tg_domain')}/payment/paypal_return",
            "cancel_url": f"{config.get('tg_domain')}/payment/paypal_cancel"
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 201:
                return await response.json()
            return await response.text()


if __name__ == '__main__':
    # To run the async function
    print(asyncio.run(create_paypal_payment(
        amount= "10", currency= "USD", descr= "Test", user_id= "1"
    )))

    # To run the async function
    # print(asyncio.run(create_paypal_webhook()))

    # To run the async function
    # print(asyncio.run(get_paypal_token()))
