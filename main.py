import mysql.connector
import random
from datetime import date
from tabulate import tabulate

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="kana",
    charset="utf8mb4"
)

cur = con.cursor()

srs = {
    1: 4,
    2: 8,
    3: 24,
    4: 48,
    5: 24 * 7,
    6: 24 * 14,
    7: 24 * 30,
    8: 24 * 30 * 4,
    9: 24 * 30 * 100,
}

level_title = {
    1: 'Apprentice 1',
    2: 'Apprentice 2',
    3: 'Apprentice 3',
    4: 'Apprentice 4',
    5: 'Guru 1',
    6: 'Guru 2',
    7: 'Master',
    8: 'Enlightened',
    9: 'Burned'
}

def clear_console():
    print("\n" * 100)

def available_lessons():
    cur.execute('''
        SELECT id, unlocked
        FROM progress
        ORDER BY id DESC LIMIT 1
    ''')

    res = cur.fetchall()

    if res:
        if res[0][0] % 10 == 0 and str(res[0][1]) >= str(date.today()):
            return 0
        if res[0][0] > 100:
            return 104 - (res[0][0] % 10)
        return 10 - (res[0][0] % 10)

    return 10


def available_reviews():
    cur.execute('''
        SELECT COUNT(*)
        FROM progress
        WHERE time < CURRENT_TIME ()
    ''')
    return cur.fetchall()[0][0]


def get_lessons():
    cur.execute('''
        SELECT hiragana.kana, katakana.kana, hiragana.romaji, hiragana.id
        FROM hiragana, katakana
        WHERE hiragana.id = katakana.id
            AND hiragana.id BETWEEN COALESCE((SELECT MAX(id) + 1 FROM progress), 1)
                AND COALESCE((SELECT MAX(id) + 5 FROM progress), 5)
    ''')
    return cur.fetchall()


def new_level(cur_level, mistakes):
    penalty = 2 if cur_level >= 5 else 1
    adjust = round(mistakes / 2)
    level = cur_level - (adjust * penalty)

    if mistakes == 0:
        level = cur_level + 1
    if level < 1:
        level = 1

    return level

def get_reviews():
    cur.execute('''
        SELECT h.kana, k.kana, h.romaji, p.id, level, 0
        FROM progress p,
            hiragana h,
            katakana k
        WHERE p.id = h.id
        AND p.id = k.id
        AND time <= CURRENT_TIME ()
        LIMIT 10
    ''')

    reviews = cur.fetchall()
    reviews = [list(r) for r in reviews]
    return reviews

def home():
    print('''
_ _ _ _ _

Welcome to KanaSRS!
> This terminal based application aims to teach you all the Japanese Kana using a Spaced Repetition System (SRS)
> SRS is an evidence-based learning system that uses flashcards and expanding intervals to improve memory retention
> Each day you can learn upto 10 Hiragana and 10 Katakana.
> With the help of this application, you can master both, Hiragana and Katakana, within just two weeks!

_ _ _ _ _

Lessons Available: {}
Reviews Available: {}

_ _ _ _ _

[0] LEARN
[1] REVIEW
[2] VIEW PROGRESS
[3] RESET PROGRESS
[X] EXIT
'''.format(available_lessons(), available_reviews()))

    choice = input('Select: ').strip().upper()

    if choice == '0' and available_lessons() > 0:
        learn()
    elif choice == '1' and available_reviews() > 0:
        review()
    elif choice == '2':
        progress()
    elif choice == '3':
        if input("Are you sure you want to reset your progress? Type YES to confirm: ") == 'YES':
            reset()
    elif choice == 'X':
        return False
    else:
        print('Unavailable!')
        input("Press Enter to continue...")
    return True


def learn():
    lessons = get_lessons()

    for lesson in lessons:
        clear_console()
        print('''
_ _ _ _ _

HIRAGANA - {}
KATAKANA - {}
ROMAJI   - {}

_ _ _ _ _
        '''.format(lesson[0], lesson[1], lesson[2]))

        input('Press Enter to continue...')

    clear_console()
    review(lessons)

def review(lessons = get_reviews()):
    random.shuffle(lessons)

    while lessons:
        lesson = lessons[0]
        print('''
_ _ _ _ _

HIRAGANA - {}
KATAKANA - {}

_ _ _ _ _
        '''.format(lesson[0], lesson[1]))

        answer = input("ROMAJI   - ").lower().strip()

        if answer == lesson[2]:
            level = 1
            interval = srs[level]
            _id = lesson[3]
            try:
                level = new_level(cur_level=lesson[4], mistakes=lesson[5])
                cur.execute('''
                    UPDATE progress
                    SET level = {}, 
                    time = DATE_ADD(DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00'), INTERVAL {} HOUR)
                    WHERE id = {}
                '''.format(level, interval, _id))

            except IndexError:
                cur.execute('''
                    INSERT INTO progress 
                    VALUES ({}, {}, DATE_ADD(DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00'), INTERVAL {} HOUR), CURRENT_DATE())
                '''.format(_id, level, interval))

            finally:
                con.commit()

            lessons.remove(lesson)

            print("Correct! ✅")
            input('Press Enter to continue...')

        else:
            try:
                lesson[5] += 1
            except IndexError:
                pass
            print("Incorrect! ❌")
            print("The correct answer was '{}'".format(lesson[2]))
            input('Press Enter to continue...')
            lessons.append(lesson)
            lessons.remove(lesson)
            random.shuffle(lessons)

        clear_console()
    input('Press Enter to go back...')

def progress():
    i = 0
    clear_console()
    while True:
        cur.execute('''
            SELECT h.kana, k.kana, h.romaji, level, time FROM progress p, hiragana h, katakana k
            WHERE p.id = h.id AND p.id = k.id
            ORDER BY level DESC, p.id
            LIMIT {}, 10
        '''.format(i * 10))
        data = cur.fetchall()

        if not data:
            input('No more pages! Press Enter to go back...')
            break
        data = [(h, k, r, level_title[l], t) for h, k, r, l, t in data]
        print(tabulate(data, headers=['HIRAGANA', 'KATAKANA', 'ROMAJI', 'LEVEL', 'NEXT REVIEW'], tablefmt='grid'))
        print('Page ' + str(i + 1))
        i += 1
        input('Press Enter to go to the next page...')
        clear_console()

def reset():
    cur.execute('''
        DELETE FROM progress
    ''')
    print("Progress has been reset!")
    input('Press Enter to go back...')
    con.commit()


while True:
    if not home():
        con.close()
        break