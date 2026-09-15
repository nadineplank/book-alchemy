from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """Represents an author in the digital library."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        """Return a representation of the Author instance."""
        return f"Author('{self.id}', '{self.name}', '{self.birth_date}', '{self.date_of_death}')"

    def __str__(self):
        """Return a human-readable representation of the Author instance."""
        death_year = self.date_of_death.year if self.date_of_death else "present"
        return f"{self.name} {self.birth_date.year} - {death_year}"


class Book(db.Model):
    """Represents a book stored in the digital library."""

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String, nullable=False)
    title = db.Column(db.String(255), unique=True, nullable=False, index=True)
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author', backref='books')

    def __repr__(self):
        """Return a representation of the Book instance."""
        return f"Book('{self.id}', '{self.isbn}', '{self.title}', '{self.publication_year}')"

    def __str__(self):
        """Return a human-readable representation of the Book instance."""
        return f"{self.title} {self.publication_year}"
