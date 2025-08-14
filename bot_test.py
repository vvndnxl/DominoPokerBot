import telebot
from telebot import types
from random import randint
from time import sleep

bot = telebot.TeleBot("")


# noinspection PyTypeChecker
class Lobby:
    def __init__(self, lobby_id, password, winner):
        self.lobby_id = lobby_id
        self.password = password
        self.winner = winner

        self.players = []
        self.game_structure = []
        self.custom_structure = []
        # self.score_screen: types.Message = None
        self.score_table = ""
        self.board = ""
        self.dark_stage = -1
        self.custom_dark_stage = -1

        self.game_started = False
        self.game_ended = False
        self.wait_flag = False
        self.dark_flag = False


# noinspection PyTypeChecker
class Player:
    def __init__(self, chat_id, name):
        self.name = name
        self.chat_id = chat_id
        self.lobby: Lobby = None

        self.hands = []
        self.score = 0

        self.current_hand = []
        self.current_bet = -1
        self.current_beats = 0
        self.current_move = "sup"

        self.restart_request = False
        self.join_request = False
        self.bet_request = False
        self.move_request = False
        self.custom_structure_request = False

        self.screen = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.hand_screen: types.Message = None
        self.board_screen: types.Message = None
        self.score_screen: types.Message = None


great_restart = False
s = []
for i in range(7):
    for j in range(i, 7):
        s += [f"({i} {j})"]
lobby_1_password = "0000"
lobbies = []
all_players = {}
zero_one = '(0 1)'
# domino_value = {'sup': -1, '(0, 1) as low': 0, '(0, 2)': 1, '(1, 2)': 2, '(0, 3)': 3, '(1, 3)': 4, '(0, 4)': 5,
#                 '(2, 3)': 6, '(1, 4)': 7, '(0, 5)': 8, '(2, 4)': 9, '(1, 5)': 10, '(0, 6)': 11, '(3, 4)': 12,
#                 '(2, 5)': 13, '(1, 6)': 14, '(3, 5)': 15, '(2, 6)': 16, '(4, 5)': 17, '(3, 6)': 18, '(4, 6)': 19,
#                 '(5, 6)': 20, '(1, 1)': 21, '(2, 2)': 22, '(3, 3)': 23, '(4, 4)': 24, '(5, 5)': 25, '(6, 6)': 26,
#                 '(0, 0)': 27, '(0, 1)': 28}
domino_value = {'sup': -1, '(0 1) as low': 0, '(0 2)': 1, '(1 2)': 2, '(0 3)': 3, '(1 3)': 4, '(0 4)': 5, '(2 3)': 6,
                '(1 4)': 7, '(0 5)': 8, '(2 4)': 9, '(1 5)': 10, '(0 6)': 11, '(3 4)': 12, '(2 5)': 13, '(1 6)': 14,
                '(3 5)': 15, '(2 6)': 16, '(4 5)': 17, '(3 6)': 18, '(4 6)': 19, '(5 6)': 20, '(1 1)': 21, '(2 2)': 22,
                '(3 3)': 23, '(4 4)': 24, '(5 5)': 25, '(6 6)': 26, '(0 0)': 27, '(0 1)': 28}


def wait(lobby):
    global great_restart
    while not lobby.wait_flag:
        sleep(0.5)
    if great_restart:
        lobby.wait_flag = False
        great_restart = False
        return True
    lobby.wait_flag = False
    return False


# def error_catcher(chat_id):
#     try:
#         return all_players[chat_id] is not None
#     except KeyError:
#         bot.send_message(chat_id, text="message can't be processed")
#         return False


def dealing(players_count, n):
    dominoes = s[::]
    local_results = [[] for _ in range(players_count)]
    for _ in range(players_count):
        for __ in range(n):
            local_results[_].append(dominoes.pop(randint(0, len(dominoes) - 1)))
        if zero_one in local_results[_]:
            local_results[_].append(zero_one + ' as low')
    return local_results


