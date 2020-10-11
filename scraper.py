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


def get_product_details(url, amazonCovertedUrl=None):

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
    }
    details = {"name": "", "price": 0, "deal": True, "url": ""}
    if amazonCovertedUrl!= None and amazonCovertedUrl != url:
        _url = amazonCovertedUrl
    else:
        _url = extract_url(url)

    if _url is None:
        details = None
    else:
        page = requests.get(_url, headers=headers)

        soup = BeautifulSoup(page.content, "html5lib")
        title = soup.find(id="productTitle")
        price = soup.find(id="priceblock_dealprice")
        mrp = soup.findAll('span', class_='priceBlockStrikePriceString')

        if price is None:
            price = soup.find(id="priceblock_ourprice")
            details["deal"] = False
        if title is not None and price is not None:
            details["name"] = title.get_text().strip()
            details["price"] = str(get_converted_price(price.get_text()))
            details["url"] = _url
            if len(mrp) > 0:
                details["mrp"] = str(get_converted_price(mrp[0].get_text()))
            else:
                details["mrp"] = details["price"]
        else:
            details = None
    return details


mysqlDb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="digital_marketing"
)

mycursor = mysqlDb.cursor()

mycursor.execute("SELECT p.id, p.name, p.amazon_url, p.amazon_converted_url, p.amazon_price FROM products p WHERE p.`status` = 'Active'")

myresult = mycursor.fetchall()

for row in myresult:
    productId,productName,amazonUrl,amazonCovertedUrl,amazonPrice = row
    amazonDetail = get_product_details(amazonUrl, amazonCovertedUrl)
    #amazonDetail = {'name': 'OnePlus 8 (Glacial Green 6GB RAM+128GB Storage)', 'price': '41999.0', 'deal': False, 'url': 'https://www.amazon.in/dp/B078BNQ318'}
    print(amazonDetail)
    if amazonDetail != None and amazonDetail['price'] != amazonPrice:
        sql = "UPDATE products SET products.name = if(products.name IS NULL, %s, products.name), products.amazon_price = %s, products.amazon_converted_url = %s, products.mrp = %s WHERE products.id = %s"
        value = (amazonDetail['name'], amazonDetail['price'], amazonDetail['url'], amazonDetail['mrp'], str(productId))
        mycursor.execute(sql, value)
        mysqlDb.commit()

    time.sleep(5)


#print(get_product_details("https://www.amazon.in/Voltas-Beko-Settings-Dishwasher-DT8S/dp/B07NF7NHSN/ref=lp_21074454031_1_1?s=kitchen&ie=UTF8&qid=1602399741&sr=1-1"))
#print(get_product_details(""))
#print(get_product_details("https://www.amazon.in/CAVALLO-Linen-Club-Coloured-Casual/dp/B08F2KXQYQ/ref=redir_mobile_desktop?ie=UTF8&aaxitk=lze-iLwniW82C-5Rsexy.g&hsa_cr_id=3048998420002&ref_=sbx_be_s_sparkle_tsld_asin_0"))
#print(get_product_details("https://www.amazon.in/Pro-Nature-Atta-Whole-Wheat/dp/B01KA3FT48?pd_rd_w=n2tTw&pf_rd_p=45a0d2f0-945c-4e46-8089-d97a17a6d036&pf_rd_r=2BKQ1YKT93GAC6DPBRP0&pd_rd_r=2dd19283-fb17-4908-b77d-eeed928d6148&pd_rd_wg=byQIV&pd_rd_i=B01KA3FT48&fpw=alm&almBrandId=ctnow&ref_=pd_alm_fs_dsk_dp_dzrp_1_4_t"))
