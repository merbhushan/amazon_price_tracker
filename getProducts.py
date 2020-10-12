import requests
import re
from bs4 import BeautifulSoup
import mysql.connector
import time

def get_converted_price(price):

    # stripped_price = price.strip("₹ ,")
    # replaced_price = stripped_price.replace(",", "")
    # find_dot = replaced_price.find(".")
    # to_convert_price = replaced_price[0:find_dot]
    # converted_price = int(to_convert_price)
    converted_price = float(re.sub(r"[^\d.]", "", price)) # Thanks to https://medium.com/@oorjahalt
    return converted_price


def extract_url(url):

    if url.find("www.amazon.in") != -1:
        index = url.find("/dp/")
        if index != -1:
            index2 = index + 14
            url = "https://www.amazon.in" + url[index:index2]
        else:
            index = url.find("/gp/")
            if index != -1:
                index2 = index + 22
                url = "https://www.amazon.in" + url[index:index2]
            else:
                url = None
    else:
        url = None
    return url


def get_products(url):

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
    }
    prefix = 'https://www.amazon.in'
    details = []

    _url = url

    if _url is None:
        details = []
    else:
        isLastPage = False
        pageNumber = 1

        while not isLastPage:
            fetchUrl = _url + '&page=' + str(pageNumber)
            print(fetchUrl)

            page = requests.get(fetchUrl, headers=headers)

            soup = BeautifulSoup(page.content, "html5lib")

            products = soup.find_all("a", {"class": ["a-link-normal", "a-text-normal"]})
            pagination = soup.find_all("ul", {"class": ["a-pagination"]})

            for product in products:
                productLink = product['href']

                if '/dp/' in productLink:
                    extractedUrl = extract_url(prefix + productLink)
                    details.append((extractedUrl,))
                    # print(productLink)
                    print(extractedUrl)

            isLastPage = False if len(pagination) > 0 else True

            pageNumber += 1
            print(isLastPage)
            time.sleep(5)

    if len(details) > 0:
        mysqlDb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="digital_marketing"
        )

        mycursor = mysqlDb.cursor()
        sql = "INSERT INTO amazon_products (amazon_products.url) VALUES (%s)"
        mycursor.executemany(sql, details)
        mysqlDb.commit()

    return;

#print(get_product_details("https://www.amazon.in/Voltas-Beko-Settings-Dishwasher-DT8S/dp/B07NF7NHSN/ref=lp_21074454031_1_1?s=kitchen&ie=UTF8&qid=1602399741&sr=1-1"))
#print(get_products("https://www.amazon.in/s?i=pantry&srs=9574332031&bbn=1350388031&rh=p_85%3A10440599031%2Cp_n_is_pantry%3A9574335031%2Cp_72%3A1318476031&dc&fst=as%3Aoff&qid=1602471022&rnid=1318475031&ref=sr_nr_p_72_1"))
#get_products("https://www.amazon.in/s?bbn=1389401031&rh=n%3A976419031%2Cn%3A%21976420031%2Cn%3A1389401031%2Cp_72%3A1318476031&dc&fst=as%3Aoff&qid=1602499329&rnid=1318475031&ref=lp_1389401031_nr_p_72_0")
get_products("https://www.amazon.in/s?k=honey&rh=p_72%3A1318476031&dc&qid=1602502086&rnid=1318475031&ref=sr_nr_p_72_1")
#print(get_product_details("https://www.amazon.in/CAVALLO-Linen-Club-Coloured-Casual/dp/B08F2KXQYQ/ref=redir_mobile_desktop?ie=UTF8&aaxitk=lze-iLwniW82C-5Rsexy.g&hsa_cr_id=3048998420002&ref_=sbx_be_s_sparkle_tsld_asin_0"))
#print(get_product_details("https://www.amazon.in/Pro-Nature-Atta-Whole-Wheat/dp/B01KA3FT48?pd_rd_w=n2tTw&pf_rd_p=45a0d2f0-945c-4e46-8089-d97a17a6d036&pf_rd_r=2BKQ1YKT93GAC6DPBRP0&pd_rd_r=2dd19283-fb17-4908-b77d-eeed928d6148&pd_rd_wg=byQIV&pd_rd_i=B01KA3FT48&fpw=alm&almBrandId=ctnow&ref_=pd_alm_fs_dsk_dp_dzrp_1_4_t"))
