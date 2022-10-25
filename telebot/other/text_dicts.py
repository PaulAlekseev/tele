

main_menu_text = {
    ':Russia: Русский': {
        'greeting': ':open_book: Главное меню',
        'keyboard': [
            ':bust_in_silhouette: Профиль',
            ':check_mark_button: Активировать аккаунт',
            ':brain: О боте',
            ':SOS_button: Поддержка',
            ':reverse_button: Назад к выбору языка'
        ]
    },
    ':United_States: English': {
        'greeting': ":open_book: Main menu",
        'keyboard': [
            ':bust_in_silhouette: Profile',
            ':check_mark_button: Activate account',
            ':brain: About',
            ':SOS_button: Support',
            ':reverse_button: Back to languages'
        ]
}
}

scan_text = {
    'Скан': {
        'text': {
            'good': 'Ваш файл готов к сканированию',
            'bad': 'Для сканирования требуется активация аккаунта'
        },
        'button': {
            'good': 'scan_start_ru',
            'bad': 'activation_ru'
        },
        'start': 'Начать сканирование',
        'no_activation': 'Активировать аккаунт',
    },
    'Scan': {
        'text': {
            'good': 'Your file ready for scanning',
            'bad': 'You need to activate your account for that'
        },
        'button': {
            'good': 'scan_start_en',
            'bad': 'activation_en'
        },
        'start': 'Start scanning',
        'no_activation': 'Activate account',
    }
}


activation_text = {
    'activation_en': 'Your account has been successfully activated for 30 days',
    'activation_ru': 'Ваш профиль был активирован на 30 дней'
}


profile_text = {
    ':bust_in_silhouette: Profile': {
        'text': '''Your id: {0}
Status:{1}
Activation expires:{2}''',
        'active': {
            'good': 'Активирован',
            'bad': 'Не активирован'
        }
    },
    ':bust_in_silhouette: Профиль': {
        'text': '''Ваш id: {0}
Статус: {1}
Активация заканчивается: {2}''',
        'active': {
            'good': 'Active',
            'bad': 'Not active'
        }
    }
}