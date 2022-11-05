

main_menu_text = {
    ':Russia: Русский': {
        'greeting': ':open_book: Главное меню',
        'keyboard': [
            ':bust_in_silhouette: Профиль',
            ':key: Активировать',
            ':brain: О боте',
            ':SOS_button: Поддержка',
            ':reverse_button: Назад к выбору языка'
        ]
    },
    ':United_States: English': {
        'greeting': ":open_book: Main menu",
        'keyboard': [
            ':bust_in_silhouette: Profile',
            ':key: Activate',
            ':brain: About',
            ':SOS_button: Support',
            ':reverse_button: Back to languages'
        ]
}
}

scan_text = {
    'Скан': {
        'text': {
            'good': 'Ваш файл был отправлен на сканирование',
            'bad': 'Для сканирования требуется активация аккаунта'
        },
        'button': {
            'good': 'scan_start_ru',
            'bad': 'activation_ru'
        },
        'start': 'Начать сканирование',
        'no_activation': 'Активировать аккаунт',
        'scan': 'Ваш файл успешно прошел сканирование'
    },
    'Scan': {
        'text': {
            'good': 'We started scanning your file',
            'bad': 'You need to activate your account for that'
        },
        'button': {
            'good': 'scan_start_en',
            'bad': 'activation_en'
        },
        'start': 'Start scanning',
        'no_activation': 'Activate account',
        'scan': 'We successfully scanned your file'
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