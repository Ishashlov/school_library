import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    filters,
    Application
)
import wikipedia
import json
import os


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


wikipedia.set_lang("ru")


DATA_FILE = "library_data.json"
FAVORITES_FILE = "favorites.json"



def load_books():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        sample_books = [
            {
                "id": 1,
                "title": "Преступление и наказание",
                "author": "Фёдор Достоевский",
                "genre": "Классика",
                "year": 1866,
                "available": True,
                "description": "Роман о бывшем студенте Родионе Раскольникове, который совершает убийство."
            },
            {
                "id": 2,
                "title": "Мастер и Маргарита",
                "author": "Михаил Булгаков",
                "genre": "Фэнтези",
                "year": 1967,
                "available": True,
                "description": "Роман о визите дьявола в Москву и истории Мастера и Маргариты."
            },
            {
                "id": 3,
                "title": "1984",
                "author": "Джордж Оруэлл",
                "genre": "Утопия",
                "year": 1949,
                "available": True,
                "description": "Роман-антиутопия о тоталитарном обществе под постоянным наблюдением."
            }
        ]
        save_books(sample_books)
        return sample_books


def save_books(books):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)


def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}



def save_favorites(favorites):
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)



async def main_menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Каталог книг", callback_data='catalog')],
        [InlineKeyboardButton("Поиск книги", callback_data='search')],
        [InlineKeyboardButton("Избранное", callback_data='favorites')],
        [InlineKeyboardButton("О библиотеке", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text('Выбирайте:',
                                        reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text('Выбирайте:',
                                                      reply_markup=reply_markup)


async def show_catalog(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("По жанрам", callback_data='by_genre')],
        [InlineKeyboardButton("По авторам", callback_data='by_author')],
        [InlineKeyboardButton("По годам", callback_data='by_year')],
        [InlineKeyboardButton("По доступности", callback_data='by_availability')],
        [InlineKeyboardButton("Все книги", callback_data='all_books')],
        [InlineKeyboardButton("<--Назад", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Каталог книг. Выберите способ сортировки:', reply_markup=reply_markup)


async def show_by_genre(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    books = load_books()
    genres = sorted(set(book['genre'] for book in books))

    keyboard = []
    for genre in genres:
        keyboard.append([InlineKeyboardButton(genre, callback_data=f'genre_{genre}')])

    keyboard.append([InlineKeyboardButton("<--Назад", callback_data='catalog')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Выберите жанр:', reply_markup=reply_markup)


async def show_by_author(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    books = load_books()
    authors = sorted(set(book['author'] for book in books))

    keyboard = []
    for author in authors:
        keyboard.append([InlineKeyboardButton(author, callback_data=f'author_{author}')])

    keyboard.append([InlineKeyboardButton("<--Назад", callback_data='catalog')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Выберите автора:', reply_markup=reply_markup)


async def show_by_year(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    books = load_books()
    years = sorted(set(book['year'] for book in books), reverse=True)

    keyboard = []
    for year in years:
        keyboard.append([InlineKeyboardButton(str(year), callback_data=f'year_{year}')])

    keyboard.append([InlineKeyboardButton("<--Назад", callback_data='catalog')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Выберите год издания:', reply_markup=reply_markup)



async def show_by_availability(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Доступные книги", callback_data='available_True')],
        [InlineKeyboardButton("Недоступные книги", callback_data='available_False')],
        [InlineKeyboardButton("<--Назад", callback_data='catalog')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Выберите доступность:', reply_markup=reply_markup)



async def show_all_books(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    books = load_books()
    await show_books_list(update, context, books, back_to='catalog')



async def show_books_by_criteria(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')
    criteria = data[0]
    value = '_'.join(data[1:]) if len(data) > 1 else None

    books = load_books()

    if criteria == 'genre':
        filtered_books = [book for book in books if book['genre'] == value]
        title = f"Книги жанра {value}:"
    elif criteria == 'author':
        filtered_books = [book for book in books if book['author'] == value]
        title = f"Книги автора {value}:"
    elif criteria == 'year':
        filtered_books = [book for book in books if book['year'] == int(value)]
        title = f"Книги {value} года:"
    elif criteria == 'available':
        filtered_books = [book for book in books if book['available'] == (value == 'True')]
        title = "Доступные книги:" if value == 'True' else "Недоступные книги:"
    else:
        filtered_books = books
        title = "Все книги:"

    await show_books_list(update, context, filtered_books, title=title, back_to='catalog')



async def show_books_list(update: Update, context: CallbackContext, books: list, title: str = "Список книг:",
                          back_to: str = 'main_menu') -> None:
    query = update.callback_query

    if not books:
        await query.edit_message_text("Книги не найдены.")
        return

    keyboard = []
    for book in books:
        status = "V" if book['available'] else "X"
        keyboard.append([
            InlineKeyboardButton(
                f"{book['title']} ({book['author']}) {status}",
                callback_data=f'book_{book["id"]}')
        ])

    keyboard.append([InlineKeyboardButton("<--Назад", callback_data=back_to)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(title, reply_markup=reply_markup)


async def show_book_info(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    book_id = int(query.data.split('_')[1])
    books = load_books()
    book = next((b for b in books if b['id'] == book_id), None)

    if not book:
        await query.edit_message_text("Книга не найдена.")
        return

    favorites = load_favorites()
    user_id = str(query.from_user.id)
    is_favorite = user_id in favorites and book_id in favorites[user_id]

    status = "Доступна" if book['available'] else "Недоступна"
    text = (
        f"<b>{book['title']}</b>\n"
        f"Автор: {book['author']}\n"
        f"Жанр: {book['genre']}\n"
        f"Год: {book['year']}\n"
        f"Статус: {status}\n"
        f"\nОписание:\n{book['description']}"
    )

    keyboard = [
        [
            InlineKeyboardButton("Аннотация из Википедии", callback_data=f'wiki_{book_id}'),
            InlineKeyboardButton("В избранное" if not is_favorite else "Удалить из избранного",
                                 callback_data=f'toggle_fav_{book_id}')
        ],
        [InlineKeyboardButton("<--Назад", callback_data='catalog')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')



async def search_wikipedia(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    book_id = int(query.data.split('_')[1])
    books = load_books()
    book = next((b for b in books if b['id'] == book_id), None)

    if not book:
        await query.edit_message_text("Книга не найдена.")
        return

    try:
        summary = wikipedia.summary(f"{book['title']} {book['author']}", sentences=3)
    except wikipedia.exceptions.PageError:
        summary = "Не удалось найти информацию в Википедии."
    except wikipedia.exceptions.DisambiguationError as e:
        summary = f"Найдены неоднозначные результаты: {e.options[0]}"
    except Exception as e:
        summary = f"Произошла ошибка: {str(e)}"

    keyboard = [
        [InlineKeyboardButton("<--Назад к книге", callback_data=f'book_{book_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"<b>{book['title']}</b>\n\nИнформация из Википедии:\n\n{summary}",
                                  reply_markup=reply_markup, parse_mode='HTML')


async def toggle_favorite(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    book_id = int(query.data.split('_')[2])
    user_id = str(query.from_user.id)

    favorites = load_favorites()

    if user_id not in favorites:
        favorites[user_id] = []

    if book_id in favorites[user_id]:
        favorites[user_id].remove(book_id)
        await query.answer("Удалено из избранного")
    else:
        favorites[user_id].append(book_id)
        await query.answer("Добавлено в избранное")

    save_favorites(favorites)


    books = load_books()
    book = next((b for b in books if b['id'] == book_id), None)

    if book:
        is_favorite = book_id in favorites.get(user_id, [])
        keyboard = [
            [
                InlineKeyboardButton("Аннотация из Википедии", callback_data=f'wiki_{book_id}'),
                InlineKeyboardButton("В избранное" if not is_favorite else "Удалить из избранного",
                                     callback_data=f'toggle_fav_{book_id}')
            ],
            [InlineKeyboardButton("<==Назад", callback_data='catalog')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup)


async def show_favorites(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    favorites = load_favorites()
    book_ids = favorites.get(user_id, [])

    if not book_ids:
        keyboard = [
            [InlineKeyboardButton("<--Назад", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("У вас пока нет избранных книг.", reply_markup=reply_markup)
        return

    books = load_books()
    favorite_books = [book for book in books if book['id'] in book_ids]

    await show_books_list(update, context, favorite_books, title="Ваши избранные книги:", back_to='main_menu')


async def search_book(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    context.user_data['waiting_for_search'] = True

    keyboard = [
        [InlineKeyboardButton("<--Отмена", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Введите название книги или автора для поиска:", reply_markup=reply_markup)


async def handle_text(update: Update, context: CallbackContext) -> None:
    if 'waiting_for_search' not in context.user_data or not context.user_data['waiting_for_search']:
        return

    search_text = update.message.text.lower()
    books = load_books()

    found_books = []
    for book in books:
        if (search_text in book['title'].lower() or
                search_text in book['author'].lower() or
                search_text in book['genre'].lower()):
            found_books.append(book)

    if found_books:
        await show_books_list_from_text(update, context, found_books)
    else:
        await update.message.reply_text("Книги не найдены. Попробуйте другой запрос.")

    context.user_data['waiting_for_search'] = False



async def show_books_list_from_text(update: Update, context: CallbackContext, books: list) -> None:
    keyboard = []
    for book in books:
        status = "V" if book['available'] else "X"
        keyboard.append([
            InlineKeyboardButton(
                f"{book['title']} ({book['author']}) {status}",
                callback_data=f'book_{book["id"]}')
        ])

    keyboard.append([InlineKeyboardButton("<--Назад", callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Результаты поиска:", reply_markup=reply_markup)


# Информация о библиотеке
async def about_library(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    text = (
        "Школьная библиотека\n\n"
        "Здесь вы можете найти книги для учебы и внеклассного чтения.\n"
        "Библиотека работает с 9:00 до 17:00.\n\n"
        "Для получения книги обратитесь к библиотекарю."
    )

    keyboard = [
        [InlineKeyboardButton("<--Назад", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)


async def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if update.callback_query:
        await update.callback_query.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")
    elif update.message:
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте снова.")



def main() -> None:
    application = Application.builder().token("7852483320:AAGP1Tx59tng-me2swo-zDWkQSry5GF2MEU").build()

    application.add_handler(CommandHandler("start", main_menu))

    application.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu$'))
    application.add_handler(CallbackQueryHandler(show_catalog, pattern='^catalog$'))
    application.add_handler(CallbackQueryHandler(show_by_genre, pattern='^by_genre$'))
    application.add_handler(CallbackQueryHandler(show_by_author, pattern='^by_author$'))
    application.add_handler(CallbackQueryHandler(show_by_year, pattern='^by_year$'))
    application.add_handler(CallbackQueryHandler(show_by_availability, pattern='^by_availability$'))
    application.add_handler(CallbackQueryHandler(show_all_books, pattern='^all_books$'))
    application.add_handler(CallbackQueryHandler(show_books_by_criteria, pattern='^(genre|author|year|available)_'))
    application.add_handler(CallbackQueryHandler(show_book_info, pattern='^book_'))
    application.add_handler(CallbackQueryHandler(search_wikipedia, pattern='^wiki_'))
    application.add_handler(CallbackQueryHandler(toggle_favorite, pattern='^toggle_fav_'))
    application.add_handler(CallbackQueryHandler(show_favorites, pattern='^favorites$'))
    application.add_handler(CallbackQueryHandler(search_book, pattern='^search$'))
    application.add_handler(CallbackQueryHandler(about_library, pattern='^about$'))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))


    application.add_error_handler(error_handler)


    application.run_polling()


if __name__ == '__main__':
    main()