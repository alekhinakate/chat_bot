import contains as keys
import telebot
import random
import urllib.request
import json
import requests
import logging
import hashlib
import time
from google.cloud import speech
import io
import pandas as pd

bot = telebot.TeleBot(keys.API_KEY)

print("Bot started...")

#краткая инструкция для пользователя
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.from_user.id, 'When you press /topic, I’ll send you a message that you need to record your conversation for a few minutes. After that, I’ll send you my feedback.')


#бот выбирает рандомную тему(topic) из списка тем
@bot.message_handler(commands=['topic'])
def send_topic(message):
    topics = open('/Users/kataalehina/Documents/projects/chat_bot/topics.txt').readlines()
    bot.send_message(message.from_user.id, random.choice(topics).strip())


#бот принимает аудио файл на вход, обрабатывает его с помощью speechkit и дает свой фитбек
@bot.message_handler(content_types=["voice"])
def handle_audio_messages(message):
    #достаю файл нужного формата
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('file.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)
    
    new_file = open('file.ogg', 'rb')
    content = new_file.read()

    #связь с google.speechkit
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=48000,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)

    #проверяю не пустой или файл(возможно бот ничего не понял)
    if not len(response.results):
        print("эть эть эть эть ВВЭЭННН")
        bot.send_message(message.from_user.id, "I don't understand you, please repeat.")

    #словарь со всеми словами, которые разобрал бот    
    words = set(['hello', 'hello'])
    bot.send_message(message.from_user.id, "This is what I heard: ")
    for result in response.results:
        res = result.alternatives[0].transcript
        tmp = set(str(res).split())
        words = words.union(tmp)
        bot.send_message(message.from_user.id, str(res))

    #словарь слов с их эмбеддингами    
    dictionary = {}
    data = pd.read_csv('lemma.txt', header = None)
    for i in range (6318):
        dictionary[((data[0][i]).split())[2]] = (data[0][i]).split()[0]
    
    #ищу всю сумму слов, максимальное слово и среднее. Оцениваю по среднему и максимальному
    average = 0
    maximum = 0
    summary = 0
    leng = 0
    for word in words:
        if (word in dictionary):
            summary += int(dictionary[word])
            leng += 1
            if (int(dictionary[word]) > maximum):
                maximum = int(dictionary[word])
    average = summary / leng
    #фитбек, который можно было бы улучшить (взять более точные цифры, давать более расширенные рекомендации), но пока так
    print("summary:", summary, ", average:", average, ", maximum:", maximum)
    if (average > 2000):
        bot.send_message(message.from_user.id, "You have excellent knowledge, you are completely ready for passing the exam, сongratulations!")
    elif (average > 1000 or maximum > 4000):
        bot.send_message(message.from_user.id, "Your vocabulary is a little lower than necessary, but you are on the right track.")
    else:
        bot.send_message(message.from_user.id, "I see that you know the language, but your level is still far from the desired one. I advise you to practice more and learn new words.")

#с текстовыми сообщениями бот не работает
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, "Unfortunately, I can't read and reply to messages, because I'm just an insensitive machine...")

bot.polling(none_stop=True)
