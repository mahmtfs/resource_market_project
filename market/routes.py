from flask import render_template, url_for, flash, redirect, request
from market import app, db, bcrypter
from market.forms import Registration, Login, ItemForm, ProfileForm, BuyForm, BalanceForm, SearchForm
from market.models import User, Item
from flask_login import login_user, current_user, logout_user, login_required


per_page_num = 4
highlights = {
    "home_highlight": False,
    "my_items_highlight": False,
    "add_item_highlight": False,
    "about_highlight": False,
    "profile_highlight": False,
    "balance_highlight": False
}


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '', type=str)
    form = SearchForm()
    items = []
    if form.validate_on_submit():
        query = ''
        page = 1
        if form.query.data:
            query = form.query.data
            items = Item.query.filter(Item.name.contains(query)).paginate(page=page, per_page=per_page_num)
        else:
            items = Item.query.paginate(page=page, per_page=per_page_num)
    else:
        if query:
            items = Item.query.filter(Item.name.contains(query)).paginate(page=page, per_page=per_page_num)
        else:
            items = Item.query.paginate(page=page, per_page=per_page_num)
    highlights_copy = highlights.copy()
    highlights_copy["home_highlight"] = True
    return render_template('home.html',
                           items=items,
                           items_my=False,
                           form=form,
                           query=query,
                           highlights=highlights_copy)


@app.route("/items/my", methods=["GET", "POST"])
@login_required
def my_items():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '', type=str)
    form = SearchForm()
    items = []
    if form.validate_on_submit():
        query = ''
        page = 1
        if form.query.data:
            query = form.query.data
            items = Item.query.filter(Item.name.contains(query)).filter_by(seller=current_user).paginate(page=page,
                                                                                                         per_page=per_page_num)
        else:
            items = Item.query.filter_by(seller=current_user).paginate(page=page, per_page=per_page_num)
    else:
        if query:
            items = Item.query.filter(Item.name.contains(query)).filter_by(seller=current_user).paginate(page=page,
                                                                                                         per_page=per_page_num)
        else:
            items = Item.query.filter_by(seller=current_user).paginate(page=page, per_page=per_page_num)
    highlights_copy = highlights.copy()
    highlights_copy["my_items_highlight"] = True
    return render_template('home.html',
                           items=items,
                           items_my=True,
                           form=form,
                           query=query,
                           highlights=highlights_copy)


