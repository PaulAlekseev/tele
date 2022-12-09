import os

main_menu_text = {
    ':Russia: Русский': {
        'greeting': ':open_book: Главное меню',
        'instructions': """Здравствуйте. 
На время тестирования бота все услуги предоставляются бесплатно. 
Для создания учетной записи нажмите кнопку “Активация”
Для проверки возможности доступа к ресурсам , вам необходимо сформировать список в файле .txt
Формат списка: путь к файлу|адрес сайта:порт|логин|пароль
Пример: C:\Cpanel\Check\passwords.txt| https://cpanel.check:2083|login|pass
Вы можете использовать наше программное обеспечение для формирования списка: ссылка
Для использования необходимо указать папку с распакованным материалом и указать место и имя файла для сохранения готового списка.
Программное обеспечение не содержит вирусов и вредоносного кода.
Загрузить файл со списком в бота  и в комментариях написать  Scan.
Максимальное количество строк за одну сессию 10000.
Через непродолжительное время бот выдаст вам файл с результатом сканирования.""",
        'keyboard': [
            ':bust_in_silhouette: Профиль',
            ':key: Активировать',
            ':brain: Правила',
            ':SOS_button: Поддержка',
            ':reverse_button: Назад к выбору языка'
        ]
    },
    ':United_States: English': {
        'greeting': ":open_book: Main menu",
        'instructions': """Hello. 
All services are free for the time of bot testing. 
To create an account, click ”Activate”.
To test the possibility of access to resources, you need to generate a list in a .txt file
The format of the list: file path|address:port|login|password
Example: C:\Cpanel\Check\passwords.txt| https://cpanel.check:2083|login|pass
You can use our software to generate a list: link
To use it you need to specify the folder with the unpacked material and specify the place and name of the file to save the finished list.
The software does not contain viruses and malicious code.
Then you need to upload the file with the list into the bot and write Scan in the comments.
The maximum number of lines per session is 10000.
After a short time the bot will give you a file with the result of scanning.""",
        'keyboard': [
            ':bust_in_silhouette: Profile',
            ':key: Activate',
            ':brain: Rules',
            ':SOS_button: Support',
            ':reverse_button: Back to languages'
        ]
}
}

scan_text = {
    'Скан': {
        'text': {
            'good': 'Ваш файл был добавлен в очередь сканирования, у вас {0} сканирований на сегодня',
            'bad': 'Для сканирования требуется активация аккаунта'
        },
        'button': {
            'good': 'scan_start_ru',
            'bad': 'activation_ru'
        },
        'start': 'Начать сканирование',
        'no_activation': 'Активировать аккаунт',
        'scan': 'Ваш файл успешно прошел сканирование, в итоге у вас осталось {0} сканирований на сегодня',
        'activation_failure': ["К сожалению лимит сканирования на сегодня для вас закончился",
                               "К сожалению лимит сканирования в этом месяце для вас закончился"]
},
    'Scan': {
        'text': {
            'good': 'Your file has been added to the queue, you got {0} scans left for today',
            'bad': 'You need to activate your account for that'
        },
        'button': {
            'good': 'scan_start_en',
            'bad': 'activation_en'
        },
        'start': 'Start scanning',
        'no_activation': 'Activate account',
        'scan': 'We successfully scanned your file, you have {0} scans for today',
        'activation_failure': ["Sorry, but you're out of scans for today",
                               "Sorry, but you're out of scans for this month"]
    }
}


activation_text = {
    'activation_en': {
        'good': 'Your account has been successfully activated',
        'bad': 'Your account is already activated',
    },
    'activation_ru': {
        'good': 'Ваш профиль был активирован на дней',
        'bad': 'Ваш аккаунт уже активирован',
    },
    ':check_mark_button: Активировать аккаунт': None,
    ':check_mark_button: Activate account': None
}


