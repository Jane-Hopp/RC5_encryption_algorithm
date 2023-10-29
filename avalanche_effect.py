import random
from rc5 import RC5

class Generator:
    ''' Формирование оценки лавинного эффекта по тексту '''
    def generate_bin(self):
        ''' Генерирование двоичного числа, размером 64 бит '''
        seq = ""
        for i in range(64):
            seq += random.choice("10")
        return seq
    
    def covert_bin_to_hex(self, seq):
        ''' Конвертирование двоичной последовательности в шестнадцатеричную '''
        bin_lst = [seq[i:i+8] for i in range(0, len(seq), 8)]
        dec = [int(i, 2) for i in bin_lst] # в 10сс
        hex_lst = [hex(i).split('x')[-1] for i in dec] # в 16сс
        for i in range(len(hex_lst)):
            if len(hex_lst[i]) == 1:
                hex_lst[i] = hex_lst[i].rjust(2, '0')
        hex_str = ' '.join(hex_lst)
        hex_bytes = bytes.fromhex(hex_str) #!
        return hex_bytes
    
    def convert_hex_to_bin(self, seq):
        ''' Конвертирование шестнадцатеричной последовательности в двоичную '''
        hex_lst = [seq[i:i+2] for i in range(0, len(seq)-1, 2)]
        bin_lst = [bin(int(i, 16))[2:] for i in hex_lst]
        bin_str = ''.join(bin_lst)
        return bin_str

    def main_sript(self, mode, num): # mode: text, key; num - число экспериментов
        ''' Получение двух списков: данные шифрования до и после изменения бита для каждого раунда '''
        data_before, data_changed = [], []
        for i in range(num):
            ''' Генерирование ключа [64 бит] и блока данных [64 бит] '''
            key = self.generate_bin() 
            data = self.generate_bin()

            ''' Шифрование блока в режиме RC5-32/12/8 '''
            rc5 = RC5(32, 12, self.covert_bin_to_hex(key))
            rc5.key_split()
            rc5.key_extend()
            rc5.shuffle()    
            rounds = rc5.encrypt_block(self.covert_bin_to_hex(data), 1) 

            ''' Сохранение исходных данных '''
            rounds = [self.convert_hex_to_bin(i) for i in rounds]
            key_data = [key, data]
            for i in rounds:
                key_data.append(i) # структура списка: [ключ, раунд 0, раунд 1, ...]
            data_before.append(key_data)

            ''' Случайное изменение одного бита входного текста '''
            if mode == 'text':
                id  = random.randint(0, 63)
                data = list(data)
                data[id] = '1' if data[id] == '0' else '0'
                data = ''.join(data)
            elif mode == 'key':
                id  = random.randint(0, 63)
                key = list(key)
                key[id] = '1' if key[id] == '0' else '0'
                key = ''.join(key)

            ''' Шифрование измененного блока '''
            rc5 = RC5(32, 12, self.covert_bin_to_hex(key))
            rc5.key_split()
            rc5.key_extend()
            rc5.shuffle()
            rounds_changed = rc5.encrypt_block(self.covert_bin_to_hex(data), 1)
             
            ''' Сохранение измененных данных '''
            rounds_changed = [self.convert_hex_to_bin(i) for i in rounds_changed]
            data = [key, data]
            for i in rounds_changed:
                data.append(i) # структура списка: [ключ, раунд 0, раунд 1, ...]
            data_changed.append(data)            
            
        return data_before, data_changed
    
