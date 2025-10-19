import mysql.connector
import random
from datetime import date

def clear_console():
    print("\n" * 100)

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="kana",
    charset='utf8mb4'
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

def welcome():
    cur.execute('''
        SELECT id, unlocked
        FROM progress
        WHERE id = (SELECT MAX(id) FROM progress)
    ''')

    data = cur.fetchall()

    if not data:
        data = [(0, '0000-00-00')]

    lessons = 10 - data[0][0] % 10
    if data[0][0] > 100:
        lessons = 104 - data[0][0]
    if data[0][0] > 0 and data[0][0] % 10 == 0:
        lessons = 0
    cur.execute('''
        SELECT COUNT(*) FROM progress
        WHERE time < CURRENT_TIME()
    ''')
    reviews = cur.fetchall()[0][0]
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
'''.format(lessons, reviews))

    choice = input('Select: ')

    if choice == '0' and (lessons > 0 or str(date.today()) > str(data[0][1])):
        learn()
    elif choice == '1' and reviews > 0:
        review()
    elif choice == '2':
        view()
    elif choice == '3':
        if input("Are you sure you want to reset? Type YES to confirm: ") == "YES":
            reset()
    elif choice.upper().strip() == 'X':
        pass
    else:
        print("Unavailable!")
        input("Press Enter to continue...")
        welcome()
def learn():
    cur.execute('''
            SELECT hiragana.kana, katakana.kana, hiragana.romaji, hiragana.id
            FROM hiragana, katakana
            WHERE hiragana.id = katakana.id
                AND hiragana.id BETWEEN COALESCE((SELECT MAX(id) + 1 FROM progress), 1)
                    AND COALESCE((SELECT MAX(id) + 5 FROM progress), 5)
        ''')

    data = cur.fetchall()

    for i in data:
        clear_console()
        print('''
_ _ _ _ _

HIRAGANA - {}
KATAKANA - {}
ROMAJI   - {}

_ _ _ _ _
'''.format(i[0], i[1], i[2]))

        input('Press Enter to continue...')

    clear_console()
    data2 = data.copy()
    for i in data2:
        print('''
_ _ _ _ _

HIRAGANA - {}
KATAKANA - {}

_ _ _ _ _
'''.format(i[0], i[1]))

        answer = input('ROMAJI   - ')

        if answer.lower().strip() == i[2]:
            print("Correct! ✅")
            input('Press Enter to continue...')
        else:
            print("Incorrect! ❌")
            print("The correct answer is '{}'".format(i[2]))
            input('Press Enter to continue...')
            data2.append(i)
        clear_console()
    else:
        for i in data:
            cur.execute('''
                    INSERT INTO progress 
                    VALUES ({}, {}, DATE_ADD(DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00'), INTERVAL 4 HOUR), CURRENT_DATE())
                '''.format(i[3], 1))
            con.commit()
    input('Press Enter to go back...')
    welcome()
def review():
    cur.execute('''
        SELECT h.kana, k.kana, h.romaji, level, p.id, 0 FROM progress p, hiragana h, katakana k
        WHERE p.id = h.id AND p.id = k.id AND time <= CURRENT_TIME()
        LIMIT 10
    ''')
    data = cur.fetchall()

    for i in range(len(data)):
        data[i] = list(data[i])

    random.shuffle(data)
    for i in data:
        print('''
_ _ _ _ _

HIRAGANA - {}
KATAKANA - {}

_ _ _ _ _
        '''.format(i[0], i[1]))
        answer = input('ROMAJI   - ')
        if answer.lower().strip() == i[2]:
            penalty = 1
            if i[3] >= 5:
                penalty = 2
            adjust = round(i[5] / 2)
            new_level = i[3] - (adjust * penalty)
            if i[5] == 0:
                new_level = 1 + i[3]
            if new_level < 0:
                new_level = 1

            print("Correct! ✅")
            input('Press Enter to continue...')
            cur.execute('''
                INSERT INTO progress (id, level, time)
                VALUES ({}, {}, DATE_ADD(DATE_FORMAT(NOW(), '%%Y-%%m-%%d %%H:00:00'), INTERVAL {} HOUR))
            '''.format(i[4], new_level, interval[new_level]))
        else:
            i[5] += 1
            print("Incorrect! ❌")
            print("The correct answer is '{}'".format(i[2]))
            input('Press Enter to continue...')
            data.append(i)
    input('Press Enter to go back...')
    welcome()
def view():
    cur.execute('''
        SELECT h.kana, k.kana, h.romaji, level, time FROM progress p, hiragana h, katakana k
        WHERE p.id = h.id AND p.id = k.id
        ORDER BY level, p.id
    ''')

    while True:
        data = cur.fetchmany(5)
        if not data:
            break
        print('Level | Kana   | Romaji | Next Review')
        for i in data:
            print('{3}     | {0} + {1} | {2}      | {4}'.format(i[0], i[1], i[2], i[3], i[4]))
        input('Press Enter to view more...')
        clear_console()
    input('Press Enter to go back...')
    welcome()
def reset():
    cur.execute('''
        DELETE FROM progress
    ''')
    con.commit()
    print("Progress has been reset!")
    input('Press Enter to go back...')
    welcome()

welcome()
con.commit()
con.close()