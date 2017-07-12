import datetime

from google.appengine.ext import ndb
from protorpc import messages

import arrow


def copyToForm(form, model):
    """
    fill entity value to endpoints messages.Message

    Args:
        form: endpoints messages.Message
        model: ndb model

    Returns:
        messages.Message

    """

    for field in form.all_fields():
        if hasattr(model, field.name):
            if type(getattr(model, field.name)) is datetime.datetime:
                setattr(form, field.name,
                        arrow.get(str(getattr(model, field.name))).replace(hours=8).format('YYYY-MM-DD HH:mm:ss'))

            elif type(getattr(model, field.name)) is ndb.Key:
                key = getattr(model, field.name)
                if key:
                    setattr(form, field.name, copyToForm(field.type(), key.get()))

            elif type(getattr(model, field.name)) is list:
                setattr(form, field.name, [copyToForm(field.type(), (f if type(f) is not ndb.Key else f.get())) for f in
                                           getattr(model, field.name)])

            else:
                setattr(form, field.name, getattr(model, field.name))

        elif field.name == "websafeKey":
            setattr(form, field.name, model.key.urlsafe())

    form.check_initialized()
    return form


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    data = messages.StringField(1, required=True)


class BooleanMessage(messages.Message):
    """BooleanMessage-- outbound Boolean value message"""
    data = messages.BooleanField(1)


class Book(ndb.Model):
    name = ndb.StringProperty(required=True)
    title = ndb.StringProperty(required=True)


class BookForm(messages.Message):
    websafeKey = messages.StringField(1)
    name = messages.StringField(2)
    title = messages.StringField(3)


class BookForms(messages.Message):
    items = messages.MessageField('BookForm', 1, repeated=True)
