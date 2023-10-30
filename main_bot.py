import logging
from threading import Thread
from time import sleep

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from ad import get_ids_from_ad
from reqs import BOT_TOKEN
from support import create_new_issue, get_project_managers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s")

# Создаем объекты бота и диспетчера
bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher()

# Словарь, в котором будут храниться данные пользователя
allow_ids = {}
users_dict = {}

users_from_project = {}


@dp.message(lambda x: str(x.from_user.id) not in allow_ids, Command("start"))
async def message_not_in_allowed(message: Message):
    global allow_ids
    users_dict[message.from_user.id] = {}
    logging.warning(
        f'User ID {message.from_user.id}:{message.from_user.username} {message.from_user.first_name}:'
        f'{message.from_user.last_name} not in ALLOWED')
    await message.reply("Я тебя не знаю, пройди аутентификацю у @sds_corp_bot, и возвращайся!")


class Get_info_for_issue(StatesGroup):
    typing_subject = State()
    typing_description = State()
    choosing_user_for_issue = State()


@dp.message(lambda x: str(x.from_user.id) in allow_ids, Command("start"))
async def message_start(message: Message, state: FSMContext):
    users_dict[message.from_user.id] = {}
    await state.clear()
    await message.answer('Напишите <b>тему</b> задачи, до 255 символов.', parse_mode="HTML")
    await state.set_state(Get_info_for_issue.typing_subject)


@dp.message(Command(commands=["cancel"]))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    users_dict[message.from_user.id] = {}
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(Get_info_for_issue.typing_subject)
async def typing_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    users_dict[message.from_user.id]['subject'] = message.text
    await message.answer(
        text="Теперь, пожалуйста, введи описание к задаче:")
    await state.set_state(Get_info_for_issue.typing_description)


@dp.message(Get_info_for_issue.typing_description)
async def typing_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    users_dict[message.from_user.id]['text'] = message.text
    await message.answer(
        text="Теперь выбери исполнителя твоей задачи:",
        reply_markup=make_row_keyboard(users_from_project)
    )
    await state.set_state(Get_info_for_issue.choosing_user_for_issue)


@dp.message(Get_info_for_issue.choosing_user_for_issue)
async def choosing_user(message: Message, state: FSMContext):
    await state.update_data(user=message.text)
    users_dict[message.from_user.id]['user'] = message.text
    await message.answer('Завожу задачу, подожди.')
    users_dict[message.from_user.id]['uri_issue'] = create_new_issue(
        subject=users_dict[message.from_user.id]['subject'][:254],
        description=users_dict[message.from_user.id]['text'],
        username=users_from_project[users_dict[message.from_user.id]['user']],
        author_issue=allow_ids[str(message.from_user.id)])

    await message.answer(
        text=f"Спасибо. Вот ссылка на твою задачу:\n"
             f"{users_dict[message.from_user.id]['uri_issue']}",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
    users_dict[message.from_user.id] = {}


def update_allow_ids():
    global allow_ids, users_from_project
    while True:
        try:
            allow_ids = get_ids_from_ad()
            users_from_project = get_project_managers()
            sleep(2)
            # print(allow_ids)
            logging.debug(f'allow_ids обновлен\n{allow_ids}')
        except Exception as e:
            logging.critical(e, exc_info=True)


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


if __name__ == '__main__':
    # asyncio.run(update_allow_ids())
    updating_IDS = Thread(target=update_allow_ids, args=(), daemon=True)
    updating_IDS.start()
    dp.run_polling(bot)
