from flask import render_template, url_for, flash, redirect, request
from forms import RegistrationForm, LoginForm, UploadForm
from models import db, User, UploadedFile # Import db and User model
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin # For session management
import os
import seaborn as sns # <--- NEW IMPORT
import io # <--- NEW IMPORT
import base64 # <--- NEW IMPORT
import matplotlib.pyplot as plt # <--- NEW IMPORT
from werkzeug.utils import secure_filename
import pandas as pd
from flask import current_app
from datetime import datetime

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login' # Where to redirect if login is required
login_manager.login_message_category = 'info' # Category for flash messages

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    # Helper function to check allowed extensions
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Define a blueprint or directly add routes to app. This example adds directly.

# Placeholder for your app instance, will be imported and used in app.py
# (This file assumes app instance will be passed/imported from app.py)
# For now, let's just make it a function that takes an app and registers routes
def register_routes(app):

    @app.route("/")
    @app.route("/home")
    @login_required # Require login to access home page
    def home():
        return render_template('home.html', title='Home', user=current_user)

    @app.route("/signup", methods=['GET', 'POST'])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(full_name=form.full_name.data,
                        username=form.username.data,
                        email=form.email.data)
            user.set_password(form.password.data) # Hash the password
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        return render_template('signup.html', title='Sign Up', form=form)

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            # Try to find user by email or username
            user = User.query.filter((User.username == form.username_or_email.data) |
                                     (User.email == form.username_or_email.data)).first()
            if user and user.check_password(form.password.data):
                login_user(user) # Log the user in
                next_page = request.args.get('next') # Redirect to the page user tried to access
                flash(f'Welcome back, {user.full_name}!', 'success')
                return redirect(next_page or url_for('home'))
            else:
                flash('Login Unsuccessful. Please check username/email and password', 'danger')
        return render_template('login.html', title='Login', form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    


    @app.route("/upload_csv", methods=['GET', 'POST'])
    @login_required
    def upload_csv():
        form = UploadForm()
        if form.validate_on_submit():
            if 'file' not in request.files:
                flash('No file part', 'danger')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file', 'danger')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                # Secure the filename to prevent directory traversal attacks
                filename = secure_filename(file.filename)
                
                # Create a unique filename to prevent overwriting
                unique_filename = f"{current_user.id}_{datetime.utcnow().timestamp()}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Ensure the upload directory exists
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                file.save(file_path)

                # Save file metadata to the database
                new_file = UploadedFile(filename=filename,
                                        storage_path=unique_filename, # Store just the unique name for easier retrieval
                                        user_id=current_user.id)
                db.session.add(new_file)
                db.session.commit()

                flash('File successfully uploaded and saved!', 'success')
                return redirect(url_for('preview_data')) # Redirect to preview after upload
            else:
                flash('Allowed file types are CSV only!', 'danger')
        return render_template('upload_csv.html', title='Upload CSV', form=form)

    @app.route("/preview_data")
    @login_required
    def preview_data():
        # Get all files uploaded by the current user
        user_files = current_user.files.order_by(UploadedFile.upload_date.desc()).all()
        
        # We'll display a small preview of the latest file, or list all.
        # For simplicity, let's just show a list and link to view.
        # More advanced: pass data from the latest file to display directly.

        # For now, let's show all files and make them clickable for future detailed view
        return render_template('preview_data.html', title='Preview Data', user_files=user_files)

    @app.route("/view_file/<int:file_id>")
    @login_required
    def view_file(file_id):
        uploaded_file = UploadedFile.query.get_or_404(file_id)

        # Ensure the current user owns this file
        if uploaded_file.user_id != current_user.id:
            flash('You do not have permission to view this file.', 'danger')
            return redirect(url_for('preview_data'))

        full_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], uploaded_file.storage_path)
        
        # Check if the file exists on the filesystem
        if not os.path.exists(full_file_path):
            flash('File not found on server.', 'danger')
            return redirect(url_for('preview_data'))

        data_html = None
        try:
            # Read CSV using pandas and convert to HTML table
            df = pd.read_csv(full_file_path)
            # Take a small head for preview
            data_html = df.head(10).to_html(classes='data-table', index=False)
        except Exception as e:
            flash(f'Error reading CSV file: {e}', 'danger')
            return redirect(url_for('preview_data'))

        return render_template('view_file.html', title=f'View {uploaded_file.filename}', 
                               uploaded_file=uploaded_file, 
                               data_html=data_html)



    @app.route("/visuals_analysis")
    @login_required
    def visuals_analysis():
        # Get the latest uploaded CSV file for the current user
        latest_file = UploadedFile.query.filter_by(user_id=current_user.id) \
                                        .order_by(UploadedFile.upload_date.desc()) \
                                        .first()

        if not latest_file:
            flash('Please upload a CSV file first to perform analysis.', 'info')
            return redirect(url_for('upload_csv'))

        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], latest_file.storage_path)

        if not os.path.exists(file_path):
            flash('The uploaded file was not found on the server.', 'danger')
            return redirect(url_for('preview_data'))

        chart_data_uri = None
        try:
            df = pd.read_csv(file_path)

            # --- Chart 1: Placement vs. Internship Experience ---
            # Ensure columns exist
            if 'Placement' in df.columns and 'Internship_Experience' in df.columns:
                # Count placed/not placed for each internship experience group
                placement_internship_counts = df.groupby(['Internship_Experience', 'Placement']).size().unstack(fill_value=0)

                plt.figure(figsize=(8, 6))
                sns.barplot(data=placement_internship_counts.reset_index(), x='Internship_Experience', y='Yes', color='skyblue', label='Placed')
                sns.barplot(data=placement_internship_counts.reset_index(), x='Internship_Experience', y='No', color='salmon', label='Not Placed')

                plt.title('Placement Status by Internship Experience')
                plt.xlabel('Internship Experience')
                plt.ylabel('Number of Students')
                plt.legend(title='Placement')
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.tight_layout()

                # Save plot to a BytesIO object
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png')
                img_buffer.seek(0) # Rewind to the beginning of the buffer
                chart_data_uri = base64.b64encode(img_buffer.getvalue()).decode()
                plt.close() # Close the plot to free up memory
            else:
                flash("Required columns 'Placement' or 'Internship_Experience' not found in the dataset for charting.", 'warning')

        except Exception as e:
            flash(f'Error generating chart: {e}', 'danger')
            # You might want to log the full traceback here for debugging
            app.logger.error(f"Error generating chart for {latest_file.filename}: {e}", exc_info=True)


        return render_template('visuals_analysis.html',
                               title='Visuals & Analysis',
                               chart_data_uri=chart_data_uri,
                               filename=latest_file.filename)
    # Temporary route for testing /home without login_required while developing
    # You can remove this after development
    # @app.route("/test_home")
    # def test_home():
    #     return render_template('home.html', title='Home', user={'full_name': 'Guest User'})