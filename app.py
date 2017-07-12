import endpoints

from apis import books

API = endpoints.api_server([
    books.BooksAPI
])
