from collections import UserDict
from datetime import datetime
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if len(value) < 3:
            raise ValueError(f"Name '{value}' was not added. It must be at least 3 characters long.")
        else:
            super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError(f"Phone number {value} was not added. It must be 10 digits")
        else:
            super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(parsed_date)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name: str) -> None:
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"

    def add_phone(self, contact_number: str):
        self.phones.append(Phone(contact_number))

    def edit_phone(self, old_number: str, new_number: str):
        matches = [phone for phone in self.phones if phone.value == old_number]

        if matches:
            matches[0].value = new_number
        else:
            print(f"Phone {old_number} not found")

    def find_phone(self, contact_number: str):
        found_phones = [phone for phone in self.phones if phone.value == contact_number]
        return found_phones[0].value if found_phones else None

    def remove_phone(self, contact_number: str):
        phone_to_remove = None
        for phone in self.phones:
            if phone.value == contact_number:
                phone_to_remove = phone
                break

        if phone_to_remove:
            self.phones.remove(phone_to_remove)
            print(f"Phone {contact_number} removed")
        else:
            print(f"Phone {contact_number} not found")

    def add_birthday(self, birthday_str: str):
        if self.birthday is None:
            self.birthday = Birthday(birthday_str)
        else:
            raise Exception(f"A birthday is already set for {self.name.value}. Current birthday: {self.birthday}")

    def show_birthday(self):
        if self.birthday:
            return str(self.birthday)
        else:
            return f"No birthday set for {self.name.value}"


class AddressBook(UserDict):

    def __str__(self):
        if len(self.data) == 0:
            return "No records"
        return "\n".join(f"{value}" for key, value in self.data.items())

    def add_record(self, record_to_add):
        self[record_to_add.name.value] = record_to_add

    def find(self, contact_name: str):
        return self.data.get(contact_name)

    def delete(self, contact_name: str):
        if contact_name in self.data:
            del self[contact_name]
            print(f"Contact {contact_name} deleted")
        else:
            print(f"Contact {contact_name} not found")

    def get_upcoming_birthdays(self, days: int = 7):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday < days:
                    upcoming_birthdays.append(record)

        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)

    return inner


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_str, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    record.add_birthday(birthday_str)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    return record.show_birthday()


@input_error
def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    return "\n".join(str(record) for record in upcoming_birthdays)


@input_error
def edit_phone(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    record.edit_phone(old_phone, new_phone)
    return f"Phone number updated for {name}."


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    return f"Phones for {name}: " + "; ".join(p.value for p in record.phones)


def parse_input(user_input):
    return user_input.split()


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        save_data(book)
        user_input = input("Enter a command: ")
        try:
            command, *args = parse_input(user_input)
        except ValueError:
            command = None
            args = None

        match command:
            case "close" | "exit":
                print("Good bye!")
                break

            case "hello":
                print("How can I help you?")

            case "add":
                print(add_contact(args, book))

            case "change":
                print(edit_phone(args, book))

            case "phone":
                print(show_phone(args, book))

            case "all":
                print(book)

            case "add-birthday":
                print(add_birthday(args, book))

            case "show-birthday":
                print(show_birthday(args, book))

            case "birthdays":
                print(birthdays(book))

            case _:
                print("Invalid command.")


if __name__ == "__main__":
    main()