def make_game(lobby):
    players_count = len(lobby.players)
    if lobby.custom_structure == ["turbo"]:
        lobby.game_structure = [_ for _ in range(1, 7)] + [7 for _ in range(len(lobby.players) * 2)]
        lobby.dark_stage = 7 + len(lobby.players)
    elif lobby.custom_structure:
        lobby.game_structure = lobby.custom_structure[::]
        lobby.dark_stage = lobby.custom_dark_stage
    else:
        lobby.game_structure = \
            [_ // players_count for _ in range(players_count, 8 * players_count)] + \
            [_ // players_count for _ in range(7 * players_count, players_count - 1, -1)] + \
            [7 for _ in range(players_count * 2)]
        lobby.dark_stage = 13 * players_count + 1
    for _ in lobby.game_structure:
        results = dealing(players_count, _)
        # print(results)
        for __ in range(players_count):
            # print(results[__], "*")
            lobby.players[__].hands.append(results[__])
            # print(lobby.players[__].name, lobby.players[__].hands)
    # print(lobby.players[0].hands, "*")
    # print(lobby.players[1].hands, "*")


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("/join_lobby"))
    markup.add(types.KeyboardButton("/create_lobby"))
    # markup.add(types.KeyboardButton("/rejoin_lobby"))
    bot.send_message(message.chat.id, text="Bot started", reply_markup=markup)


@bot.message_handler(commands=['restart_bot'])
def restart(message):
    global lobbies, all_players, great_restart
    if message.chat.id == 971385328:
        great_restart = True
        for _ in lobbies:
            _.winner = None
            for __ in _.players:
                __ = None
            _.players = None
            _ = None
        for _ in all_players.values():
            _.lobby = None
            _ = None
        lobbies = []
        all_players = {}
        # for obj in gc.get_objects():
        #     if isinstance(obj, Lobby):
        #         obj = None
        # for obj in gc.get_objects():
        #     if isinstance(obj, Player):
        #         obj = None


@bot.message_handler(commands=['create_lobby'])
def lobby_maker(message):
    if message.chat.id in all_players.keys() and all_players[message.chat.id].lobby is not None:
        return
    all_players[message.chat.id] = Player(message.chat.id, message.chat.first_name)
    lobbies.append(Lobby(str(len(lobbies) + 1), lobby_1_password, all_players[message.chat.id]))
    lobbies[-1].players.append(all_players[message.chat.id])
    all_players[message.chat.id].lobby = lobbies[-1]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/start_game")
    btn2 = types.KeyboardButton("/delete_lobby")
    btn3 = types.KeyboardButton("/customize_game_structure")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, text=f"lobby #{len(lobbies)} created", reply_markup=markup)


@bot.message_handler(func=lambda message: message.chat.id in all_players.keys() and
                                          message.text == '/customize_game_structure' and
                                          not all_players[message.chat.id].lobby.game_started)
def game_structure_editor(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/turbo_structure")
    btn2 = types.KeyboardButton("/custom_structure")
    markup.add(btn1, btn2)
    all_players[message.chat.id].screen = markup
    bot.send_message(message.chat.id, text=f"Choose game structure", reply_markup=markup)


@bot.message_handler(func=lambda message: message.chat.id in all_players.keys() and
                                          message.text == "/turbo_structure" and
                                          not all_players[message.chat.id].lobby.game_started)
def turbo_structure_setter(message):
    all_players[message.chat.id].lobby.custom_structure = ["turbo"]


# noinspection SpellCheckingInspection
@bot.message_handler(func=lambda message: message.chat.id in all_players.keys() and
                                          message.text == "/custom_structure" and
                                          not all_players[message.chat.id].lobby.game_started)
def custom_structure_editor(message):
    bot.send_message(message.chat.id, text=" Send a list of rounds. Use this format:")
    # bot.send_message(message.chat.id, text="1\n2\n3\n4\n5\n6\n7\n7\n7\n7\n\ndark rounds: 2")
    bot.send_message(message.chat.id, text="12345677-77")
    all_players[message.chat.id].custom_structure_request = True


@bot.message_handler(func=lambda message: message.chat.id in all_players.keys() and
                                          all_players[message.chat.id].custom_structure_request and
                                          message.text[0].isdigit() and
                                          not all_players[message.chat.id].lobby.game_started)
def custom_structure_getter(message):
    game_structure = ""
    data = message.text
    dark_stage = -1
    for _ in data:
        if _.isdigit():
            game_structure += _
        elif _ == "-":
            dark_stage = len(game_structure)
        else:
            break
    all_players[message.chat.id].lobby.custom_structure = [int(_) for _ in game_structure]
    if dark_stage:
        all_players[message.chat.id].lobby.custom_dark_stage = dark_stage
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/start_game")
    btn2 = types.KeyboardButton("/delete_lobby")
    btn3 = types.KeyboardButton("/customize_game_structure")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id,
                     text=f"game structure was set to {game_structure[:dark_stage]}-{game_structure[dark_stage:]}",
                     reply_markup=markup)
    all_players[message.chat.id].custom_structure_request = False


