from addrBook import AddressBook, Record, load_data, save_data


def input_error(func):
    '''
    Декоратор для обробки помилок вводу користувача
    Args:
        func (function): функція-обробник команди
    Returns:
        (function): обгорнута функція-обробник команди
    '''
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, AttributeError):
            return "Contact not found"
        except ValueError:
            return "Give me right arguments please."
        except IndexError:
            return "Please enter a name."
    return inner


@input_error
def add_contact(args, book: AddressBook):
    '''
    Функція додавання нового контакту
    Args:
        args (list): ім'я та номер телефону
        book(AddressBook): адресна книга
    Returns:
        (str): результат операції
    '''
    name, phone, *_ = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return 'Phone added.'
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return 'Contact added.'


@input_error
def change_contact(args, book: AddressBook):
    '''
    Функція зміни існуючого контакту
    Args:
        args (list): ім'я та номер телефону
        book(AddressBook): адресна книга
    Returns:
        (str): результат операції
    '''
    name, old_phone, new_phone = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return 'Contact updated.'


@input_error
def show_phone(args, book: AddressBook):
    '''
    Функція пошуку номеру телефону за ім'ям
    Args:
        args (list): ім'я
        book(AddressBook): адресна книга
    Returns:
        (str): результат операції
    '''
    name, *_ = args
    record = book.find(name)
    if record.phones:
        phones = ", ".join(p.value for p in record.phones)
        return f'{record.name.value}: {phones}'
    else:
        return "Contact has no phones."


def show_all(book: AddressBook):
    '''
    Функція виводу усіх доданих контактів
    Args:
        book(AddressBook): адресна книга
    Returns:
        (str): результат операції
    '''
    if not book.data:
        return 'No added contacts'

    records = sorted(book.data.values(), key=lambda r: r.name.value)
    lines = [str(record) for record in records]
    return "\n".join(lines)


def parse_input(user_input):
    '''
    helper функція. Парсер вводу користувача
    Args:
        user_input (str): команда користувача
    Returns:
        (str, list): назва команди, аргументи команди
    '''
    user_input = user_input.strip()
    if not user_input:
        return '', []

    parts = user_input.split()
    cmd = parts[0].lower()
    args = parts[1:]

    return cmd, args


@input_error
def add_birthday(args, book: AddressBook):
    '''
    Функція додавання дня народження до контакту
    Args:
        args (list): ім'я та дата народження
        book (AddressBook): адресна книга
    Returns:
        (str): результат операції
    '''
    name, birthday = args
    record: Record = book.find(name)
    record.add_birthday(birthday)
    return 'Birthday added.'


@input_error
def show_birthday(args, book: AddressBook):
    '''
    Функція показу дня народження контакту
    Args:
        args (list): ім'я контакту
        book (AddressBook): адресна книга
    Returns:
        (str): результат операції
    '''
    name, *_ = args
    record = book.find(name)
    if record.birthday is None:
        return f"Birthday for {name} is not set."
    return f"{name}'s birthday: {record.birthday}"


@input_error
def birthdays(book: AddressBook):
    '''
    Функція показу днів народження на наступний тиждень
    Args:
        book (AddressBook): адресна книга
    Returns:
        (str): результат операції
    '''
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next week."

    result = "Upcoming birthdays:\n"
    for item in upcoming:
        result += f"{item['name']}: {item['congratulation_date']}\n"
    return result.strip()


def main():
    book = load_data()

    print('Welcome to the assistant bot!')
    try:
        while True:
            user_input = input('Enter a command: ')
            command, args = parse_input(user_input)

            # пошук відповідної команди
            if command in ['close', 'exit']:
                save_data(book)
                print('Good bye!')
                break

            if command == '':
                continue

            if command == 'hello':
                print('How can I help you?')

            elif command == 'add':
                print(add_contact(args, book))

            elif command == 'change':
                print(change_contact(args, book))

            elif command == 'phone':
                print(show_phone(args, book))

            elif command == 'all':
                print(show_all(book))

            elif command == 'add-birthday':
                print(add_birthday(args, book))

            elif command == 'show-birthday':
                print(show_birthday(args, book))

            elif command == 'birthdays':
                print(birthdays(args, book))

            else:
                print('Invalid command')
    except KeyboardInterrupt:
        # Save before exiting on Ctrl+C
        save_data(book)
        print('\nGood bye!')


if __name__ == '__main__':
    main()