class Code_distance:
    ''' Рачет кодового расстояния '''
    def code_distance_calc(self, data, data_changed):
        dist = [] # хранит все кодовые расстояния для каждой процедуры
        for i, i_ch in zip(data, data_changed):
            r_lst = [] # кодовое расстояние для каждого раунда
            for r, r_ch in zip(i, i_ch):
                d = 0
                for s, s_ch in zip(r, r_ch):
                    if s != s_ch:
                        d += 1
                r_lst.append(d)
            dist.append(r_lst)
        return dist # нулевой элемент списка является ключом! Остальные - данные на каждом раунде
    
    def relative_value_calc(self, lst):
        ''' Расчет относительной величины λ = d/N, где N = 64 '''
        lst = [i[1:] for i in lst] # избавляемся от данных ключа - нулевого элемента
        for i in range(len(lst)):
            for j in range(len(lst[i])):
                lst[i][j] = lst[i][j] / 64
        return lst
    
    def average_value_calc(self, lst):
        ''' Усредняются значения кодовых расстояний для выхода каждого раунда '''
        k = len(lst) # число экспериментов
        r = len(lst[0]) # число раундов + нулевой раунд
        rez = [0] * r
        for i in range(k):
            for j in range(r):
                rez[j] += lst[i][j]
        rez = [round(i / k, 3) for i in rez]
        return rez
    
    def save_to_file(self, data, data_changed, lst, rel, sr, mode = 'text'):
        ''' Сохранение данных в файл '''
        r = len(sr) - 1 # число раундов
        k = len(lst) # количество экспериментов
        with open(f'.\\files\AE_{mode}.txt', 'w', encoding='utf-8') as f:
            f.write("---ДАННЫЕ ДЛЯ ОЦЕНКИ ЛАВИННОГО ЭФФЕКТА---\n")
            f.write(f"\nЧисло экспериментов -  {k}\n")
            f.write(f"Число раундов -  {r}\n")
            f.write(f"Размер блока данных -  64 бит\n")
            f.write(f"Длина ключа -  64 бит\n")
            f.write(f"\nСгенерированный ключ\n{data[0][0]}\n")
            if mode == 'text':
                f.write(f"\nПоследовательность для шифрования\n{data[0][1]}\n")
                f.write(f"\nПоследовательность для шифрования после изменения одного бита\n{data_changed[0][1]}\n")
            elif mode == 'key':
                f.write(f"\nКлюч после измения одного бита\n{data_changed[0][0]}\n")
                f.write(f"\nПоследовательность для шифрования\n{data[0][1]}\n")
            f.write("------------------------------------------------------------------------------------\n")
            f.write(f"Раунды после процедуры шифрования в первом эксперименте :\n{data[0][1:]}\n")
            f.write(f"\nРаунды после процедуры шифрования в первом эксперименте при изменении одного бита :\n{data_changed[0][1:]}\n")
            f.write(f"\nКодовое расстояние для каждого раунда в первом эксперименте :\n{lst[0][1:]}\n")
            f.write(f"\nОтносительная величина для каждого раунда в первом эксперименте :\n{rel[0]}\n")
            f.write(f"\nРасчет среднего кодового расстояния для каждого раунда во всех экспериментах :\n{sr}\n")


if __name__ == '__main__':
    g = Generator()
    cd = Code_distance()
    ''' Получение кодового расстояния при изменении текста '''
    data_text, data_text_changed = g.main_sript('text', 100)
    lst_text = cd.code_distance_calc(data_text, data_text_changed)

    ''' Получение кодового расстояния при изменении ключа '''
    data_key, data_key_changed = g.main_sript('key', 100)
    lst_key = cd.code_distance_calc(data_key, data_key_changed)  

    ''' Расчет относительной величины ''' 
    rel_text = cd.relative_value_calc(lst_text)
    rel_key = cd.relative_value_calc(lst_key)

    ''' Расчет среднего кодового расстояния для каждого раунда '''
    sr_text = cd.average_value_calc(rel_text)
    sr_key = cd.average_value_calc(rel_key)

    ''' Сохранение данных в файл '''
    cd.save_to_file(data_text, data_text_changed, lst_text, rel_text, sr_text, "text")
    cd.save_to_file(data_key, data_key_changed, lst_key, rel_key, sr_key, "key")


