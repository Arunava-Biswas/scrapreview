from bs4 import BeautifulSoup
import requests
import pandas as pd
from flask import Response
from database import connect, rec_insert, succ_insert, show_res, rec_del


class Data:
    def __init__(self, search):
        self.search_str = search

    def creating_link(self):
        base_url = "https://www.flipkart.com"

        search_url = f"{base_url}/search?q={self.search_str}"

        source1 = requests.get(search_url).text
        full_page = BeautifulSoup(source1, 'lxml')

        lst = []
        try:
            for division in full_page.find_all('div', class_="_1AtVbE col-12-12"):
                for div in division.find_all('div', class_="_2kHMtA"):
                    for anchors in div.find_all('a', class_="_1fQZEK"):
                        anchor = anchors['href']
                        lst.append(anchor)
        except Exception as err:
            print("Full_page error:", err)

        # Taking only the top 5 products results
        lst = lst[:5]
        lst2 = []
        for i in range(len(lst)):
            prod_url = search_url + lst[i]
            lst2.append(prod_url)

        com_urls = []
        try:
            for i in range(len(lst2)):
                source2 = requests.get(lst2[i]).text
                prod_page = BeautifulSoup(source2, 'lxml')

                try:
                    for division in prod_page.find_all('div', class_="_1YokD2 _3Mn1Gg"):
                        for big_box in division.find_all('div', class_="_1AtVbE col-12-12"):
                            for box in big_box.find_all('div', class_="col JOpGWq"):
                                anchors = box.find_all('a')
                                anchor = anchors[-1]
                                prod_link = anchor['href']
                                rev_url = base_url + prod_link

                                # Taking comments from 1st to 10th review pages for each product
                                urls = []
                                for var in range(1, 11):
                                    url = [rev_url + "&page=%i" % var]
                                    urls.append(url[0])

                                for n in range(len(urls)):
                                    com_urls.append(urls[n])

                except Exception as err:
                    print("Anchor detection error:", err)
        except Exception as err:
            print("Com_urls error:", err)

        return com_urls

    def data_fetching(self, url):
        # Creating empty lists to store the data
        products = []
        prices = []
        buyers = []
        ratings = []
        headings = []
        comments = []

        try:
            # Creating a dictionary on the basis of the columns
            source = requests.get(url).text
            rev_page = BeautifulSoup(source, 'lxml')

            for col in rev_page.find_all('div', class_="col _2wzgFH K0kLPL"):
                product = rev_page.find('div', class_="_2s4DIt _1CDdy2").text
                prod_name = product.replace("Reviews", "")
                products.append(prod_name)
                price = rev_page.find('div', class_="_30jeq3").text
                prices.append(price)
                buyer = col.find('div', class_="row _3n8db9").find('div', class_="row").find('p', class_="_2sc7ZR _2V5EHH").text
                buyers.append(buyer)
                rating = col.find('div', class_="row").div.text
                ratings.append(rating)
                header = col.div.p.text
                headings.append(header)
                comment = col.find('div', class_="t-ZTKy").div.div.text
                comments.append(comment)

        except Exception as err:
            print("Data fetching error:", err)
        else:
            mydict = ({'Product': products, 'Price': prices, 'Buyer': buyers, 'Rating': ratings, 'Header': headings, 'Comment': comments})

            # Creating dataframe from the dictionary
            try:
                df = pd.DataFrame(mydict)
            except Exception as err:
                print("Create df error: ", err)
            else:
                # Uploading the data into the database
                collection = connect()

                for (row, rs) in df.iterrows():
                    product = rs[0]
                    price = rs[1]
                    buyer = rs[2]
                    rating = rs[3]
                    header = rs[4]
                    comment = rs[5]

                    d = {
                        "Product_name": product,
                        "Unit Price": price,
                        "User": buyer,
                        "Ratings": rating,
                        "Comment_head": header,
                        "Comments": comment
                    }

                    rec_insert(collection, d)
                    return Response("{'a':'b'}", status=201, mimetype='application/json')
                succ_insert(collection)

    # Function to get the data from the database
    def data_show(self):
        collection = connect()
        try:
            results = show_res(collection)
        except Exception as err:
            pass
        else:
            return results

    # Deleting the collection in the database
    def data_del(self):
        collection = connect()
        rec_del(collection)
