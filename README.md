# nebook - Web-Based E-reader

![nebook screen capture](https://i.imgur.com/neIDLxc.png)

## Demo

A demo is available at https://nebook.herokuapp.com/. Free, public-domain epub files can be downloaded from [Project Gutenberg](https://www.gutenberg.org/browse/scores/top)

## Initial Proposal

[Available here.](meta/proposal.md)

## Description

This application serves as my first capstone for Springboard's Software Engineering Career Track. It provides an interface for uploading, managing, and reading epub-format ebooks.

## Features

I essentially wanted to recreate the core functionality of the [Calibre](https://github.com/kovidgoyal/calibre) ebook management application as a web application. The following features are supported:

* Upload epub-format ebooks through a simple interface
* Edit book metadata, including custom tags and comments
* Remove books as necessary
* Search and filter on various fields
* Read books through integrated reader app

## User Flow

* A user can log in or register a new account. Successful registration logs the user in.
* The user is presented with a list of books, if they've uploaded any. If not, they are prompted to upload one.
* If the user has not yet authorized access to their Google Drive, they're presented with a screen asking them to authorize.
* The user goes through the Google authorization flow, and their credentials are saved to the server for future use.
* The user is presented with a simple upload page where they can choose a file to upload. If the file is not recognized as an epub file, the user is presented with a warning.
* If the user chooses to upload an epub file, they wait (unfortunately) for the book to upload to the server, then to their Google Drive. The book information is added to the database.
* The user is presented with a page where they can edit the details of the book they've uploaded. It's populated with Google Books API data if it exists; otherwise, it's populated with the ebook's own metadata. The rest of the form functions normally, but authors and tags are parsed as comma-separated lists. (I intend to add a proper tag editor in the future.)
* The user saves the information, then is presented with the book's detail page. From here, the user can return to the index page, edit the book's metadata, read the book, or delete the book from their account. Choosing to edit the book's details returns the user to the page described above.
* Choosing to delete the book presents the user with a confirmation message. If the user accepts, they're returned to the index page with a success message. If they cancel, they're returned to the book details page.
* Choosing to read the book opens a new tab with an instance of the EpubJS Reader. It loads the selected book and allows the user to read it.
* Returning to the index page, the user can select between a list and grid view. This change is persisted in the session. They can also use the search form to search and filter through various fields.

## Technologies Used

The project is mostly written in Python, using [Flask](https://github.com/pallets/flask) as a framework and [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) as an ORM. It's backed by a [PostgreSQL](https://github.com/postgres/postgres) database.

I utilized several extensions for Flask, including [Flask-Login](https://github.com/maxcountryman/flask-login), [Flask-SQLAlchemy](https://github.com/pallets/flask-sqlalchemy), [Flask-WTForms](https://github.com/lepture/flask-wtf), and [Flask-Bcrypt](https://github.com/maxcountryman/flask-bcrypt). I also used Futurepress's [EpubJS Reader](https://github.com/futurepress/epubjs-reader) to allow the user to read their uploaded ebooks.

While I haven't made much use of them yet, I included some front-end build tools for when I decide to improve the application in the future.

## APIs

I relied on Google Drive to store users' books. I also used the Google Books API to fetch information about uploaded books. For both of these, I utilized Google's general-purpose API client, which also provided utilities for dealing with OAuth credentials. 

## Testing

Requires a postgres database named `book_project_test`. In the top-level directory, run:

```
python3 -m unittest
```

## Looking Forward

While the project meets the requirements for a capstone submission, it's far from what I'd personally consider complete. There are several touches and features I'd like to include in the future should I return to the project:

* A proper name, for one
* Google Sign-In
* Syncing with books already uploaded to the user's storage service, which (for Google Drive at least) requires app verification
* Better abstraction of the book storage service, in case I decide to utilize something other than Google Drive
* Support for other file formats (PDF, MOBI, etc.)
* A user settings page, for things like managing authorization and editing which columns should be displayed in list view
* Better search filters
* Customization of the default Bootstrap look and feel
* JS-based live search
* JS-based tag and author editors
* Asynchronous multi-file uploads via JavaScript
* Syncing reader status between devices
