import subprocess
import json
import shlex
import sys
import argparse

AUTH_TOKEN = None
SESSION_TOKEN = None

def run_curl(command: str):
    """
    Runs a curl command and returns its output as text.
    Example:
        run_curl("curl -X GET https://api.example.com/users -H 'Authorization: Bearer TOKEN'")
    """
    try:
        # Split the command safely and execute
        result = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running curl: {e}")
        print(f"stderr: {e.stderr}")
        return None

def run_curl_json(command: str):
    """
    Runs a curl command and tries to parse JSON output.
    Example:
        run_curl_json("curl -s https://api.example.com/users")
    """
    output = run_curl(command)
    if output:
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            print("Response was not valid JSON:")
            print(output)
    return None

def ask_question(question: str):
    print(question)
    return input("\n> ").strip()

##Todo - make this actually smarter
##Returns product_id, inventory_id
def find_ids(response, card):
    for currentCard in response['data']:
        if currentCard['name'] == card:
            for inventory in currentCard['inventory']:
                if inventory['total_quantity'] > 0:
                    return currentCard['id'], inventory['id']
    return None, None

def search_for_card(card: str):
    curl_cmd = f"""
        curl 'https://ipi.talaria.shop/api/products/search/inventory' \
            -H 'accept: application/json' \
            -H 'accept-language: en-US,en;q=0.9' \
            -H 'authorization: Token {AUTH_TOKEN}' \
            -H 'cache-control: no-cache' \
            -H 'content-type: application/json' \
            -H 'origin: https://oasisgamesslc.com' \
            -H 'pragma: no-cache' \
            -H 'priority: u=1, i' \
            -H 'referer: https://oasisgamesslc.com/' \
            -H 'sec-ch-ua: "Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"' \
            -H 'sec-ch-ua-mobile: ?0' \
            -H 'sec-ch-ua-platform: "macOS"' \
            -H 'sec-fetch-dest: empty' \
            -H 'sec-fetch-mode: cors' \
            -H 'sec-fetch-site: cross-site' \
            -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36' \
            -H 'x-sessionid: {SESSION_TOKEN}' \
            -H 'x-storeid: f98a01b3154fe3ede1b8f7172a1d2dce' \
            --data-raw '{{"product_line":["magic"],"is_buylist":false,"name":"{card}","aggregations":["is_sealed","condition","finish","magic_set","language"],"limit":30,"offset":0}}'
    """ 
    response = run_curl_json(curl_cmd)
    product_id, inventory_id = find_ids(response, card)
    return product_id, inventory_id


def add_to_cart(product_id: int, inventory_id: int):
    curl_cmd = f"""
        curl 'https://ipi.talaria.shop/api/carts/5b0244e5-bf5f-40d0-b64e-bef7cd24904f' \
        -H 'accept: application/json' \
        -H 'accept-language: en-US,en;q=0.9' \
        -H 'authorization: Token {AUTH_TOKEN}' \
        -H 'cache-control: no-cache' \
        -H 'content-type: application/json' \
        -H 'origin: https://oasisgamesslc.com' \
        -H 'pragma: no-cache' \
        -H 'priority: u=1, i' \
        -H 'referer: https://oasisgamesslc.com/' \
        -H 'sec-ch-ua: "Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"' \
        -H 'sec-ch-ua-mobile: ?0' \
        -H 'sec-ch-ua-platform: "macOS"' \
        -H 'sec-fetch-dest: empty' \
        -H 'sec-fetch-mode: cors' \
        -H 'sec-fetch-site: cross-site' \
        -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36' \
        -H 'x-sessionid: {SESSION_TOKEN}' \
        -H 'x-storeid: f98a01b3154fe3ede1b8f7172a1d2dce' \
        --data-raw '{{"inventory_id":{inventory_id},"quantity":1,"product_id":{product_id}}}'
    """ 
    response = run_curl_json(curl_cmd)
    print(f'Added {response['inventory']['foreign_obj']['name']} in {response['inventory']['condition']} condition to cart for {response['inventory']['sell_price']}')

def search_and_add_to_cart(card: str):
    product_id, inventory_id = search_for_card(card)
    add_to_cart(product_id, inventory_id)

def main():
    global AUTH_TOKEN, SESSION_TOKEN
    # ---- Step 1: Define arguments ----
    parser = argparse.ArgumentParser(description="Oasis CLI for card searching.")
    parser.add_argument("-aT", "--authToken", help="Authentication token")
    parser.add_argument("-sT", "--sessionToken", help="Session token")
    parser.add_argument("-c", "--card", help="Card name to search for")
    args = parser.parse_args()

    # ---- Step 2: Fallback to interactive prompts if missing ----
    AUTH_TOKEN = args.authToken or ask_question("Enter your Auth Token")
    SESSION_TOKEN = args.sessionToken or ask_question("Enter your Session Token")
    card = args.card or ask_question("Search for Card")

    # ---- Step 3: Do something with the results ----
    print(f"\nUsing Auth Token: {AUTH_TOKEN}")
    print(f"Using Session Token: {SESSION_TOKEN}")
    print(f"Card to search: {card}\n")

    search_and_add_to_cart(card)

if __name__ == "__main__":
    main()