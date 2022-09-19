from flask import Flask, request, render_template
from flask_cors import cross_origin
import pandas as pd
import webscraper
import os
import time
import concurrent.futures

# define global path for csv folders
CSV_FOLDER = os.path.join('static', 'CSVs')


app = Flask(__name__)


# config environment variables
app.config['CSVs'] = CSV_FOLDER


class CleanCache:
    def __init__(self, directory=None):
        self.clean_path = directory
# only proceed if directory is not empty
        if os.listdir(self.clean_path) != list():
            files = os.listdir(self.clean_path)
            for fileName in files:
                print(fileName)
                os.remove(os.path.join(self.clean_path, fileName))
        print("cleaned!")


# Creating routes
@app.route('/', methods=['GET'])
@app.route('/index')
@cross_origin()
def home():
    return render_template('index.html')


# Path for the csv file
def save_as(dataframe, search_str):
    filename = search_str.replace("+", "_")
    # save the CSV file to CSVs folder
    csv_path = os.path.join(app.config['CSVs'], filename)
    file_extension = '.csv'
    final_path = f"{csv_path}{file_extension}"
    # clean previous files -
    CleanCache(directory=app.config['CSVs'])
    # save new csv to the csv folder
    dataframe.to_csv(final_path, index=None)
    print("File saved successfully!!")
    return final_path


@app.route('/results', methods=['POST', 'GET'])
@cross_origin()
def data_search():

    if request.method == 'POST':
        try:
            start_time = time.time()
            search_string = request.form['content']
            search_str = search_string.replace(" ", "+")

            # Creating connection and loading to the server
            data = webscraper.Data(search_str)
            links = data.creating_link()
            t1 = time.time()
            print(f"Number of total links: {len(links)}")
            print(f"Link creation successful-- Time taken {t1 - start_time:.2f} seconds")
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                executor.map(data.data_fetching, links)

            t2 = time.time()
            print(f"Loaded to the server-- Time taken {t2 - t1:.2f} seconds")

            # Pulling data from the server and display
            results = data.data_show()
            df1 = pd.DataFrame(results)
            t3 = time.time()
            print(f"Data collected successfully-- Time taken {t3 - t2:.2f} seconds")
            # print(df1)
            # To remove the id and page_no as these are not meaningful
            df1.drop(['_id'], axis=1, inplace=True)
            df1.reset_index(drop=True, inplace=True)

            # save dataframe as a csv which will be available to download
            csv_path = save_as(df1, search_str)
            t4 = time.time()
            print(f"CSV file created-- Time taken {t4 - t3:.2f} seconds")
        except Exception as err:
            print("data search error:", err)
            return render_template("404.html")
        else:
            return render_template('results.html', tables=[df1.to_html(classes='data')], titles=df1.columns.values, search_str=search_str, download_csv=csv_path)
        finally:
            # to clear the database at the end of the result shown
            data.data_del()
            end_time = time.time()
            total_time = end_time - start_time
            print(f"Total time taken is: {total_time:.2f} seconds")


if __name__ == "__main__":
    app.run(debug=True)
