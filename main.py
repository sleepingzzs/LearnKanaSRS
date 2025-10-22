import math
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

interval = {
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
    1: 'Apprentice I',
    2: 'Apprentice II',
    3: 'Apprentice III',
    4: 'Apprentice IV',
    5: 'Guru I',
    6: 'Guru II',
    7: 'Master',
    8: 'Enlightened',
    9: 'Burned'
}

cur.execute('SELECT COUNT(*) FROM hiragana')
total = cur.fetchone()[0]

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
            return total - (res[0][0] % 10)
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
    adjust = math.ceil(mistakes / 2)
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
    clear_console()
    print('''
_ _ _ _ _ _ _ _ _ _ 

Welcome to KanaSRS!
> This terminal based application aims to teach you all the Japanese Kana using a Spaced Repetition System (SRS)
> SRS is an evidence-based learning system that uses flashcards and expanding intervals to improve memory retention
> Each day you can learn upto 10 Hiragana and 10 Katakana.
> With the help of this application, you can master both, Hiragana and Katakana, within just two weeks!

_ _ _ _ _ _ _ _ _ _ 

Lessons Available: {}
Reviews Available: {}

_ _ _ _ _ _ _ _ _ _ 

[0] LEARN
[1] REVIEW
[2] VIEW PROGRESS
[3] VIEW LIBRARY
[4] RESET PROGRESS
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
        library()
    elif choice == '4':
        if input("Are you sure you want to reset your progress? Type YES to confirm: ") == 'YES':
            reset()
    elif choice == 'X':
        return False
    else:
        clear_console()
        print('Unavailable!')
        input("Press Enter to continue...")
    return True

def learn():
    lessons = get_lessons()
    i = 0
    for lesson in lessons:
        clear_console()
        i += 1
        print('''
FLASHCARD #{}/{}
LEARNING #{}/5

_ _ _ _ _ _ _ _ _ _ 

HIRAGANA - {}
KATAKANA - {}
ROMAJI   - {}

_ _ _ _ _ _ _ _ _ _
        '''.format(lesson[3], total, i, lesson[0], lesson[1], lesson[2]))
        input('Press Enter to continue...')

    clear_console()
    review(lessons)

def review(reviews = None):
    if not reviews:
        reviews = get_reviews()

    random.shuffle(reviews)
    i = 1
    j = len(reviews)
    while reviews:
        rev = reviews[0]
        print('''
REVIEWING #{}/{}

_ _ _ _ _ _ _ _ _ _ 

HIRAGANA - {}
KATAKANA - {}

_ _ _ _ _ _ _ _ _ _ 
        '''.format(i, j, rev[0], rev[1]))

        answer = input("ROMAJI   - ").lower().strip()

        if answer == rev[2]:
            i += 1
            level = 1
            promotion = True

            _id = rev[3]
            try:
                level = new_level(cur_level=rev[4], mistakes=rev[5])
                cur.execute('''
                    UPDATE progress
                    SET level = {}, 
                    time = DATE_ADD(DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00'), INTERVAL {} HOUR)
                    WHERE id = {}
                '''.format(level, interval[level], _id))
                promotion = False if level <= rev[4] else True

            except IndexError:
                cur.execute('''
                    INSERT INTO progress 
                    VALUES ({}, {}, DATE_ADD(DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00'), INTERVAL {} HOUR), CURRENT_DATE())
                '''.format(_id, level, interval[level]))

            reviews.remove(rev)

            print("Correct! ✅")
            print("Promoted to '{}' 🌱".format(level_title[level])) if promotion else print("Demoted to '{}' 🪨".format(level_title[level]))
            input('Press Enter to continue...')

        else:
            try:
                rev[5] += 1
            except IndexError:
                pass
            print("Incorrect! ❌")
            print("The correct answer was '{}'".format(rev[2]))
            input('Press Enter to continue...')
            reviews.append(rev)
            reviews.remove(rev)
            random.shuffle(reviews)

        clear_console()
    con.commit()
    input('Press Enter to go back...')

def progress():
    clear_console()
    cur.execute('SELECT COUNT(*) FROM progress')
    page = 0
    pages = (cur.fetchone()[0] - 1) // 10 + 1
    cur.execute('''
        SELECT h.kana, k.kana, h.romaji, level, time FROM progress p, hiragana h, katakana k
        WHERE p.id = h.id AND p.id = k.id
        ORDER BY level DESC, p.id
    ''')

    while True:
        data = cur.fetchmany(10)
        page += 1

        if not data:
            input('No more pages! Press Enter to go back...')
            break
        data = [(h, k, r, level_title[l], t) for h, k, r, l, t in data]
        print('PAGE #{}/{}\n'.format(str(page), pages))
        print(tabulate(data, headers=['HIRAGANA', 'KATAKANA', 'ROMAJI', 'LEVEL', 'NEXT REVIEW'], stralign='center', tablefmt='grid', numalign='center'))
        input('\nPress Enter to go to the next page...')
        clear_console()

def library():
    cur.execute('SELECT COUNT(*) FROM hiragana')
    page = 0
    pages = (cur.fetchone()[0] - 1) // 10 + 1
    clear_console()
    cur.execute('''
        SELECT h.id, h.kana, k.kana, h.romaji
        FROM hiragana h, katakana k
        WHERE h.id = k.id
    ''')
    while True:
        data = cur.fetchmany(10)
        page += 1

        if not data:
            input('No more pages! Press Enter to go back...')
            break
        print('PAGE #{}/{}\n'.format(str(page), pages))
        print(tabulate(data, headers=['ID', 'HIRAGANA', 'KATAKANA', 'ROMAJI'], stralign='center', tablefmt='grid', numalign='center'))
        input('\nPress Enter to go to the next page...')
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