@bot.message_handler(commands=['join_lobby'])
def join_lobby_requester(message):
    if message.chat.id in all_players.keys() and all_players[message.chat.id].lobby is not None:
        return
    all_players[message.chat.id] = Player(message.chat.id, message.chat.first_name)
    flag = True
    if len(lobbies) > 0:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for _ in range(len(lobbies)):
            if len(lobbies[_].players) < 4:
                markup.add("lobby #" + str(_ + 1))
                flag = False
        if flag:
            bot.send_message(message.chat.id, text="No lobbies found")
            return

        all_players[message.chat.id].join_request = True
        bot.send_message(message.chat.id, text="Choose lobby", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text="No lobbies found")


@bot.message_handler(
    func=lambda message: message.chat.id in all_players.keys() and
                         message.text in ["lobby #" + str(_ + 1) for _ in range(len(lobbies))] and
                         all_players[message.chat.id].join_request and not
                         lobbies[int(message.text[message.text.index("#") + 1:]) - 1].game_started)
def lobby_joiner(message):
    player = all_players[message.chat.id]
    lobby_number = int(message.text[message.text.index("#") + 1:]) - 1
    if len(lobbies[lobby_number].players) > 3:
        bot.send_message(message.chat.id, text=f"lobby #{lobby_number} is full")
        return
    for _ in lobbies[lobby_number].players:
        bot.send_message(_.chat_id, text=f"<{player.name}> joined to lobby #{lobby_number + 1}")
    lobbies[lobby_number].players.append(player)
    player.join_request = False
    player.lobby = lobbies[lobby_number]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("/leave_lobby"))
    bot.send_message(player.chat_id, text=f"<{player.name}> joined to lobby #{lobby_number + 1}", reply_markup=markup)
    player.screen = markup


@bot.message_handler(func=lambda message: message.chat.id in all_players.keys() and
                                          message.text == "/leave_lobby" and
                                          all_players[message.chat.id].lobby is not None and
                                          not all_players[message.chat.id].lobby.game_started)
def lobby_kicker(message):
    player = all_players[message.chat.id]
    lobby = player.lobby
    lobby.players.remove(player)
    player.lobby = None
    for _ in lobby.players:
        bot.send_message(_.chat_id, text=f"<{player.name}> left lobby")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/join_lobby")
    btn2 = types.KeyboardButton("/create_lobby")
    markup.add(btn1, btn2)
    bot.send_message(player.chat_id, text=f"<{player.name}> left lobby", reply_markup=markup)
    if not lobby.players:
        lobbies.remove(lobby)


# @bot.message_handler(commands=['rejoin_lobby'])
# def lobby_rejoiner(message):
#     if message.chat.id not in all_players.keys():
#         return
#     player = all_players[message.chat.id]
#     bot.send_message(player.chat_id, text=player.current_hand, reply_markup=player.screen)
    # bot.send_message(player.chat_id, text=player.lobby.score_screen.text)


