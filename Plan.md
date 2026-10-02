\-what is the federal minimum wage compared to the price of a mcdonalds whopper from a period of 1980 to 2025\.

Plan:

- Make readable python code that generates a graph showcasing the rate of increase for federal minimum wage and the rate of increase for the price of the mcdonalds big mac from 2000 to 2020\. The data for the federal minimum wage can be found at [https\://fred.stlouisfed.org/series/FEDMINNFRWG](https://fred.stlouisfed.org/series/FEDMINNFRWG). The data for the price of a big mac can be found at [https\://www\.kaggle.com/datasets/mrmorj/big-mac-index-data/data](https://www.kaggle.com/datasets/mrmorj/big-mac-index-data/data). Respond if there’s any issues with how to obtain the files.

Issues for future reference:

- Claude initially claimed it couldn’t access the files because of anti-bot protocols on the sites, but was able to create the data based on the graph for minimum wage, and was able to access the date for big mac prices by “accessing through git.”  
  - I gave it the files from a download, but it remarked that the data was the same for both of them.   
- Git was not connected initially, doublecheck each time if git is connected  
- .py (python) and .ipynb (python notebook) are not directly compatible. Ask Claude to convert if python was specified.

Notes for assignment:

- The Big Mac index was missing values from before 2000 and after 2020, so the data range was changed to those values.  
- Did not mention which charts should be used, but Claude chose line charts for both of them.  
- I did not have explicitly defined expectations for the results, but due to prior knowledge I would have said that I expected the minimum wage to lag behind the big mac index further as time went on.  
- Claude did not generate a .env file. I discussed this with the teacher on tuesday; I don’t need to worry about the .gitignore if the .env file doesn’t exist.