import os
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import or_

from data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config['SECRET_KEY'] = os.urandom(24)
db.init_app(app)


@app.errorhandler(405)
def method_not_allowed(e):
    flash('This action requires a POST request. Please use the delete button.', 'error')
    return redirect(url_for('index'))


def get_authors():
    """Return a list of all authors in the database."""
    authors = Author.query.all()
    return authors

def get_author_by_id(author_id):
    """Return a single author from the database."""
    author = Author.query.filter_by(id=author_id).first()
    return author


def get_books(sort, search=None):
    """Return a list of all books in the database, optionally filtered by search and sorted."""
    query = Book.query.join(Author)

    if search: query = query.filter(
        or_(
            Book.title.contains(search),
            Author.name.contains(search)
        )
    )

    if sort == 'author':
        query = query.order_by(Author.name)
    else:
        query = query.order_by(Book.title)

    return query.all()


def get_book_by_id(book_id):
    """Return a single book from the database."""
    return Book.query.filter_by(id=book_id).first()


@app.route('/')
def index():
    """Show the home page and sort books by title (default) or author."""
    sort = request.args.get('sort', 'title')
    search = request.args.get('search')

    if sort not in ['title', 'author']:
        return 'Invalid sort', 400

    books = get_books(sort, search)

    return render_template('home.html', books=books, sort=sort, search=search)


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

        return render_template('add_book.html', message='Book added successfully!', current_year=current_year,
                               authors=authors)

    return render_template('add_book.html', current_year=current_year, authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """Delete a book from the database and if author has no more books, delete it."""
    book = get_book_by_id(book_id)

    if book is None:
        flash('Book not found!', 'error')
        return redirect(url_for('index'))

    db.session.delete(book)

    author = get_author_by_id(book.author_id)


    if author is not None and len(author.books) == 0:
        db.session.delete(author)

    db.session.commit()

    flash('Book deleted successfully!', 'success')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)

# Run once to create the tables, then comment out again:
# with app.app_context():
#     db.create_all()