def request_bet(player, hand_capacity, forbidden_bet=8):
    markup = types.InlineKeyboardMarkup()
    buttons = []
    for _ in range(hand_capacity + 1):
        if _ != forbidden_bet:
            buttons += [types.InlineKeyboardButton(str(_), callback_data=str(_))]
    for _ in range(0, len(buttons), 4):
        markup.keyboard.append(buttons[_:_ + 4])
    # player.screen = markup
    # bot.send_message(player.chat_id, text="your bet", reply_markup=markup)
    bot.edit_message_text(text=player.lobby.score_table, chat_id=player.chat_id, message_id=player.score_screen.id,
                          reply_markup=markup)

    bot.unpin_all_chat_messages(player.chat_id)
    if not player.lobby.dark_flag:
        hand = player.current_hand[::]
        if zero_one + ' as low' in hand:
            hand.remove(zero_one + ' as low')
        player.hand_screen = bot.send_message(player.chat_id, text=" ".join(str(hand)[2:-2].split("', '")))
    else:
        player.hand_screen = bot.send_message(player.chat_id, text="...")
    bot.pin_chat_message(player.chat_id, player.hand_screen.id, disable_notification=True)
    player.bet_request = True


# @bot.message_handler(
#     func=lambda message: all_players[message.chat.id].bet_request and
#                          message.text in [str(_) for _ in range(len(all_players[message.chat.id].current_hand) + 1)])
@bot.callback_query_handler(
    func=lambda call: call.data in [str(_) for _ in range(len(all_players[call.message.chat.id].current_hand) + 1)] and
                      all_players[call.message.chat.id].bet_request)
def bet_getter(call):
    message = call.message
    text = call.data
    # text = message.text
    player = all_players[message.chat.id]
    player.current_bet = int(text)
    player.bet_request = False
    player.lobby.wait_flag = True

    bot.answer_callback_query(call.id)


def request_move(player, first_move="sup"):
    # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup = types.InlineKeyboardMarkup()
    buttons = []
    previous_best_move = player.lobby.winner.current_move
    for _ in player.current_hand:
        if domino_value[_] > domino_value[previous_best_move]:
            buttons += [_]

    if (len(buttons) == 0) or (len(buttons) == 1 and buttons[0] == zero_one):
        buttons = []
        if first_move in (
                # "(2, 2)", "(3, 3)", "(4, 4)", "(5, 5)", "(6, 6)"
                "(2 2)", "(3 3)", "(4 4)", "(5 5)", "(6 6)"
        ):
            for _ in player.current_hand:
                if 20 < domino_value[_]:
                    buttons += [_]

        elif first_move in (zero_one,
                            # "(0, 0)",
                            '(0 0)'):
            for _ in player.current_hand:
                if 20 < domino_value[_]:
                    buttons += [_]
            if buttons:
                major_duple = "sup"
                for _ in buttons:
                    if domino_value[_] > domino_value[major_duple]:
                        major_duple = _
                buttons = [major_duple]

        if (len(buttons) == 0) or (len(buttons) == 1 and buttons[0] == zero_one):
            buttons = []
            for _ in player.current_hand:
                buttons += [_]

    markup_buttons = []
    for _ in buttons:
        markup_buttons += [types.InlineKeyboardButton(_, callback_data=_)]
    for _ in range(0, len(markup_buttons), 4):
        markup.keyboard.append(markup_buttons[_:_ + 4])
    player.screen = markup
    if previous_best_move == "sup":
        player.lobby.board = " $ your move"
        player.board_screen = bot.send_message(player.chat_id, text=player.lobby.board, reply_markup=markup)
        # bot.edit_message_text(text=player.hand_screen.text, chat_id=player.chat_id,
        #                       message_id=player.hand_screen.id, reply_markup=markup)
    else:
        if player.lobby.board.find("$") == -1:
            player.lobby.board = player.lobby.board + f"\n\n$ {previous_best_move} to beat"
        else:
            player.lobby.board = player.lobby.board[:player.lobby.board.find("$") - 1] + \
                                 f"\n\n$ {previous_best_move} to beat"
        # bot.send_message(player.chat_id, text=player.lobby.board, reply_markup=markup)
        bot.edit_message_text(text=player.lobby.board,
                              chat_id=player.chat_id, reply_markup=markup, message_id=player.board_screen.id)
        # bot.edit_message_text(text=player.hand_screen.text, chat_id=player.chat_id,
        #                       message_id=player.hand_screen.id, reply_markup=markup)
    player.move_request = True


