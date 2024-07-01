from flask import Flask, request, jsonify
import json
import logging
import requests
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# WooCommerce credentials
wc_api_url = os.getenv('WC_API_URL')
consumer_key = os.getenv('WC_CONSUMER_KEY')
consumer_secret = os.getenv('WC_CONSUMER_SECRET')

# WATI API credentials
wati_api_url = os.getenv('WATI_API_URL')
wati_api_key = os.getenv('WATI_API_KEY')

# Unique ID for webhook endpoint
unique_id = os.getenv('UNIQUE_ID')

def get_wati_contacts():
    logging.info("Fetching WATI contacts...")
    try:
        url = f"{wati_api_url}/getContacts?pageSize=1&pageNumber=1"
        headers = {
            "Authorization": wati_api_key,
            "accept": "*/*"
        }
        response = requests.get(url, headers=headers)
        logging.debug(f"WATI API response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            contacts = response.json()
            if 'contact_list' in contacts and len(contacts['contact_list']) > 0:
                logging.info("WATI contact fetched successfully.")
                return contacts['contact_list'][0]
            else:
                logging.warning("No contacts found.")
                return None
        else:
            logging.error(f"Failed to retrieve contacts: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logging.exception("Exception occurred while retrieving contacts:")
        return None

def create_woocommerce_order(customer_data):
    logging.info("Creating WooCommerce order...")
    try:
        first_name = customer_data['firstName']
        phone = customer_data['phone']
        custom_params = customer_data.get('customParams', [])
        last_cart_items_str = next((item['value'] for item in custom_params if item['name'] == 'last_cart_items'), '[]')
        last_cart_items = json.loads(last_cart_items_str)

        logging.debug(f"Customer data extracted: First Name={first_name}, Phone={phone}, Last Cart Items={last_cart_items}")

        order_data = {
            "payment_method": "bacs",
            "payment_method_title": "Direct Bank Transfer",
            "set_paid": False,
            "billing": {
                "first_name": first_name,
                "phone": phone
            },
            "line_items": []
        }

        for cart_item in last_cart_items:
            order_data['line_items'].append({
                "product_id": cart_item['ProductRetailerId'],
                "quantity": cart_item['Quantity']
            })

        logging.debug(f"Order data prepared: {json.dumps(order_data, indent=4)}")

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.post(f"{wc_api_url}/orders", auth=(consumer_key, consumer_secret), data=json.dumps(order_data), headers=headers)
        logging.debug(f"WooCommerce API response: {response.status_code} - {response.text}")

        if response.status_code == 201:
            order = response.json()
            logging.info(f"Order created successfully: {order}")
            return {
                "id": order['id'],
                "status": order['status'],
                "currency": order['currency'],
                "date_created": order['date_created'],
                "total": order['total'],
                "billing": order['billing'],
                "order_key": order['order_key']
            }
        else:
            logging.error(f"Failed to create order: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logging.exception("Exception occurred while creating order:")
        return None

def send_wati_message(order):
    logging.info("Sending WATI message...")
    try:
        payment_link = f"https://owltlv.com/checkout/order-pay/{order['id']}/?pay_for_order=true&key={order['order_key']}"

        wati_message_data = {
            "phone": order['billing']['phone'],
            "message": f"Hi {order['billing']['first_name']}, your order #{order['id']} has been created. You can pay using the following link: {payment_link}"
        }

        wati_response = requests.post(f"{wati_api_url}/sendMessage", headers={
            "Authorization": wati_api_key,
            "Content-Type": "application/json"
        }, data=json.dumps(wati_message_data))

        logging.debug(f"WATI sendMessage response: {wati_response.status_code} - {wati_response.text}")

        if wati_response.status_code == 200:
            logging.info("Message sent successfully.")
            return True
        else:
            logging.error(f"Failed to send message: {wati_response.status_code} - {wati_response.text}")
            return False

    except Exception as e:
        logging.exception("Exception occurred while sending message:")
        return False

@app.route(f"/wati-webhook/{unique_id}", methods=["POST"])
def wati_webhook():
    data = request.json
    logging.info(f"Received WATI webhook: {data}")
    if 'client_data' in data:
        customer_data = data['client_data']
        order = create_woocommerce_order(customer_data)
        if order:
            if send_wati_message(order):
                return jsonify({"status": "success", "order_id": order['id']}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to send message"}), 500
        else:
            return jsonify({"status": "error", "message": "Failed to create order"}), 500
    else:
        logging.error(f"Invalid data received in webhook: {data}")
        return jsonify({"status": "error", "message": "Invalid data"}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True )
