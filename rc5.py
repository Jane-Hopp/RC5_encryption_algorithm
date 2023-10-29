class RC5:
    def __init__(self, w, r, key, source=None, rezult=None):
        ''' Задание параметров '''
        self.w = w   # половина длины блока в битах [16, 32, 64]
        self.r = r   # число раундов [0..255]
        self.key = key   # ключ
        self.b = len(key)   # длина ключа в байтах [0..255]
        self.t = 2*(r + 1)  # количество слов в таблице расширенных ключей
        self.mod = 2 ** w 
        self.w8 = w // 8   # длина половины блока в байтах
        self.w4 = w // 4
        self.mask = self.mod - 1   # для операции сдвига
        self.source = source   
        self.rezult = rezult  
        
    def constants(self):
        ''' Константы псевдослучайных величин P и Q соответственно '''
        if self.w == 16:
            return 0xB7E1, 0x9E37
        elif self.w == 32:
            return 0xB7E15163, 0x9E3779B9
        elif self.w == 64:
            return 0xB7E151628AED2A6B, 0x9E3779B97F4A7C15

    def key_split(self):
        ''' Разбиение ключа на слова '''
        if self.b == 0: # если ключ пустой 
            self.c = 1 
        elif self.b % self.w8:
            while self.b % self.w8:
                self.key += b'\x00' # дополнение ключа нулевыми битами
                self.b = len(self.key)
            self.c = self.b // self.w8 
        else:
            self.c = self.b // self.w8
        L = []
        for i in range(0, self.b, self.w8):
            L.append(int.from_bytes(self.key[i : i + self.w8], byteorder="little")) # преобразование bytes в int
        self.L = L
    
    def key_extend(self):
        ''' Построение таблицы расширенных ключей '''
        P, Q = self.constants()
        self.S = [(P + i * Q) % self.mod for i in range(self.t)]

    def l_shift(self, lst, shift): 
        ''' Циклический сдвиг влево '''
        shift %= self.w
        return ((lst << shift) & self.mask) | ((lst & self.mask) >> (self.w - shift))
    
    def r_shift(self, lst, shift):
        ''' Циклический сдвиг вправо '''
        shift %= self.w
        return ((lst & self.mask) >> shift) | (lst << (self.w - shift) & self.mask)
       
    def shuffle(self):
        ''' Смешивание списков L и S '''
        A, B, i, j = 0, 0, 0, 0
        for k in range(3 * max(self.c, self.t)):
            A = self.S[i] = self.l_shift((self.S[i] + A + B), 3)
            B = self.L[j] = self.l_shift((self.L[j] + A + B), A + B)
            i = (i + 1) % self.t
            j = (j + 1) % self.c

    def encrypt_block(self, data, need_round = None):
        ''' Шифрование блока размером w.8 байт '''
        A = int.from_bytes(data[:self.w8], byteorder='little')
        B = int.from_bytes(data[self.w8:], byteorder='little')
        ''' Наложение расширенного ключа на шифруемые данные перед первым раундом: '''
        A = (A + self.S[0]) % self.mod
        B = (B + self.S[1]) % self.mod
        ''' В каждом раунде выполняются следующие действия: '''
        rounds = []
        for i in range(1, self.r + 1):
            A = (self.l_shift((A ^ B), B) + self.S[2 * i]) % self.mod
            B = (self.l_shift((A ^ B), A) + self.S[2 * i + 1]) % self.mod
            A1, B1 = A, B
            rounds.append((A1.to_bytes(self.w8, byteorder='little') + B1.to_bytes(self.w8, byteorder='little')).hex())
        if need_round:
            return rounds
        else:
            return (A.to_bytes(self.w8, byteorder='little') + B.to_bytes(self.w8, byteorder='little')).hex()
    
    def decrypt_block(self, data):
        ''' Дешифрование блока '''
        A = int.from_bytes(data[:self.w8], byteorder='little')
        B = int.from_bytes(data[self.w8:], byteorder='little')
        for i in range(self.r, 0, -1):
            B = self.r_shift(B - self.S[2 * i + 1], A) ^ A
            A = self.r_shift(A - self.S[2 * i], B) ^ B
        B = (B - self.S[1]) % self.mod
        A = (A - self.S[0]) % self.mod
        return (A.to_bytes(self.w8, byteorder='little') + B.to_bytes(self.w8, byteorder='little')).hex()
        
    def encrypt_file(self, source, rezult):
        ''' Шифрование данных из файла '''
        with open(source, 'rb') as source_f, open(rezult, 'w') as rez_f:
            flag = True
            while flag:
                text = source_f.read(self.w)
                text = text.decode("unicode_escape").encode("raw_unicode_escape")
                if not text:
                    break
                if len(text) != self.w4:
                    text = text.ljust(self.w4, b'\x00')
                    flag = False
                text = self.encrypt_block(text)
                rez_f.write(text)

    def decrypt_file(self, source, rezult):
        ''' Дешифрование данных из файла '''
        with open(source, 'rb') as source_f, open(rezult, 'w') as rez_f:
            while True:
                text = source_f.read(self.w)
                text = text.decode("unicode_escape").encode("raw_unicode_escape")
                if not text:
                    break
                if len(text) != self.w4:
                    text = text.ljust(self.w4, b'\x00')
                text = self.decrypt_block(text)
                rez_f.write(text)
    
    def encryption_script(self):
        self.key_split()
        self.key_extend()
        self.shuffle()
        self.encrypt_file(self.source, self.rezult)

    def decryption_script(self):
        self.key_split()
        self.key_extend()
        self.shuffle()
        self.decrypt_file(self.source, self.rezult)