# @bot.message_handler(func=lambda message: message.text in domino_value.keys() and message.text in all_players[
#                                           message.chat.id].current_hand and
#                                           all_players[message.chat.id].move_request)
# noinspection PyUnboundLocalVariable
@bot.callback_query_handler(
    func=lambda call: call.data in all_players[call.message.chat.id].current_hand and
                      all_players[call.message.chat.id].move_request)
def move_getter(call):
    message = call.message
    # text = message.text
    text = call.data
    player = all_players[message.chat.id]
    lobby = player.lobby
    if text in [zero_one, zero_one + " as low"]:
        player.current_hand.remove(zero_one)
        player.current_hand.remove(zero_one + " as low")
    else:
        player.current_hand.remove(text)
    hand = player.current_hand[::]
    if zero_one + ' as low' in hand:
        hand.remove(zero_one + ' as low')
    if not hand:
        hand = "......."
    if player.hand_screen.text != hand[2:5]:
        bot.edit_message_text(text=" ".join(str(hand)[2:-2].split("', '")), chat_id=player.chat_id,
                              message_id=player.hand_screen.id)
    player.current_move = text
    player.move_request = False

    # score_table = "__Scoring__"
    # for player_ in lobby.players:
    #     score_table += f"\n\n<{player_.name}>\n[{player_.score}]  {player.current_beats}/{player_.current_bet}"

    # if domino_value[player.current_move] > domino_value[lobby.winner.current_move]:  # beat or drop
    #     move = f"<{player.name}> beat {lobby.winner.current_move} with {player.current_move}"
    # elif domino_value[player.current_move] < domino_value[lobby.winner.current_move]:
    #     move = f"<{player.name}> dropped {player.current_move} against {lobby.winner.current_move}"
    # if domino_value[player.current_move] == domino_value[lobby.winner.current_move]:
    #     move = f"<{player.name}> move with {player.current_move}"
    #     bot.edit_message_text(text=move, chat_id=player.chat_id, message_id=player.main_screen.id)
    #     for _ in lobby.players:
    #         if player != _:
    #             _.main_screen = bot.send_message(text=move, chat_id=_.chat_id)
    # else:
    #     for _ in lobby.players:
    #         bot.edit_message_text(text=move, chat_id=_.chat_id, message_id=_.main_screen.id)

    if player.lobby.board.find("$") == -1:
        player.lobby.board = player.lobby.board + f"<{player.name}> move with {text}"
    else:
        player.lobby.board = player.lobby.board[:player.lobby.board.find("$") - 1] + \
                             f"<{player.name}> move with {text}"
    for _ in lobby.players:
        # if _._Player__board_screen is not None:
        # if _.board_screen is not None:
        if _.current_move != "sup":
            # print(_.main_screen.text)
            # bot.send_message(_.chat_id, text=f"<{player.name}> move with {player.current_move}")
            # print(_.main_screen.text)
            bot.edit_message_text(text=player.lobby.board, chat_id=_.chat_id, message_id=_.board_screen.id)
        else:
            _.board_screen = bot.send_message(text=player.lobby.board, chat_id=_.chat_id)

    if domino_value[player.current_move] > domino_value[lobby.winner.current_move]:
        lobby.winner = player
    # player.lobby.score_table = score_table
    # bot.clear_reply_handlers(message)
    player.screen = types.ReplyKeyboardMarkup(resize_keyboard=True)
    lobby.wait_flag = True

    bot.answer_callback_query(call.id)


def request_lobby_restart(lobby):
    lobby.game_ended = True
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/delete_lobby")
    btn2 = types.KeyboardButton("/restart_lobby")
    markup.add(btn1, btn2)
    for player in lobby.players:
        player.restart_request = True
        bot.send_message(player.chat_id, text="game finished", reply_markup=markup)
    wait(lobby)


@bot.message_handler(func=lambda message: message.chat.id in all_players.keys() and
                                          message.text == '/delete_lobby' and
                                          all_players[message.chat.id].lobby is not None and
                                          (all_players[message.chat.id].lobby.game_ended or
                                          not all_players[message.chat.id].lobby.game_started)
                     )
