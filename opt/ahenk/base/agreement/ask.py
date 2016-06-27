import sys
import easygui


def ask(content, title):
    choice = easygui.ynbox(content, title, ('Evet', 'Hayır'))
    if choice:
        print('Y')
    else:
        print('N')


if __name__ == '__main__':
    if len(sys.argv) == 3:
        try:
            ask(sys.argv[1], sys.argv[2])
        except Exception as e:
            print(str(e))
    else:
        print('Error')
