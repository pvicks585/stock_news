'''
Importing the neccesary libraries
'''
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re 
from datetime import datetime
import urllib
import urllib.request
import requests

class StockInfo:
    def __init__(self, stock):
        '''
        Params: URL - Site where to grab data
        Stock - Keyword to query by
        '''
        self.stock = stock
        


    def getStockLinks(self, url):
        '''
        Params:
        Website
        Stock
        ---------------------------------
        Function parses a url to find all of the a tags in the html
        From there it selects only the "a" tags where the stock is contained in the href link
        Only append links into our list of links if the link has not yet been appended
        
        Make sure 'html' is in the CNN's link and rule out the sitemap link

        Market watch follows the same rules as yahoo finance
        '''
        stock = self.stock
        self.internal_links = [] 
        html = urlopen(url) #Grab the html
        bsObj = BeautifulSoup(html) #Turn html to bsObj
        for link in bsObj.findAll("a", href=re.compile('.*'+stock+'.*')): #Find a tags who href attribute have our stock in it
            link = link.attrs['href']
            
            if 'cnn' in url and 'html' in link: #CNN formatting - Need html in link its an indicator of a article
                link = 'http://cnn.com'+link #Append the begining of url to link
                if link not in self.internal_links and 'sitemap' not in link: #Don't care for CNN's sitemap
                    self.internal_links.append(link)
            
            elif 'cnn' not in url:
                if link.startswith(url) and link not in self.internal_links: #More link formatting
                    self.internal_links.append(link)
                elif link.startswith('https') == False:
                    link = url+link
                    if link not in self.internal_links:
                        self.internal_links.append(link)
        return self.internal_links


    
    
    def get_YAHOO_dates(self):
        '''
        Paramters:
        List of links
        -----------------------
        Takes a list of links and grabs the datetime of publishment
        for each link

        Designed to work with the YahooFinance HTML
        '''
        links = self.getStockLinks('https://finance.yahoo.com')
        self.YAHOO_links_dict = {}
        try:
            for link in links:
                urlopen = requests.get(link).text 
                bsObj = BeautifulSoup(urlopen, 'html.parser') #Convert the html to a bsObj

                date = bsObj.find('time') #time tag is used for the published time
                if date is not None:
                    str_date = date.get_text() #Get the text associated with the time tag
                    try:
                        date = datetime.strptime(str_date, '%B %d, %Y')
                    except:
                        date = datetime.strptime('January 01, 2000' '%B %d, %Y')
                    self.YAHOO_links_dict[link] = date
        except:
            pass
        return self.YAHOO_links_dict
    
    
    def get_MW_dates(self):
        '''
        Paramters:
        List of links
        -----------------------
        Takes a list of links and grabs the datetime of publishment
        for each link

        Designed to work with the MarketWatch HTML
        '''
        def ampm(string):
            '''
            Parameters:
            datetime string
            ----------------------
            Converts a.m to AM or p.m to PM
            '''
            locate = re.compile(r'[ap]\.m\.') #pattern to match a.m or p.m
            ampm_pattern = re.findall(locate, string) #use re.findall to find the pattern
            ampm_match_string = ''.join(ampm_pattern)
            ampm = str.replace(ampm_match_string, '.', '').upper()
            ampm_string = str.replace(string, ampm_match_string, ampm)
            return ampm_string

        links = self.getStockLinks('https://www.marketwatch.com')
        self.MW_links_dict = {}
        try:
            for link in links:
                urlopen = requests.get(link).text
                bsObj = BeautifulSoup(urlopen, 'html.parser')

                date = bsObj.find('time') #where the date is located in the html

                if date is not None:
                    str_date = date.get_text() #Convert date html into a string
                    date_pattern = re.compile(r'[A-Za-z]{5}\.?\s[0-9]{1,2}\,\s[0-9]{4}') #pattern to match date
                    time_pattern = re.compile(r'[0-9]{1,2}\:[0-9]{2}\s[a-z]{1}\.[a-z]{1}\.') #pattern to match time

                    date_match = re.findall(date_pattern, str_date) #retrieve the date match
                    time_match = re.findall(time_pattern, str_date) #retrieve the time match

                    date_match_string = ''.join(date_match) #convert list of one date to a string
                    time_match_string = ''.join(time_match) #convert list of one time to a string

                    if len(date_match_string) != 0 or len(time_match_string) != 0:
                        date_and_time = date_match_string + ' ' + time_match_string #Combine the date and time strings we have retrieved
                        str_date = ampm(date_and_time) #convert a.m to AM so python strptime can work with it
                        try:
                            date = datetime.strptime(str_date, '%B %d, %Y %I:%M %p') #creates a datetime object that follows that pattern
                        except:
                            date = datetime.strptime('January 01, 2000 12:00 AM', '%B %d, %Y %I:%M %p')
                        self.MW_links_dict[link] = date #build the links_dict
        except:
            pass

        return self.MW_links_dict
    
    
    
    def get_CNN_dates(self):
        '''
        Paramters:
        List of links
        -----------------------
        Takes a list of links and grabs the datetime of publishment
        for each link

        Designed to work with the CNN HTML
        '''
        links = self.getStockLinks('https://edition.cnn.com/business')
        self.CNN_links_dict = {}
        try:
            for link in links:
                urlopen = requests.get(link).text
                bsObj = BeautifulSoup(urlopen, 'html.parser')

                date = bsObj.find("p", {'class':"update-time"}) or bsObj.find("p", {'id':"published-timestamp"}) or bsObj.find('time') #Where the date is located in the html

                if date is not None:
                    str_date = date.get_text()
                    date_pattern = re.compile('[A-Za-z]+\s[0-9]{1,2}\,\s[0-9]{4}') #pattern to match date
                    time_pattern = re.compile(r'[0-9]{1,2}\:[0-9]{2}\s[A-Z]{2}') #pattern to match time

                    date_match = re.findall(date_pattern, str_date) #retrieve the date match
                    time_match = re.findall(time_pattern, str_date) #retrieve the time match

                    date_match_string = ''.join(date_match) #convert list of one date to a string    

                    time_match_string = ''.join(time_match) #convert list of one time to a string

                    if len(date_match_string) != 0 or len(time_match_string) != 0:
                        date_and_time = date_match_string + ' ' + time_match_string #combine the date and time strings we have retrieved
                        try:
                            date = datetime.strptime(date_and_time, '%B %d, %Y %I:%M %p') #creates a datetime object that follows that pattern
                        except:
                            date = datetime.strptime('January 01, 2000 12:00 AM', '%B %d, %Y %I:%M %p')
                        self.CNN_links_dict[link] = date #build the links_dict
        except:
            pass

        return self.CNN_links_dict


    

    def links_dataframe(self, links_dictionary, url):
        '''
        Params:
        Links Dictionary
        Website URL
        ------------------------------------
        Create a links dataframe with columns labeled as URL and Published Time

        Because the published time is a datetime datatype it is easy to sort with
        Then create a standard datetime format for all links
        '''
        links_dict = links_dictionary #DO NOT USE SELF - not neccesary 
        
        if len(links_dict) != 0: #Formatting if the dictionary is filled with data
            links_df = pd.DataFrame(list(links_dict.items()), columns=['URL', 'Published Time']) #Our two columns
            links_df.columns.name = url
            links_df.sort_values(by =['Published Time'], ascending=False, inplace=True) #Format the dates in descending order
            links_df['Published Time'] = links_df['Published Time'].dt.strftime('%b %d, %Y %I:%M %p') #Datetime format that all three websites will use
            return links_df
        else: #Otherwise return a empty dataframe
            links_df = pd.DataFrame(list(links_dict.items()), columns=['URL', 'Published Time'])
            return links_df

    
    def send_mail(self, email, password):
        '''
        Parameters:
        An email username
        An email password
        The stockclass object
        ------------------------------------
        Create a personalized email with the bulk of the html
        being about the links dataframe
        '''
        
        yahoo = self.links_dataframe(self.get_YAHOO_dates(), 'https://finance.yahoo.com')
        cnn = self.links_dataframe(self.get_CNN_dates(), 'https://edition.cnn.com/business')
        mw = self.links_dataframe(self.get_MW_dates(), 'https://www.marketwatch.com')
        
        me = email #Email of sender
        you = email #Email of receiver - obviously we are sending an email to ourselves

        #Begin to build the message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Link"
        msg['From'] = me
        msg['To'] = you

        #Begin formatting your html preferences
        html = html = """\
    <html>
      <head> </head>
      <body>
      <h1>Hi John Smith, <br> Below is the news for {0} Stock On {1}</h1>
      <h2>Let me know if you want information for a different stock</h2>
      """.format(self.stock.capitalize(), datetime.now().strftime('%B-%d-%Y') ) #Use format to have a flexible header

        html += '<h3>Here is {0} stock information<h3>'.format(self.stock.capitalize())
        yahoo_html  = yahoo.to_html() #Converts our table dataframe to html directly
        cnn_html = cnn.to_html()
        mw_html = mw.to_html()
        html += yahoo_html + '<br>'
        html += cnn_html + '<br>'
        html += mw_html + '<br>'


        html += """
        </body>
    </html>
    """
        part2 = MIMEText(html,'html') #part one was the subject, from, to

        #Below are the neccessary mail configurations
        msg.attach(part2)
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(email, password)
        mail.sendmail(me, you, msg.as_string())
        mail.quit()


def main():
    stock = input("Please give a stock to query: ")
    stockinfo = StockInfo(stock) #Initiate your class
    email = input("Please give your email: ")
    password = input("Please enter your password: ")
    stockinfo.send_mail(email, password) #Send out the email and that's it

if __name__ == "__main__":
    main()