def lobby_deleter(message):
    lobby = all_players[message.chat.id].lobby
    if lobby.game_ended:
        lobby.wait_flag = True
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/join_lobby")
    btn2 = types.KeyboardButton("/create_lobby")
    markup.add(btn1, btn2)
    for _ in lobby.players:
        _.lobby = None
        bot.send_message(_.chat_id, text="lobby deleted", reply_markup=markup)
    lobbies.remove(lobby)


# noinspection PyTypeChecker
@bot.message_handler(func=lambda message: message.chat.id in all_players.keys() and
                                          message.text == '/restart_lobby' and
                                          all_players[message.chat.id].lobby.game_ended and
                                          all_players[message.chat.id].restart_request)
def lobby_restarter(message):
    player = all_players[message.chat.id]
    lobby = player.lobby
    player.restart_request = False
    for _ in lobby.players:
        bot.send_message(_.chat_id, text=f"<{player.name}> voted for restart\n"
                                         f"{sum([not _.restart_request for _ in lobby.players])}/"
                                         f"{len(lobby.players)} to restart")
    if sum([not _.restart_request for _ in lobby.players]) == len(lobby.players):
        # players = [_ for _ in player.lobby.players]
        # lobbies.remove(player.lobby)
        # lobbies.append(Lobby(str(len(lobbies) + 1), lobby_1_password, players[0]))
        # lobbies[-1].players = players
        # for _ in players:
        #     _.lobby = lobbies[-1]
        # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # btn1 = types.KeyboardButton("/start_game")
        # markup.add(btn1)
        # all_players[message.chat.id].screen = markup
        # bot.send_message(players[0], text="lobby restarted", reply_markup=markup)
        lobby.game_started = False
        lobby.game_ended = False
        lobby.dark_flag = False
        for _ in lobby.players:
            _.hands = []
            _.score = 0

            _.current_hand = []
            _.current_bet = -1
            _.current_beats = 0
            _.current_move = "sup"

            _.hand_screen = None
            _.board_screen = None
            _.score_screen = None

            _.restart_request = False

        lobby.wait_flag = True
        game_runner(message)


@bot.message_handler(func=lambda message: message.chat.id in all_players.keys() and
                                          all_players[message.chat.id].lobby is not None and
                                          all_players[message.chat.id].lobby.game_started)
def messenger(message):
    player = all_players[message.chat.id]
    lobby = player.lobby
    for _ in lobby.players:
        if _ != player:
            bot.send_message(_.chat_id, text=f"<{player.name}>: {message.text}")


