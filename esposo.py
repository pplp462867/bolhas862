import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import threading
import time
import json
import os

TOKEN = "7580064216:AAEmKr-fVQ0NYqfcOVPkwY_y4h6XTjYRvCg"
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "task_data_botrafo.json"  # Arquivo para armazenar os dados

task_scores = {
    "1": ("Escrever partituras (Jazz)", 2),
    "2": ("Estudos", 3),
    "3": ("Desenho Fusion/Solid", 2),
    "4": ("Estudar Programação", 1),
    "5": ("Idioma (🇩🇪🇮🇹🇪🇸)", 1),
    "6": ("Anki Genérico/HB", 1),
    "7": ("Exercício Físico", 1),
    "8": ("Piano", 1),
    "9": ("Progresso IC/PAD/Aula", 1),
    "10": ("Refeição Saudável", 0.5),
    "11": ("Leitura", 0.5),
    "12": ("Grind absoluta da carta", 1)
}

# Funções para carregar e salvar dados
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Carregar dados existentes
user_tasks = load_data()

def generate_task_list(chat_id):
    date_str = datetime.datetime.now().strftime("%d/%m/%Y")
    if chat_id not in user_tasks:
        user_tasks[chat_id] = {key: False for key in task_scores.keys()}

    task_list = f"📅 ★Lista de Tarefas - {date_str}★\n"
    total_points = sum(task_scores[key][1] for key, completed in user_tasks[chat_id].items() if completed)

    for key, (task, points) in task_scores.items():
        checkmark = "✅" if user_tasks[chat_id][key] else "⬜"
        task_list += f"{checkmark} *({key}) {task}* — [{points:.1f} pts]\n"

    task_list += f"\n🏆 Pontuação Diária : {total_points:.1f}/15 pts"

    save_data(user_tasks)  # Salvar a cada atualização
    return task_list

@bot.message_handler(commands=["botrafo"])
def start(message):
    chat_id = str(message.chat.id)
    if chat_id not in user_tasks:
        user_tasks[chat_id] = {key: False for key in task_scores.keys()}

    keyboard = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(str(i), callback_data=str(i)) for i in task_scores.keys()]
    keyboard.add(*buttons)

    bot.send_message(chat_id, generate_task_list(chat_id), reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in task_scores.keys())
def handle_reaction(call):
    chat_id = str(call.message.chat.id)
    task_id = call.data

    user_tasks[chat_id][task_id] = not user_tasks[chat_id][task_id]  # Alterna entre concluído e não concluído
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=generate_task_list(chat_id), reply_markup=call.message.reply_markup)

    save_data(user_tasks)  # Salvar após cada modificação

print("Bot rodando...")
bot.polling(none_stop=True)
