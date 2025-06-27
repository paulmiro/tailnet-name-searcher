import argparse
import re
from typing import TypedDict

import requests

VERBOSE = False


class Offer(TypedDict):
    tcd: str
    token: str


def main():
    (cookie, regex, amount) = parse_args()

    print("logged in as user: " + get_current_user(cookie))
    print("current tailnet name: " + get_current_tcd(cookie))
    print()
    if VERBOSE:
        print("using regex: ", regex.pattern)
        print()
    print("starting search... (press ctrl+c to stop)")
    print()

    amount_checked = 0
    while amount_checked < amount:
        offers = get_offers(cookie)
        for offer in offers:
            if amount_checked % 10 == 0 and amount_checked != 0:
                print("checked " + str(amount_checked) + " offers")
            if check_offer(offer, regex):
                print("matched offer: ", offer["tcd"])
                if VERBOSE:
                    print("token: " + offer["token"])
                if input("accept offer? [y/n] ") == "y":
                    accept_offer(offer, cookie)
                    exit(0)
            amount_checked += 1
    exit(0)


def get_offers(cookie: str) -> list[Offer]:
    res = requests.get(
        "https://login.tailscale.com/admin/api/tcd/offers",
        headers={
            "Cookie": cookie,
        },
    )
    if res.json()["status"] != "success":
        exit("ERROR: failed to get offers: status is not 'success'")
    return res.json()["data"]["tcds"]


def check_offer(offer: Offer, regex: re.Pattern) -> bool:
    if re.search(regex, offer["tcd"]):
        if VERBOSE:
            print("matched offer token: ", offer["token"])
        return True
    return False


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
        exit("ERROR: failed to get offers: status is not 'success'")
    print(res.json())


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
        exit("ERROR: failed to get current tcd: status is not 'success'")
    return res.json()["data"]["tcd"]


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
        "-w",
        "--words",
        type=str,
        help="wanted words (comma-separated)",
        dest="words",
    )
    parser.add_argument(
        "-f",
        "--words-file",
        type=str,
        help="words file path (newline-separated)",
        dest="words_file",
    )
    parser.add_argument(
        "-r", "--regex", type=str, help="regex string", dest="regex"
    )

    parser.add_argument(
        "-n",
        "--amount",
        type=int,
        default=1000,
        help="amount of offers to check",
        dest="amount",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="verbose output"
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

    words: list[str] = []
    if args.regex:
        regex = re.compile(args.regex)
        if args.words or args.words_file:
            print("WARNING: --regex overrides --words and --words-file")
    elif args.words or args.words_file:
        if args.words:
            words = words + args.words.split(",")
        if args.words_file:
            try:
                words_file = open(args.words_file).read()
            except FileNotFoundError:
                exit("ERROR: words file not found: " + args.words_file)
            words = words + words_file.split("\n")
        regex = re.compile(
            "^(" + "|".join(words) + ")-(" + "|".join(words) + ").ts.net$"
        )
    else:
        exit("ERROR: no regex or words provided")

    amount = args.amount

    if VERBOSE:
        print("cookie: ", cookie)
        print("words: ", words)
        print("regex: ", regex.pattern)
        print("amount: ", args.amount)

    return (cookie, regex, amount)


if __name__ == "__main__":
    main()
