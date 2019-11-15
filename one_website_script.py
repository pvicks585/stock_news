
#First Website we'll use
website = 'https://www.cnbc.com/' 
#Stocks for watchlist
stocks = ['disney', 'apple', 'google']

###We will turn the html into a bsObj
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re #regex


def getInternalLinks(bsObj, includeUrl):
    internalLinks = [] #List of internal links to append to
#Finds all links that begin with a "/"
    for link in bsObj.findAll("a", href=re.compile("^(/|.*"+includeUrl+")")): #In the soup object find all the <a> tags where the href involved includes the URL provided 
        if link.attrs['href'] is not None: #if the href exists
            if link.attrs['href'] not in internalLinks: #attach the URL to internalLinks list
                internalLinks.append(link.attrs['href'])
    return internalLinks #All the internal links on a webpage

def get_links_interest(list_of_stocks):
    links_to_search = []
    for stock in list_of_stocks:
        html = urlopen(website) #Open website into html 
        bsObj = BeautifulSoup(html) #Turn the html into a beatuful soup object
        internal_links = getInternalLinks(bsObj, website) #Now we have all the internal links from the website in a string list
        links_to_search.append([link for link in internal_links if stock in link])
    return links_to_search
    
links_of_interest = get_links_interest(stocks) #list of list of the links concerning the stocks wished for

links_dict = {} #Use dict to pair the stock and its links
for i in range(len(stocks)):
    links_dict[stocks[i]] = links_of_interest[i] #Pairs the stock and its link


def get_text(list_of_links):
    links_text = []
    links_date = []
    for link in list_of_links:
        html = urlopen(link) #Open link into html
        bsObj = BeautifulSoup(html) #Turn html into a bs Obj
        for x in bsObj.findAll('div', {'class':'ArticleBody-articleBody'}): #We are interested in the article body
            for body in x.findAll('p'): #Find all paragraph texts
                text = x.get_text() #Use the get_text function to extract the text
                if text not in links_text:
                    links_text.append(text) 
                    for date in bsObj.findAll('time', {'data-testid':'published-timestamp'}): #Retrieves the date
                        links_date.append(date.get_text())
                    for date in bsObj.findAll('time', {'data-testid':'single-timestamp'}):
                        links_date.append(date.get_text())
    return links_text, links_date #Use tuple notation to get text and date


text_dict = {}
date_dict = {}
for i in range(len(links_dict)):
    text, date = get_text(links_dict[stocks[i]]) #Get_text returns the body-text, timestamp from the url html
    text_dict[stocks[i]] = text #Key is the stock name, values is its texts
    date_dict[stocks[i]] = date #Key is the stock name, values is its dates


#IMPROVE THIS IT IS TOO MUCH REPITION
#THIS ONLY WORKS FOR CNBC
from datetime import datetime
def clean_dates(date_list):
    dates = []
    for date in date_list:
        date = date.split()
        date = date[2:]
        date = date[:4]
        date[2] = ''.join(date[2].split('2019'))
        date = '/'.join(date)
        d = datetime.strptime(date, '%b/%d/%I:%M/%p')
        change = d.strftime('%m/%d/2019 %I:%M %p')
        dates.append(change)
    
    return dates

for i in range(len(date_dict)):
    date_dict[stocks[i]] = clean_dates(date_dict[stocks[i]]) #Clean the dates to the desired format


for i in range(len(stocks)):
    x = date_dict[stocks[i]]
    date_dict[stocks[i]] = sorted(x) #Sort the dates for graphing purposes

