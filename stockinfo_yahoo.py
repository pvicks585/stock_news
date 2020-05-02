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
        self.url = 'https://finance.yahoo.com'
        self.stock = stock
        
    def getStockLinks(self):
        '''
        Params:
        Website
        Stock
        ---------------------------------
        Function parses a url to find all of the a tags in the html
        From there it selects only the "a" tags where the stock is contained in the href link

        Only append links into our list of links if the link has not yet been appended
        '''
        site = self.url
        stock = self.stock
        self.internal_links = [] 
        html = urlopen(site)
        bsObj = BeautifulSoup(html)
        for link in bsObj.findAll("a", href=re.compile('.*'+stock+'.*')):
            link = link.attrs['href']
            if link.startswith(site) and link not in self.internal_links: #Straithforward code - if the link starts with site - no need to format it
                    self.internal_links.append(link)
            elif link.startswith('https') == False:
                link = site+link #If the link does not start with the site, then string concatanete the site + the link
                if link not in self.internal_links:
                    self.internal_links.append(link)
        return self.internal_links

    def get_dates(self):
        '''
        Params:
        List of Links
        --------------------------------
        Create a dictionary mapping of links to date of publish

        First create a bsObj for each link in your link list
        Then use BeautifulSoup to find the tag related to the publish date/time

        As long as a date tag is found, use the get_text method to get the text related
        to that tag

        In the links_dict dictionary create a mapping from the link to the publish date
        making sure that the publish date is a datetime type
        '''
        links = self.getStockLinks()
        self.links_dict = {}
        try:
            for link in links:
                urlopen = requests.get(link).text
                bsObj = BeautifulSoup(urlopen, 'html.parser')

                date = bsObj.find('time') #find the time tags
                if date is not None:
                    str_date = date.get_text() #Get the text associated
                    try:
                        date = datetime.strptime(str_date, '%B %d, %Y') #Convert the date to datetime
                    except:
                        date = datetime.strptime('January 01, 2000', '%B %d, %Y')
                    self.links_dict[link] = date
        except:
            pass
        return self.links_dict

    def links_dataframe(self):
        '''
        Params:
        List of links
        ------------------------------------
        Create a links dataframe with columns labeled as URL and Published Time

        Because the published time is a datetime datatype it is easy to sort with
        Then create a standard datetime format for all links
        '''
        self.links_dict = self.get_dates()
        if len(self.links_dict) != 0:
            self.links_df = pd.DataFrame(list(self.links_dict.items()), columns=['URL', 'Published Time']) #our two columns
            self.links_df.columns.name = self.url
            self.links_df.sort_values(by =['Published Time'], ascending=False, inplace=True) #order datetimes in descending order
            self.links_df['Published Time'] = self.links_df['Published Time'].dt.strftime('%b %d, %Y %I:%M %p') #the format of our datetimes
            return self.links_df
        else:
            self.links_df = pd.DataFrame(list(self.links_dict.items()), columns=['URL', 'Published Time']) #empty datafrmae if links_dict is empty
            return self.links_df
    
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
        dataframe = self.links_dataframe() #Main dataframe
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

        html += '<h3>Here is {0} stock information from {1}<h3>'.format(self.stock.capitalize(), dataframe.columns.name)
        dataframe_html  = dataframe.to_html() #Converts our table dataframe to html directly
        html += dataframe_html + '<br>'


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

    