# noinspection PyUnresolvedReferences
@bot.message_handler(commands=['start_game'])
def game_runner(message):
    if message.chat.id not in all_players.keys():
        return
    lobby = all_players[message.chat.id].lobby
    players_count = len(lobby.players)
    if players_count > 4:
        return
    make_game(lobby)
    lobby.game_started = True
    for _ in lobby.players:
        bot.send_message(_.chat_id, text="game started", reply_markup=types.ReplyKeyboardRemove())
        _.screen = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # bot.clear_reply_handlers(message)
    for Round in range(len(lobby.game_structure)):  # rounds
        hand_cap = lobby.game_structure[Round]
        if Round == lobby.dark_stage:
            lobby.dark_flag = True

        lobby.score_table = "__Bets__"
        # for _ in lobby.players:
        #     if _.current_bet != -1:
        #         score_table += f"\n\n<{_.name}> ={_.current_bet}"
        for _ in lobby.players:
            _.score_screen = bot.send_message(_.chat_id, text=lobby.score_table)

        for _ in range(players_count - 1):  # bets
            player = lobby.players[(_ + Round) % players_count]
            player.current_hand = player.hands[Round][::]
            request_bet(player, hand_cap)
            if wait(lobby):
                return # bet getting
            lobby.score_table += f"\n\n<{player.name}> ={player.current_bet}"
            for __ in lobby.players:
                bot.edit_message_text(text=lobby.score_table,
                                      chat_id=__.chat_id, message_id=__.score_screen.id)

        player = lobby.players[(players_count - 1 + Round) % players_count]  # last bet
        player.current_hand = player.hands[Round][::]
        bet_sum = 0
        for _ in lobby.players:
            if _.current_bet != -1:
                bet_sum += _.current_bet
        forbidden_bet = hand_cap - bet_sum
        request_bet(player, hand_cap, forbidden_bet)
        if wait(lobby):
            return # bet getting
        lobby.score_table += f"\n\n<{player.name}> ={player.current_bet}"
        for _ in lobby.players:
            bot.edit_message_text(text=lobby.score_table,
                                  chat_id=_.chat_id, message_id=_.score_screen.id)

        lobby.winner = lobby.players[Round % players_count]
        for __ in range(hand_cap):  # moves
            first_player = lobby.winner  # first move
            request_move(first_player)
            if wait(lobby):
                return # move getting

            for _ in range(1, players_count):  # beating
                player = lobby.players[(_ + lobby.players.index(first_player)) % players_count]
                request_move(player, first_move=first_player.current_move)
                if wait(lobby):
                    return # move getting
            lobby.winner.current_beats += 1

            lobby.score_table = "__Scoring__"
            for _ in lobby.players:
                lobby.score_table += f"\n\n<{_.name}>\n" \
                                     f"[{_.score}]          {_.current_beats}/{_.current_bet}"
            if lobby.board.find("$") == -1:
                lobby.board = lobby.board + str(
                    f"\n\n<{lobby.winner.name}> wins with {lobby.winner.current_move}"
                    # f" against {''.join([_.current_move for _ in lobby.players if _ is not lobby.winner])}"
                    # f"\n{lobby.winner.current_beats}/{lobby.winner.current_bet}"
                )
            else:
                lobby.board = lobby.board[:lobby.board.find("$") - 1] + str(
                    f"\n\n<{lobby.winner.name}> wins with {lobby.winner.current_move}"
                    # f" against {''.join([_.current_move for _ in lobby.players if _ is not lobby.winner])}"
                    # f"\n{lobby.winner.current_beats}/{lobby.winner.current_bet}"
                )
            for _ in lobby.players:
                _.current_move = "sup"
                # bot.send_message(__r.chat_id,
                #                  text=f"<{lobby.winner.name}> wins with {lobby.winner.current_move}\n"
                #                       f"{lobby.winner.current_beats}/{lobby.winner.current_bet}")
                bot.edit_message_text(text=lobby.board, chat_id=_.chat_id, message_id=_.board_screen.id)
                _.board_screen = None
                if lobby.score_table != _.score_screen.text:
                    # print(lobby.score_table, "A")
                    # print(__.score_screen.text, "B")
                    bot.edit_message_text(text=lobby.score_table, chat_id=_.chat_id, message_id=_.score_screen.id)

        for player_ in lobby.players:  # score counting
            if player_.current_beats < player_.current_bet:
                player_.score -= (player_.current_bet - player_.current_beats) * 10
            elif player_.current_beats > player_.current_bet:
                player_.score += player_.current_beats
            elif player_.current_beats == player_.current_bet != 0:
                if lobby.game_structure[Round] == 1:
                    player_.score += player_.current_bet * 30
                else:
                    player_.score += player_.current_bet * 10
            else:
                player_.score += 5

        lobby.score_table = "__Round results__"
        for player_ in lobby.players:
            lobby.score_table += f"\n\n<{player_.name}>\n" \
                                 f"[{player_.score}]          {player_.current_beats}/{player_.current_bet}"
            player_.current_bet = -1
            player_.current_move = "sup"
            player_.current_beats = 0
        for player_ in lobby.players:
            # bot.send_message(player_.chat_id, text=score_table)
            bot.edit_message_text(text=lobby.score_table, chat_id=player_.chat_id, message_id=player_.score_screen.id)
        # player__.lobby.score_table = score_table

    lobby.score_table = "__Results__"
    players_set = lobby.players[::]
    for __ in range(len(players_set)):
        for _ in range(len(players_set) - 1):
            if players_set[_].score < players_set[_ + 1].score:
                players_set[_], players_set[_ + 1] = players_set[_ + 1], players_set[_]
    for _ in range(len(players_set)):
        lobby.score_table += f"\n\n#{_ + 1} <{players_set[_].name}> [{players_set[_].score}]"
    for _ in lobby.players:
        bot.send_message(_.chat_id, text=lobby.score_table)
    request_lobby_restart(lobby)


bot.infinity_polling()

