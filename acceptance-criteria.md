

# ACCEPTANCE CRITERA 

### CONNECT TO DATA BASE
1.) The web app should be successfully connected to a PostgreSQL database. A local connection to a database on your local computer is fine.

### INIT MIGRATIONS
As a fellow developer on this application, I should be able to run flask db migrate, and have my local database (once set up and created) be populated with the right tables to run this application and have it interact with my local postgres server, serving the application's needs completely with real data

### I CAN SEE MY DATABASE 
I can seed my local database with.

### REMOVE MOCK DATA
2.) There should be no use of mock data throughout the app. The data structure of the mock data per controller should be kept unmodified when satisfied by real data.

### SEARCH AND MODELS WORKS
The application should behave just as before with mock data, but now uses real data from a real backend server, with real search functionality. For example:

    - search is working with real data


4.) when a user submits a new artist record, the user should be able to see it populate in /artists, as well as search for the artist by name and have the search return results.

5.) I should be able to go to the URL /artist/<artist-id> to visit a particular artist’s page using a unique ID per artist and see real data about that particular artist.

### VENUES ARE GROUPED BY CITY AND STATE

6.) Venues should continue to be displayed in groups by city and state.

### SEARCH IS CASE INSENSITIVE

7.) Search should be allowed to be partial string matching and case-insensitive.

8.) Past shows versus Upcoming shows should be distinguished in Venue and Artist pages.

### MODEL DATA IS COMPLETED
The models should be completed (see TODOs in the Models section of app.py) and model the objects used throughout Fyyur.

9.) A user should be able to click on the venue for an upcoming show on the Artist's page, and on that Venue's page, see the same show in the Venue Page's upcoming shows section.

### SEPERATION OF CONCERNS
Define the models in a different file to follow Separation of Concerns design principles. You can refactor the models to a new file, such as models.py.

### CORRERCT RELATIONSHIPS
The right type of relationship and parent-child dynamics between models should be accurately identified and fit the needs of this particular application.
The relationship between the models should be accurately configured, and referential integrity amongst the models should be preserved.