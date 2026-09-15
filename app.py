import os
from datetime import date

from flask import Flask, render_template, request

from data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)


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


if __name__ == '__main__':
    app.run(debug=True, port=5001)

# Run once to create the tables, then comment out again:
# with app.app_context():
#     db.create_all()

