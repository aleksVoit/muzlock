from models import Users


def create_user(first_name, last_name, tg_id, lang):
    new_user = Users(
        first_name = first_name,
        last_name = last_name,
        tg_id = tg_id,
        language = lang
    )
    new_user.save()
    print('New user added.')
