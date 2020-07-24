from flask_login import current_user
from invenio_oauthclient.models import UserIdentity


def user_externalid():

    if current_user.is_authenticated:
        id = current_user.get_id()
        user_external = UserIdentity.query.filter_by(id_user=id).first()
        if user_external:
            return user_external.id
    return False
