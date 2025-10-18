import mysql.connector

# Connect to your database
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # blank if no password
    database="kana",
    charset='utf8mb4'
)

cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS hiragana (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kana VARCHAR(5) NOT NULL,
    romaji VARCHAR(10) NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS katakana (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kana VARCHAR(5) NOT NULL,
    romaji VARCHAR(10) NOT NULL
)
""")

cur.execute('''
CREATE TABLE IF NOT EXISTS progress (
    id INT PRIMARY KEY,
    level INT NOT NULL DEFAULT 1,
    time DATETIME NOT NULL,
    unlocked DATETIME
)
    ''')


# List of all katakana (basic, small kana, g-, z-, d-, b-, p-, digraphs)
katakana = [
    # Basic vowels
    ('ア', 'a'), ('イ', 'i'), ('ウ', 'u'), ('エ', 'e'), ('オ', 'o'),

    # K-row + G-row
    ('カ', 'ka'), ('キ', 'ki'), ('ク', 'ku'), ('ケ', 'ke'), ('コ', 'ko'),
    ('ガ', 'ga'), ('ギ', 'gi'), ('グ', 'gu'), ('ゲ', 'ge'), ('ゴ', 'go'),

    # S-row + Z-row
    ('サ', 'sa'), ('シ', 'shi'), ('ス', 'su'), ('セ', 'se'), ('ソ', 'so'),
    ('ザ', 'za'), ('ジ', 'ji'), ('ズ', 'zu'), ('ゼ', 'ze'), ('ゾ', 'zo'),

    # T-row + D-row
    ('タ', 'ta'), ('チ', 'chi'), ('ツ', 'tsu'), ('テ', 'te'), ('ト', 'to'),
    ('ダ', 'da'), ('ヂ', 'ji'), ('ヅ', 'zu'), ('デ', 'de'), ('ド', 'do'),

    # N-row
    ('ナ', 'na'), ('ニ', 'ni'), ('ヌ', 'nu'), ('ネ', 'ne'), ('ノ', 'no'),

    # H-row + B + P
    ('ハ', 'ha'), ('ヒ', 'hi'), ('フ', 'fu'), ('ヘ', 'he'), ('ホ', 'ho'),
    ('バ', 'ba'), ('ビ', 'bi'), ('ブ', 'bu'), ('ベ', 'be'), ('ボ', 'bo'),
    ('パ', 'pa'), ('ピ', 'pi'), ('プ', 'pu'), ('ペ', 'pe'), ('ポ', 'po'),

    # M-row
    ('マ', 'ma'), ('ミ', 'mi'), ('ム', 'mu'), ('メ', 'me'), ('モ', 'mo'),

    # Y-row
    ('ヤ', 'ya'), ('ユ', 'yu'), ('ヨ', 'yo'),

    # R-row
    ('ラ', 'ra'), ('リ', 'ri'), ('ル', 'ru'), ('レ', 're'), ('ロ', 'ro'),

    # W-row + N
    ('ワ', 'wa'), ('ヲ', 'wo'), ('ン', 'n'),

    # Digraphs (common only)
    ('キャ', 'kya'), ('キュ', 'kyu'), ('キョ', 'kyo'),
    ('ギャ', 'gya'), ('ギュ', 'gyu'), ('ギョ', 'gyo'),
    ('シャ', 'sha'), ('シュ', 'shu'), ('ショ', 'sho'),
    ('ジャ', 'ja'), ('ジュ', 'ju'), ('ジョ', 'jo'),
    ('チャ', 'cha'), ('チュ', 'chu'), ('チョ', 'cho'),
    ('ニャ', 'nya'), ('ニュ', 'nyu'), ('ニョ', 'nyo'),
    ('ヒャ', 'hya'), ('ヒュ', 'hyu'), ('ヒョ', 'hyo'),
    ('ビャ', 'bya'), ('ビュ', 'byu'), ('ビョ', 'byo'),
    ('ピャ', 'pya'), ('ピュ', 'pyu'), ('ピョ', 'pyo'),
    ('ミャ', 'mya'), ('ミュ', 'myu'), ('ミョ', 'myo'),
    ('リャ', 'rya'), ('リュ', 'ryu'), ('リョ', 'ryo'),
]
hiragana = [
    # Basic vowels
    ('あ', 'a'), ('い', 'i'), ('う', 'u'), ('え', 'e'), ('お', 'o'),

    # K-row + G-row
    ('か', 'ka'), ('き', 'ki'), ('く', 'ku'), ('け', 'ke'), ('こ', 'ko'),
    ('が', 'ga'), ('ぎ', 'gi'), ('ぐ', 'gu'), ('げ', 'ge'), ('ご', 'go'),

    # S-row + Z-row
    ('さ', 'sa'), ('し', 'shi'), ('す', 'su'), ('せ', 'se'), ('そ', 'so'),
    ('ざ', 'za'), ('じ', 'ji'), ('ず', 'zu'), ('ぜ', 'ze'), ('ぞ', 'zo'),

    # T-row + D-row
    ('た', 'ta'), ('ち', 'chi'), ('つ', 'tsu'), ('て', 'te'), ('と', 'to'),
    ('だ', 'da'), ('ぢ', 'ji'), ('づ', 'zu'), ('で', 'de'), ('ど', 'do'),

    # N-row
    ('な', 'na'), ('に', 'ni'), ('ぬ', 'nu'), ('ね', 'ne'), ('の', 'no'),

    # H-row + B + P
    ('は', 'ha'), ('ひ', 'hi'), ('ふ', 'fu'), ('へ', 'he'), ('ほ', 'ho'),
    ('ば', 'ba'), ('び', 'bi'), ('ぶ', 'bu'), ('べ', 'be'), ('ぼ', 'bo'),
    ('ぱ', 'pa'), ('ぴ', 'pi'), ('ぷ', 'pu'), ('ぺ', 'pe'), ('ぽ', 'po'),

    # M-row
    ('ま', 'ma'), ('み', 'mi'), ('む', 'mu'), ('め', 'me'), ('も', 'mo'),

    # Y-row
    ('や', 'ya'), ('ゆ', 'yu'), ('よ', 'yo'),

    # R-row
    ('ら', 'ra'), ('り', 'ri'), ('る', 'ru'), ('れ', 're'), ('ろ', 'ro'),

    # W-row + N
    ('わ', 'wa'), ('を', 'wo'), ('ん', 'n'),

    # Digraphs (only common ones)
    ('きゃ', 'kya'), ('きゅ', 'kyu'), ('きょ', 'kyo'),
    ('ぎゃ', 'gya'), ('ぎゅ', 'gyu'), ('ぎょ', 'gyo'),
    ('しゃ', 'sha'), ('しゅ', 'shu'), ('しょ', 'sho'),
    ('じゃ', 'ja'), ('じゅ', 'ju'), ('じょ', 'jo'),
    ('ちゃ', 'cha'), ('ちゅ', 'chu'), ('ちょ', 'cho'),
    ('にゃ', 'nya'), ('にゅ', 'nyu'), ('にょ', 'nyo'),
    ('ひゃ', 'hya'), ('ひゅ', 'hyu'), ('ひょ', 'hyo'),
    ('びゃ', 'bya'), ('びゅ', 'byu'), ('びょ', 'byo'),
    ('ぴゃ', 'pya'), ('ぴゅ', 'pyu'), ('ぴょ', 'pyo'),
    ('みゃ', 'mya'), ('みゅ', 'myu'), ('みょ', 'myo'),
    ('りゃ', 'rya'), ('りゅ', 'ryu'), ('りょ', 'ryo'),
]


# Insert all entries
# Check if katakana table is empty
cur.execute("SELECT COUNT(*) FROM katakana")
if cur.fetchone()[0] == 0:
    cur.executemany("INSERT INTO katakana (kana, romaji) VALUES (%s, %s)", katakana)
    con.commit()

# Check if hiragana table is empty
cur.execute("SELECT COUNT(*) FROM hiragana")
if cur.fetchone()[0] == 0:
    cur.executemany("INSERT INTO hiragana (kana, romaji) VALUES (%s, %s)", hiragana)
    con.commit()

cur.close()
con.close()
