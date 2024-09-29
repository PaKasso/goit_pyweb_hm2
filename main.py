import pickle
from collections import UserDict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

# Базовий клас для всіх полів
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Клас для імені, що наслідується від Field і перевіряє, що ім'я непорожнє
class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)

# Клас для телефону, що наслідується від Field і перевіряє, що телефон складається з 10 цифр
class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)

    @staticmethod
    def validate_phone(phone):
        return phone.isdigit() and len(phone) == 10

# Клас для дня народження, що наслідується від Field і перевіряє формат дати (DD.MM.YYYY)
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# Клас для запису, що містить ім'я, список телефонів і дату народження
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # Метод для додавання телефону до запису
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    # Метод для видалення телефону з запису
    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone number not found")

    # Метод для редагування телефону у записі
    def edit_phone(self, old_phone, new_phone):
        old_phone_obj = self.find_phone(old_phone)
        if old_phone_obj:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError("Old phone number not found")

    # Метод для пошуку телефону у записі
    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj
        return None

    # Метод для додавання дня народження до запису
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = '; '.join(phone.value for phone in self.phones)
        birthday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"

# Клас для адресної книги, що наслідується від UserDict і зберігає записи
class AddressBook(UserDict):
    # Метод для додавання запису до адресної книги
    def add_record(self, record):
        self.data[record.name.value] = record

    # Метод для пошуку запису за ім'ям
    def find(self, name):
        return self.data.get(name, None)

    # Метод для видалення запису за ім'ям
    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Record not found")

    # Метод для отримання днів народження на наступні 7 днів
    def get_upcoming_birthdays(self):
        today = datetime.today()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                try:
                    birthday_this_year = record.birthday.value.replace(year=today.year)
                except ValueError:
                    # Обробка 29 лютого на невисокосний рік
                    birthday_this_year = record.birthday.value.replace(year=today.year, day=28)
                if today <= birthday_this_year <= today + timedelta(days=7):
                    birthday_str = birthday_this_year.strftime("%d.%m.%Y")
                    upcoming_birthdays.append({"name": record.name.value, "birthday": birthday_str})

        return upcoming_birthdays

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())

# Функція для збереження адресної книги у файл
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

# Функція для завантаження адресної книги з файлу
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

# Декоратор для обробки помилок введення
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Error: Contact not found."
        except ValueError as e:
            return f"Error: {e}"
        except IndexError:
            return "Error: Invalid command format."
    return inner

# Функція для розбору введеного рядка на команду та аргументи
def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    cmd = parts[0].lower()
    args = parts[1:]
    return cmd, args

# Функція для додавання контакту
@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError("Add command requires at least name and phone.")
    name = args[0]
    phones = args[1:]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    for phone in phones:
        record.add_phone(phone)
    return message

# Функція для зміни телефону контакту
@input_error
def change_contact(args, book):
    if len(args) < 3:
        raise ValueError("Change command requires name, old phone, and new phone.")
    name, old_phone, new_phone = args[:3]
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        raise KeyError("Contact not found.")

# Функція для показу телефону контакту
@input_error
def show_phone(args, book):
    if not args:
        raise ValueError("Phone command requires a name.")
    name = args[0]
    record = book.find(name)
    if record:
        phones = ', '.join(phone.value for phone in record.phones)
        return f"{name}: {phones}"
    else:
        raise KeyError("Contact not found.")

# Функція для показу всіх контактів
@input_error
def show_all(book):
    return str(book) if book else "No contacts found."

# Функція для додавання дня народження до контакту
@input_error
def add_birthday(args, book):
    if len(args) < 2:
        raise ValueError("Add-birthday command requires name and birthday.")
    name, birthday = args[:2]
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        raise KeyError("Contact not found.")

# Функція для показу дня народження контакту
@input_error
def show_birthday(args, book):
    if not args:
        raise ValueError("Show-birthday command requires a name.")
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}: {record.birthday.value.strftime('%d.%m.%Y')}"
    elif record:
        return f"{name} has no birthday set."
    else:
        raise KeyError("Contact not found.")

# Функція для показу днів народження на наступні 7 днів
@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return '\n'.join([f"{record['name']}: {record['birthday']}" for record in upcoming_birthdays])
    else:
        return "No upcoming birthdays in the next 7 days."

# Абстрактний базовий клас для користувальницьких уявлень
class View(ABC):
    @abstractmethod
    def show_message(self, message: str):
        """Виводить повідомлення користувачу."""
        pass

    @abstractmethod
    def get_input(self, prompt: str = "") -> str:
        """Отримує ввід від користувача."""
        pass

    @abstractmethod
    def display_contacts(self, contacts: str):
        """Відображає список контактів."""
        pass

    @abstractmethod
    def display_help(self, commands: str):
        """Відображає інформацію про доступні команди."""
        pass

# Конкретна реалізація консольного інтерфейсу
class ConsoleView(View):
    def show_message(self, message: str):
        print(message)

    def get_input(self, prompt: str = "") -> str:
        return input(prompt)

    def display_contacts(self, contacts: str):
        print(contacts)

    def display_help(self, commands: str):
        print(commands)

# Основна функція програми
def main(view: View):
    # Завантажуємо адресну книгу з файлу при запуску
    book = load_data()

    view.show_message("Welcome to the assistant bot!")
    while True:
        user_input = view.get_input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            # Зберігаємо адресну книгу у файл перед виходом
            save_data(book)
            view.show_message("Good bye!")
            break
        elif command == "hello":
            view.show_message("How can I help you?")
        elif command == "add":
            result = add_contact(args, book)
            view.show_message(result)
        elif command == "change":
            result = change_contact(args, book)
            view.show_message(result)
        elif command == "phone":
            result = show_phone(args, book)
            view.show_message(result)
        elif command == "all":
            result = show_all(book)
            view.display_contacts(result)
        elif command == "add-birthday":
            result = add_birthday(args, book)
            view.show_message(result)
        elif command == "show-birthday":
            result = show_birthday(args, book)
            view.show_message(result)
        elif command == "birthdays":
            result = birthdays(args, book)
            view.show_message(result)
        elif command == "help":
            help_text = "Available commands: hello, add, change, phone, all, add-birthday, show-birthday, birthdays, close, exit"
            view.display_help(help_text)
        else:
            view.show_message("Invalid command. Type 'help' to see the list of available commands.")

# Точка входу програми
if __name__ == "__main__":
    console_view = ConsoleView()
    main(console_view)