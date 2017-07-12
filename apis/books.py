import endpoints
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import messages

from models import copyToForm, BooleanMessage
from models import Book
from models import BookForm
from models import BookForms

from settings import books_api
from utils import LoginAdminRequired, get_entity_by_websafeKey_key

BOOKS_LIST_RESOURCE = endpoints.ResourceContainer()

BOOKS_CREATE_RESOURCE = endpoints.ResourceContainer(
        BookForm
)

BOOKS_UPDATE_RESOURCE = endpoints.ResourceContainer(
        BookForm,
        websafeKey=messages.StringField(2)
)

BOOKS_DELETE_RESOURCE = endpoints.ResourceContainer(
        websafeKey=messages.StringField(1)
)

init_book_items = [
    Book(**{"name": "Harper Lee", "title": "To Kill a Mockingbird", "key": ndb.Key(Book, "To Kill a Mockingbird")}),
    Book(**{"name": "Shel Silverstein", "title": "The Giving Tree", "key": ndb.Key(Book, "The Giving Tree")}),
]

books_count = Book.query().count()
if books_count == 0:
    input = []
    for item in init_book_items:
        input.append(item)
    ndb.put_multi(input)


@books_api.api_class(resource_name="books")
class BooksAPI(remote.Service):
    """
    Books API
    """

    # @LoginAdminRequired
    def _listBooks(self, request):
        res = BookForms()
        res.items = [copyToForm(BookForm(), item) for item in Book.query().fetch()]
        return res

    @endpoints.method(BOOKS_LIST_RESOURCE, BookForms, path="books",
                      http_method="GET", name="list")
    def listBooks(self, request):
        """List books"""
        return self._listBooks(request)

    def _addBook(self, request):
        try:
            data = {field.name: getattr(request, field.name) for field in request.all_fields()}
            data['key'] = ndb.Key(Book, data['title'])
            del data['websafeKey']

            r = Book(**data).put()

            return copyToForm(BookForm(), r.get())

        except Exception, e:
            raise endpoints.BadRequestException(e.message)

    @endpoints.method(BOOKS_CREATE_RESOURCE, BookForm, path="books",
                      http_method="POST", name="post")
    def addBook(self, request):
        """Add books"""
        return self._addBook(request)

    @LoginAdminRequired
    def _deleteBook(self, request):
        book = get_entity_by_websafeKey_key(request.websafeKey)

        try:
            book.key.delete()
            return BooleanMessage(data=True)

        except Exception, e:
            raise endpoints.InternalServerErrorException(e.message)

    @endpoints.method(BOOKS_DELETE_RESOURCE, BooleanMessage, path="books/{websafeKey}",
                      http_method="DELETE", name="delete")
    def deleteBook(self, request):
        """Delete book"""
        return self._deleteBook(request)

    def _updateBook(self, request):
        try:
            book = get_entity_by_websafeKey_key(request.websafeKey)

            for field in request.all_fields():
                data = getattr(request, field.name)
                # only copy fields where we get data
                if data not in (None, []):
                    # special handling for dates (convert string to Date)
                    if field.name in ('created'):
                        continue

                    setattr(book, field.name, data)

            book.put()
            return copyToForm(BookForm(), book)

        except Exception, e:
            raise endpoints.BadRequestException(e.message)

    @endpoints.method(BOOKS_UPDATE_RESOURCE, BookForm, path="books/{websafeKey}",
                      http_method="PUT", name="put")
    def updateBook(self, request):
        """Update book"""
        return self._updateBook(request)
