from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                            ConversationHandler, PicklePersistence)

import logging 

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s -%(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Age', 'Favourite Colour'],
                    ['Number of siblings', 'Something else...'],
                    ['Done']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))
    
    return "\n".join(facts).join(['\n', '\n'])

def start(update, context):
    reply_text = "Hi! My name is Doctor Botter."
    if context.user_data:
        reply_text += " You already told me your {}. Why don`t you tell me something more " \
                      "about yourself? Or change anything I "\
                      "already know.".format(", ".join(context.user_data.keys()))
    else:
        reply_text += " I will hold a more complex conversatino with you. Why don`t you tell me " \
                      "something about yourself?"
    update.message.reply_text(reply_text, reply_markup=markup)

    return CHOOSING

def regular_choice(update, context):
    text = update.message.text.lower()
    context.user_data['choice'] = text
    if context.user_data.get(text):
        reply_text = 'Your {}, I already know the following ' \
                    'about that: {}'.format(text, context.user_data[text])
    else:
        reply_text = 'Your {}? Yes, I would love to hear about that!'.format(text)
    update.message.reply_text(reply_text)

    return TYPING_REPLY

def custom_choice(update, context):
    update.message.reply_text('Alright, please send me the category first, '
                                'for example "Most impressive skill"')
    return TYPING_CHOICE

def received_information(update, context):
    text = update.message.text
    category = context.user_data['choice']
    context.user_data[category] = text.lower()
    del context.user_data['choice']

    update.message.reply_text("Neat! Just so you know, this is what you already told me:"
                                "{}"
                                "You can tell me more, or change your opinion on"
                                "something.".format(facts_to_str(context.user_data)),
                                reply_markup=markup)
    return CHOOSING

def show_data(update, context):
    update.message.reply_text("This is what you already told me:"
                                "{}".format(facts_to_str(context.user_data)))

def done(update, context):
    if 'choice' in context.user_data:
        del context.user_data['choice']

    update.message.reply_text("I learned these facts about you:"
                                "{}"
                                "Until next time!".format(facts_to_str(context.user_data)))
    return ConversationHandler.END

def error(update, context):
    "Log errors caused by updates"
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it to your bots Token.
    pp = PicklePersistence(filename='conversationAIbot')
    updater = Updater("1082763394:AAHGpcIg_W0CEaToU4M96Pv0y4VCJDTw_4s", persistence=pp, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Age|Favourite colour|Number of siblings)$'),
                            regular_choice),
                       MessageHandler(Filters.regex('^Something else...$'),
                                        custom_choice),
                        ],
            TYPING_CHOICE: [MessageHandler(Filters.text,
                                            regular_choice),
                        ],
            TYPING_REPLY: [MessageHandler(Filters.text,
                                            received_information),
                            ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
        name="my_conversation",
        persistent=True
    )

    dp.add_handler(conv_handler)

    show_data_handler = CommandHandler('show_data', show_data)
    dp.add_handler(show_data_handler)
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run till stopped
    updater.idle()




if __name__ == '__main__':
    main()

