import os
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config['SECRET_KEY'] = os.urandom(24)
db.init_app(app)


@app.errorhandler(405)
def method_not_allowed(e):
    flash('This action requires a POST request.', 'error')
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(e):
    flash('Page not found.', 'error')
    return redirect(url_for('index'))


@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    app.logger.error(f"Server error: {e}")
    flash('An unexpected error occurred.', 'error')
    return redirect(url_for('index'))


def get_authors():
    """Return a list of all authors in the database."""
    authors = Author.query.all()
    return authors


def get_author_by_id(author_id):
    """Return a single author from the database, or None if not found."""
    return db.session.get(Author, author_id)


def get_book_by_id(book_id):
    """Return a single book from the database, or None if not found."""
    return db.session.get(Book, book_id)


def get_books(sort, search=None):
    """Return a list of all books in the database, optionally filtered by search and sorted."""
    query = Book.query.join(Author)

    if search:
        query = query.filter(
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


@app.route('/')
def index():
    """Show the home page and sort books by title (default) or author."""
    sort = request.args.get('sort', 'title')
    search = request.args.get('search')

    if sort not in ['title', 'author']:
        flash('Invalid sort', 'error')

    books = get_books(sort, search)

    return render_template('home.html', books=books, sort=sort, search=search)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Show the add-author form and handle new author submissions."""
    if request.method == 'POST':

        def form_error(message):
            flash(message, 'error')
            return render_template('add_author.html')

        name = request.form.get('name', '').strip()
        birth_date_str = request.form.get('birthdate', '').strip()
        date_of_death_str = request.form.get('date_of_death', '').strip()

        # Validate name
        if not name:
            return form_error('Author name is required.')

        # Validate birthdate
        if not birth_date_str:
            return form_error('Birth date is required.')

        try:
            birth_date = date.fromisoformat(birth_date_str)
        except ValueError:
            return form_error('Invalid birth date format. Please use YYYY-MM-DD.')

        # Validate death date
        date_of_death = None
        if date_of_death_str:
            try:
                date_of_death = date.fromisoformat(date_of_death_str)
            except ValueError:
                flash('Invalid death date format. Please use YYYY-MM-DD.', 'error')
                return form_error('Invalid death date format. Please use YYYY-MM-DD.')

        # Validate logical constraints
        if date_of_death and date_of_death < birth_date:
            return form_error('Date of death cannot be before birth date.')

        author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )
        db.session.add(author)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return form_error('Could not save author — please check your input.')

        flash('Author added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """Show the add-book form and handle new book submissions."""
    current_year = date.today().year
    authors = get_authors()

    if request.method == 'POST':

        def form_error(message):
            flash(message, 'error')
            return render_template('add_book.html', current_year=current_year, authors=authors)

        title = request.form.get('title', '').strip()
        isbn = request.form.get('isbn', '').strip()
        publication_year = request.form.get('publication_year', type=int)
        author_id = request.form.get('author_id', type=int)

        if not title:
            return form_error('Book title is required.')

        if not isbn:
            return form_error('ISBN is required.')

        if publication_year is None or not (1000 <= publication_year <= current_year):
            return form_error(f'Publication year must be between 1000 and {current_year}.')

        if author_id is None or get_author_by_id(author_id) is None:
            return form_error('Please choose a valid author.')

        book = Book(
            title=request.form.get('title'),
            isbn=request.form.get('isbn'),
            publication_year=request.form.get('publication_year', type=int),
            author_id=request.form.get('author_id', type=int)
        )
        db.session.add(book)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return form_error('Could not save book — please check your input.')

        flash('Book added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_book.html', current_year=current_year, authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """Delete a book from the database and if author has no more books, delete it."""
    book = get_book_by_id(book_id)


    if book is None:
        flash('Book not found!', 'error')
        return redirect(url_for('index'))

    author = get_author_by_id(book.author_id)

    if author is not None and len(author.books) == 1:
        db.session.delete(author)

    db.session.delete(book)
    db.session.commit()

    flash('Book deleted successfully!', 'success')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)

# Run once to create the tables, then comment out again:
# with app.app_context():
#     db.create_all()
