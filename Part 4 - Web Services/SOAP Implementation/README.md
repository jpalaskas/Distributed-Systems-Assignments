Final part of the whole assignment was implementing our bank database connection and functionality while using soap and rest web services' principles and protocols

Problem around soap implementation(in case of python 3.7 and later - async keyword error):
Since python 3.7 the 'async' word became a reserved keyword by python.

Solution: 
Navigate to the lib folder of the installed spyne lib in your system.
e.g. C:\Users\USERNAME\AppData\Local\Programs\Python\Python37\Lib\site-packages\spyne
Navigate to the server folder inside the spyne lib and find the null.py file.
Edit it and 'find and replace' all appearences of the 'async' word with 'async_'
That should do it.
