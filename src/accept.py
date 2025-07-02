import argparse
import re
from typing import TypedDict

import requests

VERBOSE = False


class Offer(TypedDict):
    tcd: str
    token: str


def main():
    print()
    (cookie, token) = parse_args()

    offer = token_to_offer(token)

    print("logged in as user: " + get_current_user(cookie))
    print("current tailnet name: " + get_current_tcd(cookie))
    print("new tailnet name: ", offer["tcd"])

    print()

    if input("accept new name? [y/n] ") == "y":
        print("accepting offer...")
        accept_offer(offer, cookie)
    else:
        print("not accepting offer")

    exit(0)


def accept_offer(offer: Offer, cookie: str) -> None:
    res = requests.post(
        "https://login.tailscale.com/admin/api/tcd",
        headers={
            "Cookie": cookie,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        },
        json=offer,
    )
    if res.json()["status"] != "success":
        exit("ERROR: failed to accept offer: status is not 'success'")
    print("success!")


def get_current_user(cookie: str) -> str:
    res = requests.get(
        "https://login.tailscale.com/admin/api/self",
        headers={
            "Cookie": cookie,
        },
    )
    if res.json()["status"] != "success":
        exit("ERROR: failed to get current user: status is not 'success'")
    return res.json()["data"]["user"]["loginName"]


def get_current_tcd(cookie: str) -> str:
    res = requests.get(
        "https://login.tailscale.com/admin/api/tcd",
        headers={
            "Cookie": cookie,
        },
    )
    if res.json()["status"] != "success":
        exit(
            "ERROR: failed to get current tailnet name: status is not 'success'"
        )
    return res.json()["data"]["tcd"]


def token_to_offer(token: str) -> Offer:
    tcd = token.split("/")[0]
    return {
        "tcd": tcd,
        "token": token,
    }


def parse_args() -> tuple[str, re.Pattern]:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c", "--curl-file", type=str, help="curl file path", dest="curl_file"
    )
    parser.add_argument(
        "--cookie-file",
        type=str,
        help="cookie file path",
        dest="cookie_file",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="verbose output"
    )

    parser.add_argument(
        "token",
        type=str,
        help="the full token",
    )
    args = parser.parse_args()

    global VERBOSE
    if args.verbose:
        VERBOSE = True

    if args.cookie_file:
        try:
            cookie = open(args.cookie_file).read()
        except FileNotFoundError:
            exit("ERROR: cookie file not found: " + args.cookie_file)
        if args.curl_file:
            print("WARNING: --cookie-file overrides --curl-file")
    elif args.curl_file:
        try:
            curl_file = open(args.curl_file).read()
            cookie_regex = re.compile(r"'Cookie: (.*)'")
            cookie = cookie_regex.search(curl_file).group(1)
            if not cookie:
                exit("ERROR: no cookie found in curl file: " + args.curl_file)
        except FileNotFoundError:
            exit("ERROR: curl file not found: " + args.curl_file)
    else:
        exit("ERROR: no cookie or curl file provided")

    if args.token:
        token = args.token
    else:
        exit("ERROR: no token provided")

    token_regex = re.compile(r"[a-zA-Z]*-[a-zA-Z]*\.ts\.net/[0-9]*/[0-9a-f]*")
    if not token_regex.search(token):
        exit("ERROR: token does not match the expected format")

    if VERBOSE:
        print("cookie: ", cookie)
        print("token: ", token)

    return (cookie, token)


if __name__ == "__main__":
    main()
