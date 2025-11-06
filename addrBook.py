from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    '''
    Базовий клас для полів запису.
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Birthday(Field):
    '''
    Клас для збереження дати народження.
    '''
    def __init__(self, value):
        '''
        Ініціалізація дати народження з валідацією.
        Args:
            value (str): дата народження у форматі 'DD.MM.YYYY'
        '''
        try:
            date_obj = datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use 'DD.MM.YYYY'.")
        super().__init__(date_obj)

    def __str__(self):
        return self.value.strftime('%d.%m.%Y')


class Name(Field):
    '''
    Клас для імені контакту.
    '''
    def __init__(self, value):
        '''
        Ініціалізація імені з валідацією.
        Args:
            value (str): ім'я контакту
        '''
        if not value or not value.strip():  # перевірка на пусте ім'я
            raise ValueError("Name cannot be empty")
        super().__init__(value.strip().title())


class Phone(Field):
    '''
    Клас для телефонного номера.
    '''
    def __init__(self, value):
        if not isinstance(value, str):
            raise TypeError("Phone number must be a string")
        value_str = value.strip()
        # перевірка на 10-значний числовий номер
        if not (value_str.isdigit() and len(value_str) == 10):
            raise ValueError("Phone number must be exactly 10 digits")
        super().__init__(value)

    def __eq__(self, other):
        '''
        Перевірка на рівність телефонних номерів.
        '''
        # Порівняння з іншим об'єктом Phone або рядком
        if isinstance(other, Phone):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False


class Record:
    '''
    Клас для запису контакту.
    '''
    def __init__(self, name):
        # Нормалізація і валідація імені
        if isinstance(name, str):
            name = Name(name)
        elif not isinstance(name, Name):
            raise TypeError("Name must be a string or an instance of Name")
        self.name = name
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        if isinstance(birthday, str):
            birthday = Birthday(birthday)
        elif not isinstance(birthday, Birthday):
            raise TypeError("Birthday must be a string or an instance "
                            "of Birthday")
        self.birthday = birthday

    def __norm_phone(self, phone):
        # нормалізація телефону
        if isinstance(phone, Phone):
            return phone
        elif isinstance(phone, str):
            return Phone(phone)
        else:
            raise TypeError("Phone must be a string or an instance of Phone")

    def add_phone(self, phone):
        phone_ = self.__norm_phone(phone)
        if phone_ in self.phones:
            raise ValueError("This phone number already exists.")
        self.phones.append(phone_)

    def remove_phone(self, phone):
        phone_ = self.__norm_phone(phone)
        if phone_ in self.phones:
            self.phones.remove(phone_)
        else:
            raise ValueError("This phone number does not exist.")

    def edit_phone(self, old_phone, new_phone):
        old_phone_ = self.__norm_phone(old_phone)
        new_phone_ = self.__norm_phone(new_phone)

        # Перевірка наявності старого номера телефону
        if old_phone_ not in self.phones:
            raise ValueError("Phone number for editing does not exist.")
        # якщо новий номер такий же, як старий, нічого не робимо
        if old_phone_ == new_phone_:
            return
        # Знаходимо індекс старого номера телефону
        idx_phone = self.phones.index(old_phone_)
        # Якщо новий номер вже існує, видаляємо старий номер
        # (не додаємо дублікат)
        if new_phone_ in self.phones:
            self.phones.pop(idx_phone)
            return
        # Інакше замінюємо старий номер на новий
        self.phones[idx_phone] = new_phone_

    def find_phone(self, phone):
        phone_ = self.__norm_phone(phone)
        for p in self.phones:
            if p == phone_:
                return p
        return None

    def __str__(self):
        if self.phones:
            phones = ", ".join(p.value for p in self.phones)
        else:
            phones = "No phones"
        birthday_str = (self.birthday if self.birthday else 'No birthday')
        return (f"Contact name: {self.name.value}, phones: {phones}, "
                f"birthday: {birthday_str}")


class AddressBook(UserDict):
    def add_record(self, record):
        if not isinstance(record, Record):
            raise TypeError("Only instances of Record can be added")
        self.data[record.name.value] = record

    def get_upcoming_birthdays(self):
        self.congrat_dates = []
        users = [{'name': record.name.value,
                  'birthday': record.birthday.value.date()}
                 for record in self.data.values() if record.birthday]
        date_current = datetime.today().date()
        for user in users:
            birthday_cur = user['birthday']
            next_birthday = self.__next_birthday(birthday_cur, date_current)
            days_delta = (next_birthday - date_current).days
            if 0 <= days_delta <= 7:
                congrat_date = self.__if_weekend(next_birthday)
                self.congrat_dates.append({
                    'name': user['name'],
                    'congratulation_date': congrat_date
                })
        self.congrat_dates.sort(
            key=lambda user: (user['congratulation_date'], user['name']))

        return self.congrat_dates

    def __next_birthday(self, birthday, today):
        '''helper функція, яка розраховує дату наступного дня народження
        Args:
        birthday(date): ДР людини today(date): поточна дата
        Returns:
        date: дата наступного ДР людини '''

        year = today.year
        cur_bday = birthday.replace(year=year)

        if cur_bday < today:
            cur_bday = birthday.replace(year=year+1)

        return cur_bday

    def __if_weekend(self, cur_bday):
        '''helper функція, яка перевіряє, чи припадає ДР на вихідний
        (субота та неділя)
        Args:
        cur_bday(date): дата наступного ДР людини
        Returns:
        str: дата, коли слід привітати людину у строковому форматі '''

        weekday = cur_bday.isoweekday()

        if weekday == 6:
            cur_bday += timedelta(days=2)
        if weekday == 7:
            cur_bday += timedelta(days=1)

        return cur_bday.strftime('%d.%m.%Y')

    def __norm_name(self, name):
        if isinstance(name, Name):
            return name.value
        if isinstance(name, str):
            return Name(name).value  # нормалізація + валідація
        raise TypeError("Name must be a string or an instance of Name")

    def find(self, name):
        key = self.__norm_name(name)
        return self.data.get(key)

    def delete(self, name):
        key = self.__norm_name(name)
        if key in self.data:
            del self.data[key]
        else:
            raise KeyError("This contact does not exist")

    def __str__(self):
        if self.data:
            return "\n".join(str(r) for r in self.data.values())
        return "Address book is empty"


def save_data(book, filename: str = "addressbook.pkl"):
    """Зберегти AddressBook на диск за допомогою pickle.

    Args:
        book (AddressBook): екземпляр адресної книги для
            серіалізації
        filename (str): шлях до файлу для збереження
    """
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename: str = "addressbook.pkl") -> "AddressBook":
    """Завантажити AddressBook з диска за допомогою pickle.

    Повертає новий AddressBook, якщо файл відсутній або не
    може бути прочитаний.
    """
    try:
        with open(filename, "rb") as f:
            data = pickle.load(f)
            if isinstance(data, AddressBook):
                return data
            return AddressBook()
    except FileNotFoundError:
        return AddressBook()
    except Exception:
        return AddressBook()
