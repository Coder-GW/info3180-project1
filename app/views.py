"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file contains the routes for your application.
"""

import os
from app import app, db
from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from .models import Property
from .forms import PropertyForm


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


# Route 1: Display the Add New Property form (GET) and handle submission (POST)
@app.route('/properties/create', methods=['GET', 'POST'])
def new_property():
    form = PropertyForm()

    if form.validate_on_submit():
        # Handle photo upload
        photo_file = form.photo.data
        filename = secure_filename(photo_file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        photo_file.save(upload_path)

        # Save property to database
        prop = Property(
            title=form.title.data,
            description=form.description.data,
            bedrooms=form.bedrooms.data,
            bathrooms=form.bathrooms.data,
            price=form.price.data,
            prop_type=form.prop_type.data,
            location=form.location.data,
            photo=filename
        )
        db.session.add(prop)
        db.session.commit()

        flash('Property successfully added!', 'success')
        return redirect(url_for('properties'))

    # Flash any form validation errors
    flash_errors(form)
    return render_template('new_property.html', form=form)


# Route 2: Display list of all properties
@app.route('/properties')
def properties():
    all_props = Property.query.all()
    return render_template('properties.html', properties=all_props)


# Route 3: Display a single property by its id
@app.route('/properties/<int:propertyid>')
def property_detail(propertyid):
    prop = Property.query.get_or_404(propertyid)
    return render_template('property.html', property=prop)


###
# The functions below should be applicable to all Flask apps.
###

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
