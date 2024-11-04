# import re
# from typing import List
# import scrapy
# from scrapy.cmdline import execute
# import pandas as pd
# import unicodedata
# import string
# from deep_translator import GoogleTranslator
# from datetime import datetime
#
#
# class ArgentinaGobArDataSpider(scrapy.Spider):
#     name = "argentina_gob_ar_data"
#
#     def start_requests(self):
#         cookies = {
#             '_gcl_au': '1.1.1135452616.1729256521',
#             '_ga': 'GA1.1.934766915.1729256521',
#             '_fbp': 'fb.2.1729256521361.831383320621035232',
#             '_ga_RYBJESQW41': 'GS1.1.1729256521.1.1.1729258394.60.0.0',
#         }
#
#         headers = {
#             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#             'accept-language': 'en-US,en;q=0.9',
#             'cache-control': 'no-cache',
#             'pragma': 'no-cache',
#             'priority': 'u=0, i',
#             'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
#             'sec-ch-ua-mobile': '?0',
#             'sec-ch-ua-platform': '"Windows"',
#             'sec-fetch-dest': 'document',
#             'sec-fetch-mode': 'navigate',
#             'sec-fetch-site': 'none',
#             'sec-fetch-user': '?1',
#             'upgrade-insecure-requests': '1',
#             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
#         }
#
#         yield scrapy.Request(
#             url="https://www.argentina.gob.ar/cnv/denuncias-penales",
#             headers=headers,
#             cookies=cookies,
#             callback=self.parse
#         )
#
#     def remove_diacritics(self, input_str: str) -> str:
#         normalized_str = unicodedata.normalize('NFD', input_str)
#         return ''.join(char for char in normalized_str if unicodedata.category(char) != 'Mn')
#
#     # def to_title_case(self, input_str: str) -> str:
#     #     return input_str.title()
#
#     def remove_punctuation(self, input_str: str) -> str:
#         # Replace specific characters first
#         input_str = input_str.replace("“", "").replace("”", "").replace("°", " ").replace("-", " ")
#         # Use translate to remove remaining
#         input_str = input_str.translate(str.maketrans('', '', string.punctuation))
#         return ' '.join(input_str.split())
#
#     def parse(self, response, **kwargs):
#         # Extract column names and clean them
#         columns = response.xpath('//table[@class="table table-responsive-poncho"]/thead/tr/th/text()').getall()
#         columns = [self.remove_diacritics(col.strip()) for col in columns]
#
#         # Extract rows and prepare data
#         data_list = []
#         rows = response.xpath('//table[@class="table table-responsive-poncho"]/tbody/tr')
#         for row in rows:
#             data_dict = {}
#             data_dict['url'] = "https://www.argentina.gob.ar/denuncias-penales"
#             for index, column in enumerate(columns):
#                 cell = row.xpath(f'./td[{index + 1}]')
#                 link = cell.xpath('./a/@href').get()
#                 text = cell.xpath('./a/text()').get(default=cell.xpath('./text()').get())
#
#                 # Clean text: remove diacritics and convert to title case
#                 clean_text = self.remove_diacritics(text.strip()).replace('"', '') if text else None
#                 if clean_text:
#                     # Skip punctuation removal and convert to date format if it's a date column
#                     if "date" in column.lower() or "fecha" in column.lower():
#                         date_obj = datetime.strptime(clean_text, "%d/%m/%Y")  # Assuming original format is DD/MM/YYYY
#                         clean_text = date_obj.strftime("%Y-%m-%d")
#
#                     if 'entidad' in column.lower():
#                         # Regular expression to identify URLs
#                         url_pattern = re.compile(r'https?://\S+|www\.\S+')
#                         # Find all URLs in the text and separate them
#                         urls = url_pattern.findall(clean_text)
#                         main_text = url_pattern.sub('', clean_text).strip()  # Remove URLs from the main text
#
#                         # Convert the main text to title case
#                         # main_text = ' '.join(
#                         #     [word if word.isupper() else word.capitalize() for word in main_text.split()])
#                         main_text = main_text.title()
#                         # Reattach the URL(s) if they were present
#                         clean_text = self.remove_punctuation(main_text)
#                         if urls:
#                             clean_text += ' ' + ' '.join(urls).replace('.', ' ')
#                     clean_text = clean_text.replace('“', '').replace('”', '').replace('°', '')
#                 data_dict[column] = clean_text
#                 if link:
#                     data_dict[f"{column}_link"] = link.strip()
#
#             data_list.append(data_dict)
#
#         # Create a DataFrame
#         df = pd.DataFrame(data_list).fillna('N/A')
#         df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('°', '')
#
#         # Save the original data
#         original_file = 'argentina_gob_ar_native.xlsx'
#         df.to_excel(original_file, index=False)
#         print(f"Data saved to {original_file}")
#
#         # Translate to English for specific columns
#         columns_to_translate = [col for col in df.columns if not col.endswith('_link')]
#         translated_df = self.translate_dataframe(df, columns_to_translate)
#         translated_df = self.translate_columns(translated_df.columns)
#         translated_file = 'argentina_gob_ar_english.xlsx'
#         translated_df.to_excel(translated_file, index=False)
#         print(f"Data translated and saved to {translated_file}")
#
#     def translate_dataframe(self, df: pd.DataFrame, columns_to_translate: List[str]) -> pd.DataFrame:
#         translator = GoogleTranslator(source='es', target='en')
#         translated_data = df.copy()
#
#         for col in columns_to_translate:
#             translated_data[col] = translated_data[col].apply(
#                 lambda x: translator.translate(x) if isinstance(x, str) else x
#             )
#
#         return translated_data
#
#     def translate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
#         translator = GoogleTranslator(source='es', target='en')
#         translated_columns = {col: translator.translate(col.replace('_', ' ')).lower().replace(' ', '_') for col in
#                               df.columns}
#         df.rename(columns=translated_columns, inplace=True)
#         return df
#
#
# if __name__ == '__main__':
#     execute(f'scrapy crawl {ArgentinaGobArDataSpider.name}'.split())

