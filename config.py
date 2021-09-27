TOKEN = 'YOUR_BOT_TOKEN'
URL_SITE_WITH_JOKES = 'URL_SITE' # you may have to change the function code in main file
text = [
	"Привет!",
	"Я бот, который поможет тебе выбрать случайное число.",
	"",
	"Тебе стоит лишь указать диапозон.",
	"",
	"Список команд /commands",
	"",
	"Powered by aiogram"
]

filters = [
	"reset",
	"increase_1",
	"decrease_1",
	"increase_10",
	"decrease_10",
]

emoji = {
	'Rocket': '\U0001F680',
	'Camera': '\U0001F4F8',
	'Cine-Film': '\U0001F39E',
	'TV': '\U0001F4FA',
	'Inst': '\U000026A1',
	'Cute': '\U0001F97A',
	'HandShake': '\U0001F91D',
	'Bomb': '\U0001F9E8'
}

commands_text = [
	f"/start {emoji['Bomb']}",
	f"/number {emoji['HandShake']}",
]
