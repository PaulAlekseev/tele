

main_menu_text = {
    ':Russia: Русский': {
        'greeting': ':open_book: Главное меню',
        'instructions': 'Какие-то инструкции',
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
        'instructions': 'Some instructions',
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
        'activation_failure': "К сожалению лимит сканирования на сегодня для вас закончился"
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
        'activation_failure': "Sorry, but you're out of the checks for today"
    }
}


activation_text = {
    'activation_en': 'Your account has been successfully activated for 30 days',
    'activation_ru': 'Ваш профиль был активирован на 30 дней',
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

available_crypto = [
    'BTC',
    'TCN'
]


support_text = {
    ':SOS_button: Support': {
        'text': 'Some support @some_support',
    },
    ':SOS_button: Поддержка': {
        'text': 'Саппорт @some_support',
    }
}

rules_text = {
    ':SOS_button: Support': {
        'text': 'Some rules',
    },
    ':SOS_button: Поддержка': {
        'text': 'Какие-то правила',
    }
}
