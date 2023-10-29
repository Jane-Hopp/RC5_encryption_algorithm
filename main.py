from rc5 import RC5

class Menu:
    ''' Ввод данных пользователем: w, r, key, путей к файлам '''
    def user_input(self):
        print("----------Алгоритм шифрования RC5----------")
        print("\nШифрование/дешифрование осуществялется в 16-ой системе счисления")
        mode = input("\nУкажите режим работы программы [e] - шифрование, [d] - дешифрование]: ")

        input_mode = input("Хотите ли вы вводить данные вручную или оставить данные по умолчанию? [d] - по умолчанию, [m] - вручную  ")
        if input_mode == 'd':
            print('''Данные по умолчанию:
                Путь к файлу с исходными данными: .\\files\source.txt
                Путь к файлу с результатами: .\\files\\rezult.txt
                Путь к файлу с ключом: .\\files\key.txt
                Длина блока шифрования: 32 бита
                Количество раундов: 12''')
            source = '.\\files\source.txt'
            rezult = '.\\files\\rezult.txt'
            path_key = '.\\files\key.txt'
            w = 32
            r = 12
        elif input_mode == 'm':
            print("\n---Задайте параметры:---")
            print("\n---Укажите пути к файлам:--")
            source = input("Путь к файлу с исходными данными: ")      
            rezult = input("Путь к файлу с результатами: ")
            path_key = input("Путь к файлу с ключом: ")
            w = int(input('Длина блока шифрования в битах [16, 32, 64]: '))
            r = int(input('Количество раундов [0..255]: '))
        else:
            print("Задан несуществующий режим ввода данных")
        with open(path_key, 'rb') as f:
            key = f.read()
            key = key.decode("unicode_escape").encode("raw_unicode_escape")
        return mode, source, key, rezult, w, r

if __name__ == '__main__':
    mode, source, key, rezult, w, r = Menu().user_input()
    if mode == 'e':
        RC5(w, r, key, source, rezult).encryption_script()
        print("\nШифрование завершено")
    elif mode == 'd':
        RC5(w, r, key, source, rezult).decryption_script()
        print("\nДешифрование завершено")
    else:
        print("Задан несуществующий режим работы программы")