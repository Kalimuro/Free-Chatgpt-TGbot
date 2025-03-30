from aiogram import Router, types, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, CallbackQuery
from aiogram.filters import CommandStart, Command
from utils.chatgpt import *
import utils.keyboards as kb
from aiogram.types import Message

ADMIN_IDS = []  # сюда добавьте id админов
SUBSCRIPTION_CHANNELS = []


class SubscriptionChecker:
    def __init__(self, channel_id: str):
        self.channel_id = channel_id

    async def check_podpisku(self, bot: Bot, user_id: int) -> bool:
        try:
            chat_member = await bot.get_chat_member(chat_id=self.channel_id, user_id=user_id)
            return chat_member.status in ("member", "administrator", "creator")
        except TelegramBadRequest as e:
            print(f"Произошла ошибка: {e}")
            return False


router = Router()

photo = FSInputFile("imgs/gptlog.jpg")

subscription_checker = SubscriptionChecker(channel_id="@pavel")
# Замените на юз вашего канала !ВАЖНО! Бот должен быть администратором тгк


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


class AdminPanelStates(StatesGroup):
    waiting_for_channel_to_add = State()
    waiting_for_channel_to_remove = State()


@router.message(Command("add_channel"), F.from_user.id.in_(ADMIN_IDS))
async def add_channel(message: Message, bot: Bot):
    try:
        channel_id = message.text.split()[1]
        SUBSCRIPTION_CHANNELS.append(channel_id)
        subscription_checker.channels = SUBSCRIPTION_CHANNELS
        await message.reply(f"Канал {channel_id} добавлен в список обязательных для подписки.")
    except IndexError:
        await message.reply("Пожалуйста, укажите ID канала после команды /add_channel.")
    except Exception as e:
        await message.reply(f"Произошла ошибка при добавлении канала в список: {e}")


@router.message(Command("remove_channel"), F.from_user.id.in_(ADMIN_IDS))
async def remove_channel(message: Message, bot: Bot):
    try:
        channel_id = message.text.split()[1]
        if channel_id in SUBSCRIPTION_CHANNELS:
            SUBSCRIPTION_CHANNELS.remove(channel_id)
            subscription_checker.channels = SUBSCRIPTION_CHANNELS
            await message.reply(f"Канал {channel_id} удален из списка обязательных для подписки.")
        else:
            await message.reply(f"Канал {channel_id} не найден в списке обязательных для подписки.")
    except IndexError:
        await message.reply("Пожалуйста, укажите ID канала после команды /remove_channel.")
    except Exception as e:
        await message.reply(f"Ошибка при удалении канала из списка: {e}")


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    if await subscription_checker.check_podpisku(bot, message.from_user.id):
        await message.answer('Задайте любой вопрос и получите мгновенный ответ от ChatGPT!',
                             parse_mode='HTML', reply_markup=kb.main)
    else:
        await message.reply("Перед использованием бота, пожалуйста, подпишитесь на канал @pavel")


@router.message(F.text == 'Мой профиль')
async def profile(message: Message, bot: Bot):
    if await subscription_checker.check_podpisku(bot, message.from_user.id):
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name or "Не указано"

        profile_text = f"""
Ваш профиль:
ID: {user_id}
Username: @{username or "Отсутствует"}
Nickname: {first_name} {last_name}

"""
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=profile_text, parse_mode="HTML", reply_markup=kb.inlines)

    else:
        await message.reply("Для использования бота, пожалуйста, подпишитесь на канал @pavel")


@router.callback_query(F.data == 'adminpanel')
async def admin_panel_callback(query: CallbackQuery, bot: Bot):
    if is_admin(query.from_user.id):

        await query.message.reply("Добро пожаловать администратор, здесь собраны все удобные инструменты для управления"
                                  " вашим ботом!", reply_markup=kb.adminpanel)
    else:

        await query.answer("Вы не являетесь администратором бота", show_alert=True)
    await query.answer()


@router.callback_query(F.data == 'add_channel')
async def add_channel_callback(query: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(AdminPanelStates.waiting_for_channel_to_add)
    await query.message.reply("Введите ID канала, который хотите добавить:")
    await query.answer()


@router.callback_query(F.data == 'remove_channel')
async def remove_channel_callback(query: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(AdminPanelStates.waiting_for_channel_to_remove)
    await query.message.reply("Введите ID канала, который хотите удалить:")
    await query.answer()


@router.message(AdminPanelStates.waiting_for_channel_to_add, F.from_user.id.in_(ADMIN_IDS))
async def process_add_channel(message: Message, bot: Bot, state: FSMContext):
    try:
        channel_id = message.text
        SUBSCRIPTION_CHANNELS.append(channel_id)
        subscription_checker.channels = SUBSCRIPTION_CHANNELS
        await message.reply(f"Канал {channel_id} добавлен в список обязательных для подписки.")
    except Exception as e:
        await message.reply(f"Произошла ошибка при добавлении канала: {e}")
    finally:
        await state.clear()


@router.message(AdminPanelStates.waiting_for_channel_to_remove, F.from_user.id.in_(ADMIN_IDS))
async def process_remove_channel(message: Message, bot: Bot, state: FSMContext):
    try:
        channel_id = message.text
        if channel_id in SUBSCRIPTION_CHANNELS:
            SUBSCRIPTION_CHANNELS.remove(channel_id)
            subscription_checker.channels = SUBSCRIPTION_CHANNELS
            await message.reply(f"Канал {channel_id} удален из списка обязательных для подписки.")
        else:
            await message.reply(f"Канал {channel_id} не найден в списке обязательных для подписки.")
    except Exception as e:
        await message.reply(f"Произошла ошибка при удалении канала: {e}")
    finally:
        await state.clear()


@router.message(F.text, ~F.state)
async def echo_message(message: types.Message, bot: Bot) -> None:
    if await subscription_checker.check_podpisku(bot, message.from_user.id):

        waiting_message = await message.reply("Ваш запрос обрабатывается, ожидайте...")

        try:
            user_message = message.text
            gpt_response = await get_gpt_otvet(user_message)

            await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=gpt_response)

        finally:

            await bot.delete_message(chat_id=message.chat.id, message_id=waiting_message.message_id)
    else:
        await message.reply("Для использования бота, пожалуйста, подпишитесь на канал @pavel")

