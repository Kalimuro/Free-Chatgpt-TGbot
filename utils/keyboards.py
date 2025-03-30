from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мой профиль')],
    [KeyboardButton(text='Начать диалог с chat-gpt')]
],
    resize_keyboard=True
)

inlines = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Админ панель', callback_data='adminpanel')]
])

adminpanel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить канал в список обязательных для подписки', callback_data='add_channel')],
    [InlineKeyboardButton(text='Удалить канал из списка обязательных для подписки', callback_data='remove_channel')]
])