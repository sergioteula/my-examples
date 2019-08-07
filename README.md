# Some of my works
Here you can check some of my works. They are not supposed to work out of the box, because some of the dependencies are not included in this packages. But you can get some ideas for your own projects. You can also contact me on [Twitter](https://twitter.com/sergio_teula) if you want.

### 💾 persistent-class-example: Persistent Python class example with Shelve and SQLite
This is an example of persistent Python classes using both Shelve and SQLite. There is a superclass named Persistent that saves the subclasses on a Shelve and loads the previous status on each init. On the other hand, some classes use SQLite to save the data and get it for later use.

### 📚 amazon-scraper: Amazon scraper using the Product Advertising API and web scraping
This scraper works for both the main product page and also offer listing page. It uses product advertising API to fetch basic data and web scraping to get more specific data not provided by the Amazon API like flash prices. Also, it compares data obtained from both sources in order to increase reliability.

### 🌍 requests-browser-class: Get web code using requests, proxies or headless browser
With this class you can get the page code of any web using three methods. You can use simple method to get the code using requests, use proxies to avoid getting banned while scraping or use your web browser (in this case Google Chrome) in headless mode to scrape sites that doesn't work with requests methods.