import re
import scrapy
from scrapy.cmdline import execute
import pandas as pd
import unicodedata
import string
from deep_translator import GoogleTranslator
from datetime import datetime
from typing import List, Dict


class ArgentinaGobArDataSpider(scrapy.Spider):
    name = "argentina_gob_ar_data"

    def start_requests(self):
        """
        Initiates the requests to scrape data from the Argentina government website.
        """
        cookies = self.get_request_cookies()
        headers = self.get_request_headers()

        yield scrapy.Request(
            url="https://www.argentina.gob.ar/cnv/denuncias-penales",
            headers=headers,
            cookies=cookies,
            callback=self.parse
        )

    def get_request_cookies(self) -> Dict[str, str]:
        """
        Returns a dictionary of cookies for the request.
        """
        return {
            '_gcl_au': '1.1.1135452616.1729256521',
            '_ga': 'GA1.1.934766915.1729256521',
            '_fbp': 'fb.2.1729256521361.831383320621035232',
            '_ga_RYBJESQW41': 'GS1.1.1729256521.1.1.1729258394.60.0.0',
        }

    def get_request_headers(self) -> Dict[str, str]:
        """
        Returns a dictionary of headers for the request.
        """
        return {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        }

    def remove_diacritics(self, input_str: str) -> str:
        """
        Removes diacritic marks from a given string.

        Args:
            input_str (str): The string from which to remove diacritics.

        Returns:
            str: The normalized string without diacritics.
        """
        normalized_str = unicodedata.normalize('NFD', input_str)
        return ''.join(char for char in normalized_str if unicodedata.category(char) != 'Mn')

    def remove_punctuation(self, input_str: str) -> str:
        """
        Removes punctuation and unnecessary characters from the input string.

        Args:
            input_str (str): The string to clean.

        Returns:
            str: The cleaned string without punctuation.
        """
        # Replace specific characters first
        input_str = input_str.replace("“", "").replace("”", "").replace("°", " ").replace("-", " ")
        # Use translate to remove remaining punctuation
        input_str = input_str.translate(str.maketrans('', '', string.punctuation))
        return ' '.join(input_str.split())

    def parse(self, response, **kwargs):
        """
        Parses the response from the web page and extracts relevant data.

        Args:
            response (scrapy.http.Response): The response object containing the page data.
        """
        # Extract column names and clean them
        columns = self.extract_columns(response)

        # Extract rows and prepare data
        data_list = self.extract_data(response, columns)

        # Create a DataFrame and save the original data
        self.save_original_data(data_list)

        # Translate to English and save the translated data
        self.save_translated_data(data_list)

    def extract_columns(self, response) -> List[str]:
        """
        Extracts and cleans column names from the response.

        Args:
            response (scrapy.http.Response): The response object containing the page data.

        Returns:
            List[str]: A list of cleaned column names.
        """
        columns = response.xpath('//table[@class="table table-responsive-poncho"]/thead/tr/th/text()').getall()
        return [self.remove_diacritics(col.strip()) for col in columns]

    def extract_data(self, response, columns: List[str]) -> List[Dict[str, str]]:
        """
        Extracts and processes data rows from the response.

        Args:
            response (scrapy.http.Response): The response object containing the page data.
            columns (List[str]): A list of cleaned column names.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the extracted data.
        """
        data_list = []
        rows = response.xpath('//table[@class="table table-responsive-poncho"]/tbody/tr')

        for row in rows:
            data_dict = self.extract_row_data(row, columns)
            data_list.append(data_dict)

        return data_list

    def extract_row_data(self, row, columns: List[str]) -> Dict[str, str]:
        """
        Extracts data for a single row and cleans it.

        Args:
            row (scrapy.selector.unified.Selector): The row selector object.
            columns (List[str]): A list of cleaned column names.

        Returns:
            Dict[str, str]: A dictionary containing the cleaned data for the row.
        """
        data_dict = {'url': "https://www.argentina.gob.ar/denuncias-penales"}

        for index, column in enumerate(columns):
            cell = row.xpath(f'./td[{index + 1}]')
            link = cell.xpath('./a/@href').get()
            text = cell.xpath('./a/text()').get(default=cell.xpath('./text()').get())

            clean_text = self.clean_text(text, column) if text else None
            data_dict[column] = clean_text

            if link:
                data_dict[f"{column}_link"] = link.strip()

        return data_dict

    def clean_text(self, text: str, column: str) -> str:
        """
        Cleans the text extracted from a cell based on its column type.

        Args:
            text (str): The text to clean.
            column (str): The name of the column from which the text was extracted.

        Returns:
            str: The cleaned text.
        """
        clean_text = self.remove_diacritics(text.strip()).replace('"', '')
        if "fecha" in column.lower():
            # Convert date format from DD/MM/YYYY to YYYY-MM-DD
            date_obj = datetime.strptime(clean_text, "%d/%m/%Y")
            clean_text = date_obj.strftime("%Y-%m-%d")

        if 'entidad' in column.lower():
            urls = self.extract_urls(clean_text)
            main_text = self.remove_urls(clean_text).title()

            # Clean the main text and reattach URLs if present
            clean_text = self.remove_punctuation(main_text)
            if urls:
                clean_text += ' ' + ' '.join(urls).replace('.', ' ')

        return clean_text.replace('“', '').replace('”', '').replace('°', '')

    def extract_urls(self, text: str) -> List[str]:
        """
        Extracts URLs from the given text.

        Args:
            text (str): The text to extract URLs from.

        Returns:
            List[str]: A list of extracted URLs.
        """
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return url_pattern.findall(text)

    def remove_urls(self, text: str) -> str:
        """
        Removes URLs from the text.

        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned text without URLs.
        """
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return url_pattern.sub('', text).strip()

    def save_original_data(self, data_list: List[Dict[str, str]]):
        """
        Saves the original extracted data to an Excel file.

        Args:
            data_list (List[Dict[str, str]]): The list of extracted data.
        """
        df = pd.DataFrame(data_list).fillna('N/A')
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('°', '')

        original_file = f"../files/argentina_gob_ar_native{datetime.today().strftime('%Y%m%d')}.xlsx"
        df.to_excel(original_file, index=False)
        print(f"Data saved to {original_file}")

    def save_translated_data(self, data_list: List[Dict[str, str]]):
        """
        Translates the extracted data to English and saves it to an Excel file.

        Args:
            data_list (List[Dict[str, str]]): The list of extracted data.
        """
        df = pd.DataFrame(data_list).fillna('N/A')
        columns_to_translate = [col for col in df.columns if not col.endswith('_link') or col == 'url']
        translated_df = self.translate_dataframe(df, columns_to_translate)
        translated_df = self.translate_columns(translated_df)

        translated_file = f"../files/argentina_gob_ar_english{datetime.today().strftime('%Y%m%d')}.xlsx"
        translated_df.to_excel(translated_file, index=False)
        print(f"Data translated and saved to {translated_file}")

    def translate_dataframe(self, df: pd.DataFrame, columns_to_translate: List[str]) -> pd.DataFrame:
        """
        Translates specified columns of a DataFrame from Spanish to English.

        Args:
            df (pd.DataFrame): The DataFrame to translate.
            columns_to_translate (List[str]): The list of column names to translate.

        Returns:
            pd.DataFrame: The DataFrame with translated columns.
        """
        translator = GoogleTranslator(source='es', target='en')
        translated_data = df.copy()
        for col in columns_to_translate:
            translated_data[col] = translated_data[col].apply(
                lambda x: translator.translate(x) if isinstance(x, str) else x
            )
            translated_data['ENTIDAD'] = translated_data['ENTIDAD'].str.replace('.', '')
        return translated_data

    def translate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Translates the column names of a DataFrame from Spanish to English.

        Args:
            df (pd.DataFrame): The DataFrame whose columns are to be translated.

        Returns:
            pd.DataFrame: The DataFrame with translated column names.
        """
        translator = GoogleTranslator(source='es', target='en')
        translated_columns = {
            col: translator.translate(col).lower().replace('_', ' ').replace(' ', '_').replace('.', '') for col in
            df.columns}

        df.rename(columns=translated_columns, inplace=True)
        return df


if __name__ == '__main__':
    execute(f'scrapy crawl {ArgentinaGobArDataSpider.name}'.split())