contractions = { 
"ain't": "am not",
"aren't": "are not",
"can't": "cannot",
"can't've": "cannot have",
"'cause": "because",
"could've": "could have",
"couldn't": "could not",
"couldn't've": "could not have",
"didn't": "did not",
"doesn't": "does not",
"don't": "do not",
"hadn't": "had not",
"hadn't've": "had not have",
"hasn't": "has not",
"haven't": "have not",
"he'd": "he would",
"he'd've": "he would have",
"he'll": "he will",
"he's": "he is",
"how'd": "how did",
"how'll": "how will",
"how's": "how is",
"i'd": "i would",
"i'll": "i will",
"i'm": "i am",
"i've": "i have",
"isn't": "is not",
"it'd": "it would",
"it'll": "it will",
"it's": "it is",
"let's": "let us",
"ma'am": "madam",
"mayn't": "may not",
"might've": "might have",
"mightn't": "might not",
"must've": "must have",
"mustn't": "must not",
"needn't": "need not",
"oughtn't": "ought not",
"shan't": "shall not",
"sha'n't": "shall not",
"she'd": "she would",
"she'll": "she will",
"she's": "she is",
"should've": "should have",
"shouldn't": "should not",
"that'd": "that would",
"that's": "that is",
"there'd": "there had",
"there's": "there is",
"they'd": "they would",
"they'll": "they will",
"they're": "they are",
"they've": "they have",
"wasn't": "was not",
"we'd": "we would",
"we'll": "we will",
"we're": "we are",
"we've": "we have",
"weren't": "were not",
"what'll": "what will",
"what're": "what are",
"what's": "what is",
"what've": "what have",
"where'd": "where did",
"where's": "where is",
"who'll": "who will",
"who's": "who is",
"won't": "will not",
"wouldn't": "would not",
"you'd": "you would",
"you'll": "you will",
"you're": "you are"
} 

from nltk.corpus import stopwords
def clean_text(text, remove_stopwords=True):
    text = text.lower()   
    # Replace contractions with their longer forms 
    if True:
        text = text.split()
        new_text = []
        for word in text:
            if word in contractions:
                new_text.append(contractions[word])
            else:
                new_text.append(word)
                text = " ".join(new_text)   
    # Format words and remove unwanted characters
    text = re.sub(r'&amp;', '', text) 
    text = re.sub(r'0,0', '00', text) 
    text = re.sub(r'[_"\-;%()|.,+&=*%.,!?:#@\[\]]', ' ', text)
    text = re.sub(r'\'', ' ', text)
    text = re.sub(r'\$', ' $ ', text)
    text = re.sub(r'u s ', ' united states ', text)
    text = re.sub(r'u n ', ' united nations ', text)
    text = re.sub(r'u k ', ' united kingdom ', text)
    text = re.sub(r'j k ', ' jk ', text)
    text = re.sub(r' s ', ' ', text)
    text = re.sub(r' yr ', ' year ', text)
    text = re.sub(r' l g b t ', ' lgbt ', text)
    text = re.sub(r'0km ', '0 km ', text)  
    # Optionally, remove stop-words
    if remove_stopwords:
        text = text.split()
        stops = set(stopwords.words("english"))
        text = [w for w in text if not w in stops]
        text = " ".join(text)
        return text


def text_clean_iterator(i): #Function that cleans text in list in dict
    if type(text_dict[stocks[i]]) == list:
        return [clean_text(text) for text in text_dict[stocks[i]]]

for i in range(len(stocks)):
    text_dict[stocks[i]] = text_clean_iterator(i) #Clean the text in list of dict for each stock


#Syntax error with grabbing text form URL
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()
polarity_scores = {}
for i in range(len(stocks)):
    if text_dict[stocks[i]] != []:
        for j in range(len(text_dict[stocks[i]])):
            pos = sid.polarity_scores(text_dict[stocks[i]][j])['pos'] #Find the positive sentinment of tex            
            if stocks[i] in polarity_scores:
                polarity_scores[stocks[i]].append({date_dict[stocks[i]][j]:pos})
            else:
                polarity_scores[stocks[i]] = [{date_dict[stocks[i]][j]:pos}] #If not set the first key-value pair


def main():
    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(1, 4, figsize=(20, 5), sharey=True)
    for i in range(len(stocks)):
        for dict in polarity_scores[stocks[i]]:
            for key, value in dict.items():
                axs[i].plot_date(key, value)
                axs[i].set(title=str(stocks[i].upper()))
                axs[i].set_xlabel('Timestamp')
    
    axs[0].set_ylabel('Sentiment Score')
    fig.suptitle('Positive Sentimenent for Watchlist Stocks')

    
if __name__ == "__main__":
    main()