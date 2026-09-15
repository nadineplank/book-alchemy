import os
from datetime import date

from flask import Flask, render_template, request

from data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)


def get_authors():
    """Return a list of all authors in the database."""
    authors = Author.query.all()
    return authors


def get_books():
    """Return a list of all books in the database."""
    books = Book.query.all()
    print(books)
    return books


@app.route('/')
def index():
    return render_template('home.html', books=get_books())


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Show the add-author form and handle new author submissions."""
    if request.method == 'POST':

        author = Author(
            name=request.form.get('name'),
            birth_date=request.form.get('birthdate', type=date.fromisoformat),
            date_of_death=request.form.get('date_of_death', type=date.fromisoformat)
        )

        db.session.add(author)
        db.session.commit()

        return render_template('add_author.html', message='Author added successfully!')
    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """Show the add-book form and handle new book submissions."""
    current_year = date.today().year
    authors = get_authors()

    if request.method == 'POST':

        book = Book(
            title=request.form.get('title'),
            isbn=request.form.get('isbn'),
            publication_year=request.form.get('publication_year', type=int),
            author_id=request.form.get('author_id', type=int)
        )

        db.session.add(book)
        db.session.commit()

        return render_template('add_book.html', message='Book added successfully!', current_year=current_year, authors=authors)

    return render_template('add_book.html', current_year=current_year, authors=authors)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

# Run once to create the tables, then comment out again:
# with app.app_context():
#     db.create_all()

