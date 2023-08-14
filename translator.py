import time
import requests
from bs4 import BeautifulSoup
import urllib.parse
import logging


def chunk(completion):
    completions = []

    while len(completion) > 4096:
        cut_index = 0
        for i in range(4096, -1, -1):
            if completion[i] in [' ', '\n', '\t', '\r']:
                cut_index = i
                break
        completions.append(completion[:cut_index])
        completion = completion[cut_index:]

    completions.append(completion)

    return completions


RETRY_DELAY = 1  # adjust this as necessary
RETRY_ATTEMPTS = 10  # adjust this as necessary


def translate(sl, tl, q):
    qs = chunk(q)  # splitting the string into a list of characters

    for i in range(len(qs)):
        retry_delay = RETRY_DELAY
        attempts = 0

        while True:
            attempts += 1
            try:
                resp = requests.get(f"https://translate.google.com/m?sl={sl}&tl={tl}&q={urllib.parse.quote(qs[i])}")
            except Exception as e:
                logging.error(f"Can't do request: {e}")
                return None
            if resp.status_code != 200:
                logging.error(f"Bad status: {resp.status_code}")
                if attempts < RETRY_ATTEMPTS:
                    time.sleep(retry_delay)
                    i -= 1
                    continue
                else:
                    return None

            soup = BeautifulSoup(resp.text, 'html.parser')
            result_container = soup.find('div', {'class': 'result-container'})

            if result_container is None:
                logging.error("Not found")
                return None

            qs[i] = result_container.text

            break  # break the while loop if the request is successful and result is found

    return ' '.join(qs)


if __name__ == "__main__":
    while True:
        text = input()
        print(translate("auto", "uz", text))
