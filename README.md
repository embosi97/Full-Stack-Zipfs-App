<h2> "IsItZipf's" </h2> is a Full-Stack application that allows users to check how closely a given site or file follows Zipf's Law. 


Django 3 is used for the backend and React-Bootstrap/Vanilla Bootstrap 5 for the frontend component.

Site parsing is achieved using Python's BeautifulSoup4 and Requests libraries. 

File parsing utilizes BeautifulSoup4, PyPDF2, and Pytesserant, an optical character recognition tool that can parse images. Langdetect and Regex are used to validate each word. 

Supported languages include English, Spanish, German, and Italian.

From the home page, the user is directed to the core of the app where he/she is presented with an option to input a website or file of his/her choice. Here the user can provide a 
site and can choose the language of the provided site. Validated words are then stored in a Counter data structure.

If the language is not valid for that particular site (i.e. selecting German for Elpais.com), the user will be redirected to this page.

![Alt text](https://i.imgur.com/hhtkVob.png?raw=true "Selection page")

Supported file extensions are '.txt', '.html', '.png', '.jpeg', '.jpg', '.doc', '.docx', and '.pdf'. 

The Bokeh Visualization Library is utilized to create an interactive Zipf's graph that displays the top one hundred words, their frequencies, and their corresponding rank.

The graph can be zoomed in on/expanded, allows for scrolling, and hovering over the individual points on the scatter plot will display the word's exact number of occurrances (I.e. Word 'the' has 2450 occurances). 

An algorithm produces a similarity percentage to a theoretically “perfect” Zipf's graph, which essentially compares the words' actual frequencies to those of the aforementioned perfect graph all relative to highest rank word.

![Alt text](https://i.imgur.com/H1ZjWhh.png?raw=true "Graph for FILE")

![Alt text](https://i.imgur.com/M5FpUlX.png?raw=true "Graph for Site")

Database models were used for storing inputted sites and their information, which includes the URL itself, the dictionary the words and the frequencies are stored in,
the last modified date, the similarity percentage, and the language of the site.

This information is saved to a PostgreSQL database and is updated if the site has been modified. If there is no conflict with modified dates, the appropriate information is pulled from
the database and used without need of updating. This process works seamlessly and saves time.

![Alt text](https://i.imgur.com/QFPnN4R.png?raw=true "Graph for Site")

If you're unfamiliar with how Zipf's Law works, please watch this video by VSauce
https://www.youtube.com/watch?v=fCn8zs912OE


