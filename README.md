# Tailscale Tailnet Name Searcher

This program automates the process of clicking that one "Re-roll options" button on the tailscale dashboard

![At least I didn't have to click the same button over and over again](https://imgs.xkcd.com/comics/automation.png)

## ⚠️⚠️⚠️ WARNING ⚠️⚠️⚠️

Using this software is _probably_ against Tailscale's terms of service. Do not use it.

## How to use

1. Go to [login.tailscale.com/admin/dns](https://login.tailscale.com/admin/dns)
2. Click on `Rename Tailnet`
3. Open your browser's devtools (`F12`) and go to the `Network` tab
4. Click on `Re-roll options`
5. Right-Click the new entry in the Network Menu (`GET https://login.tailscale.com/admin/api/tcd/offers`) and select `Copy as cUrl`
6. Save the copied text to a file on your system (referenced as `CURL_FILE` below)

I have included a (probably almost exhaustive) wordlist for both the first and second word, if you want to see what the options are.

### Arguments

```
  -c, --curl-file CURL_FILE     curl file path
  -w, --words WORDS             wanted words (comma-separated)
  -f, --words-file WORDS_FILE   words file path (newline-separated)
  -r, --regex REGEX             regex string
  -n, --amount AMOUNT           amount of offers to check
  -v, --verbose                 verbose output
```

This program will automatically extract your auth cookie from the cUrl file. If you want, you can also specify a file that contains only the cookie with `--cookie-file` instead of `--curl-file`

You don't have to accept the offer immediately. They stay valid even if you reroll again. (I'm not sure for how long though)

I included a second script that takes the full token as the first argument and accepts the offer for you (src/accept.py).

### Installation

### With Nix

No need to install anything. You can just run the program with

```sh
nix run github:paulmiro/tailscale_name_searcher -- <arguments>
```

### Whithout Nix

Make sure you have python 3 and `requests` installed

```sh
python src/main.py <arguments>
```