profile_text = {
    ':bust_in_silhouette: Profile': {
        'text': ''':key: Your id: {0}
:briefcase: Status: {1}
:spiral_calendar: Activation expires: {2}''',
        'active': {
            'good': 'Active',
            'bad': 'Not active'
        }
    },
    ':bust_in_silhouette: Профиль': {
        'text': ''':key: Ваш id: {0}
:briefcase: Статус: {1}
:spiral_calendar: Активация заканчивается: {2}''',
        'active': {
            'good': 'Активирован',
            'bad': 'Не активирован'
        }
    }
}


activation_tariffs_text = {
    ':key: Активировать': {
        'lang': 'rus',
        'text': 'Выберите из доступных тарифов'
    },
    ':key: Activate': {
        'lang': 'eng',
        'text': 'Choose between available tariffs',
    }
}


crypto_payment_choice = {
    'eng': {
        'text': 'Choose between available payment methods'
    },
    'rus': {
        'text': 'Выберите между доступных методов оплаты'
    }
}

available_crypto = {
    'BTC': {
        'API-key': os.getenv('BITCOIN_KEY'),
        'password': os.getenv('BITCOIN_PASSWORD')
    },
    'TCN': {
        'API-key': os.getenv('TCN_KEY'),
        'password': os.getenv('TCN_PASSWORD')
    },
    'QIWI': {
        'API-key': os.getenv('QIWI_KEY'),
    }
}


crypto_payment_start_choice = {
    'rus': {
        'fail_text': 'Данный тариф устарел.'
    },
    'eng': {
        'fail_text': 'This tariff is outdated.'
    }
}


support_text = {
    ':SOS_button: Support': {
        'text': 'Support @SMTPGod',
    },
    ':SOS_button: Поддержка': {
        'text': 'Саппорт @SMTPGod',
    }
}

rules_text = {
    ':brain: Rules': {
        'text': """The administration is not responsible for the materials used and your actions.
    In case of necessity or wrongful actions on the part of the user, the administration has the right to deny access to this user.
    By using the bot, you automatically agree to the rules of use.
    Administration is always ready to help you in any matter.""",
    },
    ':brain: Правила': {
        'text': """Администрация не несет ответственности за использованные материалы и ваши действия.
В случае необходимости или неправомерных действий со стороны пользователя, администрация вправе отказать в доступе данному пользователю.
Используя бота, вы автоматически соглашаетесь с правилами использования.
Администрация всегда готова помочь вам в любом вопросе.""",
    }
}


admin_help_text = {
    'text': """Команды админа:
 - date
Возвращает текстовый файл с удачными аккаунтами за заданныйм промежуток времени
Формат записи:
/date ДД.ММ.ГГГГ-ДД.ММ.ГГГГ
Пример записи:
/date 01.01.2022-02.01.2022

 - send
Отправляет сообщение всем зарегистрированным пользователям
Формат записи:
/send message
Пример записи:
/send Какое-то сообщение

 - create_type
Создает тариф активации
Формат записи:
/create_type (стоимость тарифа) (разовое ограничение) (дневное ограничение) (ограничение на месяц)
Пример записи:
/create_type 10 100 1000 100000

 - types
Возвращает все АКТИВНЫЕ тарифы
Формат записи:
/types

 - types_all
Возвращает ВСЕ тарифы
Формат записи:
/types_all

 - activate
Активирует тариф
Формат записи:
/activate (айдишник тарифа)
Пример записи:
/activate 1

 - deactivate
Деактивирует тариф
Формат записи:
/deactivate (айдишник тарифа)
Пример записи:
/deactivate 1

 - statistics
Возвращает такстовый файл со статистикой сканирования по пользователям
Формат записи:
/statistics

 - activate_user
Активирует тариф
Формат записи:
/activate_user (айдишник пользователя) (одиночное ограничение) (ограничение на день) (ограничение на месяц)
Пример записи:
/activate_user 123456789 10 100 10000
    """
}


activate_text_dict = {
    ':key: Активировать': 'activation_ru',
    ':key: Activate': 'activation_en',
}