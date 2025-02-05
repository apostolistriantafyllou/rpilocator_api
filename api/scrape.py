import re

from dotenv import load_dotenv

from utils.utils import get_soup, get_status, get_feed, get_twitter_client

load_dotenv()

FEED_URL = "https://rpilocator.com/feed/"


class rpiLoc:
    @staticmethod
    def rpi_all(country: str):
        URL = f"https://rpilocator.com/?country={country}&cat=PI4"
        status = get_status(URL)
        response = get_soup(URL)

        # find table get th and td into rows
        tbody = response.find("tbody")
        containers = tbody.find_all("tr")

        if containers:
            api = []
            for container in containers:
                cells = container.find_all("td")
                product = cells[0].text
                url = cells[1].find('a')['href']
                update_status = cells[2].find("i")["class"][2]
                vendor = cells[3].text
                in_stock = cells[4].text
                price = "$" + cells[6].text[6:]
                cells = container.find_all("td")
                if update_status == "text-success":
                    api.append(
                        {
                            "product": product,
                            "url": url,
                            "vendor": vendor,
                            "in_stock": in_stock,
                            "price": price,
                        }

                    )
            data = {"status": status, "data": api}

            if status != 200:
                raise Exception("API response: {}".format(status))
            return data
        else:
            raise Exception("No data found")

    @staticmethod
    def rpi_model(country: str, gbs: int):
        URL = f"https://rpilocator.com/?country={country}&cat=PI4"
        status = get_status(URL)
        response = get_soup(URL)

        # find table get th and td into rows
        tbody = response.find("tbody")
        containers = tbody.find_all("tr")

        if containers:
            api = []
            for container in containers:
                cells = container.find_all("td")
                product = cells[0].text
                url = cells[1].find('a')['href']
                update_status = cells[2].find("i")["class"][2]
                vendor = cells[3].text
                in_stock = cells[4].text
                price = "$" + cells[6].text[6:]

                if update_status == "text-success":
                    if f"{gbs}GB" in product:
                        api.append(
                            {
                                "product": product,
                                "url": url,
                                "vendor": vendor,
                                "in_stock": in_stock,
                                "price": price,
                            }

                        )
            data = {"status": status, "data": api}

            if status != 200:
                raise Exception("API response: {}".format(status))
            return data
    @staticmethod
    def pi4_8gig_stockcheck(gblist):
        URL = f"https://rpilocator.com/"
        status = get_status(URL)
        response = get_soup(URL)

        # find table get th and td into rows
        tbody = response.find("tbody")
        containers = tbody.find_all("tr")
        api = []
        raspis = []

        if containers:
            for container in containers:
                cells = container.find_all("td")
                product = cells[0].text
                url = cells[1].find('a')['href']
                update_status = cells[2].find("i")["class"][2]
                vendor = cells[3].text
                in_stock = cells[4].text
                price = cells[6].text

                if in_stock == 'Yes':
                    if update_status == "text-success":
                        for gb in gblist:
                            #if str(gb)+"GB" in product:
                            if str(gb)+"MB" in product:
                                raspis.append([url, price])
            data = {"status": status, "data": api}
            print(raspis)
            if status != 200:
                raise Exception("API response: {}".format(status))
            if str(raspis) != "[]":
                return raspis

    @staticmethod
    def get_rss_entires(region: str):
        all_entries = get_feed(FEED_URL)
        status = get_status(FEED_URL)

        results = []
        for entries in all_entries:
            for entry in entries:
                url = entry.link
                title = entry.title
                country = entry.tags[1].term

                title = re.sub(r"<.*?>", "", title)
                # remove new lines from post content
                title = re.sub(r"\n", " ", title)
                # remove extra spaces from post content
                title = re.sub(r"\s{2,}", " ", title)

                # remove case sensitive
                if region.lower() in country.lower():
                    model = title.split(f"): ")[1]
                    model = model.split(" is")[0]

                    vendor = title.split(f"at ")[1]
                    vendor = vendor.split(" ")[0]

                    amount = title.split(" units")[0]
                    amount = amount.split(" ")[15]
                    if amount <= "1":
                        amount = amount + " unit"
                    elif amount > "1":
                        amount = amount + " units"

                    # IF RPI4  is in title
                    if "RPi 4" in title:
                        results.append(
                            {
                                "title": title,
                                "model": model,
                                "vendor": vendor,
                                "amount": amount,
                                "url": url,
                                "country": country.upper(),
                            }
                        )
        data = {"status": status, "data": results}

        if status != 200:
            raise Exception("API response: {}".format(status))
        return data

    @staticmethod
    def get_rss_model_entires(region: str, gbs: int):
        all_entries = get_feed(FEED_URL)
        status = get_status(FEED_URL)

        results = []
        for entries in all_entries:
            for entry in entries:
                url = entry.link
                title = entry.title
                country = entry.tags[1].term

                title = re.sub(r"<.*?>", "", title)
                # remove new lines from post content
                title = re.sub(r"\n", " ", title)
                # remove extra spaces from post content
                title = re.sub(r"\s{2,}", " ", title)

                # search for RPI 4 in title
                if f"{gbs}GB" in title:
                    # remove case sensitive
                    if region.lower() in country.lower():
                        model = title.split(f"): ")[1]
                        model = model.split(" is")[0]

                        vendor = title.split(f"at ")[1]
                        vendor = vendor.split(" ")[0]

                        amount = title.split(" units")[0]
                        amount = amount.split(" ")[15]
                        if amount <= "1":
                            amount = amount + " unit"
                        elif amount > "1":
                            amount = amount + " units"

                        # IF RPI4  is in title
                        if "RPi 4" in title:
                            results.append(
                                {
                                    "title": title,
                                    "model": model,
                                    "vendor": vendor,
                                    "amount": amount,
                                    "url": url,
                                    "country": country.upper(),
                                }
                            )
        data = {"status": status, "data": results}

        if status != 200:
            raise Exception("API response: {}".format(status))
        return data

    @staticmethod
    def get_rpil_tweets(region: str):
        all_tweets = []
        new_tweets = []
        client = get_twitter_client()
        new_tweets = client.user_timeline(screen_name="rpilocator", count=5)
        while len(new_tweets) > 0:
            for tweet in new_tweets:
                # check for stock alert wording in tweet then also check for RPi 4 in tweet
                if f"Stock Alert ({region})" and "RPi 4 Model B" in tweet.text:
                    parsed_tweet = {'date': tweet.created_at,
                                    'twitter_name': tweet.user.screen_name,
                                    'text': tweet.text}
                    all_tweets.append(parsed_tweet)
            max_id = new_tweets[-1].id - 1
            new_tweets = client.user_timeline(screen_name="rpilocator",
                                              count=5, max_id=max_id)
        return all_tweets


if __name__ == '__main__':
    print(rpiLoc.get_rss_entires("US"))