@app.route("/about")
@login_required
def about():
    highlights_copy = highlights.copy()
    highlights_copy["about_highlight"] = True
    return render_template('about.html',
                           title="About",
                           highlights=highlights_copy)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Registration()
    if form.validate_on_submit():
        hashed_password = bcrypter.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! Now you can log in.', 'success')
        return redirect(url_for('home'))
    return render_template('register.html',
                           title="Register",
                           form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypter.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Welcome, {user.username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash("Wrong username or password! Login failed!", 'danger')

    return render_template('login.html',
                           title="Login",
                           form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.description = form.description.data
        db.session.commit()
        flash("Your profile has been updated!", 'success')
    elif request.method == 'GET':
        form.description.data = current_user.description
    highlights_copy = highlights.copy()
    highlights_copy["profile_highlight"] = True
    return render_template("profile.html",
                           title='Profile',
                           user=current_user,
                           form=form,
                           display_delete=False,
                           highlights=highlights_copy)


@app.route("/profile/<int:user_id>", methods=["GET", "POST"])
@login_required
def profile_not_mine(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        return redirect(url_for('profile'))
    if current_user.admin:
        form = ProfileForm()
        if form.delete.data:
            items = Item.query.filter_by(seller=user)
            for item_fetch in items:
                db.session.delete(item_fetch)
            db.session.delete(user)
            db.session.commit()
            flash("The user has been banned!", 'success')
            return redirect(url_for('home'))
        if form.validate_on_submit():
            user.description = form.description.data
            db.session.commit()
            flash("The profile has been updated!", 'success')
        elif request.method == 'GET':
            form.description.data = user.description
        highlights_copy = highlights.copy()
        highlights_copy["profile_highlight"] = True
        return render_template('profile.html',
                               title=user.username,
                               user=user,
                               form=form,
                               display_delete=True,
                               highlights=highlights_copy)
    return render_template('profile_not_mine.html',
                           title=user.username,
                           user=user,
                           highlights=highlights)


@app.route("/item/new", methods=["GET", "POST"])
@login_required
def new_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(name=form.name.data,
                    type=form.item_type.data,
                    cost=form.cost.data,
                    volume=form.volume.data,
                    description=form.description.data,
                    seller=current_user)
        db.session.add(item)
        db.session.commit()
        flash("Your item has been created!", 'success')
        return redirect(url_for('home'))
    highlights_copy = highlights.copy()
    highlights_copy["add_item_highlight"] = True
    return render_template('item_mine.html',
                           title='New Item',
                           form=form,
                           seller=current_user,
                           header_text='Create Item',
                           display_delete=False,
                           highlights=highlights_copy)


@app.route("/item/<int:item_id>", methods=["GET", "POST"])
@login_required
def item(item_id):
    item_fetch = Item.query.get_or_404(item_id)
    if item_fetch.seller == current_user or current_user.admin:
        return redirect(url_for('update_item', item_id=item_fetch.id))
    form = BuyForm()
    if form.validate_on_submit():
        if item_fetch.volume >= form.volume_to_buy.data:
            total_cost = form.volume_to_buy.data * item_fetch.cost
            if total_cost <= current_user.balance:
                current_user.balance -= total_cost
                item_fetch.volume -= form.volume_to_buy.data
                if item_fetch.volume == 0:
                    db.session.delete(item_fetch)
                    db.session.commit()
                    flash("The purchase was successful! Item's supply has depleted!", 'success')
                    return redirect(url_for('home'))
                db.session.commit()
                flash("Item bought successfully!", 'success')
            else:
                flash("Insufficient funds!", 'danger')
        else:
            flash("The volume specified is too high!", 'danger')
    return render_template('item_not_mine.html',
                           title=item_fetch.name,
                           item=item_fetch,
                           form=form,
                           highlights=highlights)


@app.route("/item/<int:item_id>/update", methods=["GET", "POST"])
@login_required
def update_item(item_id):
    item_fetch = Item.query.get_or_404(item_id)
    if item_fetch.seller != current_user and not current_user.admin:
        return redirect(url_for('item', item_id=item_fetch.id))
    form = ItemForm()
    if form.delete.data:
        return redirect(url_for('delete_item', item_id=item_fetch.id), code=307)
    if form.validate_on_submit():
        item_fetch.name = form.name.data
        item_fetch.type = form.item_type.data
        item_fetch.cost = form.cost.data
        item_fetch.volume = form.volume.data
        item_fetch.description = form.description.data
        db.session.commit()
        if current_user == item_fetch.seller:
            flash("Your item has been updated!", 'success')
        else:
            flash("The item has been updated!", 'success')
    elif request.method == 'GET':
        form.name.data = item_fetch.name
        form.item_type.data = item_fetch.type
        form.cost.data = item_fetch.cost
        form.volume.data = item_fetch.volume
        form.description.data = item_fetch.description
    return render_template('item_mine.html',
                           title='Update Item',
                           form=form,
                           seller=item_fetch.seller,
                           header_text='Update Item',
                           display_delete=True,
                           delete_id=item_id,
                           highlights=highlights)


@app.route("/item/<int:item_id>/delete/<int:from_main>", methods=["POST"])
@login_required
def delete_item(item_id, from_main=True):
    item_fetch = Item.query.get_or_404(item_id)
    if item_fetch.seller != current_user:
        return redirect(url_for('item', item_id=item_fetch.id))
    db.session.delete(item_fetch)
    db.session.commit()
    flash("Your item has been deleted!", 'success')
    if from_main:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('my_items'))


@app.route("/balance", methods=["GET", "POST"])
@login_required
def balance_page():
    form = BalanceForm()
    if form.validate_on_submit():
        current_user.balance += form.deposit.data
        db.session.commit()
        flash("Transaction complete!", 'success')
    highlights_copy = highlights.copy()
    highlights_copy["balance_highlight"] = True
    return render_template('balance.html',
                           title='Balance',
                           form=form,
                           highlights=highlights_copy)
