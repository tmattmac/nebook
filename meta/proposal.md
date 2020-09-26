# Capstone Proposal

## 1. What goal will your website be designed to achieve?
   
The goal is to allow people to manage, organize, and consume a cloud-based collection of ebooks through a web interface accessible from any device. Specifically, I want to attempt to normalize the book metadata into a consistent format to make it easier for the user to find what they're looking for.

## 2. What kind of users will visit your site? In other words, what is the demographic of your users?

The main users of the site will be readers who maintain a collection of DRM-free ePub format books. Since most people who buy ebooks in bulk tend to have dedicated e-readers already, I do understand the audience for an app like this might be a bit narrow.

## 3. What data do you plan on using? You may have not picked your actual API yet, which is fine, just outline what kind of data you would like it to contain.

The book metadata will be retrieved from the Google Books API. The app will also make use of the Google Drive API to facilitate cloud-based storage of ebooks.

## 4. In brief, outline your approach to creating your project (knowing that you may not know everything in advance and that these details might change later). Answer questions like the ones below, but feel free to add more information:

### a. What does your database schema look like?

The schema will tentatively consist of Users, Books, user-defined Collections (Reading, To Read, etc.), Categories (Book, Magazine, etc.), Genres, Authors, Publishers, Progress (to store user's reading progress for a book). Since each user will potentially be able to define their own metadata for a particular book, I'll likely store custom metadata in a Users_Books table and default to the book's canonical data if it's available. I'll also have to figure out how to handle books that Google Books doesn't know about, such as those sourced from Leanpub.

### b. What kinds of issues might you run into with your API?

It's possible I might not consider the entire breadth of possibilities in regards to how book data is organized. Things like multiple editions of a book might pose a problem if I don't design carefully around them. Also, given my goal of normalizing metadata, I can't be fully certain that the API will facilitate that goal.

### c. Is there any sensitive information you need to secure?

I'll need to figure out the best way to store OAuth tokens, since I'll need them to access a user's Google Drive.

### d. What functionality will your app include?

The minimum functionality I'd like the app to have includes: book uploading, categorization, custom metadata, sorting and search, and an integrated reader for actually reading the books.

### e. What will the user flow look like?

The user registers, then is prompted to log in to their Google Drive account and allow permissions. They're then given instructions on how to import their existing book collection through Google Drive. If they choose to upload their books through Google Drive, the app will process the books and add them to the database, allowing the user to then interact with the book data. By default, the app will show the last few read books in a table near the top of the page, with another table sorted according to the user's preferences (saved in localStorage, most likely) below. From the homepage, they can search and sort through all books (AJAX), add books to a collection, and view/edit metadata for a book. From either the homepage or the details page, they can open a reader and begin reading the book.

### f. What features make your site more than CRUD? Do you have any stretch goals?

The main feature that makes the site more than CRUD is Google Drive integration. Some stretch goals might include syncing with e-readers using the WebUSB API, recommending books (from DRM-free sources) based on a user's reading activity, implementing single sign-on through Google, PDF book support, and having a portal for downloading freely available ebooks.