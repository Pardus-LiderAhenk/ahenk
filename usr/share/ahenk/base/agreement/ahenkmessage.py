import sys
from easygui import multpasswordbox, msgbox

def ask(message, title, host):

    field_names=[]

    if host =='':
        field_names.append("Etki Alanı Sunucusu:")

    field_names.append("Yetkili Kullanıcı")
    field_names.append("Parola")

    field_values = multpasswordbox(
        msg=message,
        title=title, fields=(field_names))

    if field_values is None:
        return print('N');

    is_fieldvalue_empty = False;

    for value in field_values:
        if value == '':
            is_fieldvalue_empty = True;

    if is_fieldvalue_empty:
        msgbox("Lütfen zorunlu alanları giriniz.", ok_button="Tamam")
        return print('Z');

    if host =='':
        print(field_values[0],field_values[1],field_values[2])
    else:
        print(field_values[0], field_values[1])

if __name__ == '__main__':

    if len(sys.argv) > 1:
        try:
            message=sys.argv[1]
            title=sys.argv[2]
            host=sys.argv[3]
            ask(message,title, host)
        except Exception as e:
            print(str(e))
    else:
        print('Argument fault. Check your parameters or content of parameters. Parameters: ' + str(sys.argv))