from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError
from models import db, Course, Category, User, Review
from tools import CoursesFilter, ImageSaver

bp = Blueprint('courses', __name__, url_prefix='/courses')

COURSE_PARAMS = [
    'author_id', 'name', 'category_id', 'short_desc', 'full_desc'
]

RATING_CHOICES = [
    (5, 'отлично'),
    (4, 'хорошо'),
    (3, 'удовлетворительно'),
    (2, 'неудовлетворительно'),
    (1, 'плохо'),
    (0, 'ужасно'),
]

REVIEW_SORTS = {
    'newest': Review.created_at.desc(),
    'positive': Review.rating.desc(),
    'negative': Review.rating.asc(),
}

def params():
    return { p: request.form.get(p) or None for p in COURSE_PARAMS }

def search_params():
    return {
        'name': request.args.get('name'),
        'category_ids': [x for x in request.args.getlist('category_ids') if x],
    }

def review_sort():
    sort = request.args.get('sort', 'newest')
    if sort not in REVIEW_SORTS:
        return 'newest'
    return sort

def user_review(course_id):
    if not current_user.is_authenticated:
        return None
    return db.session.execute(
        db.select(Review).filter_by(course_id=course_id, user_id=current_user.id)
    ).scalar()

def render_new_course(course):
    categories = db.session.execute(db.select(Category)).scalars()
    users = db.session.execute(db.select(User)).scalars()
    return render_template('courses/new.html',
                           categories=categories,
                           users=users,
                           course=course)

@bp.route('/')
def index():
    courses = CoursesFilter(**search_params()).perform()
    pagination = db.paginate(courses)
    courses = pagination.items
    categories = db.session.execute(db.select(Category)).scalars()
    return render_template('courses/index.html',
                           courses=courses,
                           categories=categories,
                           pagination=pagination,
                           search_params=search_params())

@bp.route('/new')
@login_required
def new():
    course = Course()
    return render_new_course(course)

@bp.route('/create', methods=['POST'])
@login_required
def create():
    f = request.files.get('background_img')
    img = None
    course = Course()
    try:
        if f and f.filename:
            if not f.mimetype.startswith('image/'):
                flash('Для фонового изображения можно выбрать только файл изображения.', 'danger')
                return render_new_course(course)
            img = ImageSaver(f).save()

        image_id = img.id if img else None
        course = Course(**params(), background_image_id=image_id)
        db.session.add(course)
        db.session.commit()
    except IntegrityError as err:
        flash(f'Возникла ошибка при записи данных в БД. Проверьте корректность введённых данных. ({err})', 'danger')
        db.session.rollback()
        return render_new_course(course)

    flash(f'Курс {course.name} был успешно добавлен!', 'success')

    return redirect(url_for('courses.index'))

@bp.route('/<int:course_id>')
def show(course_id):
    course = db.get_or_404(Course, course_id)
    latest_reviews = db.session.execute(
        db.select(Review)
        .filter_by(course_id=course_id)
        .order_by(Review.created_at.desc())
        .limit(5)
    ).scalars()
    return render_template('courses/show.html',
                           course=course,
                           latest_reviews=latest_reviews,
                           rating_choices=RATING_CHOICES,
                           user_review=user_review(course_id))

@bp.route('/<int:course_id>/reviews')
def reviews(course_id):
    course = db.get_or_404(Course, course_id)
    sort = review_sort()
    reviews_query = (
        db.select(Review)
        .filter_by(course_id=course_id)
        .order_by(REVIEW_SORTS[sort], Review.created_at.desc())
    )
    pagination = db.paginate(reviews_query, per_page=5)
    return render_template('courses/reviews.html',
                           course=course,
                           reviews=pagination.items,
                           pagination=pagination,
                           sort=sort,
                           rating_choices=RATING_CHOICES,
                           user_review=user_review(course_id))

@bp.route('/<int:course_id>/reviews/create', methods=['POST'])
@login_required
def create_review(course_id):
    course = db.get_or_404(Course, course_id)
    if user_review(course_id):
        flash('Вы уже оставили отзыв к этому курсу.', 'warning')
        return redirect(request.referrer or url_for('courses.show', course_id=course.id))

    try:
        rating = int(request.form.get('rating'))
        if rating < 0 or rating > 5:
            raise ValueError
    except (TypeError, ValueError):
        flash('Выберите корректную оценку от 0 до 5.', 'danger')
        return redirect(request.referrer or url_for('courses.show', course_id=course.id))

    text = request.form.get('text')
    if not text:
        flash('Заполните текст отзыва.', 'danger')
        return redirect(request.referrer or url_for('courses.show', course_id=course.id))

    review = Review(rating=rating, text=text, course=course, user=current_user)
    course.rating_sum += rating
    course.rating_num += 1
    db.session.add(review)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Не удалось сохранить отзыв. Проверьте корректность введённых данных.', 'danger')
    else:
        flash('Отзыв был успешно добавлен.', 'success')

    return redirect(request.referrer or url_for('courses.show', course_id=course.id))
