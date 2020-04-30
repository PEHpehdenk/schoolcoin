from data import db_session
from data.users import User
from data.news import News
from data.tasks import Tasks
from data.vacancys import Vacancys
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_login import login_user, LoginManager, logout_user, login_required
from flask import redirect, render_template, Flask, session
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, PasswordField
from flask_login import current_user
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_httpauth import HTTPBasicAuth
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/blogs.sqlite")
auth = HTTPBasicAuth()


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')


class TasksForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Условие")
    cost = TextAreaField('При правильном ответе пользователь получит:')
    reusable = TextAreaField('Всего пользователей смогут ответить на эту задачу:')
    answer = TextAreaField('Ответ на задачу:')
    submit = SubmitField('Применить')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


class AnswerForm(FlaskForm):
    answer = StringField('Ваш ответ', validators=[DataRequired()])
    submit = SubmitField('Ответить')


class SupportForm(FlaskForm):
    question = StringField('Объясните вашу проблему', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class VacancyForm(FlaskForm):
    title = StringField('Цель', validators=[DataRequired()])
    content = TextAreaField("Нужные факторы")
    submit = SubmitField('Выложить')


class QuestionnaireForm(FlaskForm):
    text = StringField('Опишите себя', validators=[DataRequired()])
    vkOfUser = StringField('Укажите ваш вк (если нет, введите None)', validators=[DataRequired()])
    phoneNumber = StringField('Укажите ваш номер телефон (если нет, введите None)', validators=[DataRequired()])
    submit = SubmitField('Отправить заявку')


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 500)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/tasks',  methods=['GET', 'POST'])
@login_required
def add_tasks():
    form = TasksForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        tasks = Tasks()
        tasks.title = form.title.data
        tasks.content = form.content.data
        tasks.reusable = form.reusable.data
        tasks.cost = form.cost.data
        tasks.answeroftask = form.answer.data
        current_user.tasks.append(tasks)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('tasks.html', title='Добавление задачи',
                           form=form)


@app.route('/vacancy',  methods=['GET', 'POST'])
@login_required
def add_vacancy():
    form = VacancyForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        vacancys = Vacancys()
        vacancys.title = form.title.data
        vacancys.content = form.content.data
        current_user.vacancys.append(vacancys)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('vacancy.html', title='Добавление вакансии',
                           form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id,
                                      News.user == current_user).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    form = SupportForm()
    if form.validate_on_submit():
        fromaddr = "schoolcoin@mail.ru"
        toaddr = 'schoolcoin@mail.ru'
        mypass = "08924137667denk123321"
        theme = 'Проблема клента'
        content = "Сообщение от клиента с id = " + str(current_user.id) + '\n' + '\n' + '\n' + form.question.data

        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = theme

        body = content
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
        server.login(fromaddr, mypass)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return redirect('/')
    return render_template('support.html', title='Обращение в службу поддержки',
                            form=form)


@app.route('/vacancys_form/<int:id>', methods=['GET', 'POST'])
@login_required
def vacancys_form(id):
    form = QuestionnaireForm()
    info = form.text.data
    if form.validate_on_submit():
        try:
            session = db_session.create_session()
            for vacancy in session.query(Vacancys).all():
                if vacancy.id == id:
                    idUser = vacancy.user_id
                    for user in session.query(User).all():
                        if user.id == idUser:
                            mail = user.email
                            break

            fromaddr = "schoolcoin@mail.ru"
            toaddr = mail
            mypass = "08924137667denk123321"
            theme = 'Заявка по вакансии по номеру ' + str(id)
            content = "Сообщение от клиента с id = " + str(current_user.id) + '\n' + '\n' + '\n' + info
            content += '\n' + 'вы можете связаться с ним по:' + '\n' + '\n'
            content += 'email: ' + str(current_user.email) + '\n'
            if form.vkOfUser.data != 'None':
                content += 'vk: ' + str(form.vkOfUser.data) + '\n'
            if form.phoneNumber.data != 'None':
                content += 'телефону: ' + str(form.phoneNumber.data) + '\n'

            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = theme

            body = content
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
            server.login(fromaddr, mypass)
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            server.quit()
        except Exception:
            return make_response(jsonify({'error': 'Mail is incorrect'}), 501)
        return redirect('/')
    return render_template('questionnaire.html', title='Отправить заявку',
                           form=form)


@app.route('/tasks_answer/<int:id>', methods=['GET', 'POST'])
@login_required
def tasks_asnwer(id):
    form = AnswerForm()
    answ = 0
    cost = 0
    people = 0
    istrue = []
    session = db_session.create_session()
    for task in session.query(Tasks).all():
        if task.id == id:
            answ = task.answeroftask
            cost = task.cost
            people = task.reusable
            if type(task.correctUsers).__name__ != 'NoneType':
                istrue = task.correctUsers.split()
            break
    if form.answer.data == answ and people > 0 and str(current_user.id) not in istrue:
        task = session.query(Tasks).filter(Tasks.id == id).first()
        if task:
            minusUser = task.reusable - 1
            task.reusable = minusUser
            if type(task.correctUsers).__name__ != 'NoneType':
                text = task.correctUsers + str(current_user.id) + ' '
            else:
                text = str(current_user.id) + ' '
            task.correctUsers = text
            session.commit()
        current_user.answer = form.answer.data
        current_user.schoolcoins = current_user.schoolcoins + cost
        current_user.numberoftasks = current_user.numberoftasks + 1
        if form.validate_on_submit():
            session = db_session.create_session()
            user = User()
            user.schoolcoins = current_user.schoolcoins
            user.numberoftasks = current_user.numberoftasks
            session.merge(current_user)
            session.commit()
    return render_template('answer.html', title='Отправить ответ',
                           form=form)


@app.route('/tasks_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def tasks_delete(id):
    session = db_session.create_session()
    tasks = session.query(Tasks).filter(Tasks.id == id,
                                      Tasks.user == current_user).first()
    if tasks:
        session.delete(tasks)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/vacancys_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def vacancys_delete(id):
    session = db_session.create_session()
    vacancys = session.query(Vacancys).filter(Vacancys.id == id,
                                      Vacancys.user == current_user).first()
    if vacancys:
        session.delete(vacancys)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/account/', methods=['GET'])
@login_required
def account():
    return render_template('account.html')


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование новости', form=form)


@app.route("/")
def index():
    session = db_session.create_session()
    tasks = session.query(Tasks)
    vacancys = session.query(Vacancys)
    if current_user.is_authenticated:
        news = session.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = session.query(News).filter(News.is_private != True)
    return render_template("indexMain.html", news=news, tasks=tasks, vacancys=vacancys)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    app.run()


if __name__ == '__main__':
    main()
