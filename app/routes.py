from flask import redirect, url_for

import app
from app.forms import LoginForm

# ...

@app.route('/login', methods=['GET', 'POST'])  # type: ignore # noqa: F821
def login():
    form = LoginForm()  # noqa: F821
    if form.validate_on_submit():
        # ...
        return redirect(url_for('index'))
    # ...